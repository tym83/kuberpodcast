"""Markdown rendering: the full digest, the short show-notes file and the rejected log."""
from __future__ import annotations

import logging
import pathlib
import re
from datetime import datetime

log = logging.getLogger("digestbot.render")

LANG_LABEL = {"en": "EN", "ru": "RU", "zh": "ZH", "ja": "JA", "ko": "KO",
              "de": "DE", "fr": "FR", "es": "ES", "pt": "PT", "pl": "PL",
              "nl": "NL", "it": "IT", "tr": "TR"}
# Every non-English, non-Russian title gets a Russian gloss line.
NEEDS_GLOSS = set(LANG_LABEL) - {"en", "ru"}

KIND_LABEL = {"feed": "blog", "release": "release", "hn": "discussion",
              "reddit": "discussion", "lobsters": "discussion", "devto": "blog"}

FLAG_LABEL = {
    "breaking_change": "breaking",
    "security": "CVE",
    "incident": "постмортем",
    "benchmark_numbers": "бенчмарк",
    "contested": "спорно",
    "updated": "обновлено",
    "late": "догоняющее",
    "followup": "развитие темы",
    "paywalled": "платно",
    "video": "видео",
    "old_material": "старый материал",
}
FLAG_ORDER = ["security", "breaking_change", "incident", "benchmark_numbers", "contested",
              "updated", "followup", "late", "old_material", "paywalled", "video"]


