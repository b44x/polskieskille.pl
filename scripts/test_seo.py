#!/usr/bin/env python3
"""Offline checks for crawlable skill pages, metadata, links and structured data."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_seo

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.elements, self.schemas = [], []
        self.h1_count, self.collect, self.script = 0, False, ""
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag == "h1":
            self.h1_count += 1
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.collect, self.script = True, ""

    def handle_data(self, data):
        if self.collect:
            self.script += data

    def handle_endtag(self, tag):
        if tag == "script" and self.collect:
            self.schemas.append(json.loads(self.script))
            self.collect = False


class StaticSeoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "assets/registry.min.json").read_text(encoding="utf-8"))
        cls.copy = build_seo.load_copy()
        cls.pages = {}
        for skill in cls.registry["skills"]:
            path = ROOT / "skille" / skill["name"] / "index.html"
            source = path.read_text(encoding="utf-8")
            cls.pages[skill["name"]] = (source, Page(source))

    def test_unique_titles_descriptions_and_canonicals(self):
        titles, descriptions = [], []
        for name, (source, page) in self.pages.items():
            with self.subTest(skill=name):
                self.assertEqual(page.h1_count, 1)
                self.assertIn('<html lang="pl">', source)
                titles.extend(re.findall(r"<title>(.*?)</title>", source))
                description = [a["content"] for tag, a in page.elements if tag == "meta" and a.get("name") == "description"]
                self.assertEqual(description, [self.copy[name]["description"]])
                descriptions.extend(description)
                canonical = [a["href"] for tag, a in page.elements if tag == "link" and a.get("rel") == "canonical"]
                self.assertEqual(canonical, [build_seo.skill_url(name)])
                self.assertTrue(any(tag == "meta" and a.get("property") == "og:url" and a.get("content") == canonical[0] for tag, a in page.elements))
                self.assertTrue(any(tag == "meta" and a.get("name") == "twitter:card" for tag, a in page.elements))
        self.assertEqual(len(titles), len(self.pages))
        self.assertEqual(len(set(titles)), len(titles))
        self.assertEqual(len(set(descriptions)), len(descriptions))

    def test_static_copy_prompts_and_actual_script_paths(self):
        for skill in self.registry["skills"]:
            name = skill["name"]
            source, page = self.pages[name]
            with self.subTest(skill=name):
                visible = re.sub(r"<[^>]+>", " ", source)
                self.assertIn(self.copy[name]["h1"], visible)
                for prompt in self.copy[name]["prompts"]:
                    self.assertIn(prompt, visible)
                for limit in self.copy[name]["limits"]:
                    self.assertIn(limit, visible)
                help_command = "python3 .agents/skills/{}/{} --help".format(name, skill["entrypoint"])
                self.assertIn(help_command, visible)
                self.assertNotIn('id="app"', source)

    def test_internal_links_resolve_to_published_files(self):
        for name, (source, page) in self.pages.items():
            for tag, attrs in page.elements:
                value = attrs.get("href", attrs.get("src", ""))
                if not value.startswith("/"):
                    continue
                with self.subTest(skill=name, link=value):
                    target = ROOT / value.split("#", 1)[0].lstrip("/")
                    if target.is_dir():
                        target = target / "index.html"
                    self.assertTrue(target.is_file())

    def test_structured_data_matches_visible_skill_and_breadcrumbs(self):
        for name, (source, page) in self.pages.items():
            with self.subTest(skill=name):
                self.assertEqual(len(page.schemas), 1)
                graph = {item["@type"]: item for item in page.schemas[0]["@graph"]}
                self.assertEqual(set(graph), {"SoftwareSourceCode", "BreadcrumbList"})
                software = graph["SoftwareSourceCode"]
                self.assertEqual(software["name"], self.copy[name]["h1"])
                self.assertEqual(software["url"], build_seo.skill_url(name))
                self.assertNotIn("aggregateRating", software)
                crumbs = graph["BreadcrumbList"]["itemListElement"]
                self.assertEqual(crumbs[0]["item"], build_seo.SITE + "/")
                self.assertEqual(crumbs[-1]["item"], software["url"])

    def test_sitemap_matches_the_catalogue(self):
        urls = [item.find("{*}loc").text for item in ET.parse(ROOT / "sitemap.xml").findall("{*}url")]
        expected = {build_seo.SITE + "/"} | {build_seo.skill_url(s["name"]) for s in self.registry["skills"]}
        self.assertEqual(set(urls), expected)
        self.assertEqual(len(urls), len(expected))

    def test_home_catalogue_links_and_item_list_count(self):
        page = Page(build_seo.catalogue_html(self.registry, self.copy))
        cards = [a for tag, a in page.elements if tag == "article" and a.get("class") == "card"]
        self.assertEqual(len(cards), len(self.pages))
        links = {a.get("href") for tag, a in page.elements if tag == "a"}
        for name in self.pages:
            self.assertIn("/skille/" + name + "/", links)
        graph = build_seo.home_schema(self.registry, self.copy)["@graph"]
        catalog = next(item for item in graph if item["@type"] == "CollectionPage")["mainEntity"]
        self.assertEqual(catalog["numberOfItems"], len(self.pages))
        self.assertEqual(len(catalog["itemListElement"]), len(self.pages))


if __name__ == "__main__":
    unittest.main()
