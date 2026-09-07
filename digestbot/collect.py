"""Fetchers. Every fetcher returns a list of raw item dicts sharing one schema."""
from __future__ import annotations

import concurrent.futures as cf
import json
import logging
import os
import re
import time
from datetime import datetime, timezone

import feedparser

from .util import (
    BROWSER_UA,
    canonical_url,
    parse_loose_date,
    detect_lang,
    domain_of,
    get,
    item_id,
    new_session,
    parse_struct_time,
    strip_html,
    to_utc,
)

log = logging.getLogger("digestbot.collect")


def _mk(**kw) -> dict:
    """Build an item with every field present so downstream code never KeyErrors."""
    url = kw.get("url", "")
    canon = canonical_url(url)
    item = {
        "id": item_id(canon or url),
        "title": (kw.get("title") or "").strip(),
        "url": url,
        "canonical_url": canon,
        "domain": domain_of(canon or url),
        "source_id": kw.get("source_id", ""),
        "source_title": kw.get("source_title", ""),
        "source_kind": kw.get("source_kind", "feed"),
        "category": kw.get("category", "other"),
        "lang": kw.get("lang", "en"),
        "source_weight": float(kw.get("source_weight", 2)),
        "published": kw.get("published"),
        "summary": kw.get("summary", ""),
        "engagement": kw.get("engagement", {}),
        "release": kw.get("release"),
        "discussions": kw.get("discussions", []),
    }
    return item


# ── RSS / Atom ───────────────────────────────────────────────────────────────

def fetch_feeds(feeds: list[dict], start, end, workers: int = 16,
                probes: list | None = None) -> list[dict]:
    """`probes` collects a per-feed health record: a feed that 404s or parses to
    zero entries must be visible, not silently absent from the digest."""
    session = new_session(browser_ua=True)
    out: list[dict] = []

    def one(feed: dict) -> list[dict]:
        r = get(session, feed["url"], timeout=25, retries=1)
        if r is None or r.status_code >= 400:
            log.warning("feed %-22s HTTP %s", feed["id"],
                        r.status_code if r is not None else "ERR")
            if probes is not None:
                probes.append({"id": feed["id"], "ok": False, "items": 0,
                               "status": r.status_code if r is not None else None})
            return []
        parsed = feedparser.parse(r.content)
        items = []
        for e in parsed.entries[:60]:
            pub = parse_struct_time(
                getattr(e, "published_parsed", None) or getattr(e, "updated_parsed", None)
            )
            if pub is None:
                pub = (parse_loose_date(getattr(e, "published", None))
                       or parse_loose_date(getattr(e, "updated", None))
                       or parse_loose_date(getattr(e, "date", None)))
            # Feeds with no usable date are kept only if the feed is small and
            # fresh-by-position; otherwise they poison the freshness guarantee.
            if pub is None or not (start <= pub <= end):
                continue
            link = getattr(e, "link", "") or ""
            if not link:
                continue
            summary = strip_html(
                getattr(e, "summary", "")
                or (e.content[0].value if getattr(e, "content", None) else "")
            )
            title = strip_html(getattr(e, "title", ""), 300)
            items.append(
                _mk(
                    title=title,
                    url=link,
                    source_id=feed["id"],
                    source_title=feed["title"],
                    source_kind="feed",
                    category=feed.get("category", "other"),
                    lang=detect_lang(title + " " + summary, feed.get("lang", "en")),
                    source_weight=feed.get("weight", 2),
                    published=pub.isoformat(),
                    summary=summary,
                )
            )
        if probes is not None:
            probes.append({"id": feed["id"], "ok": bool(parsed.entries),
                           "items": len(items), "status": r.status_code,
                           "entries": len(parsed.entries)})
        if not parsed.entries:
            log.warning("feed %-22s HTTP %s but parsed 0 entries",
                        feed["id"], r.status_code)
        else:
            log.info("feed %-22s %2d items in window", feed["id"], len(items))
        return items

    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for res in pool.map(one, feeds):
            out.extend(res)
    return out


# ── Hacker News (Algolia) ────────────────────────────────────────────────────

HN_API = "https://hn.algolia.com/api/v1/search"


