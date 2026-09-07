"""Window admission: dates are the one thing this digest cannot get wrong.

Implements review-5 §5 — resolution chain, future clamping, late arrivals, the
old-link rule for HN/Reddit, and cold-start quarantine for date-less items.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone

log = logging.getLogger("digestbot.freshness")

URL_DATE = re.compile(r"/(20\d\d)[/-](\d{1,2})[/-](\d{1,2})[/-]?")


def _parse(value) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def resolve_date(item: dict, store, now: datetime) -> tuple[datetime | None, str]:
    """Return (effective_date, provenance). Provenance drives the quarantine rule."""
    dt = _parse(item.get("published"))
    if dt:
        return dt, "feed"

    m = URL_DATE.search(item.get("canonical_url") or item.get("url", ""))
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                            tzinfo=timezone.utc), "url"
        except ValueError:
            pass

    seen = store.first_seen(item["id"]) if store else None
    if seen:
        return seen, "first_seen"
    return None, "none"


def admit(item: dict, start: datetime, end: datetime, store, cfg: dict,
          now: datetime, counters: dict) -> str | None:
    """Return a rejection reason, or None. Sets `_effective_dt` and freshness flags."""
    dt, provenance = resolve_date(item, store, now)

    if dt is None:
        return "stale"

    if dt > now + timedelta(days=cfg["future_drop_days"]):
        return "bogus_future_date"
    if dt > now + timedelta(hours=cfg["future_clamp_hours"]):
        dt = now
        item.setdefault("flags", {})["clamped_future"] = True

    if provenance == "first_seen":
        # Cold start: a newly added source would otherwise dump its whole archive.
        age = store.source_age_days(item.get("source_id", ""), now) if store else 0
        if age < cfg["cold_start_quarantine_days"]:
            return "stale"

    item["_effective_dt"] = dt
    item["date_provenance"] = provenance

    if start <= dt <= end:
        return _old_link_check(item, cfg, counters)

    # Late arrival: published before the window but genuinely new to us.
    if store is not None:
        first = store.first_seen(item["id"])
        grace = timedelta(days=cfg["late_arrival_days"])
        if first and start <= first <= end and (now - dt) <= grace:
            if counters["late"] >= cfg["late_arrival_max"]:
                return "stale"
            counters["late"] += 1
            item["late_arrival"] = True
            item.setdefault("flags", {})["late"] = True
            return _old_link_check(item, cfg, counters)

    return "stale"


def _old_link_check(item: dict, cfg: dict, counters: dict) -> str | None:
    """An old article resurfacing on HN/Reddit is only news if the thread is."""
    if item.get("source_kind") not in ("hn", "reddit", "lobsters"):
        return None
    article_dt = _parse(item.get("article_published"))
    if not article_dt:
        return None
    age_days = (item["_effective_dt"] - article_dt).days
    if age_days <= cfg["old_link_days"]:
        return None
    e = item.get("engagement", {})
    comments = (e.get("hn_comments") or 0) + (e.get("reddit_comments") or 0)
    if comments < cfg["old_link_min_comments"]:
        return "stale"
    if counters["old_link"] >= cfg["old_link_max"]:
        return "stale"
    counters["old_link"] += 1
    item["thread_is_canonical"] = True
    item.setdefault("flags", {})["old_material"] = True
    item["article_age_days"] = age_days
    return None


def new_counters() -> dict:
    return {"late": 0, "old_link": 0}
