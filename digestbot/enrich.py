"""Editorial comments for the selected items.

Uses the Claude API when a key is available; otherwise falls back to deterministic
comments built from the item's own text, so the weekly job never fails on a
missing secret. Comments are Russian, titles stay in the source language
(sources/review-5-editorial.md §4).
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import logging
import os
import re
import textwrap

from pydantic import BaseModel, Field

log = logging.getLogger("digestbot.enrich")

DEFAULT_MODEL = "claude-opus-5"
BATCH_SIZE = 8

SYSTEM = textwrap.dedent(
    """\
    Ты — редактор еженедельного дайджеста для подкаста про DevOps, Kubernetes,
    инфраструктуру и облака. Ведущие — опытные инженеры: объяснять, что такое под
    или CI, не нужно. Им нужно за одну строку понять, открывать ли ссылку и есть
    ли здесь тема для выпуска.

    Для каждого материала верни поля:

    `what` — «Что внутри», 1-2 предложения на русском, ТОЛЬКО факты: версии,
    цифры, имена компонентов, суть решения или спора. Обязано содержать хотя бы
    одно число или конкретное имя (версия, CVE, компонент, компания). Не пересказ
    заголовка.

    `why` — «Почему важно», РОВНО одно предложение: что это меняет для того, кто
    держит это в проде. Не «это интересно», а «что с этим делать / о чём тут
    спорить».

    `tags` — 2-5 коротких латинских тегов (например: cni, ebpf, breaking).

    `angle` — один из: release, deep-dive, incident, discussion, announcement,
    tooling, security, opinion, research, howto.

    `gloss` — перевод заголовка на русский. Заполняй ТОЛЬКО если заголовок не на
    английском и не на русском (китайский, японский, корейский, немецкий).
    Иначе — пустая строка.

    `angle_line` — «Подкаст-угол»: одно предложение о том, в чём спор, кто
    оппонент и что спросить у гостя. Заполняй только если `podcast_angle` в
    входных данных true, иначе — пустая строка.

    Жёсткие правила:
    - Никогда не выдумывай версии, цифры, имена и факты. Если из данных суть
      неясна — честно опиши, что известно, и скажи, что деталей нет.
    - Не переводи внутри комментария: имена проектов, версии, CVE/GHSA, флаги,
      названия CRD и команды — оставляй латиницей.
    - Запрещённые слова: важный, интересный, значительный, революционный,
      «меняет правила игры», «нельзя пропустить», must-have, «в современном мире»,
      «как известно», «в этой статье», «автор рассказывает».
    - Не начинай с «Статья о том, как…» — сразу с сути.
    - Для релиза: что реально приехало и стоит ли обновляться.
    - Для обсуждения: о чём спорят и какая позиция побеждает, а не только тема.
    - Регистр — принятый инфраструктурный жаргон (нода, под, апстрим, деплой),
      не академические кальки.
    """
)


class Entry(BaseModel):
    id: str = Field(description="id материала из входных данных")
    what: str = Field(description="Что внутри: 1-2 предложения, факты и цифры")
    why: str = Field(description="Почему важно: ровно одно предложение")
    tags: list[str] = Field(default_factory=list, description="2-5 латинских тегов")
    angle: str = Field(default="deep-dive")
    gloss: str = Field(default="", description="перевод заголовка для zh/ja/ko/de")
    angle_line: str = Field(default="", description="подкаст-угол, если запрошен")


class Batch(BaseModel):
    entries: list[Entry]


def _payload(item: dict, angle_top: bool) -> dict:
    eng = {k: v for k, v in (item.get("engagement") or {}).items() if v not in (None, 0, "")}
    body = (item.get("body") or item.get("summary") or "")[:4000]
    out = {
        "id": item["id"],
        "title": item["title"],
        "url": item["url"],
        "source": item.get("source_title") or item.get("source_id"),
        "kind": item.get("source_kind"),
        "section": item.get("section"),
        "lang": item.get("lang"),
        "published": str(item.get("_effective_dt") or item.get("published") or ""),
        "words": item.get("words", 0),
        "text": body,
        "podcast_angle": angle_top,
    }
    if eng:
        out["signals"] = eng
    if item.get("flags"):
        out["flags"] = sorted(k for k, v in item["flags"].items() if v)
    if item.get("release"):
        rel = item["release"]
        out["release"] = {"repo": rel.get("repo"), "tag": rel.get("tag"),
                          "bump": rel.get("bump"), "prerelease": rel.get("prerelease")}
    if item.get("also_seen"):
        out["also_seen"] = item["also_seen"]
    return out


def _fallback(item: dict) -> None:
    """Deterministic comment when no API key is configured."""
    text = re.sub(r"\s+", " ", item.get("body") or item.get("summary") or "").strip()
    if item.get("release"):
        rel = item["release"]
        what = f"Релиз {rel['repo']} {rel['tag']}. " + text[:260]
        why = "Проверьте release notes перед апгрейдом — автоматический комментарий, суть не разобрана."
        angle = "release"
    elif item.get("source_kind") in ("hn", "reddit", "lobsters"):
        what = f"Обсуждение на {item.get('source_title')}. " + text[:260]
        why = "Тред стоит прочитать целиком — автоматический комментарий, позиции сторон не разобраны."
        angle = "discussion"
    else:
        what = text[:300] or item.get("title", "")
        why = "Автоматический комментарий: текст не разобран моделью."
        angle = "deep-dive"
    if what and not what.endswith((".", "!", "?")):
        what += "…"
    item["what"], item["why"], item["angle"] = what, why, angle
    item.setdefault("tags", [])
    item.setdefault("gloss", "")


def _lint(entry: Entry, banned: re.Pattern | None) -> bool:
    """True when the entry is usable."""
    if not entry.what.strip() or not entry.why.strip():
        return False
    if banned and (banned.search(entry.what) or banned.search(entry.why)):
        return False
    if not re.search(r"\d|[A-Za-z]{3}", entry.what):
        return False
    return True


def enrich(items: list[dict], banned: re.Pattern | None = None,
           model: str | None = None, effort: str = "high",
           workers: int = 4, angle_top: int = 20) -> list[dict]:
    if not items:
        return items

    ranked = sorted(items, key=lambda i: -i.get("final", i.get("score", 0)))
    angle_ids = {i["id"] for i in ranked[:angle_top]}

    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")):
        log.warning("no Anthropic credentials - falling back to deterministic comments")
        for it in items:
            _fallback(it)
        return items

    try:
        import anthropic
    except ImportError:
        log.warning("anthropic SDK missing - falling back to deterministic comments")
        for it in items:
            _fallback(it)
        return items

    client = anthropic.Anthropic(max_retries=4, timeout=600.0)
    model = model or os.getenv("DIGEST_MODEL", DEFAULT_MODEL)
    chunks = [items[i:i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]
    results: dict[str, Entry] = {}

    def one(chunk: list[dict]) -> list[Entry]:
        user = ("Материалы недели (JSON). Верни запись для КАЖДОГО id.\n\n"
                + json.dumps([_payload(i, i["id"] in angle_ids) for i in chunk],
                             ensure_ascii=False, indent=1))
        try:
            resp = client.messages.parse(
                model=model,
                max_tokens=16000,
                thinking={"type": "adaptive"},
                output_config={"effort": effort},
                system=[{"type": "text", "text": SYSTEM,
                         "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": user}],
                output_format=Batch,
            )
            if resp.stop_reason == "refusal":
                log.warning("batch refused: %s", getattr(resp, "stop_details", None))
                return []
            return resp.parsed_output.entries
        except Exception as exc:  # noqa: BLE001
            log.warning("enrichment batch failed: %s", exc)
            return []

    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for batch in pool.map(one, chunks):
            for e in batch:
                results[e.id] = e

    filled = 0
    for it in items:
        e = results.get(it["id"])
        if e and _lint(e, banned):
            it["what"] = e.what.strip()
            it["why"] = e.why.strip()
            it["tags"] = [t.strip() for t in e.tags if t.strip()][:5]
            it["angle"] = e.angle.strip() or "deep-dive"
            it["gloss"] = e.gloss.strip()
            it["angle_line"] = e.angle_line.strip()
            filled += 1
        else:
            _fallback(it)
    log.info("enriched %d/%d items via %s", filled, len(items), model)
    return items
