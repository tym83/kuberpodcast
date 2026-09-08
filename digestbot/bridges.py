"""Sources that publish no feed at all.

Telegram, Bluesky and Google Groups carry material the RSS catalog cannot see —
Russian infrastructure channels, maintainers announcing things before they blog,
and upstream mailing-list threads. None of them offer RSS, so each is read
through the public surface it does expose.
"""
from __future__ import annotations

import html
import logging
import re
import time
from datetime import datetime, timezone

from .collect import _mk
from .util import get, new_session, strip_html, to_utc

log = logging.getLogger("digestbot.bridges")


# ── Telegram ─────────────────────────────────────────────────────────────────
# Public channels render a read-only web preview at t.me/s/<channel>. It is
# server-side HTML with datetimes, so no API key and no login are involved.

# One regex spanning a whole message proved brittle — the optional text group
# silently matched empty. Each message block is isolated first, then read.
TG_SPLIT = re.compile(r'<div class="tgme_widget_message_wrap')
TG_POST = re.compile(r'data-post="(?P<chan>[^/"]+)/(?P<id>\d+)"')
TG_TEXT = re.compile(
    r'<div class="tgme_widget_message_text[^"]*"[^>]*>(?P<text>.*?)</div>\s*(?:<div class="tgme_widget_message_(?:footer|reply_markup)|<span class="tgme_widget_message_meta)',
    re.S,
)
TG_TIME = re.compile(r'<time[^>]+datetime="(?P<dt>[^"]+)"')
TG_LINK = re.compile(r'href="(https?://[^"]+)"', re.I)


def fetch_telegram(cfg: dict, start, end) -> list[dict]:
    channels = cfg.get("channels", [])
    if not channels:
        return []
    session = new_session(browser_ua=True)
    out: list[dict] = []

    for ch in channels:
        name = ch["name"]
        r = get(session, f"https://t.me/s/{name}", timeout=25, retries=1)
        if r is None or r.status_code != 200:
            log.warning("telegram %-18s HTTP %s", name,
                        r.status_code if r else "ERR")
            continue

        count = 0
        for block in TG_SPLIT.split(r.text)[1:]:
            post = TG_POST.search(block)
            when = TG_TIME.search(block)
            if not post or not when:
                continue
            try:
                pub = to_utc(datetime.fromisoformat(when.group("dt")))
            except (TypeError, ValueError):
                continue
            if not (start <= pub <= end):
                continue
            body_match = TG_TEXT.search(block)
            body_html = body_match.group("text") if body_match else ""
            text = strip_html(body_html, 3000)
            if len(text) < 60:
                continue          # a bare forward or a picture caption
            permalink = f"https://t.me/{post.group('chan')}/{post.group('id')}"

            # A channel post is usually a pointer; the link it carries is the story.
            outbound = [u for u in TG_LINK.findall(body_html)
                        if "t.me/" not in u and "telegram." not in u]
            title = re.split(r"(?<=[.!?])\s|\n", text.strip())[0][:200].strip()
            if len(title) < 20:
                title = text[:120].strip()

            count += 1
            out.append(_mk(
                title=title,
                url=outbound[0] if outbound else permalink,
                source_id=f"tg/{name}",
                source_title=ch.get("title", f"@{name}"),
                source_kind="feed",
                category=ch.get("category", "community"),
                lang=ch.get("lang", "ru"),
                source_weight=ch.get("weight", 3),
                published=pub.isoformat(),
                summary=text,
                discussions=[{"kind": "telegram", "url": permalink,
                              "score": None, "comments": None}],
            ))
        log.info("telegram %-18s %2d posts in window", name, count)
        time.sleep(0.5)

    log.info("telegram %d posts", len(out))
    return out


# ── Bluesky ──────────────────────────────────────────────────────────────────
# The AppView API is public and unauthenticated for read access, which is the
# only social surface in this space that still is.

BSKY_FEED = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"


