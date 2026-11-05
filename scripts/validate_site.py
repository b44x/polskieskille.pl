#!/usr/bin/env python3
"""Check static discovery, metadata, structured data and internal links without dependencies."""

import json
from html.parser import HTMLParser
from pathlib import Path
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://polskieskille.pl"


class Page(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.titles, self.headings, self.schemas, self.links = [], [], [], []
        self.meta, self.canonicals, self.ids = {}, [], set()
        self.capture, self.buffer = None, []
        self.feed(raw)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "meta":
            self.meta[attrs.get("name") or attrs.get("property")] = attrs.get("content")
        if tag in ("title", "h1") or (tag == "script" and attrs.get("type") == "application/ld+json"):
            self.capture, self.buffer = tag, []

    def handle_data(self, data):
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag != self.capture:
            return
        value = "".join(self.buffer).strip()
        if tag == "title":
            self.titles.append(value)
        elif tag == "h1":
            self.headings.append(value)
        else:
            self.schemas.append(json.loads(value))
        self.capture, self.buffer = None, []


def main():
    registry = json.loads((ROOT / "assets/registry.min.json").read_text(encoding="utf-8"))
    paths = [ROOT / "index.html"] + [ROOT / "skille" / skill["name"] / "index.html" for skill in registry["skills"]]
    titles, descriptions, urls = set(), set(), set()
    pages = {}
    for path in paths:
        page = Page(path.read_text(encoding="utf-8"))
        pages[path] = page
        url = ORIGIN + "/" + ("" if path == ROOT / "index.html" else str(path.parent.relative_to(ROOT)) + "/")
        assert page.canonicals == [url], "Wrong canonical: " + str(path)
        assert len(page.titles) == 1 and page.titles[0] and page.titles[0] not in titles, "Missing or duplicate title: " + str(path)
        assert len(page.headings) == 1 and page.headings[0], "Expected one visible H1: " + str(path)
        description = page.meta.get("description")
        assert description and description not in descriptions, "Missing or duplicate description: " + str(path)
        assert page.meta.get("og:url") == url, "Wrong Open Graph URL: " + str(path)
        assert page.meta.get("og:title") and page.meta.get("og:image"), "Incomplete social preview: " + str(path)
        assert page.meta.get("twitter:card") == "summary_large_image", "Missing Twitter card: " + str(path)
        assert page.schemas, "Missing JSON-LD: " + str(path)
        titles.add(page.titles[0]); descriptions.add(description); urls.add(url)
    sitemap = ET.parse(ROOT / "sitemap.xml")
    assert {e.text for e in sitemap.findall(".//{*}loc")} == urls, "Sitemap does not match canonical pages"
    home = pages[ROOT / "index.html"]
    for skill in registry["skills"]:
        assert "/skille/{}/".format(skill["name"]) in home.links, "Skill missing from static HTML: " + skill["name"]
    for path, page in pages.items():
        for href in page.links:
            parsed = urllib.parse.urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            target = (ROOT / parsed.path.lstrip("/")) if parsed.path.startswith("/") else path.parent / parsed.path
            target = target.resolve()
            if target.is_dir():
                target = target / "index.html"
            assert target.is_file(), "Broken internal link {} in {}".format(href, path)
            if parsed.fragment and target.suffix == ".html":
                destination = pages.get(target) or Page(target.read_text(encoding="utf-8"))
                assert parsed.fragment in destination.ids, "Missing anchor {} in {}".format(href, path)
    print("Validated {} static pages: unique metadata, canonical URLs, JSON-LD, sitemap and internal links".format(len(paths)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, OSError, ValueError) as error:
        print("Site validation failed: " + str(error), file=sys.stderr)
        sys.exit(1)
