"""Cross-week state: what has already been emitted, and how healthy each feed is.

Without this the digest re-emits last week's stories under new URLs, and dead
feeds rot silently for months.
"""
from __future__ import annotations

import json
import logging
import pathlib
import sqlite3
from datetime import datetime, timedelta, timezone

log = logging.getLogger("digestbot.state")

DB_PATH = pathlib.Path("state/emitted.sqlite")
HEALTH_PATH = pathlib.Path("state/feed_health.json")

SCHEMA = """
CREATE TABLE IF NOT EXISTS emitted (
  url_hash     TEXT PRIMARY KEY,
  norm_title_h TEXT,
  simhash      INTEGER,
  entity       TEXT,
  digest_date  TEXT NOT NULL,
  section      TEXT,
  score        REAL,
  title        TEXT,
  url          TEXT
);
CREATE INDEX IF NOT EXISTS ix_title  ON emitted(norm_title_h);
CREATE INDEX IF NOT EXISTS ix_entity ON emitted(entity);
CREATE INDEX IF NOT EXISTS ix_date   ON emitted(digest_date);
CREATE TABLE IF NOT EXISTS seen (
  url_hash   TEXT PRIMARY KEY,
  first_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS source_first_poll (
  source_id  TEXT PRIMARY KEY,
  first_poll TEXT NOT NULL
);
"""


class Store:
    def __init__(self, path: pathlib.Path = DB_PATH):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ── emitted ──────────────────────────────────────────────────────────────
    def seen_url(self, url_hash: str, weeks: int = 8) -> str | None:
        cutoff = (datetime.now(timezone.utc) - timedelta(weeks=weeks)).date().isoformat()
        row = self.conn.execute(
            "SELECT digest_date FROM emitted WHERE url_hash=? AND digest_date>=?",
            (url_hash, cutoff),
        ).fetchone()
        return row[0] if row else None

    def seen_title(self, title_hash: str, weeks: int = 8) -> str | None:
        cutoff = (datetime.now(timezone.utc) - timedelta(weeks=weeks)).date().isoformat()
        row = self.conn.execute(
            "SELECT digest_date FROM emitted WHERE norm_title_h=? AND digest_date>=?",
            (title_hash, cutoff),
        ).fetchone()
        return row[0] if row else None

    def recent_simhashes(self, weeks: int = 1) -> list[tuple[int, str]]:
        cutoff = (datetime.now(timezone.utc) - timedelta(weeks=weeks)).date().isoformat()
        return [
            (r[0], r[1]) for r in self.conn.execute(
                "SELECT simhash, entity FROM emitted "
                "WHERE digest_date>=? AND simhash IS NOT NULL", (cutoff,))
        ]

    def entity_emitted_recently(self, entity: str, weeks: int = 1) -> bool:
        if not entity:
            return False
        cutoff = (datetime.now(timezone.utc) - timedelta(weeks=weeks)).date().isoformat()
        return self.conn.execute(
            "SELECT 1 FROM emitted WHERE entity=? AND digest_date>=? LIMIT 1",
            (entity, cutoff),
        ).fetchone() is not None

    def record(self, items: list[dict], digest_date: str) -> None:
        rows = [
            (it["id"], it.get("norm_title_hash"), it.get("simhash"), it.get("entity"),
             digest_date, it.get("section"), it.get("score"),
             it.get("title", "")[:400], it.get("url", ""))
            for it in items
        ]
        self.conn.executemany(
            "INSERT OR REPLACE INTO emitted "
            "(url_hash, norm_title_h, simhash, entity, digest_date, section, score, title, url) "
            "VALUES (?,?,?,?,?,?,?,?,?)", rows)
        self.conn.commit()
        log.info("state: recorded %d emitted items for %s", len(rows), digest_date)

    # ── first-seen tracking (freshness fallback + cold-start quarantine) ─────
    def note_seen(self, url_hashes: list[str], when: datetime) -> None:
        ts = when.isoformat()
        self.conn.executemany(
            "INSERT OR IGNORE INTO seen (url_hash, first_seen) VALUES (?,?)",
            [(h, ts) for h in url_hashes])
        self.conn.commit()

    def first_seen(self, url_hash: str) -> datetime | None:
        row = self.conn.execute(
            "SELECT first_seen FROM seen WHERE url_hash=?", (url_hash,)).fetchone()
        if not row:
            return None
        try:
            return datetime.fromisoformat(row[0])
        except ValueError:
            return None

    def note_source_poll(self, source_ids: list[str], when: datetime) -> None:
        ts = when.isoformat()
        self.conn.executemany(
            "INSERT OR IGNORE INTO source_first_poll (source_id, first_poll) VALUES (?,?)",
            [(s, ts) for s in source_ids])
        self.conn.commit()

    def source_age_days(self, source_id: str, now: datetime) -> float:
        row = self.conn.execute(
            "SELECT first_poll FROM source_first_poll WHERE source_id=?",
            (source_id,)).fetchone()
        if not row:
            return 0.0
        try:
            return (now - datetime.fromisoformat(row[0])).total_seconds() / 86400
        except ValueError:
            return 0.0

    def close(self) -> None:
        self.conn.close()


# ── feed health ──────────────────────────────────────────────────────────────

def load_health() -> dict:
    if HEALTH_PATH.exists():
        try:
            return json.loads(HEALTH_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def save_health(health: dict) -> None:
    HEALTH_PATH.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_PATH.write_text(json.dumps(health, ensure_ascii=False, indent=1),
                           encoding="utf-8")


def update_health(results: list[dict], now: datetime) -> dict:
    """`results` are per-feed probe records emitted by the collector."""
    health = load_health()
    ts = now.isoformat()
    for r in results:
        entry = health.setdefault(r["id"], {"consecutive_failures": 0})
        entry["last_status"] = r.get("status")
        entry["last_attempt"] = ts
        entry["last_items"] = r.get("items", 0)
        if r.get("ok"):
            entry["last_success"] = ts
            entry["consecutive_failures"] = 0
        else:
            entry["consecutive_failures"] = entry.get("consecutive_failures", 0) + 1
    save_health(health)
    return health


def dead_feeds(health: dict, threshold: int = 3) -> list[str]:
    return sorted(fid for fid, e in health.items()
                  if e.get("consecutive_failures", 0) >= threshold)
