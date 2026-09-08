"""Source-catalog loading."""
from __future__ import annotations

import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"


def _load(name: str) -> dict:
    path = SOURCES / name
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def feeds() -> list[dict]:
    return _load("feeds.yaml").get("feeds", [])


def community() -> dict:
    return _load("community.yaml")


def releases() -> dict:
    return _load("releases.yaml").get("repos", {})


def editorial() -> dict:
    return _load("editorial.yaml")


def blocklists() -> dict:
    return _load("blocklists.yaml")


def signals() -> dict:
    return _load("signals.yaml")


def bridges() -> dict:
    return _load("bridges.yaml")


def repo_policy() -> dict:
    """Flatten releases.yaml into repo -> policy, so filters can consult per-repo rules."""
    out: dict[str, dict] = {}
    for group, meta in releases().items():
        defaults = {k: v for k, v in meta.items() if k not in ("list", "repos")}
        for entry in meta.get("list", []):
            if isinstance(entry, str):
                out[entry] = {"group": group, **defaults}
            else:
                repo = entry.get("repo")
                if repo:
                    out[repo] = {"group": group, **defaults, **entry}
    return out
