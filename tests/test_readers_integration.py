"""Illustrated readers are wired into the laboratory: map, manifest, guide links and integrity."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urldefrag, urlparse

LAB = Path(__file__).resolve().parents[1]
HREF = re.compile(r'(?:href|src)="([^"]+)"')


def local_links(page):
    for target in HREF.findall(page.read_text(encoding="utf-8")):
        target, _ = urldefrag(target)
        if not target or urlparse(target).scheme or target.startswith(("//", "mailto:")):
            continue
        yield target


class ReaderIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.entries = json.loads((LAB / "chapter-map.json").read_text())

    def test_chapter_map_reader_paths_exist(self):
        self.assertEqual(len(self.entries), 27)
        for entry in self.entries:
            reader = LAB / entry["reader"]
            self.assertTrue(reader.is_file(), entry["reader"])
            self.assertTrue(entry["reader"].startswith(f"readers/{entry['chapter']:02d}-"))

    def test_manifest_counts_readers_and_matches_map(self):
        manifest = json.loads((LAB / "lab-manifest.json").read_text())
        self.assertEqual(manifest["readers"], 27)
        self.assertTrue((LAB / manifest["readers_index"]).is_file())
        self.assertEqual(manifest["canonical_sources"], self.entries)

    def test_guide_pages_link_readers_and_links_resolve(self):
        index = LAB / "guide/index.html"
        text = index.read_text(encoding="utf-8")
        self.assertIn('href="../readers/index.html"', text)
        pages = [index, LAB / "readers/index.html", *(LAB / "guide/chapters").glob("*.html")]
        for entry in self.entries:
            self.assertIn(f'href="../{entry["reader"]}"', text)
            chapter_page = LAB / "guide/chapters" / (Path(entry["notebook"]).stem + ".html")
            self.assertIn(f'href="../../{entry["reader"]}"', chapter_page.read_text(encoding="utf-8"))
        for entry in self.entries:
            pages.append(LAB / entry["reader"])
        for page in pages:
            for target in local_links(page):
                self.assertTrue((page.parent / unquote(target)).exists(), f"{page.relative_to(LAB)} -> {target}")

    def test_readers_make_no_external_requests(self):
        for page in [LAB / "readers/index.html", *(LAB / e["reader"] for e in self.entries)]:
            text = page.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r'(?:src|href)="(?:https?:)?//', text), page.name)

    def test_integrity_manifest_covers_readers(self):
        files = json.loads((LAB / "file-integrity.json").read_text())["files"]
        expected = ["readers/index.html", *(e["reader"] for e in self.entries)]
        for name in expected:
            self.assertIn(name, files)
            self.assertEqual(files[name], hashlib.sha256((LAB / name).read_bytes()).hexdigest(), name)


if __name__ == "__main__":
    unittest.main()
