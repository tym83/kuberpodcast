#!/usr/bin/env python
"""Build the Pages archive from committed Markdown; no pipeline imports or network IO."""
from __future__ import annotations

import argparse
from datetime import date
from html import escape
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as etree

import markdown
from markdown.extensions import Extension
from markdown.extensions.toc import slugify_unicode
from markdown.treeprocessors import Treeprocessor
import nh3


WEEK_FILE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
VIEWS = (("", "Digest"), ("short", "Short"), ("rejected", "Pipeline report"))
MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")
STYLE = Path(__file__).resolve().parent.parent / "pages" / "style.css"


class ReadingLayout(Treeprocessor):
    """Give generated news entries structure without editing their Markdown."""

    @staticmethod
    def paragraphs(element):
        # Before inline parsing: stray asterisks in an excerpt must not consume
        # the next field's bold label. Fenced/indented code is already protected.
        paragraphs = []
        for line in (element.text or "").splitlines():
            if line.strip():
                paragraph = etree.Element("p")
                paragraph.text = line
                paragraphs.append(paragraph)
        return paragraphs

    def run(self, root):
        entry = None
        for element in list(root):
            if element.tag == "p" and "".join(element.itertext()).startswith("Окно:"):
                details = etree.Element("details", {"class": "issue-details"})
                etree.SubElement(details, "summary").text = "Сводка выпуска и источники"
                root.insert(list(root).index(element), details)
                root.remove(element)
                details.append(element)
                continue
            if element.tag in {"h1", "h2", "h3", "hr"}:
                entry = None
            if element.tag == "h3" and re.match(r"^\d+\.\s", "".join(element.itertext())):
                entry = etree.Element("section", {"class": "news-item"})
                root.insert(list(root).index(element), entry)
            if entry is None:
                continue
            root.remove(element)
            # The generator writes editorial fields on separate soft lines.
            # Ordinary paragraphs, nested lists and fenced code remain untouched.
            fields = {"Что внутри:": "news-body", "Почему важно:": "news-impact",
                      "Подкаст-угол:": "news-angle", "Ещё:": "news-related"}
            if element.tag != "p":
                entry.append(element)
                continue
            has_fields = any(line.startswith(f"**{label}**")
                             for line in (element.text or "").splitlines() for label in fields)
            for paragraph in self.paragraphs(element) if has_fields else [element]:
                text = paragraph.text or ""
                name = next((name for label, name in fields.items()
                             if text.startswith(f"**{label}**")), None)
                if name:
                    paragraph.set("class", name)
                elif text.startswith("`"):
                    name = "news-footer" if text.startswith(("`теги:", "`score ")) else "news-meta"
                    paragraph.set("class", name)
                else:
                    paragraph.attrib.pop("class", None)
                entry.append(paragraph)


class ReadingExtension(Extension):
    def extendMarkdown(self, md):
        # After block parsing, before inline parsing and heading anchors.
        md.treeprocessors.register(ReadingLayout(md), "reading_layout", 25)


def discover_weeks(source: Path) -> list[date]:
    """Only exact dated filenames are issues; reject invalid calendar dates."""
    return sorted(
        (date.fromisoformat(path.stem) for path in source.iterdir()
         if path.is_file() and WEEK_FILE.fullmatch(path.name)),
        reverse=True,
    )


def source_path(source: Path, week: date, view: str) -> Path:
    return source / f"{week.isoformat()}{'-' + view if view else ''}.md"


def page_path(week: date, view: str = "") -> Path:
    return Path("weeks") / week.isoformat() / view / "index.html"


def date_label(week: date, with_year: bool = True) -> str:
    # Do not depend on the machine's locale.
    return f"{week.day:02d} {MONTHS[week.month - 1]}" + (f" {week.year}" if with_year else "")


def time_tag(week: date, with_year: bool = True) -> str:
    return f'<time datetime="{week.isoformat()}">{date_label(week, with_year)}</time>'


def render_markdown(text: str) -> str:
    rendered = markdown.markdown(
        text, extensions=["tables", "fenced_code", "toc", "sane_lists", ReadingExtension()],
        extension_configs={"toc": {"slugify": slugify_unicode}},
    )
    # Sanitize the final HTML, including raw HTML and Markdown-generated hrefs.
    # A maintained HTML5 parser handles malformed markup and encoded URL schemes.
    return nh3.clean(
        rendered,
        tags={"h1", "h2", "h3", "h4", "h5", "h6", "p", "a", "ul", "ol", "li",
              "table", "thead", "tbody", "tr", "th", "td", "pre", "code", "em",
              "strong", "blockquote", "hr", "br", "sub", "sup", "del", "div", "section",
              "details", "summary"},
        attributes={**{f"h{n}": {"id"} for n in range(1, 7)},
                    "a": {"href", "title"}, "ol": {"start"},
                    "code": {"class"},
                    "th": {"style"}, "td": {"style"}},
        allowed_classes={"div": {"toc"}, "section": {"news-item"},
                         "details": {"issue-details"},
                         "p": {"news-meta", "news-body", "news-impact", "news-angle",
                               "news-related", "news-footer"}},
        filter_style_properties={"text-align"},
        url_schemes={"http", "https", "mailto"},
    )