def fetch_bluesky(cfg: dict, start, end) -> list[dict]:
    accounts = cfg.get("accounts", [])
    if not accounts:
        return []
    session = new_session()
    out: list[dict] = []

    for acc in accounts:
        handle = acc["handle"]
        r = get(session, BSKY_FEED,
                params={"actor": handle, "limit": cfg.get("limit", 30)},
                timeout=20, retries=1)
        if r is None or r.status_code != 200:
            log.warning("bluesky %-28s HTTP %s", handle,
                        r.status_code if r else "ERR")
            continue
        try:
            payload = r.json()
        except ValueError:
            continue
        if payload.get("error"):
            log.warning("bluesky %-28s %s", handle, payload["error"])
            continue

        count = 0
        for entry in payload.get("feed", []):
            post = entry.get("post") or {}
            record = post.get("record") or {}
            # Reposts say what the account finds worth amplifying, but the text
            # belongs to someone else; only original posts are collected.
            if entry.get("reason"):
                continue
            created = record.get("createdAt")
            try:
                pub = to_utc(datetime.fromisoformat(str(created).replace("Z", "+00:00")))
            except (TypeError, ValueError):
                continue
            if not (start <= pub <= end):
                continue
            text = (record.get("text") or "").strip()
            if len(text) < 80:
                continue          # a reply or a one-liner
            link = _bsky_outbound(record) or _bsky_permalink(handle, post.get("uri", ""))
            count += 1
            out.append(_mk(
                title=text.split("\n")[0][:200],
                url=link,
                source_id=f"bsky/{handle}",
                source_title=acc.get("title", handle),
                source_kind="feed",
                category=acc.get("category", "person"),
                lang=acc.get("lang", "en"),
                source_weight=acc.get("weight", 3),
                published=pub.isoformat(),
                summary=text,
                engagement={"bsky_likes": post.get("likeCount"),
                            "bsky_reposts": post.get("repostCount"),
                            "bsky_replies": post.get("replyCount")},
                discussions=[{"kind": "bluesky",
                              "url": _bsky_permalink(handle, post.get("uri", "")),
                              "score": post.get("likeCount"),
                              "comments": post.get("replyCount")}],
            ))
        log.info("bluesky %-28s %2d posts in window", handle, count)
        time.sleep(0.4)

    log.info("bluesky %d posts", len(out))
    return out


def _bsky_outbound(record: dict) -> str | None:
    embed = record.get("embed") or {}
    external = embed.get("external") or {}
    if external.get("uri"):
        return external["uri"]
    for facet in record.get("facets") or []:
        for feature in facet.get("features") or []:
            if feature.get("uri"):
                return feature["uri"]
    return None


def _bsky_permalink(handle: str, uri: str) -> str:
    rkey = uri.rsplit("/", 1)[-1] if uri else ""
    if rkey:
        return f"https://bsky.app/profile/{handle}/post/{rkey}"
    return f"https://bsky.app/profile/{handle}"


# ── Google Groups ────────────────────────────────────────────────────────────
# Google retired the public RSS endpoints, but the group page still ships its
# conversation list as a server-rendered data island.

GG_TOPIC = re.compile(
    r'\["(?P<gid>\d{15,25})","(?P<tid>[A-Za-z0-9_-]{6,})",'
    r'"(?P<title>(?:[^"\\]|\\.)*)","(?P<snippet>(?:[^"\\]|\\.)*)",'
    r'\[(?P<ts>\d{10})',
)


def _js_unescape(text: str) -> str:
    try:
        text = text.encode("utf-8").decode("unicode_escape")
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    return html.unescape(text)


def fetch_google_groups(cfg: dict, start, end) -> list[dict]:
    groups = cfg.get("groups", [])
    if not groups:
        return []
    session = new_session(browser_ua=True)
    out: list[dict] = []

    for g in groups:
        name = g["name"]
        r = get(session, f"https://groups.google.com/g/{name}", timeout=30, retries=1)
        if r is None or r.status_code != 200:
            log.warning("groups %-28s HTTP %s", name,
                        r.status_code if r else "ERR")
            continue

        seen: set[str] = set()
        count = 0
        for m in GG_TOPIC.finditer(r.text):
            tid = m.group("tid")
            if tid in seen:
                continue
            seen.add(tid)
            try:
                pub = to_utc(datetime.fromtimestamp(int(m.group("ts")), tz=timezone.utc))
            except (TypeError, ValueError, OSError):
                continue
            if not (start <= pub <= end):
                continue
            title = _js_unescape(m.group("title")).strip()
            if len(title) < 12:
                continue
            count += 1
            out.append(_mk(
                title=title,
                url=f"https://groups.google.com/g/{name}/c/{tid}",
                source_id=f"groups/{name}",
                source_title=g.get("title", name),
                source_kind="feed",
                category=g.get("category", "project"),
                lang="en",
                source_weight=g.get("weight", 4),
                published=pub.isoformat(),
                summary=_js_unescape(m.group("snippet")).strip(),
            ))
        log.info("groups %-28s %2d threads in window", name, count)
        time.sleep(0.5)

    log.info("google groups %d threads", len(out))
    return out
