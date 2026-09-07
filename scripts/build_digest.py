#!/usr/bin/env python
"""Stage 2: raw candidates -> dedup -> freshness -> filters -> score -> select -> markdown."""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys
from collections import Counter
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from digestbot import config, dedup, enrich, freshness, render, score, state, text  # noqa: E402
from digestbot.filters import Filters, compile_list  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--outdir", default="digest")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-enrich", action="store_true")
    ap.add_argument("--comments", default=None,
                    help="JSON map id -> {what, why, tags, angle, gloss, angle_line}")
    ap.add_argument("--selection-out", default=None)
    ap.add_argument("--fetch-budget", type=int, default=700,
                    help="max uncached article fetches for full-text extraction")
    ap.add_argument("--no-state", action="store_true",
                    help="skip the cross-week store (useful for the very first run)")
    ap.add_argument("--name", default=None)
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    ed = config.editorial()
    if args.limit:
        ed["target_total"] = args.limit
    fl = Filters(config.blocklists())
    banned = compile_list(config.blocklists().get("comment_banned"))
    repo_policy = config.repo_policy()

    raw = json.loads(pathlib.Path(args.raw).read_text(encoding="utf-8"))
    start = datetime.fromisoformat(raw["window_start"])
    end = datetime.fromisoformat(raw["window_end"])
    now = datetime.now(timezone.utc)
    items = raw["items"]
    curated = set(raw.get("curated_urls") or [])
    logging.info("loaded %d raw items, %d curated newsletter URLs", len(items), len(curated))

    store = None if args.no_state else state.Store()
    if store:
        store.note_seen([i["id"] for i in items], now)
        store.note_source_poll(sorted({i.get("source_id", "") for i in items}), now)

    # 1. Collapse surfaces.
    items = dedup.deduplicate(items)
    dedup.attach_thread_signals(items)

    # 2. Freshness admission.
    counters = freshness.new_counters()
    rejected: Counter = Counter()
    hard_drops: list[dict] = []
    fresh = []
    for it in items:
        reason = freshness.admit(it, start, end, store, ed["freshness"], now, counters)
        if reason:
            rejected[reason] += 1
            it["reject"] = reason
            hard_drops.append(it)
        else:
            fresh.append(it)
    logging.info("freshness: %d in window, %d rejected", len(fresh), len(items) - len(fresh))

    # 3. Cross-week repost check.
    if store:
        weeks = ed["freshness"]["cross_week_dedup_weeks"]
        kept = []
        for it in fresh:
            if store.seen_url(it["id"], weeks):
                rejected["repost"] += 1
                it["reject"] = "repost"
                hard_drops.append(it)
                continue
            kept.append(it)
        fresh = kept

    # 4. Cheap pre-rank so full-text fetching is spent on plausible candidates.
    scfg = ed["scoring"]
    for it in fresh:
        it["flags"] = it.get("flags", {})
        it["in_newsletter"] = (it.get("canonical_url") or it["url"]) in curated
        score.score_item(it, fl, scfg, start, end)
    fresh.sort(key=lambda i: -i["score"])
    hydrate_pool = fresh[: max(args.fetch_budget * 3, ed["target_total"] * 8)]
    text.hydrate(hydrate_pool, budget=args.fetch_budget)

    # 5. Hard filters (most need the body text fetched above).
    survivors = []
    for it in fresh:
        reason, flags = None, {}
        reason, flags = _screen(it, fl, repo_policy, ed)
        it["flags"].update(flags)
        if reason:
            rejected[reason] += 1
            it["reject"] = reason
            hard_drops.append(it)
            continue
        survivors.append(it)
    logging.info("filters: %d survivors, %d dropped %s",
                 len(survivors), len(fresh) - len(survivors),
                 dict(sorted(rejected.items(), key=lambda kv: -kv[1])[:10]))

    # 6. Entities, clustering, final scoring, routing.
    vocab = score.build_vocab(config.feeds(), config.releases())
    for it in survivors:
        it["entity"] = score.entity_of(it, vocab)
    for it in survivors:
        score.score_item(it, fl, scfg, start, end)
    score.cluster(survivors, scfg)

    if store:
        recent = store.recent_simhashes(weeks=1)
        for it in survivors:
            if any(score.hamming(it["simhash"], h) <= 3 for h, _ in recent):
                it["flags"]["repeat_cluster"] = True
                it["flags"]["followup"] = True

    novelty_sources = _novelty_sources(store)
    for it in survivors:
        it["novelty"] = _is_novel(it, novelty_sources)
        score.score_item(it, fl, scfg, start, end)
        it["section_key"] = score.classify(it, fl, ed)

    # Off-topic gate runs after TOP is final.
    gate = scfg["top_gate"]
    on_topic = []
    for it in survivors:
        # Judge relevance only where there is text to judge. An item from a
        # high-authority curated feed whose body we never fetched gets the
        # benefit of the doubt at a lower bar rather than a silent drop.
        has_text = it.get("words", 0) >= 120 or len(it.get("summary", "")) >= 200
        effective_gate = gate if has_text else min(gate, 0.07)
        if it.get("lang", "en") != "en":
            # The topic vocabulary is English-biased by construction, which is the
            # very bias the protected non-English quota exists to counter. Judging
            # a Chinese post by how many English keywords it contains would empty
            # that bucket every week.
            effective_gate = min(effective_gate, gate / 2)
        if it["components"]["TOP"] < effective_gate and it["source_kind"] != "release":
            rejected["off_topic"] += 1
            it["reject"] = "off_topic"
            hard_drops.append(it)
            continue
        on_topic.append(it)
    logging.info("topic gate: %d pass, %d off-topic", len(on_topic),
                 len(survivors) - len(on_topic))

    # Watchlist candidates are ranked on inverted engagement.
    for it in on_topic:
        if it["section_key"] == "watchlist":
            wl = next(s for s in ed["sections"] if s["key"] == "watchlist")
            if it["components"]["TOP"] < wl.get("min_top", 0.35) or \
                    it.get("orig_class") != wl.get("require_orig", "primary"):
                it["section_key"] = "deep"
            else:
                score.score_item(it, fl, scfg, start, end, inverted_eng=True)

    # 7. Selection under quotas.
    sections_ordered, leftovers = score.select(on_topic, ed)
    section_titles = {s["key"]: s["title"] for s in ed["sections"]}
    sections = [(section_titles[k], group) for k, group in sections_ordered]
    selected = [i for _, g in sections for i in g]

    # 8. Comments.
    if args.comments:
        overrides = json.loads(pathlib.Path(args.comments).read_text(encoding="utf-8"))
        missing = []
        for it in selected:
            o = overrides.get(it["id"])
            if o and o.get("what"):
                it.update({k: o.get(k, it.get(k)) for k in
                           ("what", "why", "tags", "angle", "gloss", "angle_line", "more")})
            else:
                missing.append(it)
        if missing:
            logging.warning("%d selected items have no supplied comment", len(missing))
            if args.no_enrich:
                for it in missing:
                    enrich._fallback(it)
            else:
                enrich.enrich(missing, banned,
                              angle_top=ed["output"]["podcast_angle_top"])
    elif args.no_enrich:
        for it in selected:
            enrich._fallback(it)
    else:
        enrich.enrich(selected, banned, angle_top=ed["output"]["podcast_angle_top"])

    # 9. Render.
    health = state.load_health()
    meta = {
        "start": start, "end": end,
        "n_raw": len(raw["items"]), "n_unique": len(items),
        "n_feeds": len(config.feeds()),
        "n_feeds_alive": len(config.feeds()) - len(state.dead_feeds(health)),
        "n_subreddits": len(config.community().get("reddit", {}).get("subreddits", [])),
        "n_repos": len(repo_policy),
        "rejected": dict(rejected),
        "langs": Counter(i.get("lang", "en") for i in selected),
        "dead_feeds": state.dead_feeds(health),
    }

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = args.name or end.date().isoformat()
    (outdir / f"{stem}.md").write_text(render.render(sections, meta, ed), encoding="utf-8")
    logging.info("wrote %s", outdir / f"{stem}.md")

    out_cfg = ed.get("output", {})
    if out_cfg.get("short_digest"):
        (outdir / f"{stem}-short.md").write_text(
            render.render_short(sections, meta, out_cfg.get("short_count", 15)),
            encoding="utf-8")
    if out_cfg.get("rejected_log"):
        near = [i for i in leftovers
                if 35 <= (i.get("base", 0) + i.get("bonus", 0) - i.get("penalty", 0))
                < ed["admit_threshold"]][: out_cfg.get("rejected_near_miss", 50)]
        drops = sorted(hard_drops, key=lambda i: -(i.get("source_weight", 0)))[
            : out_cfg.get("rejected_hard_drops", 20)]
        for i in near:
            i["score"] = i.get("base", 0) + i.get("bonus", 0) - i.get("penalty", 0)
        (outdir / f"{stem}-rejected.md").write_text(
            render.render_rejected(near, drops, dict(rejected), meta), encoding="utf-8")

    if args.selection_out:
        sel = pathlib.Path(args.selection_out)
        sel.parent.mkdir(parents=True, exist_ok=True)
        sel.write_text(json.dumps(
            {"window_start": raw["window_start"], "window_end": raw["window_end"],
             "sections": [{"title": t, "items": [_slim(i) for i in g]} for t, g in sections],
             "leftovers": [_slim(i) for i in leftovers[:120]]},
            ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        logging.info("wrote %s", sel)

    if store:
        store.record(selected, stem)
        store.close()

    render.update_index(outdir)
    return 0


def _screen(it, fl, repo_policy, ed):
    from digestbot.filters import screen
    repo = (it.get("release") or {}).get("repo", "")
    return screen(it, fl, repo_policy.get(repo, {}), ed)


def _novelty_sources(store) -> set[str]:
    """Sources that have appeared in at most two prior digests count as novel."""
    if store is None:
        return set()
    rows = store.conn.execute(
        "SELECT url, COUNT(*) FROM emitted GROUP BY url HAVING COUNT(*) <= 2").fetchall()
    return {r[0] for r in rows}


def _is_novel(item: dict, novelty_sources: set[str]) -> bool:
    if item.get("release") and (item["release"].get("stars") or 0) < 2000:
        return True
    title = item.get("title", "").lower()
    if "kep-" in title or "rfc " in title or "spec draft" in title:
        return True
    return item.get("url") in novelty_sources


def _slim(item: dict) -> dict:
    keep = ("id", "title", "url", "canonical_url", "domain", "source_id", "source_title",
            "source_kind", "category", "lang", "published", "section", "section_key",
            "entity", "cluster_id", "cluster_rank", "score", "final", "base", "bonus",
            "penalty", "components", "orig_class", "flags", "tags", "what", "why",
            "gloss", "angle", "angle_line", "words", "release", "engagement",
            "discussions", "also_seen", "headline", "summary")
    return {k: item[k] for k in keep if k in item}


if __name__ == "__main__":
    raise SystemExit(main())