def _slug(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", (text or "").lower(), flags=re.UNICODE)
    return re.sub(r"\s+", "-", s.strip())


def _clean_title(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).replace("[", "⟦").replace("]", "⟧").strip()


def _date(item: dict) -> str:
    dt = item.get("_effective_dt") or item.get("published")
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return ""
    return dt.strftime("%Y-%m-%d") if dt else ""


def _flags(item: dict) -> str:
    flags = item.get("flags", {})
    labels = [f"[{FLAG_LABEL[k]}]" for k in FLAG_ORDER if flags.get(k) and k in FLAG_LABEL]
    return " " + " ".join(labels[:3]) if labels else ""


def _discussion_links(item: dict, limit: int = 4) -> list[str]:
    out = []
    for d in sorted(item.get("discussions", []),
                    key=lambda d: -((d.get("score") or 0) + (d.get("comments") or 0))):
        url = d.get("url")
        if not url or url == item.get("url"):
            continue
        label = {"hn": "HN", "reddit": "Reddit", "lobsters": "Lobsters"}.get(
            d.get("kind"), d.get("kind", "тред"))
        if d.get("kind") == "reddit" and item.get("engagement", {}).get("reddit_sub"):
            label = f"r/{item['engagement']['reddit_sub']}"
        parts = ""
        if d.get("score"):
            parts = f" {d['score']}↑"
            if d.get("comments"):
                parts += f"/{d['comments']}💬"
        elif d.get("comments"):
            parts = f" {d['comments']}💬"
        out.append(f"[{label}{parts}]({url})")
        if len(out) >= limit:
            break
    return out


def render_entry(n: int, item: dict, section_title: str, with_angle: bool = False) -> str:
    lines: list[str] = []
    title = _clean_title(item.get("title") or item.get("url"))
    star = "⭐ " if item.get("headline") else ""
    lines.append(f"### {n}. {star}{title}{_flags(item)}")

    gloss = (item.get("gloss") or "").strip()
    if gloss and item.get("lang") in NEEDS_GLOSS:
        lines.append(f"*({gloss})*")

    kind = KIND_LABEL.get(item.get("source_kind"), item.get("source_kind", "blog"))
    if item.get("flags", {}).get("incident"):
        kind = "postmortem"
    elif item.get("flags", {}).get("security") and item.get("source_kind") != "release":
        kind = "advisory"
    source = item.get("source_title") or item.get("source_id", "")
    domain = item.get("domain") or ""
    # Always link the canonical form: the raw feed URL carries tracking params.
    url = item.get("canonical_url") or item.get("url", "")
    meta = f"`{kind}` · `{section_title}` · {source} · {_date(item)} · **[{domain}]({url})**"
    if item.get("lang", "en") != "en":
        meta += f" · `{LANG_LABEL.get(item['lang'], item['lang'].upper())}`"
    lines.append(meta)

    what = (item.get("what") or "").strip()
    why = (item.get("why") or "").strip()
    if what:
        lines.append(f"**Что внутри:** {what}")
    if why:
        lines.append(f"**Почему важно:** {why}")
    if not what and not why and item.get("comment"):
        lines.append(item["comment"].strip())
    if with_angle and item.get("angle_line"):
        lines.append(f"**Подкаст-угол:** {item['angle_line'].strip()}")

    extra = []
    for label, u in (item.get("more") or []):
        extra.append(f"[{label}]({u})")
    if item.get("also_seen"):
        extra.append("также у: " + ", ".join(item["also_seen"][:3]))
    if extra:
        lines.append("**Ещё:** " + " · ".join(extra))

    footer = []
    tags = item.get("tags") or []
    if tags:
        footer.append("`теги: " + ", ".join(tags[:5]) + "`")
    footer.append(f"`score {int(round(item.get('final', item.get('score', 0))))}`")
    footer += _discussion_links(item)
    lines.append(" · ".join(footer))
    return "\n".join(lines)


def render(sections, meta: dict, ed: dict) -> str:
    total = sum(len(g) for _, g in sections)
    target = ed.get("target_total", 100)
    start, end = meta["start"], meta["end"]

    out = [f"# Дайджест за {start.date().isoformat()} — {end.date().isoformat()}", ""]
    head = (f"Окно: {start.strftime('%Y-%m-%dT%H:%MZ')} — {end.strftime('%Y-%m-%dT%H:%MZ')} · "
            f"собрано {meta['n_raw']} кандидатов · ")
    if meta.get("n_unique"):
        head += f"уникальных {meta['n_unique']} · "
    head += f"отобрано {total}"
    if total < target:
        head += f"  \n**Отобрано {total} из {target} — порог не понижался.**"
    out.append(head + "  ")
    out.append(f"Источники: {meta['n_feeds']} RSS (живых {meta['n_feeds_alive']}), "
               f"{meta['n_subreddits']} subreddit, Hacker News, Lobsters, "
               f"{meta['n_repos']} репозиториев  ")
    if meta.get("rejected"):
        top = sorted(meta["rejected"].items(), key=lambda kv: -kv[1])[:8]
        out.append("Отброшено по фильтрам: "
                   + ", ".join(f"{k} {v}" for k, v in top) + "  ")
    langs = meta.get("langs", {})
    if langs:
        out.append("Языки: " + ", ".join(
            f"{LANG_LABEL.get(k, k.upper())} {v}"
            for k, v in sorted(langs.items(), key=lambda kv: -kv[1])) + "  ")
    out.append("")
    out.append("> Заголовки — в оригинале. Комментарии — на русском: "
               "`Что внутри` — факты, `Почему важно` — последствие для эксплуатации.")
    out.append("")

    # Numbering is continuous so "top 100" is literally true.
    numbered: list[tuple[int, dict, str]] = []
    per_section: list[tuple[str, list[tuple[int, dict]]]] = []
    n = 0
    for title, group in sections:
        rows = []
        for item in group:
            n += 1
            numbered.append((n, item, title))
            rows.append((n, item))
        per_section.append((title, rows))

    headline = [t for t in numbered if t[1].get("headline")]
    headline.sort(key=lambda t: -t[1].get("final", 0))
    if headline:
        out.append("## ⭐ Главное недели")
        out.append("")
        for num, item, sect in headline:
            out.append(f"{num}. **{_clean_title(item['title'])}** — "
                       f"{(item.get('why') or item.get('comment') or '').strip()[:180]} "
                       f"[→]({item.get('canonical_url') or item['url']})")
        out.append("")

    out.append("## Содержание")
    out.append("")
    n = 0
    for title, group in sections:
        if not group:
            continue
        first, last = n + 1, n + len(group)
        n = last
        out.append(f"- [{title}](#{_slug(title)}) — {first}–{last}")
    out.append("")
    out.append("---")
    out.append("")

    angle_top = ed.get("output", {}).get("podcast_angle_top", 20)
    for title, rows in per_section:
        if not rows:
            continue
        out.append(f"## {title}")
        out.append("")
        for num, item in rows:
            out.append(render_entry(num, item, title, with_angle=num <= angle_top))
            out.append("")

    out.append("---")
    out.append("")
    dead = meta.get("dead_feeds") or []
    if dead:
        out.append(f"<sub>Мёртвые источники ({len(dead)}): "
                   + ", ".join(dead[:20]) + ("…" if len(dead) > 20 else "") + "</sub>")
        out.append("")
    out.append("<sub>Собрано автоматически: `scripts/collect_raw.py` → "
               "`scripts/build_digest.py`. Источники — `sources/`. "
               "Отклонённые кандидаты — в файле `*-rejected.md`.</sub>")
    out.append("")
    return "\n".join(out)


def render_short(sections, meta: dict, count: int = 15) -> str:
    flat = [i for _, g in sections for i in g]
    flat.sort(key=lambda i: -i.get("final", 0))
    out = [f"# Шорт-лист — {meta['end'].date().isoformat()}", "",
           f"{min(count, len(flat))} материалов для шоу-нот. "
           f"Полная версия — `{meta['end'].date().isoformat()}.md`.", ""]
    for n, item in enumerate(flat[:count], 1):
        line = (item.get("why") or item.get("what") or item.get("comment") or "").strip()
        line = re.sub(r"\s+", " ", line)
        if len(line) > 200:
            line = line[:197].rstrip() + "…"
        url = item.get("canonical_url") or item["url"]
        out.append(f"{n}. **[{_clean_title(item['title'])}]({url})** — {line}")
    out.append("")
    return "\n".join(out)


def render_rejected(near_miss: list[dict], hard_drops: list[dict],
                    counts: dict, meta: dict) -> str:
    out = [f"# Отклонённые кандидаты — {meta['end'].date().isoformat()}", "",
           "Единственный способ заметить ошибку в фильтрах — смотреть, что они выбросили.", ""]
    out.append("## Сводка по причинам")
    out.append("")
    out.append("| причина | штук |")
    out.append("|---|---:|")
    for reason, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        out.append(f"| `{reason}` | {n} |")
    out.append("")

    out.append("## Почти прошли (score ниже порога)")
    out.append("")
    for it in near_miss:
        out.append(f"- **{int(round(it.get('score', 0)))}** · "
                   f"[{_clean_title(it['title'])}]({it.get('canonical_url') or it['url']}) — "
                   f"`{it.get('source_title') or it.get('source_id')}`, "
                   f"TOP {it.get('components', {}).get('TOP', 0)}")
    out.append("")

    out.append("## Отброшены жёсткими фильтрами (самые заметные)")
    out.append("")
    for it in hard_drops:
        out.append(f"- `{it.get('reject')}` · "
                   f"[{_clean_title(it['title'])}]({it.get('canonical_url') or it['url']}) — "
                   f"`{it.get('source_title') or it.get('source_id')}`")
    out.append("")
    return "\n".join(out)


def update_index(outdir: pathlib.Path) -> None:
    files = sorted((p for p in outdir.glob("*.md")
                    if p.name != "README.md" and not p.stem.endswith(("-short", "-rejected"))),
                   reverse=True)
    lines = ["# Дайджесты", "", "Еженедельные подборки, свежие сверху.", ""]
    for p in files:
        summary = ""
        try:
            for line in p.read_text(encoding="utf-8").splitlines()[:8]:
                if line.startswith("Окно:"):
                    summary = line.strip().rstrip(" ")
                    break
        except OSError:
            pass
        extras = []
        for suffix, label in (("-short", "шорт-лист"), ("-rejected", "отклонённые")):
            if (outdir / f"{p.stem}{suffix}.md").exists():
                extras.append(f"[{label}]({p.stem}{suffix}.md)")
        line = f"- [{p.stem}]({p.name})"
        if extras:
            line += " · " + " · ".join(extras)
        if summary:
            line += f"  \n  <sub>{summary}</sub>"
        lines.append(line)
    lines.append("")
    (outdir / "README.md").write_text("\n".join(lines), encoding="utf-8")
    log.info("index updated: %d digests", len(files))