def fetch_hackernews(cfg: dict, start, end) -> list[dict]:
    session = new_session()
    start_ts, end_ts = int(start.timestamp()), int(end.timestamp())
    seen: dict[str, dict] = {}

    def collect(params: dict, min_points: int, tag: str):
        r = get(session, HN_API, params=params, timeout=25)
        if r is None or r.status_code != 200:
            log.warning("hn %s HTTP %s", tag, r.status_code if r else "ERR")
            return
        for h in r.json().get("hits", []):
            points = h.get("points") or 0
            ncomments = h.get("num_comments") or 0
            if points < min_points and ncomments < cfg.get("min_comments", 15):
                continue
            hn_url = f"https://news.ycombinator.com/item?id={h['objectID']}"
            url = h.get("url") or hn_url
            title = h.get("title") or h.get("story_title") or ""
            if not title:
                continue
            created = h.get("created_at")
            try:
                pub = to_utc(datetime.fromisoformat(created.replace("Z", "+00:00")))
            except (AttributeError, ValueError):
                continue
            if not (start <= pub <= end):
                continue
            key = canonical_url(url)
            prev = seen.get(key)
            if prev and (prev["engagement"].get("hn_points", 0) >= points):
                continue
            seen[key] = _mk(
                title=strip_html(title, 300),
                url=url,
                source_id="hackernews",
                source_title="Hacker News",
                source_kind="hn",
                category="community",
                lang=detect_lang(title, "en"),
                source_weight=4,
                published=pub.isoformat(),
                summary=strip_html(h.get("story_text") or h.get("comment_text") or ""),
                engagement={
                    "hn_points": points,
                    "hn_comments": ncomments,
                    "hn_url": hn_url,
                },
                discussions=[{"kind": "hn", "url": hn_url,
                              "score": points, "comments": ncomments}],
            )

    # 1) everything above the front-page bar in the window
    collect(
        {
            "tags": "story",
            "numericFilters": f"created_at_i>{start_ts},created_at_i<{end_ts},"
                              f"points>={cfg.get('front_page_min_points', 150)}",
            "hitsPerPage": 200,
        },
        cfg.get("front_page_min_points", 150),
        "frontpage",
    )
    # 2) topic queries at a lower bar
    for q in cfg.get("queries", []):
        collect(
            {
                "query": q,
                "tags": "story",
                "numericFilters": f"created_at_i>{start_ts},created_at_i<{end_ts}",
                "hitsPerPage": 60,
            },
            cfg.get("min_points", 60),
            q,
        )
        time.sleep(0.15)

    log.info("hackernews %d stories", len(seen))
    return list(seen.values())


# ── Reddit ───────────────────────────────────────────────────────────────────

def _reddit_token() -> str | None:
    cid, secret = os.getenv("REDDIT_CLIENT_ID"), os.getenv("REDDIT_CLIENT_SECRET")
    if not (cid and secret):
        return None
    s = new_session()
    try:
        r = s.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(cid, secret),
            data={"grant_type": "client_credentials"},
            timeout=20,
        )
        if r.status_code == 200:
            return r.json().get("access_token")
        log.warning("reddit oauth HTTP %s", r.status_code)
    except Exception as exc:  # noqa: BLE001
        log.warning("reddit oauth failed: %s", exc)
    return None


