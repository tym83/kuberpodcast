#!/usr/bin/env python
"""Config sanity checks. Run in CI so a broken regex or a duplicate id fails fast
instead of silently deleting a whole category from the next digest."""
from __future__ import annotations

import pathlib
import re
import sys
from collections import Counter
from urllib.parse import urlparse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from digestbot import config  # noqa: E402
from digestbot.filters import Filters  # noqa: E402

REQUIRED_FEED_KEYS = {"id", "title", "url", "lang", "category", "weight"}
VALID_LANGS = {"en", "ru", "zh", "ja", "ko", "de", "fr", "es", "pt", "pl",
               "nl", "it", "tr", "multi"}
VALID_CATEGORIES = {"foundation", "project", "vendor", "cloud", "media",
                    "newsletter", "person", "community", "security", "incident",
                    "research"}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    feeds = config.feeds()
    if not feeds:
        errors.append("feeds.yaml is empty")

    ids = Counter(f.get("id") for f in feeds)
    for fid, n in ids.items():
        if n > 1:
            errors.append(f"duplicate feed id: {fid} ({n}x)")

    urls = Counter(f.get("url") for f in feeds)
    for url, n in urls.items():
        if n > 1:
            errors.append(f"duplicate feed url: {url} ({n}x)")

    for f in feeds:
        missing = REQUIRED_FEED_KEYS - set(f)
        if missing:
            errors.append(f"feed {f.get('id')}: missing keys {sorted(missing)}")
            continue
        if f["lang"] not in VALID_LANGS:
            errors.append(f"feed {f['id']}: unknown lang {f['lang']!r}")
        if f["category"] not in VALID_CATEGORIES:
            errors.append(f"feed {f['id']}: unknown category {f['category']!r}")
        if not 1 <= int(f["weight"]) <= 5:
            errors.append(f"feed {f['id']}: weight {f['weight']} outside 1..5")
        p = urlparse(f["url"])
        if p.scheme not in ("http", "https") or not p.netloc:
            errors.append(f"feed {f['id']}: malformed url {f['url']!r}")

    # blocklists: every pattern must compile.
    bl = config.blocklists()
    for key, value in bl.items():
        if not isinstance(value, list) or key.endswith(("_domains", "_sources", "_flair",
                                                        "_hosts")):
            continue
        if key in ("tier_a", "tier_b", "tier_c", "ai_terms", "ai_slop_phrases"):
            continue
        for pattern in value:
            try:
                re.compile(pattern, re.I | re.U)
            except re.error as exc:
                errors.append(f"blocklists.{key}: bad regex {pattern!r} -> {exc}")
    try:
        Filters(bl)
    except re.error as exc:
        errors.append(f"blocklists.yaml does not compile as a filter set: {exc}")

    # editorial: quotas must add up and every section must be routable.
    ed = config.editorial()
    sections = ed.get("sections", [])
    keys = [s["key"] for s in sections]
    quota_total = sum(s["quota"] for s in sections if not s.get("promotion"))
    target = ed.get("target_total", 100)
    if quota_total != target:
        errors.append(f"section quotas sum to {quota_total}, target_total is {target}")
    for s in sections:
        if s.get("min", 0) > s["quota"]:
            errors.append(f"section {s['key']}: min {s['min']} > quota {s['quota']}")
    ne = next((s for s in sections if s["key"] == "nonenglish"), None)
    if ne and sum(ne.get("sub_quotas", {}).values()) > ne["quota"]:
        errors.append("nonenglish sub_quotas exceed the section quota")
    for key in ed.get("classify_order", []) + ed.get("spill_order", []):
        if key not in keys:
            errors.append(f"unknown section key referenced: {key}")
    for key in keys:
        if key != "headline" and key not in ed.get("classify_order", []):
            warnings.append(f"section {key} is never produced by the classifier")

    # releases: policy values must be understood by the filter.
    policy = config.repo_policy()
    for repo, cfg in policy.items():
        if cfg.get("min_bump") not in ("patch", "minor", "major"):
            errors.append(f"repo {repo}: bad min_bump {cfg.get('min_bump')!r}")
        if "/" not in repo:
            errors.append(f"repo {repo!r} is not owner/name")
        parent = cfg.get("mirror_of")
        if parent and parent not in policy:
            errors.append(f"repo {repo}: mirror_of points at unknown repo {parent}")

    comm = config.community()
    subs = comm.get("reddit", {}).get("subreddits", [])
    sub_names = Counter(s["name"] for s in subs)
    for name, n in sub_names.items():
        if n > 1:
            errors.append(f"duplicate subreddit: r/{name}")

    print(f"feeds: {len(feeds)} | subreddits: {len(subs)} | repos: {len(policy)} | "
          f"sections: {len(sections)} (quota {quota_total})")
    langs = Counter(f["lang"] for f in feeds)
    print("languages: " + ", ".join(f"{k} {v}" for k, v in langs.most_common()))

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
