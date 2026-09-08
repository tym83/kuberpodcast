"""Collapse the same story arriving from several surfaces into one entry."""
from __future__ import annotations

import logging
from collections import defaultdict

log = logging.getLogger("digestbot.dedup")

# Which surface deserves to own the canonical entry when URLs collide.
KIND_RANK = {"feed": 5, "release": 5, "hn": 2, "lobsters": 2, "reddit": 2, "devto": 1}


def _merge(primary: dict, other: dict) -> None:
    """Fold `other` into `primary`, preserving every signal and discussion link."""
    for key, value in (other.get("engagement") or {}).items():
        cur = primary.setdefault("engagement", {}).get(key)
        if isinstance(value, (int, float)) and isinstance(cur, (int, float)):
            primary["engagement"][key] = max(cur, value)
        elif cur in (None, "", 0):
            primary["engagement"][key] = value

    seen = {d.get("url") for d in primary.get("discussions", [])}
    for d in other.get("discussions", []):
        if d.get("url") and d["url"] not in seen:
            primary.setdefault("discussions", []).append(d)
            seen.add(d["url"])

    label = other.get("source_title") or other.get("source_id")
    also = primary.setdefault("also_seen", [])
    if label and label != primary.get("source_title") and label not in also:
        also.append(label)

    if len(other.get("summary", "")) > len(primary.get("summary", "")):
        primary["summary"] = other["summary"]
    if other.get("published") and (not primary.get("published")
                                   or other["published"] < primary["published"]):
        primary["published"] = other["published"]
    primary["surfaces"] = sorted(
        set(primary.get("surfaces", [primary["source_kind"]])) | {other["source_kind"]})


def pick_canonical(group: list[dict]) -> dict:
    """§6.4: primary source first, then body length, then source authority.

    A thread never wins over a reachable article — unless the thread *is* the
    story (self-post, or an argument with more comments than points).
    """
    if len(group) == 1:
        return group[0]

    articles = [i for i in group if i["source_kind"] not in ("hn", "reddit", "lobsters")]
    threads = [i for i in group if i["source_kind"] in ("hn", "reddit", "lobsters")]

    if articles:
        primaries = [i for i in articles
                     if i["source_kind"] == "release"
                     or i.get("category") in ("foundation", "project", "person", "vendor", "cloud")]
        pool = primaries or articles
        fat = [i for i in pool if i.get("words", 0) >= 600]
        if fat:
            return max(fat, key=lambda i: i.get("words", 0))
        return max(pool, key=lambda i: (i.get("source_weight", 0), i.get("words", 0),
                                        len(i.get("summary", ""))))

    best = max(threads, key=lambda i: (
        (i.get("engagement", {}).get("hn_points") or 0)
        + (i.get("engagement", {}).get("reddit_score") or 0)))
    best["thread_is_canonical"] = True
    return best


def deduplicate(items: list[dict]) -> list[dict]:
    by_url: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        by_url[it.get("canonical_url") or it["url"]].append(it)

    out: list[dict] = []
    for group in by_url.values():
        primary = pick_canonical(group)
        primary["surfaces"] = sorted({i["source_kind"] for i in group})
        for other in group:
            if other is not primary:
                _merge(primary, other)
        out.append(primary)

    before = len(out)
    out = _collapse_identical_titles(out)
    log.info("dedup: %d raw -> %d unique (%d collapsed by title)",
             len(items), len(out), before - len(out))
    return out


def _collapse_identical_titles(items: list[dict]) -> list[dict]:
    """Same normalised title from the same source is the same thing said twice —
    GitHub issue feeds in particular repeat a title across separate issues."""
    from .score import norm_title

    seen: dict[tuple[str, str], dict] = {}
    out = []
    for it in items:
        key = (it.get("source_id", ""), norm_title(it.get("title", "")))
        if not key[1]:
            out.append(it)
            continue
        first = seen.get(key)
        if first is None:
            seen[key] = it
            out.append(it)
        else:
            _merge(first, it)
    return out


def attach_thread_signals(items: list[dict]) -> None:
    """A discussion whose comments outweigh its points is an argument, not applause."""
    for it in items:
        e = it.get("engagement", {})
        points = (e.get("hn_points") or 0) + (e.get("reddit_score") or 0)
        comments = (e.get("hn_comments") or 0) + (e.get("reddit_comments") or 0)
        if points and comments / points > 0.8:
            it.setdefault("flags", {})["contested"] = True