def fetch_reddit(cfg: dict, start, end) -> list[dict]:
    subs = cfg.get("subreddits", [])
    token = _reddit_token()
    out: list[dict] = []

    if token:
        session = new_session()
        session.headers["Authorization"] = f"bearer {token}"
        base = "https://oauth.reddit.com"
        for sub in subs:
            r = get(session, f"{base}/r/{sub['name']}/top",
                    params={"t": "week", "limit": 50}, timeout=25)
            if r is None or r.status_code != 200:
                log.warning("reddit r/%s HTTP %s", sub["name"],
                            r.status_code if r else "ERR")
                continue
            for child in r.json().get("data", {}).get("children", []):
                d = child.get("data", {})
                score = d.get("score", 0)
                if score < sub.get("min_score", 20):
                    continue
                pub = to_utc(datetime.fromtimestamp(d.get("created_utc", 0),
                                                    tz=timezone.utc))
                if not (start <= pub <= end):
                    continue
                permalink = "https://www.reddit.com" + d.get("permalink", "")
                url = d.get("url_overridden_by_dest") or permalink
                title = d.get("title", "")
                out.append(
                    _mk(
                        title=strip_html(title, 300),
                        url=url,
                        source_id=f"reddit/{sub['name']}",
                        source_title=f"r/{sub['name']}",
                        source_kind="reddit",
                        category="community",
                        lang=detect_lang(title, "en"),
                        source_weight=sub.get("weight", 3),
                        published=pub.isoformat(),
                        summary=strip_html(d.get("selftext", "")),
                        engagement={
                            "reddit_score": score,
                            "reddit_comments": d.get("num_comments", 0),
                            "reddit_url": permalink,
                            "reddit_ratio": d.get("upvote_ratio"),
                            "reddit_flair": d.get("link_flair_text"),
                        },
                        discussions=[{"kind": "reddit", "url": permalink,
                                      "score": score,
                                      "comments": d.get("num_comments", 0)}],
                    )
                )
            time.sleep(0.4)
        log.info("reddit (oauth) %d posts", len(out))
        return out

    # Fallback: public .rss listings. Ordered by score but scores are not exposed,
    # so rank inside the weekly top listing is used as the engagement proxy.
    log.warning("REDDIT_CLIENT_ID/SECRET not set - using public .rss fallback")
    reddit_delay = float(os.getenv("REDDIT_RSS_DELAY", "6"))
    session = new_session(browser_ua=True)
    consecutive_failures = 0
    for sub in subs:
        # Reddit rate-limits anonymous datacenter traffic hard; pace slowly and
        # back off on 429 rather than losing the whole subreddit.
        r = None
        for attempt in range(4):
            r = get(session, f"https://www.reddit.com/r/{sub['name']}/top/.rss",
                    params={"t": "week"}, timeout=25, retries=0)
            if r is not None and r.status_code == 200:
                break
            time.sleep(5 * (attempt + 1))
            r = None
        if r is None:
            consecutive_failures += 1
            log.warning("reddit r/%s rss unavailable after retries", sub["name"])
            # Reddit blocks datacenter egress wholesale rather than per-subreddit.
            # Once that is clear, stop burning minutes on the remaining listings.
            if consecutive_failures >= 3:
                log.error("reddit unreachable from this host - skipping the remaining "
                          "%d subreddits; set REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET "
                          "to use the API instead", len(subs) - subs.index(sub) - 1)
                break
            continue
        consecutive_failures = 0
        parsed = feedparser.parse(r.content)
        for rank, e in enumerate(parsed.entries[:40]):
            pub = parse_struct_time(getattr(e, "published_parsed", None)
                                    or getattr(e, "updated_parsed", None))
            if pub is None or not (start <= pub <= end):
                continue
            permalink = getattr(e, "link", "")
            title = strip_html(getattr(e, "title", ""), 300)
            body = strip_html(getattr(e, "summary", ""))
            # Link posts embed the outbound target in the RSS body.
            m = re.search(r'href="(https?://[^"]+)"[^>]*>\[link\]', getattr(e, "summary", ""))
            url = m.group(1) if m else permalink
            out.append(
                _mk(
                    title=title,
                    url=url,
                    source_id=f"reddit/{sub['name']}",
                    source_title=f"r/{sub['name']}",
                    source_kind="reddit",
                    category="community",
                    lang=detect_lang(title, "en"),
                    source_weight=sub.get("weight", 3),
                    published=pub.isoformat(),
                    summary=body,
                    engagement={"reddit_rank": rank + 1, "reddit_url": permalink},
                    discussions=[{"kind": "reddit", "url": permalink,
                                  "score": None, "comments": None}],
                )
            )
        time.sleep(reddit_delay)
    log.info("reddit (rss) %d posts", len(out))
    return out


# ── Lobsters ─────────────────────────────────────────────────────────────────

def fetch_lobsters(cfg: dict, start, end) -> list[dict]:
    session = new_session()
    out, seen = [], set()
    for tag in cfg.get("tags", []):
        r = get(session, f"https://lobste.rs/t/{tag}.json", timeout=25)
        if r is None or r.status_code != 200:
            continue
        try:
            stories = r.json()
        except json.JSONDecodeError:
            continue
        for s in stories:
            score = s.get("score", 0)
            if score < cfg.get("min_score", 10):
                continue
            try:
                pub = to_utc(datetime.fromisoformat(
                    s["created_at"].replace("Z", "+00:00")))
            except (KeyError, ValueError):
                continue
            if not (start <= pub <= end):
                continue
            url = s.get("url") or s.get("short_id_url")
            if not url or url in seen:
                continue
            seen.add(url)
            out.append(
                _mk(
                    title=strip_html(s.get("title", ""), 300),
                    url=url,
                    source_id="lobsters",
                    source_title="Lobsters",
                    source_kind="lobsters",
                    category="community",
                    lang="en",
                    source_weight=3,
                    published=pub.isoformat(),
                    summary=strip_html(s.get("description", "")),
                    engagement={"lobsters_score": score,
                                "lobsters_comments": s.get("comment_count", 0),
                                "lobsters_url": s.get("comments_url")},
                    discussions=[{"kind": "lobsters", "url": s.get("comments_url"),
                                  "score": score,
                                  "comments": s.get("comment_count", 0)}],
                )
            )
        time.sleep(0.3)
    log.info("lobsters %d stories", len(out))
    return out


# ── dev.to ───────────────────────────────────────────────────────────────────

