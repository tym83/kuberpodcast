#!/usr/bin/env python
"""Stage 1: fetch every source and dump raw candidates to data/raw-<date>.json."""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from digestbot import collect, config, signals as sig  # noqa: E402
from digestbot.util import window_bounds  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--end", default=None, help="ISO end of window (default: now)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--skip", default="", help="comma-separated: feeds,hn,reddit,\n                    lobsters,devto,releases,security,incidents,governance,newsletters")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}

    end = datetime.fromisoformat(args.end) if args.end else datetime.now(timezone.utc)
    start, end = window_bounds(args.days, end)
    logging.info("window %s .. %s", start.isoformat(), end.isoformat())

    comm = config.community()
    items: list[dict] = []
    if "feeds" not in skip:
        items += collect.fetch_feeds(config.feeds(), start, end)
    if "hn" not in skip:
        items += collect.fetch_hackernews(comm.get("hackernews", {}), start, end)
    if "reddit" not in skip:
        items += collect.fetch_reddit(comm.get("reddit", {}), start, end)
    if "lobsters" not in skip:
        items += collect.fetch_lobsters(comm.get("lobsters", {}), start, end)
    if "devto" not in skip:
        items += collect.fetch_devto(comm.get("devto", {}), start, end)
    if "releases" not in skip:
        items += collect.fetch_releases(config.releases(), start, end)

    sig_cfg = config.signals()
    if "security" not in skip:
        items += sig.fetch_security(sig_cfg.get("security", {}), start, end)
    if "incidents" not in skip:
        items += sig.fetch_incidents(sig_cfg.get("incidents", {}), start, end)
    if "governance" not in skip:
        items += sig.fetch_governance(sig_cfg.get("governance", {}), start, end)

    curated: list[str] = []
    if "newsletters" not in skip:
        curated = sorted(sig.mine_newsletters(sig_cfg.get("newsletter_mining", {}),
                                              start, end))

    out = pathlib.Path(args.out or f"data/raw-{end.date().isoformat()}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {"window_start": start.isoformat(), "window_end": end.isoformat(),
             "collected_at": datetime.now(timezone.utc).isoformat(),
             "curated_urls": curated, "items": items},
            ensure_ascii=False, indent=1,
        ),
        encoding="utf-8",
    )
    logging.info("wrote %s (%d raw items)", out, len(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
