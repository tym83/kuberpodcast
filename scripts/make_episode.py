#!/usr/bin/env python
"""One command from a recording to a YouTube page.

    python scripts/make_episode.py запись.mp4 --number 1

Extracts audio, transcribes it with Whisper, cleans up the names Whisper
mishears, then asks Claude for chapters and copy. Every intermediate file is
kept and reused, so re-running after a tweak does not re-transcribe.
"""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import re
import subprocess
import sys

import yaml
from pydantic import BaseModel, Field

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from digestbot import episode as ep  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent


class Chapter(BaseModel):
    time: str = Field(description="M:SS или H:MM:SS — ровно как у блока")
    title: str = Field(description="о чём эта часть, до 70 символов")


class Speaker(BaseModel):
    name: str
    role: str = Field(default="", description="должность и компания, если названы")


class Page(BaseModel):
    hook: str = Field(description="1-2 предложения: о чём выпуск и в чём спор")
    chapters: list[Chapter]
    speakers: list[Speaker]
    topics: list[str]
    short_description: str
    title_suggestions: list[str] = Field(
        default_factory=list, description="3 варианта заголовка ролика")


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower(), flags=re.UNICODE)
    return re.sub(r"[\s_]+", "-", text.strip())[:60] or "episode"


def media_duration(path: pathlib.Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def ask_model(transcript: str, cfg: dict, model: str | None, effort: str) -> Page | None:
    try:
        import anthropic
    except ImportError:
        logging.error("нет пакета anthropic — установите: pip install -r requirements.txt")
        return None

    client = anthropic.Anthropic(max_retries=3, timeout=900.0)
    model = model or "claude-opus-5"
    logging.info("прошу %s разметить главы и написать описание", model)
    try:
        resp = client.messages.parse(
            model=model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            output_config={"effort": effort},
            system=[{"type": "text", "text": ep.build_prompt(cfg),
                     "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user",
                       "content": "Расшифровка выпуска:\n\n" + transcript}],
            output_format=Page,
        )
    except Exception as exc:  # noqa: BLE001
        logging.error("модель не ответила: %s", exc)
        return None

    if resp.stop_reason == "refusal":
        logging.error("запрос отклонён: %s", getattr(resp, "stop_details", None))
        return None
    u = resp.usage
    cost = (u.input_tokens / 1e6 * 5 + u.output_tokens / 1e6 * 25)
    logging.info("готово: вход %s, выход %s -> ~$%.2f",
                 f"{u.input_tokens:,}", f"{u.output_tokens:,}", cost)
    return resp.parsed_output


def render(page: Page, chapters: list[dict], cfg: dict, number: str) -> str:
    de = cfg.get("description", {})
    tags = " ".join(f"#{t}" for t in de.get("hashtags", []))
    host = de.get("host", "")

    speakers = []
    for s in page.speakers:
        role = s.role.strip()
        speakers.append(f"• {s.name} — {role}" if role else f"• {s.name}")

    out = [f"# Выпуск {number}", ""]
    if page.title_suggestions:
        out += ["## Варианты заголовка", ""]
        out += [f"{i}. {t}" for i, t in enumerate(page.title_suggestions, 1)]
        out += [""]
    out += ["## Описание для YouTube", "", "```", page.hook.strip(), ""]
    if speakers:
        out += ["В студии:"] + speakers + [""]
    out += ["О чём поговорили:"]
    out += [f"— {t.strip()}" for t in page.topics]
    out += ["",
            "Таймкоды ниже. Пишите в комментариях, какие темы разобрать дальше —",
            "и приходите в гости, если есть чем поделиться.",
            "", tags, "```", ""]
    out += ["## Таймкоды", "", "```", ep.render_chapters(chapters), "```", ""]
    out += ["## Короткое описание", "",
            "Для Apple Podcasts, Spotify и шапки соцсетей.", "",
            "```", page.short_description.strip(), "```", ""]
    if host:
        out += [f"<sub>Ведущий: {host}. Страница собрана "
                f"`scripts/make_episode.py`.</sub>", ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="видео- или аудиофайл записи")
    ap.add_argument("--number", "-n", required=True, help="номер выпуска, например 1")
    ap.add_argument("--outdir", default="episodes")
    ap.add_argument("--model", default=None, help="модель Claude")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--transcript-only", action="store_true",
                    help="только расшифровка, без обращения к модели")
    ap.add_argument("--redo", action="store_true",
                    help="перерасшифровать, даже если расшифровка уже есть")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    cfg = yaml.safe_load((ROOT / "sources" / "episode.yaml").read_text(encoding="utf-8"))

    source = pathlib.Path(args.source).expanduser()
    if not source.is_file():
        raise SystemExit(f"файл не найден: {source}")

    workdir = ROOT / args.outdir / str(args.number)
    workdir.mkdir(parents=True, exist_ok=True)
    if args.redo:
        for stale in ("transcript.srt", "transcript.txt"):
            (workdir / stale).unlink(missing_ok=True)

    ffmpeg, whisper = ep.require_tools()
    model_path = ep.ensure_model(cfg["whisper"])
    wav = ep.extract_audio(source, workdir / "audio.wav", ffmpeg)
    srt = ep.transcribe(wav, model_path, cfg["whisper"], workdir / "transcript", whisper)

    segments = ep.clean(ep.parse_srt(srt), cfg)
    duration = media_duration(source)
    logging.info("расшифровка: %d реплик, запись %s",
                 len(segments), ep.hhmmss(duration))

    # Rewrite the artefacts with the corrected names, so the subtitle file that
    # gets uploaded says Talos rather than "Сталос".
    (workdir / "transcript.txt").write_text(
        "\n".join(s.text for s in segments), encoding="utf-8")
    (workdir / "transcript.clean.srt").write_text(_to_srt(segments, srt), encoding="utf-8")

    if args.transcript_only:
        logging.info("готово: %s", workdir)
        return 0

    page = ask_model(ep.transcript_for_model(segments), cfg, args.model, args.effort)
    if page is None:
        logging.error("описание не собрано; расшифровка на месте: %s", workdir)
        return 1

    chapters = ep.enforce_chapter_rules(
        [c.model_dump() for c in page.chapters], duration, cfg.get("chapters", {}))
    logging.info("глав: %d", len(chapters))

    out_file = workdir / "youtube.md"
    out_file.write_text(render(page, chapters, cfg, str(args.number)), encoding="utf-8")
    (workdir / "page.json").write_text(
        json.dumps({"page": page.model_dump(), "chapters": chapters},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    logging.info("готово: %s", out_file)
    return 0


def _to_srt(segments, original: pathlib.Path) -> str:
    """Rebuild an SRT from the cleaned segments, keeping the original timings."""
    raw = original.read_text(encoding="utf-8")
    times = re.findall(r"(\d{2}:\d{2}:\d{2},\d+ --> \d{2}:\d{2}:\d{2},\d+)", raw)
    out = []
    for i, seg in enumerate(segments):
        stamp = times[i] if i < len(times) else None
        if not stamp:
            break
        out.append(f"{i + 1}\n{stamp}\n{seg.text}\n")
    return "\n".join(out)


if __name__ == "__main__":
    raise SystemExit(main())
