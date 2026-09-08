"""Turn a recording into a YouTube page: transcript, chapters, description.

Whisper is fast and accurate enough on Russian technical speech, but it
mishears product names and invents subtitle credits on trailing silence, so
the transcript is cleaned before anything reads it. Chapters then come from a
model that sees the whole conversation at once — the topic boundaries in a
podcast are semantic, and no heuristic over pauses finds them.
"""
from __future__ import annotations

import logging
import os
import pathlib
import re
import shutil
import subprocess
from dataclasses import dataclass

log = logging.getLogger("digestbot.episode")

MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{name}.bin"


@dataclass
class Segment:
    start: float
    text: str


# ── transcription ────────────────────────────────────────────────────────────

def require_tools() -> tuple[str, str]:
    ffmpeg = shutil.which("ffmpeg")
    whisper = shutil.which("whisper-cli") or shutil.which("whisper-cpp")
    missing = []
    if not ffmpeg:
        missing.append("ffmpeg (brew install ffmpeg)")
    if not whisper:
        missing.append("whisper-cli (brew install whisper-cpp)")
    if missing:
        raise SystemExit("не хватает инструментов: " + ", ".join(missing))
    return ffmpeg, whisper


def ensure_model(cfg: dict) -> pathlib.Path:
    directory = pathlib.Path(os.path.expanduser(cfg["model_dir"]))
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"ggml-{cfg['model']}.bin"
    if path.exists():
        return path
    log.info("скачиваю модель %s (это разово)", cfg["model"])
    url = MODEL_URL.format(name=cfg["model"])
    subprocess.run(["curl", "-L", "--fail", "-o", str(path), url], check=True)
    return path


def extract_audio(source: pathlib.Path, dest: pathlib.Path, ffmpeg: str) -> pathlib.Path:
    """Whisper wants 16 kHz mono PCM; anything else it resamples internally."""
    if dest.exists():
        log.info("аудио уже извлечено: %s", dest)
        return dest
    log.info("извлекаю аудио из %s", source.name)
    subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(source), "-vn",
         "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(dest), "-y"],
        check=True,
    )
    return dest


def transcribe(wav: pathlib.Path, model: pathlib.Path, cfg: dict,
               out_prefix: pathlib.Path, whisper: str) -> pathlib.Path:
    srt = out_prefix.with_suffix(".srt")
    if srt.exists():
        log.info("расшифровка уже есть: %s", srt)
        return srt
    log.info("расшифровываю (примерно минута на каждые восемь минут записи)")
    subprocess.run(
        [whisper, "-m", str(model), "-f", str(wav), "-l", cfg["language"],
         "-osrt", "-otxt", "-of", str(out_prefix), "-pp"],
        check=True,
    )
    return srt


# ── cleanup ──────────────────────────────────────────────────────────────────

def parse_srt(path: pathlib.Path) -> list[Segment]:
    raw = path.read_text(encoding="utf-8")
    out = []
    for stamp, text in re.findall(
            r"(\d{2}:\d{2}:\d{2}),\d+ --> .*?\n(.*?)(?=\n\n|\Z)", raw, re.S):
        h, m, sec = map(int, stamp.split(":"))
        body = " ".join(text.split())
        if body:
            out.append(Segment(h * 3600 + m * 60 + sec, body))
    return out


def apply_glossary(segments: list[Segment], glossary: dict) -> int:
    """Fix the product names Whisper reliably mishears."""
    if not glossary:
        return 0
    patterns = [
        (re.compile(rf"(?<!\w){re.escape(wrong)}(?!\w)", re.I | re.U), right)
        for wrong, right in sorted(glossary.items(), key=lambda kv: -len(kv[0]))
    ]
    fixed = 0
    for seg in segments:
        for pattern, right in patterns:
            seg.text, n = pattern.subn(right, seg.text)
            fixed += n
    return fixed


def clean(segments: list[Segment], cfg: dict) -> list[Segment]:
    """Fix misheard names, then drop invented credits from the tail.

    Only the tail is examined: "спасибо за просмотр" spoken mid-episode is real
    speech; the same words after the last exchange are the model filling
    silence with what its training data put at the end of subtitle files.
    """
    fixed = apply_glossary(segments, cfg.get("glossary") or {})
    rx_list = cfg.get("hallucinations") or []
    rx = re.compile("|".join(f"(?:{p})" for p in rx_list), re.I | re.U) if rx_list else None
    if rx and segments:
        cutoff = segments[-1].start - 30.0
        before = len(segments)
        segments = [s for s in segments
                    if s.start < cutoff or not rx.search(s.text)]
        dropped = before - len(segments)
    else:
        dropped = 0
    log.info("правки словаря: %d, отброшено выдуманных строк: %d", fixed, dropped)
    return segments


# ── shaping the transcript for the model ─────────────────────────────────────

