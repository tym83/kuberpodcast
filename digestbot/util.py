"""Shared helpers: HTTP session, URL canonicalisation, text and language utilities."""
from __future__ import annotations

import hashlib
import logging
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests

log = logging.getLogger("digestbot")

# Some hosts (rachelbythebay.com, among others) return 429 as soon as two
# requests arrive at once. Serialising per host costs nothing across a
# many-host crawl and stops those sources vanishing silently.
_HOST_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_GUARD = threading.Lock()
_HOST_MIN_INTERVAL = 0.4
_LAST_HIT: dict[str, float] = {}


def _host_lock(host: str) -> threading.Lock:
    with _LOCKS_GUARD:
        lock = _HOST_LOCKS.get(host)
        if lock is None:
            lock = _HOST_LOCKS[host] = threading.Lock()
        return lock

USER_AGENT = (
    "kuberpodcast-digest/1.0 (+https://github.com/tym83/kuberpodcast) "
    "python-requests"
)
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Query parameters that never change the identity of a document.
TRACKING_PARAMS = re.compile(
    r"^(utm_\w+|ref|ref_src|ref_url|referrer|source|src|fbclid|gclid|dclid|msclkid|"
    r"mc_cid|mc_eid|igshid|spm|share_\w+|from|__twitter_impression|at_medium|"
    r"at_campaign|cmp|campaign_id|s_cid|sc_channel|sc_campaign|sc_content|sc_geo|"
    r"sc_country|sc_outcome|trk|trkCampaign|li_fat_id|_hsenc|_hsmi|hss_channel|"
    r"amp|output_type|guccounter|guce_referrer\w*)$",
    re.I,
)

_WS = re.compile(r"\s+")
_TAG = re.compile(r"<[^>]+>")
_ENTITY = re.compile(r"&(#\d+|#x[0-9a-fA-F]+|[a-zA-Z]+);")


def new_session(browser_ua: bool = False) -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": BROWSER_UA if browser_ua else USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, "
            "text/xml, application/json;q=0.9, text/html;q=0.8, */*;q=0.5",
            "Accept-Language": "en,ru;q=0.9,zh;q=0.8,ja;q=0.7,*;q=0.5",
        }
    )
    return s


def get(session: requests.Session, url: str, *, timeout: int = 25, retries: int = 2,
        **kwargs) -> requests.Response | None:
    """GET with bounded retries and per-host serialisation. Returns None, never raises."""
    host = (urlparse(url).hostname or "").lower()
    with _host_lock(host):
        gap = _HOST_MIN_INTERVAL - (time.monotonic() - _LAST_HIT.get(host, 0.0))
        if gap > 0:
            time.sleep(gap)
        try:
            return _get(session, url, timeout=timeout, retries=retries, **kwargs)
        finally:
            _LAST_HIT[host] = time.monotonic()


def _get(session: requests.Session, url: str, *, timeout: int, retries: int,
         **kwargs) -> requests.Response | None:
    for attempt in range(retries + 1):
        try:
            r = session.get(url, timeout=timeout, allow_redirects=True, **kwargs)
            if r.status_code == 429 and attempt < retries:
                time.sleep(3 * (attempt + 1))
                continue
            return r
        except requests.RequestException as exc:
            if attempt >= retries:
                log.debug("GET failed %s: %s", url, exc)
                return None
            time.sleep(1.5 * (attempt + 1))
    return None


def canonical_url(url: str) -> str:
    """Normalise a URL so the same document from different surfaces collapses."""
    if not url:
        return ""
    url = url.strip()
    if url.startswith("//"):
        url = "https:" + url
    try:
        p = urlparse(url)
    except ValueError:
        return url
    if p.scheme not in ("http", "https"):
        return url

    host = (p.hostname or "").lower()
    for prefix in ("www.", "m.", "mobile.", "amp."):
        if host.startswith(prefix):
            host = host[len(prefix) :]
    # Language subdomains that serve the same article.
    host = re.sub(r"^(en|zh|ja|ko|ru)\.(medium\.com)$", r"\2", host)

    path = p.path or "/"
    path = re.sub(r"/amp/?$", "/", path)
    # Habr serves the same article under a hub path and a company path; the
    # bare /articles/<id>/ form is the identity.
    if host == "habr.com":
        path = re.sub(r"^/(ru|en)/(?:companies|company)/[^/]+/(?:articles|blog|blogs)/(\d+)",
                      r"/\1/articles/\2", path)
        path = re.sub(r"^/(ru|en)/post/(\d+)", r"/\1/articles/\2", path)
    if len(path) > 1:
        path = path.rstrip("/")
    if not path:
        path = "/"

    query = [
        (k, v)
        for k, v in parse_qsl(p.query, keep_blank_values=False)
        if not TRACKING_PARAMS.match(k)
    ]
    query.sort()

    return urlunparse(("https", host, path, "", urlencode(query), ""))


def domain_of(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def strip_html(text: str, limit: int = 1200) -> str:
    if not text:
        return ""
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    text = _TAG.sub(" ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    text = text.replace("&#39;", "'").replace("&mdash;", "—").replace("&ndash;", "–")
    text = _ENTITY.sub(" ", text)
    text = _WS.sub(" ", text).strip()
    return text[:limit]


def item_id(canonical: str) -> str:
    return hashlib.sha1(canonical.encode("utf-8", "replace")).hexdigest()[:16]


CYRILLIC = re.compile(r"[Ѐ-ӿ]")
HAN = re.compile(r"[一-鿿]")
KANA = re.compile(r"[぀-ヿ]")
HANGUL = re.compile(r"[가-힯]")


def detect_lang(text: str, default: str = "en") -> str:
    """Script-based language guess. Cheap and good enough for routing/quotas."""
    if not text:
        return default
    sample = text[:600]
    if HANGUL.search(sample):
        return "ko"
    if KANA.search(sample):
        return "ja"
    if HAN.search(sample):
        return "zh"
    if len(CYRILLIC.findall(sample)) >= 4:
        return "ru"
    return default


def to_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


MIN_SANE_YEAR = 2000


def parse_struct_time(st) -> datetime | None:
    if not st:
        return None
    try:
        dt = datetime(*st[:6], tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None
    # Hugo templates with an unset date emit 0001-01-01; treat it as no date.
    return dt if dt.year >= MIN_SANE_YEAR else None


def parse_loose_date(value: str | None) -> datetime | None:
    """Fallback for feeds feedparser cannot date, e.g. an RFC822 stamp with no
    timezone offset (Grafana). Without this those items are silently dropped."""
    if not value:
        return None
    try:
        from dateutil import parser as dateparser
    except ImportError:
        return None
    try:
        dt = dateparser.parse(value, fuzzy=False)
    except (ValueError, OverflowError, TypeError):
        return None
    if dt is None or dt.year < MIN_SANE_YEAR:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def window_bounds(days: int = 7, end: datetime | None = None
                  ) -> tuple[datetime, datetime]:
    end = to_utc(end or datetime.now(timezone.utc))
    return end - timedelta(days=days), end
