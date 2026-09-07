"""Structured sources: CVE feeds, status pages, newsletter link mining, governance."""
from __future__ import annotations

import concurrent.futures as cf
import logging
import os
import re
from datetime import datetime, timezone

from .collect import _mk, fetch_feeds
from .util import canonical_url, domain_of, get, new_session, strip_html, to_utc

log = logging.getLogger("digestbot.signals")

HREF = re.compile(r'href=["\'](https?://[^"\'\s>]+)["\']', re.I)


def _as_feed(entry: dict, category: str) -> dict:
    return {"id": entry["id"], "title": entry["title"], "url": entry["url"],
            "lang": "en", "category": category, "weight": entry.get("weight", 3)}


# ── security ─────────────────────────────────────────────────────────────────

def fetch_security(cfg: dict, start, end) -> list[dict]:
    items: list[dict] = []
    feeds = [_as_feed(f, "security") for f in cfg.get("feeds", [])]
    if feeds:
        items += fetch_feeds(feeds, start, end, workers=8)

    session = new_session()
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    session.headers["Accept"] = "application/vnd.github+json"

    # Kubernetes' own CVE feed is JSON, not RSS.
    url = cfg.get("k8s_cve_json")
    if url:
        r = get(session, url, timeout=25)
        if r is not None and r.status_code == 200:
            try:
                data = r.json()
            except ValueError:
                data = {}
            for cve in data.get("items", []):
                pub = _iso(cve.get("date_published") or cve.get("date_modified"))
                if not pub or not (start <= pub <= end):
                    continue
                items.append(_mk(
                    title=strip_html(cve.get("summary") or cve.get("id", ""), 300),
                    url=cve.get("external_url") or cve.get("url", ""),
                    source_id="k8s-cve-feed", source_title="Kubernetes CVE feed",
                    source_kind="feed", category="security", lang="en",
                    source_weight=5, published=pub.isoformat(),
                    summary=strip_html(cve.get("content_text") or ""),
                ))
            log.info("security: k8s CVE feed contributed %d", len(items))

    def advisories(repo: str) -> list[dict]:
        r = get(session, f"https://api.github.com/repos/{repo}/security-advisories",
                params={"per_page": 10, "state": "published"}, timeout=25, retries=1)
        if r is None or r.status_code != 200:
            return []
        out = []
        for a in r.json():
            pub = _iso(a.get("published_at"))
            if not pub or not (start <= pub <= end):
                continue
            sev = (a.get("severity") or "").upper()
            out.append(_mk(
                title=f"{repo}: {a.get('summary', a.get('ghsa_id', ''))}"
                      + (f" [{sev}]" if sev else ""),
                url=a.get("html_url", ""),
                source_id=f"ghsa/{repo}", source_title=f"{repo} advisory",
                source_kind="feed", category="security", lang="en",
                source_weight=5, published=pub.isoformat(),
                summary=strip_html(a.get("description") or "", 4000),
            ))
        return out

    repos = cfg.get("advisory_repos", [])
    if repos:
        before = len(items)
        with cf.ThreadPoolExecutor(max_workers=8) as pool:
            for res in pool.map(advisories, repos):
                items += res
        log.info("security: %d GitHub advisories from %d repos",
                 len(items) - before, len(repos))
    return items


# ── incidents ────────────────────────────────────────────────────────────────

def fetch_incidents(cfg: dict, start, end) -> list[dict]:
    feeds = [_as_feed(f, "incident") for f in cfg.get("feeds", [])]
    items = fetch_feeds(feeds, start, end, workers=8) if feeds else []
    floor = cfg.get("min_body_chars", 240)
    # Status pages emit one entry per maintenance window; only real writeups qualify.
    kept = [i for i in items if len(i.get("summary", "")) >= floor
            or re.search(r"(?i)\b(post[- ]?mortem|root cause|incident report)\b",
                         i.get("title", "") + i.get("summary", ""))]
    log.info("incidents: %d entries (%d after the substance floor)", len(items), len(kept))
    return kept


# ── newsletter link mining ───────────────────────────────────────────────────

def mine_newsletters(cfg: dict, start, end) -> set[str]:
    """Return canonical URLs that a human curator picked this week."""
    import feedparser

    session = new_session(browser_ua=True)
    ignore = set(cfg.get("ignore_domains", []))
    picked: set[str] = set()

    for src in cfg.get("sources", []):
        r = get(session, src["url"], timeout=25, retries=1)
        if r is None or r.status_code != 200:
            log.warning("newsletter %s HTTP %s", src["id"],
                        r.status_code if r else "ERR")
            continue
        parsed = feedparser.parse(r.content)
        found = 0
        for e in parsed.entries[:8]:
            pub = _struct(getattr(e, "published_parsed", None)
                          or getattr(e, "updated_parsed", None))
            if pub is None or not (start <= pub <= end):
                continue
            html = (getattr(e, "summary", "") or "")
            if getattr(e, "content", None):
                html += " ".join(c.value for c in e.content)
            for url in HREF.findall(html):
                canon = canonical_url(url)
                dom = domain_of(canon)
                if not dom or dom in ignore or any(dom.endswith("." + d) for d in ignore):
                    continue
                picked.add(canon)
                found += 1
        log.info("newsletter %-14s %d outbound links", src["id"], found)
    log.info("newsletter mining: %d distinct curated URLs", len(picked))
    return picked


# ── CNCF / KEP governance ────────────────────────────────────────────────────

def fetch_governance(cfg: dict, start, end) -> list[dict]:
    session = new_session()
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    session.headers["Accept"] = "application/vnd.github+json"
    out: list[dict] = []
    limit = cfg.get("max_items", 40)

    for src in cfg.get("github_issue_feeds", []):
        r = get(session, f"https://api.github.com/repos/{src['repo']}/issues",
                params={"state": "all", "sort": "updated", "direction": "desc",
                        "per_page": 60}, timeout=25, retries=1)
        if r is None or r.status_code != 200:
            log.warning("governance %s HTTP %s", src["repo"],
                        r.status_code if r else "ERR")
            continue
        count = 0
        for issue in r.json():
            pub = _iso(issue.get("created_at"))
            if not pub or not (start <= pub <= end):
                continue
            if count >= limit:
                break
            count += 1
            out.append(_mk(
                title=f"{src['title']}: {issue.get('title','')}",
                url=issue.get("html_url", ""),
                source_id=src["id"], source_title=src["title"],
                source_kind="feed", category="foundation", lang="en",
                source_weight=src.get("weight", 4), published=pub.isoformat(),
                summary=strip_html(issue.get("body") or "", 4000),
            ))
        log.info("governance %-22s %d items", src["repo"], count)
    return out


def _iso(value) -> datetime | None:
    if not value:
        return None
    try:
        return to_utc(datetime.fromisoformat(str(value).replace("Z", "+00:00")))
    except ValueError:
        return None


def _struct(st) -> datetime | None:
    if not st:
        return None
    try:
        return datetime(*st[:6], tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None
