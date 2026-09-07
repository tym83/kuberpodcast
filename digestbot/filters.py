"""Noise filtering. Every rejection carries a reason code (see review-5 Appendix A)."""
from __future__ import annotations

import logging
import re

log = logging.getLogger("digestbot.filters")

SEMVER = re.compile(r"v?(\d+)\.(\d+)(?:\.(\d+))?(?:[-+]([0-9A-Za-z.\-]+))?\b")
NEVER_NEWS_TAG = re.compile(r"^v?(nightly|daily|canary|snapshot|latest|edge|dev)\b", re.I)
DATE_TAG = re.compile(r"^(v|release[-_])?\d{8}(\.\d+)?$", re.I)
DEP_BUMP = re.compile(
    r"^\s*[-*]\s*(build|chore|deps)?\(?deps\)?[: ]|"
    r"^\s*[-*]\s*(bump|update|upgrade)\s+[\w./@-]+\s+from\s+v?[\d.]+\s+to\s+v?[\d.]+|"
    r"dependabot|renovate(\[bot\])?",
    re.I,
)
BOILERPLATE_NOTES = re.compile(r"^\s*(bug ?fixes?|maintenance|patch|minor) release\.?\s*$", re.I)
PR_BOILERPLATE = re.compile(r"(?im)^#{1,4}\s+About\s+[A-Z][\w .&-]{2,40}\s*$")
PR_CONTACT = re.compile(r"(?i)\b((media|press) (contact|inquiries)|for more information,? visit)\b")
PR_QUOTE = re.compile(r'[,"”]\s*(said|says|according to)\s+[A-Z][a-z]+ [A-Z]')
PR_CTA = re.compile(r"/(pricing|demo|signup|sign-up|contact-sales|get-started|trial)\b")
MOJIBAKE = re.compile(r"Ð[°-¿]|Ñ[\x80-\xbf]|â€|ï¿½")


def compile_list(patterns) -> re.Pattern | None:
    if not patterns:
        return None
    return re.compile("|".join(f"(?:{p})" for p in patterns), re.I | re.U)


