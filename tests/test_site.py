"""Site tests: the noindex guarantees. Builds with Hugo when it is installed, else skips that part."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_site  # noqa: E402

NOINDEX = '<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class CheckSiteTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.public = Path(tmp.name)
        write(self.public / "index.html", f"<html><head>{NOINDEX}</head></html>")
        write(self.public / "robots.txt", "User-agent: *\nDisallow: /\n")

    def test_good_site_passes(self):
        self.assertEqual(check_site.check(self.public), [])

    def test_page_without_noindex_fails(self):
        write(self.public / "posts" / "a" / "index.html", "<html><head></head></html>")
        self.assertTrue(any("posts/a/index.html" in p.replace("\\", "/") for p in check_site.check(self.public)))

    def test_index_only_noindex_value_is_not_enough(self):
        write(self.public / "x.html", '<meta name="robots" content="index, follow">')
        self.assertTrue(check_site.check(self.public))

    def test_missing_or_weak_robots_txt_fails(self):
        (self.public / "robots.txt").unlink()
        self.assertTrue(check_site.check(self.public))
        write(self.public / "robots.txt", "User-agent: *\nDisallow:\n")
        self.assertTrue(check_site.check(self.public))
        write(self.public / "robots.txt", "User-agent: *\nDisallow: /\nAllow: /public\n")
        self.assertTrue(check_site.check(self.public))

    def test_sitemap_and_feeds_fail(self):
        write(self.public / "sitemap.xml", "<urlset/>")
        write(self.public / "index.xml", "<rss/>")
        self.assertEqual(len(check_site.check(self.public)), 2)


@unittest.skipUnless(shutil.which("hugo"), "hugo is not installed")
class HugoBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.tmp.name)
        for name in ("hugo.toml", "layouts", "static"):
            src = ROOT / name
            (shutil.copytree if src.is_dir() else shutil.copy)(src, cls.site / name)
        post = ("---\ntitle: A post\nsource: Src\nsource_url: https://orig.example/a\ndate: '2026-10-10T00:00:00Z'\n"
                "image: https://i.example/i.jpg\ntags: [one]\n---\n\nHello **world**.\n\n![pic](https://i.example/p.png)\n")
        write(cls.site / "content" / "posts" / "src" / "a-post-123456.md", post)
        write(cls.site / "content" / "posts" / "src" / "gone-abcdef.md",
              "---\ntitle: Gone\nsource: Src\nsource_url: https://orig.example/gone\nstub: true\n---\n")
        result = subprocess.run(["hugo", "--baseURL", "https://me.github.io/rss/", "--destination", "public"],
                                cwd=cls.site, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        cls.public = cls.site / "public"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_generated_page_passes_the_check(self):
        self.assertEqual(check_site.check(self.public), [])
        self.assertGreaterEqual(len(list(self.public.rglob("*.html"))), 6)  # home, posts, tag pages, 404 ...

    def test_post_page_has_notice_canonical_and_banner(self):
        html = (self.public / "posts" / "src" / "a-post-123456" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="canonical" href="https://orig.example/a">', html)
        self.assertIn("Excerpted from Src for reading purposes, not distribution. Read the original:", html)
        self.assertIn('href="https://orig.example/a"', html)
        self.assertIn('class="banner" src="https://i.example/i.jpg"', html)
        self.assertIn("<strong>world</strong>", html)

    def test_other_pages_have_no_canonical_pointing_at_the_mirror(self):
        for page in self.public.rglob("*.html"):
            html = page.read_text(encoding="utf-8")
            if "orig.example" not in html:
                self.assertNotIn('rel="canonical"', html, page)

    def test_stub_redirects_to_the_original_and_is_not_listed(self):
        html = (self.public / "posts" / "src" / "gone-abcdef" / "index.html").read_text(encoding="utf-8")
        self.assertIn('http-equiv="refresh" content="0; url=https://orig.example/gone"', html)
        self.assertIn("This mirror copy has been removed.", html)
        home = (self.public / "index.html").read_text(encoding="utf-8")
        self.assertIn("A post", home)
        self.assertNotIn("Gone", home)

    def test_no_sitemap_or_feeds(self):
        self.assertFalse((self.public / "sitemap.xml").exists())
        self.assertEqual(list(self.public.rglob("index.xml")), [])


if __name__ == "__main__":
    unittest.main()
