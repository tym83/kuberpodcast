"""Offline archive tests; run with python -m unittest discover -s pages -v."""
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit

from scripts.build_pages import build, discover_weeks, render_markdown


class HTML(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def attrs(self, tag):
        return [attrs for name, attrs in self.elements if name == tag]


class PagesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "digest"
        self.source.mkdir()
        self.output = self.root / "_site"

    def write(self, filename, text="# Выпуск\n\nРусский текст."):
        (self.source / filename).write_text(text, encoding="utf-8")

    def read(self, relative="index.html"):
        return (self.output / relative).read_text(encoding="utf-8")

    def test_exact_filenames_sorting_and_years(self):
        for filename in ["2026-09-08.md", "2025-12-26.md", "2026-09-11-short.md",
                         "2026-09-11.md", "2026-09-11-rejected.md", "README.md",
                         "2027-01-01-short.md", "2026-9-12.md", "2026-09-12.md.bak"]:
            self.write(filename)
        (self.source / "2028-01-01.md").mkdir()
        self.assertEqual(discover_weeks(self.source),
                         [date(2026, 9, 11), date(2026, 9, 8), date(2025, 12, 26)])
        self.assertEqual(build(self.source, self.output), 3)
        home = self.read()
        self.assertIn("11 September 2026", home)
        self.assertLess(home.index("2026-09-11/index.html"), home.index("2026-09-08/index.html"))
        self.assertLess(home.index("<h3>2026</h3>"), home.index("<h3>2025</h3>"))
        self.assertEqual(len(list((self.output / "weeks").iterdir())), 3)

    def test_optional_views_and_previous_next(self):
        for filename in ["2025-12-26.md", "2026-09-08.md", "2026-09-11.md",
                         "2026-09-08-short.md", "2026-09-08-rejected.md"]:
            self.write(filename)
        build(self.source, self.output)
        for view in ["", "short/", "rejected/"]:
            page = HTML(self.read(f"weeks/2026-09-08/{view}index.html"))
            links = page.attrs("a")
            self.assertTrue(any(a.get("rel") == "prev" and "2025-12-26" in a["href"] for a in links))
            self.assertTrue(any(a.get("rel") == "next" and "2026-09-11" in a["href"] for a in links))
            self.assertEqual(len([a for a in links if a.get("aria-current") == "page"]), 1)
        newest = self.read("weeks/2026-09-11/index.html")
        oldest = self.read("weeks/2025-12-26/index.html")
        self.assertNotIn('rel="next"', newest)
        self.assertNotIn('rel="prev"', oldest)
        self.assertNotIn("Pipeline report", newest)
        self.assertNotIn(">Short<", newest)
        self.assertFalse((self.output / "weeks/2026-09-11/short/index.html").exists())
        self.assertIn("Pipeline report", self.read())
        self.assertNotIn(">Rejected<", self.read())
        self.assert_local_links()

    def assert_local_links(self):
        for path in self.output.rglob("*.html"):
            relative = path.relative_to(self.output).as_posix()
            parsed = HTML(path.read_text(encoding="utf-8"))
            for tag, attrs in parsed.elements:
                if tag not in {"a", "link"} or "href" not in attrs:
                    continue
                href = attrs["href"]
                if urlsplit(href).scheme:
                    continue
                for base in ["https://tym83.github.io/kuberpodcast/", self.output.as_uri() + "/"]:
                    target = urlsplit(urljoin(base + relative, href))
                    base_path = urlsplit(base).path
                    self.assertTrue(target.path.startswith(base_path), (relative, href))
                    local = self.output / unquote(target.path[len(base_path):])
                    self.assertTrue(local.is_file(), (relative, href, local))
                    if target.fragment:
                        ids = {a["id"] for _, a in HTML(local.read_text()).elements if "id" in a}
                        self.assertIn(unquote(target.fragment), ids)

    def test_single_week_and_empty_archive(self):
        self.assertEqual(build(self.source, self.output), 0)
        self.assertIn("No digests published yet", self.read())
        self.assertTrue((self.output / "style.css").is_file())
        self.write("2026-09-11.md")
        self.assertEqual(build(self.source, self.output), 1)
        page = self.read("weeks/2026-09-11/index.html")
        self.assertNotIn('rel="prev"', page)
        self.assertNotIn('rel="next"', page)
        self.assert_local_links()

    def test_markdown_and_cyrillic_toc(self):
        text = '''# Выпуск

- [Безопасность и supply chain](#безопасность-и-supply-chain)

## Безопасность и supply chain

Русский текст с [ссылкой](https://example.org/news?q=1&lang=ru).

| Причина | Штук |
|---|---:|
| тест | 42 |

```yaml
name: пример
literal: <script>alert(1)</script>
```

3. Первый
4. Второй

> Цитата

---

<sub>Источник</sub>
'''
        self.write("2026-09-11.md", text)
        build(self.source, self.output)
        page = self.read("weeks/2026-09-11/index.html")
        for fragment in ['id="безопасность-и-supply-chain"', "<table>", "<thead>",
                         "<pre><code", 'class="language-yaml"', '<ol start="3">',
                         "<blockquote>", "<hr", "<sub>Источник</sub>", "Русский текст",
                         "&lt;script&gt;"]:
            self.assertIn(fragment, page)
        self.assertEqual(HTML(page).attrs("th")[1]["style"].replace(" ", "").rstrip(";"),
                         "text-align:right")
        links = HTML(page).attrs("a")
        self.assertTrue(any(a.get("href") == "https://example.org/news?q=1&lang=ru" for a in links))
        self.assert_local_links()

    def test_untrusted_html_and_unsafe_urls(self):
        rendered = render_markdown('''# Safe

<script>alert(1)</script><style>body{display:none}</style>
<iframe src="https://evil.example"></iframe>
<img src="x" onerror="alert(1)">
<a href="jav&#x61;script:alert(1)" onclick="alert(1)">bad</a>
<sub onclick="alert(1)">source</sub>

[bad](javascript:alert%281%29)
[data](data:text/html;base64,PHNjcmlwdD4=)
[good](https://example.org)
''')
        parsed = HTML(rendered)
        self.assertFalse({"script", "style", "iframe", "img"} & {tag for tag, _ in parsed.elements})
        for _, attrs in parsed.elements:
            self.assertFalse(any(key.startswith("on") for key in attrs))
            if "href" in attrs:
                self.assertEqual(urlsplit(attrs["href"]).scheme, "https")
        self.assertIn("<sub>source</sub>", rendered)

    def test_rebuild_is_deterministic_and_removes_stale_views(self):
        self.write("2026-09-11.md")
        self.write("2026-09-11-short.md")
        build(self.source, self.output)
        before = {p.relative_to(self.output): p.read_bytes() for p in self.output.rglob("*") if p.is_file()}
        build(self.source, self.output)
        self.assertEqual(before, {p.relative_to(self.output): p.read_bytes()
                                 for p in self.output.rglob("*") if p.is_file()})
        (self.source / "2026-09-11-short.md").unlink()
        build(self.source, self.output)
        self.assertFalse((self.output / "weeks/2026-09-11/short/index.html").exists())
        (self.source / "2026-09-11.md").unlink()
        build(self.source, self.output)
        self.assertFalse(list((self.output / "weeks").rglob("*.html")))

    def test_bad_input_fails_before_writing(self):
        self.write("2026-02-30.md")
        with self.assertRaises(ValueError):
            build(self.source, self.output)
        self.assertFalse(self.output.exists())
        with self.assertRaises(ValueError):
            build(self.source, self.source)
        with self.assertRaises(ValueError):
            build(self.source, self.source / "site")


if __name__ == "__main__":
    unittest.main()