def blocks(segments: list[Segment], window: float = 20.0) -> list[tuple[float, str]]:
    """Group into fixed windows so the model can point at a start time.

    Twenty seconds is a compromise: fine enough that a chapter lands on the
    right sentence, coarse enough that a 75-minute episode stays well inside
    the context window.
    """
    out: list[tuple[float, str]] = []
    if not segments:
        return out
    bucket = segments[0].start // window * window
    buf: list[str] = []
    for seg in segments:
        b = seg.start // window * window
        if b != bucket:
            if buf:
                out.append((bucket, " ".join(buf)))
            bucket, buf = b, []
        buf.append(seg.text)
    if buf:
        out.append((bucket, " ".join(buf)))
    return out


def hhmmss(seconds: float) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def to_seconds(stamp: str) -> int:
    parts = [int(p) for p in stamp.strip().split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


# ── chapter validation ───────────────────────────────────────────────────────

def enforce_chapter_rules(chapters: list[dict], duration: float,
                          cfg: dict) -> list[dict]:
    """YouTube refuses a chapter list that breaks any of its rules, silently.

    It wants at least three chapters, the first at 0:00, ascending order and a
    minimum length each. A list that violates one of these is simply not shown,
    with no error anywhere — so it is checked here rather than hoped for.
    """
    min_gap = cfg.get("min_gap_seconds", 25)
    cleaned: list[dict] = []
    for ch in chapters:
        try:
            t = to_seconds(ch["time"])
        except (ValueError, KeyError):
            log.warning("пропускаю главу с неразборчивым временем: %r", ch)
            continue
        title = " ".join(str(ch.get("title", "")).split())
        if not title or t > duration:
            continue
        cleaned.append({"seconds": t, "title": title})

    cleaned.sort(key=lambda c: c["seconds"])

    deduped: list[dict] = []
    for ch in cleaned:
        if deduped and ch["seconds"] - deduped[-1]["seconds"] < min_gap:
            continue                      # too close together to be readable
        deduped.append(ch)

    if deduped:
        deduped[0]["seconds"] = 0         # YouTube requires the first at 0:00
    if len(deduped) < cfg.get("min_count", 3):
        log.warning("глав получилось %d — YouTube покажет их только от %d",
                    len(deduped), cfg.get("min_count", 3))
    return deduped


def render_chapters(chapters: list[dict]) -> str:
    return "\n".join(f"{hhmmss(c['seconds'])} {c['title']}" for c in chapters)


# ── writing the page ─────────────────────────────────────────────────────────

SYSTEM = """\
Ты — редактор подкаста про Kubernetes, инфраструктуру и облака. Ведущий и
гости — практикующие инженеры. Тебе дают расшифровку выпуска, разбитую на
блоки по 20 секунд с отметками времени.

Твоя задача — подготовить страницу выпуска для YouTube.

ГЛАВЫ (chapters). Правила:
{rules}
Ориентир — примерно {per_hour} глав на час записи. Время бери РОВНО такое,
какое стоит у блока, где тема начинается, в формате M:SS или H:MM:SS.
Заголовок — до {max_title} символов.

КРЮЧОК (hook). Одно-два предложения о том, про что выпуск и в чём его спор.
До {hook_max} символов. YouTube показывает эти строки в поиске, поэтому они
должны работать в отрыве от всего остального. Без «в этом выпуске мы
поговорили о» — сразу к сути.

УЧАСТНИКИ (speakers). Кто в студии: имя, должность и компания, если их
назвали во вступлении. Ведущего помечай как «ведущий». Если что-то не
прозвучало — не выдумывай, оставь только то, что есть.

ТЕМЫ (topics). От {topics_min} до {topics_max} пунктов о том, что разобрали.
Каждый — законченная мысль, а не рубрика. Не «Про сеть», а «Почему проблемы
с сетью — это ядро Linux, а не Kubernetes».

КОРОТКОЕ ОПИСАНИЕ (short_description). До 300 символов, для Apple Podcasts
и Spotify. Самостоятельный текст, не обрезанный крючок.

Жёсткие правила:
- Ничего не выдумывай: ни имён, ни цифр, ни компаний, ни выводов, которых
  в записи нет.
- Названия продуктов — в правильном регистре и латиницей: Kubernetes, etcd,
  OpenShift, Talos, Argo CD, Cilium. Никакой транслитерации.
- Расшифровка автоматическая, в ней есть оговорки и ошибки распознавания.
  Если слово выглядит искажённым, восстанавливай по смыслу.
- Без канцелярита и рекламных оборотов. Пиши так, как говорят инженеры.
"""


def build_prompt(cfg: dict) -> str:
    ch = cfg.get("chapters", {})
    de = cfg.get("description", {})
    lo, hi = (de.get("topics_count") or [5, 8])[:2]
    return SYSTEM.format(
        rules=(ch.get("rules") or "").strip(),
        per_hour=ch.get("target_per_hour", 25),
        max_title=ch.get("max_title_chars", 70),
        hook_max=de.get("hook_max_chars", 300),
        topics_min=lo, topics_max=hi,
    )


def transcript_for_model(segments: list[Segment], window: float = 20.0) -> str:
    return "\n".join(f"[{hhmmss(t)}] {text}" for t, text in blocks(segments, window))
