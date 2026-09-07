"""Full-text extraction with an on-disk cache.

FORM, ORIG, the beginner filter and the AI-slop filter all need body text, which
RSS summaries do not provide. Fetching is the slow part of the pipeline, so every
extraction is cached by URL hash and reused across runs.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import logging
import pathlib
import re
import time

import trafilatura

from .util import canonical_url, domain_of, get, new_session

log = logging.getLogger("digestbot.text")

CACHE_DIR = pathlib.Path("data/textcache")
CODE_FENCE = re.compile(r"```|<pre[\s>]|<code[\s>]")
TABLE = re.compile(r"<table[\s>]|^\s*\|.+\|\s*$", re.M)
HEADING = re.compile(r"^#{2,4}\s+\S|<h[23][\s>]", re.M | re.I)

# Hosts where fetching is pointless or hostile: the body is behind a login, is a
# binary, or the feed already carries everything worth reading.
SKIP_FETCH_DOMAINS = {
    "news.ycombinator.com", "reddit.com", "old.reddit.com", "lobste.rs",
    "twitter.com", "x.com", "youtube.com", "youtu.be", "linkedin.com",
}


def _cache_path(url: str) -> pathlib.Path:
    h = hashlib.sha256(url.encode("utf-8", "replace")).hexdigest()
    return CACHE_DIR / h[:2] / f"{h}.json"


def load_cached(url: str) -> dict | None:
    p = _cache_path(url)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _store(url: str, data: dict) -> None:
    p = _cache_path(url)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        log.debug("cache write failed for %s: %s", url, exc)


def analyse(text: str, html: str = "") -> dict:
    words = len(re.findall(r"\S+", text))
    return {
        "words": words,
        "code_blocks": len(CODE_FENCE.findall(html or text)),
        "headings": len(HEADING.findall(html or text)),
        "has_table": bool(TABLE.search(html or text)),
    }


def fetch_one(item: dict, session) -> dict:
    """Return the extraction record for one item, from cache when possible."""
    url = item.get("canonical_url") or item["url"]
    cached = load_cached(url)
    if cached is not None:
        return cached

    domain = domain_of(url)
    if domain in SKIP_FETCH_DOMAINS or item.get("source_kind") == "release":
        # Release bodies and thread self-text already arrive with the item.
        body = item.get("summary", "")
        rec = {"url": url, "text": body, "final_url": url, "status": 0,
               "fetched": False, **analyse(body)}
        _store(url, rec)
        return rec

    r = get(session, url, timeout=20, retries=1)
    if r is None or r.status_code >= 400 or "html" not in r.headers.get("content-type", "html"):
        body = item.get("summary", "")
        rec = {"url": url, "text": body, "final_url": url,
               "status": r.status_code if r is not None else 0,
               "fetched": False, **analyse(body)}
        _store(url, rec)
        return rec

    html = r.text
    extracted = ""
    try:
        extracted = trafilatura.extract(
            html, include_comments=False, include_tables=True,
            favor_precision=True, no_fallback=False
        ) or ""
    except Exception as exc:  # noqa: BLE001 - trafilatura raises a wide range
        log.debug("extract failed %s: %s", url, exc)

    if len(extracted) < len(item.get("summary", "")):
        extracted = extracted or item.get("summary", "")

    # rel=canonical wins over our normalisation, but only same-registrable-domain.
    canon = ""
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
                  html, re.I) or \
        re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',
                  html, re.I)
    if m:
        cand = canonical_url(m.group(1))
        if domain_of(cand) == domain:
            canon = cand

    rec = {
        "url": url,
        "canonical": canon,
        "final_url": str(r.url),
        "status": r.status_code,
        "fetched": True,
        "text": extracted[:120_000],
        "byline": bool(re.search(r'(?i)(rel=["\']author["\']|itemprop=["\']author["\']|'
                                 r'class=["\'][^"\']*author)', html)),
        **analyse(extracted, html),
    }
    _store(url, rec)
    return rec


def hydrate(items: list[dict], workers: int = 12, budget: int | None = None) -> None:
    """Attach `body`, `words`, `code_blocks`, `headings` to each item, in place.

    `budget` caps how many uncached network fetches are performed, so a run never
    spends unbounded time on the long tail of low-scoring candidates.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    session = new_session(browser_ua=True)
    fetched = 0
    start = time.time()

    def work(item: dict) -> tuple[dict, dict]:
        return item, fetch_one(item, session)

    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for item, rec in pool.map(work, items):
            if rec.get("fetched"):
                fetched += 1
            item["body"] = rec.get("text", "")
            item["words"] = rec.get("words", 0)
            item["code_blocks"] = rec.get("code_blocks", 0)
            item["headings"] = rec.get("headings", 0)
            item["has_table"] = rec.get("has_table", False)
            item["has_byline"] = rec.get("byline", False)
            item["fetch_status"] = rec.get("status", 0)
            if rec.get("canonical"):
                item["canonical_url"] = rec["canonical"]
            if budget is not None and fetched >= budget:
                break

    log.info("text: hydrated %d items (%d network fetches) in %.1fs",
             len(items), fetched, time.time() - start)