def document(title: str, body: str, root: str = "") -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{escape(title)} · Kuberpodcast</title>
  <link rel="stylesheet" href="{root}style.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <a class="brand" href="{root}index.html">
      <img src="{root}brand-mark.svg" width="72" height="72" alt="">
      <span>Kuberpodcast</span>
    </a>
    <p>Kubernetes / DevOps Weekly Digest</p>
    <img class="float float-cloud" src="{root}objects/cloud.svg" alt="" aria-hidden="true">
    <img class="float float-rocket" src="{root}objects/rocket.svg" alt="" aria-hidden="true">
    <img class="float float-gear" src="{root}objects/gear.svg" alt="" aria-hidden="true">
  </header>
  <span class="rule" aria-hidden="true"></span>
  <main id="main">{body}</main>
  <span class="rule" aria-hidden="true"></span>
  <footer>Weekly reading for the Kubernetes &amp; DevOps community.</footer>
</body>
</html>
'''


def archive_links(source: Path, week: date) -> str:
    return '<div class="view-links">' + "".join(
        f'<a href="{page_path(week, view).as_posix()}">{"Read digest" if not view else label}</a>'
        for view, label in VIEWS if source_path(source, week, view).is_file()
    ) + "</div>"


def archive(source: Path, weeks: list[date]) -> str:
    if not weeks:
        return document("Weekly archive", '<h1>Weekly archive</h1><p>No digests published yet.</p>')
    latest = weeks[0]
    parts = [f'<section class="latest" aria-labelledby="latest">'
             f'<p class="eyebrow" id="latest">Latest / Свежий выпуск</p><h1>{time_tag(latest)}</h1>'
             '<p class="latest-note" lang="ru">Что произошло в инфраструктуре — '
             'и почему это важно для тех, кто её строит.</p>'
             f'{archive_links(source, latest)}'
             '<img class="sticker" src="objects/db.svg" alt="" aria-hidden="true">'
             '</section>',
             '<h2 class="with-mark">Archive</h2>']
    current_year = None
    for week in weeks:
        if week.year != current_year:
            if current_year is not None:
                parts.append("</ul></section>")
            parts.append(f'<section class="archive-year"><h3>{week.year}</h3><ul>')
            current_year = week.year
        parts.append(f'<li><a class="issue-date" href="{page_path(week).as_posix()}">'
                     f'{time_tag(week, False)}</a>{archive_links(source, week)}</li>')
    parts.append("</ul></section>")
    return document("Weekly archive", "\n".join(parts))


def weekly_page(source: Path, weeks: list[date], index: int, view: str) -> str:
    week = weeks[index]
    text = source_path(source, week, view).read_text(encoding="utf-8")
    root = "../../../" if view else "../../"
    navigation = ['<nav class="week-nav" aria-label="Weekly archive">']
    if index + 1 < len(weeks):
        navigation.append(f'<a rel="prev" href="{root}{page_path(weeks[index + 1]).as_posix()}">'
                          '← Previous week</a>')
    navigation.append(f'<a href="{root}index.html">Archive</a>')
    if index > 0:
        navigation.append(f'<a rel="next" href="{root}{page_path(weeks[index - 1]).as_posix()}">'
                          'Next week →</a>')
    navigation.append('</nav><nav class="view-links" aria-label="Issue views">')
    for candidate, label in VIEWS:
        if source_path(source, week, candidate).is_file():
            current = ' aria-current="page"' if candidate == view else ""
            navigation.append(f'<a href="{root}{page_path(week, candidate).as_posix()}"{current}>'
                              f'{label}</a>')
    if re.search(r"^## Содержание\s*$", text, re.MULTILINE):
        navigation.append('<a class="contents-link" href="#содержание" lang="ru">К разделам ↓</a>')
    navigation.append("</nav>")
    content = render_markdown(text)
    body = "\n".join(navigation) + f'<article class="digest view-{view or "full"}" lang="ru">{content}</article>'
    return document(f"{dict(VIEWS)[view]} · {date_label(week)}", body, root)


def build(source: Path, output: Path) -> int:
    source, output = source.resolve(), output.resolve()
    if source == output or source in output.parents or output in source.parents:
        raise ValueError("Input and output directories must not overlap")
    weeks = discover_weeks(source)
    # Render everything before writing, so bad input cannot leave a partial build.
    pages = {Path("index.html"): archive(source, weeks)}
    for index, week in enumerate(weeks):
        for view, _ in VIEWS:
            if source_path(source, week, view).is_file():
                pages[page_path(week, view)] = weekly_page(source, weeks, index, view)
    output.mkdir(parents=True, exist_ok=True)
    for path, content in pages.items():
        destination = output / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    shutil.copyfile(STYLE, output / "style.css")
    shutil.copyfile(STYLE.with_name("brand-mark.svg"), output / "brand-mark.svg")
    # The brand objects, exported from the kit that draws the openers. Copied
    # wholesale so adding one to the kit needs no change here.
    objects = STYLE.with_name("objects")
    if objects.is_dir():
        shutil.copytree(objects, output / "objects", dirs_exist_ok=True)
    # Remove obsolete generated views on rebuild, never unrelated output files.
    for path in (output / "weeks").glob("*/**/index.html"):
        relative = path.relative_to(output)
        if (WEEK_FILE.fullmatch(relative.parts[1] + ".md")
                and relative not in pages
                and (len(relative.parts) == 3
                     or (len(relative.parts) == 4 and relative.parts[2] in {"short", "rejected"}))):
            path.unlink()
    return len(weeks)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("digest"))
    parser.add_argument("--output", type=Path, default=Path("_site"))
    args = parser.parse_args()
    try:
        count = build(args.input, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Pages build failed: {error}\n")
    print(f"Built {count} weekly issues in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