class Filters:
    """Compiled view of sources/blocklists.yaml."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.seo = compile_list(cfg.get("seo_listicle"))
        self.pr = compile_list(cfg.get("vendor_pr"))
        self.pr_domains = set(cfg.get("pr_domains", []))
        self.beginner_body = compile_list(cfg.get("beginner_body"))
        self.beginner_exempt = set(cfg.get("beginner_exempt_sources", []))
        self.slop_phrases = [p.lower() for p in cfg.get("ai_slop_phrases", [])]
        self.slop_strict = set(cfg.get("ai_slop_strict_domains", []))
        self.reddit_flair = {f.lower() for f in cfg.get("reddit_drop_flair", [])}
        self.reddit_title = compile_list(cfg.get("reddit_drop_title"))
        self.reddit_images = set(cfg.get("reddit_image_hosts", []))
        self.job = compile_list(cfg.get("job_post"))
        self.recycled = compile_list(cfg.get("recycled"))
        self.paywall_domains = set(cfg.get("paywall_domains", []))
        self.paywall_body = compile_list(cfg.get("paywall_body"))
        self.not_article = compile_list(cfg.get("not_an_article"))

        self.tier_a = [t.lower() for t in cfg.get("tier_a", [])]
        self.tier_b = [t.lower() for t in cfg.get("tier_b", [])]
        self.tier_c = [t.lower() for t in cfg.get("tier_c", [])]
        self.ai_terms = [t.lower() for t in cfg.get("ai_terms", [])]
        self.ecosystem = compile_list(cfg.get("ecosystem_terms"))
        self.incident = compile_list(cfg.get("incident_terms"))
        self.security = compile_list(cfg.get("security_terms"))
        self.breaking = compile_list(cfg.get("breaking_terms"))
        self.benchmark = compile_list(cfg.get("benchmark_terms"))
        self.comment_banned = compile_list(cfg.get("comment_banned"))

    # ── term counting ────────────────────────────────────────────────────────
    @staticmethod
    def _count(terms: list[str], text: str) -> int:
        return sum(1 for t in terms if t in text)

    def tier_hits(self, text: str) -> tuple[int, int, int]:
        t = text.lower()
        return (self._count(self.tier_a, t), self._count(self.tier_b, t),
                self._count(self.tier_c, t))

    def ai_hits(self, text: str) -> int:
        return self._count(self.ai_terms, text.lower())

    def slop_hits(self, body: str) -> int:
        b = body.lower()
        hits = self._count(self.slop_phrases, b)
        structural = 0
        if len(re.findall(r"\bnot (just|only) \w+,? but\b", b)) >= 2:
            structural += 1
        if re.search(r"(?i)^#{2,3}\s+(conclusion|final thoughts|wrapping up)\s*$", body, re.M) \
                and "```" not in body:
            structural += 1
        return hits + (1 if structural >= 2 else 0)


def _headings(body: str) -> int:
    return len(re.findall(r"(?m)^#{2,4}\s+\S", body))


def _strip_md(body: str) -> str:
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    body = re.sub(r"[#*_`>\-]+", " ", body)
    return re.sub(r"\s+", " ", body).strip()


def classify_bump(tag: str, previous: str | None) -> str:
    m = SEMVER.search(tag or "")
    if not m:
        return "unknown"
    major, minor, patch, pre = m.group(1), m.group(2), m.group(3), m.group(4)
    if pre:
        return "prerelease"
    if previous:
        pm = SEMVER.search(previous)
        if pm:
            if pm.group(1) != major:
                return "major"
            if pm.group(2) != minor:
                return "minor"
            return "patch"
    # No previous tag known: fall back to the version shape.
    if (patch in (None, "0")) and minor == "0":
        return "major"
    if patch in (None, "0"):
        return "minor"
    return "patch"


def release_verdict(item: dict, f: Filters, repo_cfg: dict) -> tuple[str | None, dict]:
    """Return (drop_reason | None, flags). Asset count is deliberately ignored."""
    rel = item.get("release") or {}
    flags: dict = {}
    tag = rel.get("tag", "")
    body = item.get("summary") or ""

    if NEVER_NEWS_TAG.match(tag) or DATE_TAG.match(tag):
        return "release_draft", flags
    if not SEMVER.search(tag) and len(body) < 1500:
        return "unparseable_tag", flags
    if repo_cfg.get("mirror_of"):
        return "mirror_repo", flags

    if f.security and f.security.search(body):
        flags["security"] = True
        return None, flags
    if f.breaking and f.breaking.search(body):
        flags["breaking_change"] = True
        return None, flags

    bump = classify_bump(tag, rel.get("previous_tag"))
    rel["bump"] = bump
    min_bump = repo_cfg.get("min_bump", "minor")
    order = {"patch": 0, "minor": 1, "major": 2}

    if bump == "major":
        return None, flags

    if rel.get("prerelease") or bump == "prerelease":
        if repo_cfg.get("rc") and re.search(r"\.0[-.](rc|beta|alpha)", tag, re.I):
            return None, flags
        return "prerelease", flags

    lines = [l for l in body.splitlines() if re.match(r"\s*[-*]\s+\S", l)]
    if lines and sum(bool(DEP_BUMP.search(l)) for l in lines) / len(lines) > 0.70:
        return "dependency_bump", flags
    if BOILERPLATE_NOTES.fullmatch(_strip_md(body)):
        return "boilerplate_notes", flags

    if bump in order and order[bump] < order.get(min_bump, 1):
        # Below this repo's newsworthiness floor unless the notes are substantial.
        stripped = _strip_md(body)
        a, b, _ = f.tier_hits(stripped)
        if not (len(stripped) >= 600 and _headings(body) >= 2 and (a + b) >= 2):
            return "patch_bump" if bump == "patch" else "thin_minor", flags
        return None, flags

    if bump == "patch":
        stripped = _strip_md(body)
        a, b, _ = f.tier_hits(stripped)
        if not (len(stripped) >= 600 and _headings(body) >= 2 and (a + b) >= 2):
            return "patch_bump", flags
        return None, flags

    if bump == "minor":
        if len(_strip_md(body)) < 400 and _headings(body) < 2:
            return "thin_minor", flags
        return None, flags

    return None, flags


def screen(item: dict, f: Filters, repo_cfg: dict, ed: dict) -> tuple[str | None, dict]:
    """Hard filters. Returns (reason | None, flags) — first hard match wins."""
    title = item.get("title") or ""
    body = item.get("body") or item.get("summary") or ""
    text = f"{title}\n{body[:6000]}"
    domain = item.get("domain", "")
    kind = item.get("source_kind", "")
    flags: dict = {}

    if MOJIBAKE.search(title):
        return "encoding_error", flags
    if not item.get("url") or len(title) < 12:
        return "not_an_article", flags

    # Releases are judged by their own rules; a release URL is never a listing page.
    if kind == "release":
        return release_verdict(item, f, repo_cfg)

    if self_url_is_listing(item, f):
        return "not_an_article", flags

    if f.job and f.job.search(title):
        return "job_post", flags
    if domain in f.pr_domains:
        return "vendor_pr", flags
    if f.pr and f.pr.search(title):
        return "vendor_pr", flags
    if f.seo and f.seo.search(title):
        return "seo_listicle", flags
    if f.recycled and f.recycled.search(title):
        return "repost", flags

    if kind == "reddit":
        reason = _reddit_screen(item, f)
        if reason:
            return reason, flags

    if domain in f.paywall_domains and item.get("source_weight", 0) < 5:
        return "paywall", flags
    if f.paywall_body and item.get("words", 0) < 400 and f.paywall_body.search(body):
        return "paywall", flags

    # AI slop: stricter on known content-farm surfaces.
    slop = f.slop_hits(body) if body else 0
    limit = 2 if domain in f.slop_strict else 3
    if slop >= limit:
        return "ai_slop", flags
    if slop == 2:
        flags["slop_two_hits"] = True

    # Beginner content: title patterns already handled by SEO; this is the body check.
    if item.get("source_id") not in f.beginner_exempt and kind not in ("release", "reddit", "hn"):
        if f.beginner_body and f.beginner_body.search(body):
            return "beginner", flags
        words = item.get("words", 0)
        if words >= 400:
            a, b, _ = f.tier_hits(body)
            density = 1000 * (a + b) / max(words, 1)
            if density < 4:
                return "beginner", flags

    # Structural vendor PR (2+ signals is a drop, 1 is a penalty).
    signals = 0
    if PR_BOILERPLATE.search(body):
        signals += 1
    if PR_CONTACT.search(body):
        signals += 1
    if len(PR_QUOTE.findall(body)) >= 3 and item.get("code_blocks", 0) < 2:
        signals += 1
    if item.get("words", 0) < 350 and PR_CTA.search(body):
        signals += 1
    if signals >= 2:
        return "vendor_pr", flags
    if signals == 1:
        flags["vendor_pitch"] = True

    if not item.get("has_byline", True) and item.get("category") == "vendor":
        flags["no_byline_vendor"] = True

    # Routing flags used later by the classifier and the bonus terms.
    if f.security and f.security.search(text):
        flags["security"] = True
    # The marker has to be in the headline or the opening, or every post that
    # mentions an outage in passing lands in the incidents section.
    opening = f"{title}\n{body[:600]}"
    if f.incident and f.incident.search(opening) and _incident_is_first_party(item):
        flags["incident"] = True
    if f.breaking and f.breaking.search(text):
        flags["breaking_change"] = True
    if f.benchmark and f.benchmark.search(text) and re.search(r"\d", text):
        flags["benchmark_numbers"] = True
    return None, flags


def self_url_is_listing(item: dict, f: Filters) -> bool:
    url = item.get("canonical_url") or item.get("url", "")
    path = re.sub(r"^https?://[^/]+", "", url)
    if not path or path == "/":
        return item.get("source_kind") not in ("hn", "reddit", "lobsters")
    return bool(f.not_article and f.not_article.search(path))


def _incident_is_first_party(item: dict) -> bool:
    """An RCA from the affected party is an incident; press coverage of it is not."""
    if item.get("category") in ("media",):
        return False
    if item.get("source_kind") in ("hn", "reddit", "lobsters"):
        # A linked postmortem still counts; a news article about it does not.
        return item.get("domain", "") not in ("theregister.com", "techcrunch.com")
    return True


def _reddit_screen(item: dict, f: Filters) -> str | None:
    eng = item.get("engagement", {})
    flair = (eng.get("reddit_flair") or "").lower()
    title = item.get("title", "")
    score = eng.get("reddit_score") or 0
    comments = eng.get("reddit_comments") or 0

    if item.get("domain") in f.reddit_images:
        return "not_an_article"
    if flair in f.reddit_flair:
        return "reddit_help"
    # The exception that has to exist: a busy discussion thread is the story.
    if flair == "discussion" and comments >= 120:
        return None
    if f.reddit_title and f.reddit_title.search(title):
        return "reddit_help"
    is_self = (item.get("canonical_url") or "").startswith("https://reddit.com/r/")
    if is_self and comments < 120 and score < 80:
        return "reddit_selfpost"
    return None