def fetch_devto(cfg: dict, start, end) -> list[dict]:
    session = new_session()
    out, seen = [], set()
    for tag in cfg.get("tags", []):
        r = get(session, "https://dev.to/api/articles",
                params={"tag": tag, "top": 7, "per_page": 40}, timeout=25)
        if r is None or r.status_code != 200:
            continue
        for a in r.json():
            reactions = a.get("positive_reactions_count", 0)
            if reactions < cfg.get("min_reactions", 40):
                continue
            try:
                pub = to_utc(datetime.fromisoformat(
                    a["published_at"].replace("Z", "+00:00")))
            except (KeyError, ValueError):
                continue
            if not (start <= pub <= end):
                continue
            url = a.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            out.append(
                _mk(
                    title=strip_html(a.get("title", ""), 300),
                    url=url,
                    source_id="devto",
                    source_title="dev.to",
                    source_kind="devto",
                    category="community",
                    lang="en",
                    source_weight=2,
                    published=pub.isoformat(),
                    summary=strip_html(a.get("description", "")),
                    engagement={"devto_reactions": reactions,
                                "devto_comments": a.get("comments_count", 0)},
                )
            )
        time.sleep(0.2)
    log.info("dev.to %d articles", len(out))
    return out


# ── GitHub releases ──────────────────────────────────────────────────────────

def fetch_releases(groups: dict, start, end, workers: int = 12) -> list[dict]:
    session = new_session()
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    session.headers["Accept"] = "application/vnd.github+json"
    session.headers["X-GitHub-Api-Version"] = "2022-11-28"

    tasks = []
    for group, meta in groups.items():
        defaults = {k: v for k, v in meta.items() if k != "list"}
        for entry in meta.get("list", []):
            cfg = {"group": group, **defaults,
                   **(entry if isinstance(entry, dict) else {"repo": entry})}
            if cfg.get("mirror_of") or cfg.get("changelog_url"):
                # Mirrors are credited to their parent; repos with no GitHub
                # Releases are tracked through their changelog, not this poller.
                continue
            tasks.append(cfg)

    def one(cfg) -> list[dict]:
        repo, group = cfg["repo"], cfg["group"]
        r = get(session, f"https://api.github.com/repos/{repo}/releases",
                params={"per_page": 10}, timeout=25, retries=1)
        if r is None or r.status_code != 200:
            if r is not None and r.status_code not in (404,):
                log.debug("releases %s HTTP %s", repo, r.status_code)
            return []
        items = []
        # Releases come newest-first; the next entry is the previous release,
        # which is what tells a patch bump apart from a minor one.
        payload = [x for x in r.json() if not x.get("draft")]
        prev_of = {x.get("tag_name"): (payload[i + 1].get("tag_name")
                                       if i + 1 < len(payload) else None)
                   for i, x in enumerate(payload)}
        for rel in payload:
            if rel.get("draft"):
                continue
            published = rel.get("published_at")
            if not published:
                continue
            try:
                pub = to_utc(datetime.fromisoformat(published.replace("Z", "+00:00")))
            except ValueError:
                continue
            # Publication time, not tag time: a re-tagged old version still counts
            # as news only if it was published inside the window.
            if not (start <= pub <= end):
                continue
            tag = rel.get("tag_name", "")
            body = strip_html(rel.get("body") or "", 4000)
            name = rel.get("name") or tag
            items.append(
                _mk(
                    title=f"{repo} {tag}" + (f" — {name}" if name and name != tag else ""),
                    url=rel.get("html_url", ""),
                    source_id=f"gh/{repo}",
                    source_title=repo,
                    source_kind="release",
                    category="release",
                    lang="en",
                    source_weight={"patch": 4, "minor": 3, "major": 3}.get(
                        cfg.get("min_bump", "minor"), 3),
                    published=pub.isoformat(),
                    summary=body,
                    engagement={"reactions": (rel.get("reactions") or {}).get("total_count", 0)},
                    release={
                        "repo": repo,
                        "group": group,
                        "min_bump": cfg.get("min_bump", "minor"),
                        "previous_tag": prev_of.get(tag),
                        "tag": tag,
                        "name": name,
                        "prerelease": bool(rel.get("prerelease")),
                        "body_len": len(rel.get("body") or ""),
                        "assets": len(rel.get("assets") or []),
                    },
                )
            )
        return items

    out: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for res in pool.map(one, tasks):
            out.extend(res)
    # Stars are only needed for repos that actually shipped; one call each.
    shipped = sorted({i["release"]["repo"] for i in out})

    def stars(repo: str) -> tuple[str, int]:
        r = get(session, f"https://api.github.com/repos/{repo}", timeout=20, retries=0)
        if r is None or r.status_code != 200:
            return repo, 0
        return repo, r.json().get("stargazers_count", 0)

    star_map: dict[str, int] = {}
    if shipped:
        with cf.ThreadPoolExecutor(max_workers=workers) as pool:
            star_map = dict(pool.map(stars, shipped))
    for item in out:
        item["release"]["stars"] = star_map.get(item["release"]["repo"], 0)

    log.info("github releases %d in window (from %d repos, %d shipped)",
             len(out), len(tasks), len(shipped))
    return out
