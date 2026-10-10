"""Offline tests for the article mirror: python -m unittest tests.test_mirror"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import feedparser

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import notify  # noqa: E402
from mirror import extract, feedconf, http_client  # noqa: E402
from mirror import posts as mposts  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parent.parent
HOUR = 3600


class SlugTest(unittest.TestCase):
    def test_slug_is_url_safe_and_stable(self):
        slug = mposts.make_slug("Hello, Wörld! It's 100% “fun”", "guid-1")
        self.assertRegex(slug, r"^[a-z0-9-]+-[0-9a-f]{6}$")
        self.assertEqual(slug, mposts.make_slug("Hello, Wörld! It's 100% “fun”", "guid-1"))
        self.assertTrue(slug.startswith("hello-world-its-100-fun-"))

    def test_same_title_different_guid_does_not_collide(self):
        self.assertNotEqual(mposts.make_slug("Same", "a"), mposts.make_slug("Same", "b"))

    def test_long_and_empty_titles(self):
        self.assertLessEqual(len(mposts.slugify("word " * 50)), 60)
        self.assertEqual(mposts.slugify("日本語"), "post")
        self.assertEqual(mposts.slugify("Anna's Archive blog"), "annas-archive-blog")


class FrontmatterTest(unittest.TestCase):
    def test_fields_roundtrip_in_documented_order(self):
        fields = {"title": "A: tricky 'title'", "source": "Reason", "source_url": "https://r.example/a",
                  "author": "Jo", "date": "2026-10-10T12:00:00Z", "fetched": "2026-10-10T13:00:00Z",
                  "image": "https://r.example/i.jpg", "summary": "Two\nlines", "tags": ["x", "y: z"],
                  "guid": "g1"}
        block = mposts.build_frontmatter(fields)
        self.assertTrue(block.startswith("---\n") and block.endswith("---\n"))
        data, body = mposts.split_frontmatter(block + "\nBody text\n")
        self.assertEqual(data["title"], "A: tricky 'title'")
        self.assertEqual(data["summary"], "Two lines")  # snippet is one line
        self.assertEqual(data["tags"], ["x", "y: z"])
        self.assertEqual(data["subtitle"], "")
        self.assertEqual(data["date"], "2026-10-10T12:00:00Z")
        self.assertEqual(body.strip(), "Body text")
        self.assertEqual(list(data)[:3], ["title", "subtitle", "source"])

    def test_extra_flags(self):
        data, _ = mposts.split_frontmatter(mposts.build_frontmatter({"title": "t"}, {"excerpt_only": True}))
        self.assertTrue(data["excerpt_only"])
        self.assertEqual(data["tags"], [])


class ExpiryTest(unittest.TestCase):
    def test_read_posts_expire_after_24h_unread_after_72h(self):
        unread = {"fetched": 1000, "notified_at": 2000}
        self.assertEqual(mposts.expires_at(unread, 24, 72), 2000 + 72 * HOUR)
        read = {**unread, "read_at": 5000}
        self.assertEqual(mposts.expires_at(read, 24, 72), 5000 + 24 * HOUR)

    def test_never_announced_counts_from_fetch(self):
        self.assertEqual(mposts.expires_at({"fetched": 1000}, 24, 72), 1000 + 72 * HOUR)

    def test_read_late_still_bounded_by_unread_deadline(self):
        post = {"notified_at": 0, "read_at": 71 * HOUR}
        self.assertEqual(mposts.expires_at(post, 24, 72), 72 * HOUR)


class ContentModeTest(unittest.TestCase):
    def entry(self, content="", summary=""):
        e = {"summary": summary}
        if content:
            e["content"] = [{"value": content}]
        return e

    def test_forced_modes(self):
        self.assertEqual(extract.choose_mode({"mode": "feed"}, self.entry()), "feed")
        self.assertEqual(extract.choose_mode({"mode": "fetch"}, self.entry("<p>" + "x" * 5000 + "</p>")), "fetch")

    def test_auto_uses_feed_only_when_substantial(self):
        cfg = {"mode": "auto", "min_chars": 600}
        self.assertEqual(extract.choose_mode(cfg, self.entry("<p>" + "word " * 200 + "</p>")), "feed")
        self.assertEqual(extract.choose_mode(cfg, self.entry(summary="<p>short teaser</p>")), "fetch")

    def test_min_chars_zero_accepts_short_posts(self):
        self.assertEqual(extract.choose_mode({"mode": "auto", "min_chars": 0}, self.entry(summary="hi")), "feed")


class MarkdownTest(unittest.TestCase):
    def test_reason_feed_item(self):
        html = (FIXTURES / "reason_item.html").read_text(encoding="utf-8")
        md = extract.html_to_markdown(extract.sanitize_html(html, "https://reason.com/2026/10/10/x/"))
        self.assertIn("SpaceX's initial public offering", md.replace("’", "'"))
        self.assertRegex(md, r"\[2 trillion reasons\]\(https://www\.wsj\.com/")  # links kept
        self.assertNotIn("appeared first on", md)  # WordPress footer dropped
        self.assertNotIn("<", md)
        self.assertNotRegex(md, r"\n{3,}")

    def test_ai2_page_extraction(self):
        page = (FIXTURES / "ai2_page.html").read_text(encoding="utf-8")
        url = "https://allenai.org/blog/impactful-scheduling"
        content, meta = extract.extract_page(page, url)
        md = extract.html_to_markdown(extract.sanitize_html(content, url))
        self.assertIn("Overcommitting", md)
        self.assertRegex(md, r"(?m)^#{2,6} Overcommitting")  # headings kept
        self.assertGreater(len(md), 5000)
        self.assertNotIn("cookie", md.lower())
        self.assertTrue(meta["image"])

    def hltv(self):
        cfg = {f["url"]: f for f in feedconf.load_feeds(ROOT / "feeds.yml")}["https://www.hltv.org/rss/news"]
        page = (FIXTURES / "hltv_page.html").read_text(encoding="utf-8")
        url = "https://www.hltv.org/news/45691/vitality-beat-aurora-to-reach-epl-final"
        content, meta = extract.extract_page(page, url, cfg["selector"], cfg["remove"], cfg["subtitle_selector"])
        return extract.html_to_markdown(extract.sanitize_html(content, url)), meta

    def test_hltv_overrides_keep_only_the_article(self):
        md, meta = self.hltv()
        self.assertEqual(meta["subtitle"], "apEX's troops will go up against Spirit or MOUZ in Sunday's title decider.")
        self.assertTrue(md.startswith("[Vitality](https://www.hltv.org/team/9565/vitality) are through"))
        self.assertIn("triple kill from [ZywOo]", md)  # the last paragraph is there
        for junk in ("Past 3 months", "K - D", "Best of 3", "teamlogo", "flags/", "|", "apEX's troops"):
            self.assertNotIn(junk, md)  # hover cards, stats tables, scoreboard, subtitle
        self.assertLess(len(md), 4000)

    def test_invisible_characters_are_removed(self):
        md, _ = self.hltv()
        self.assertIn('"woxic"', md)
        self.assertNotRegex(md, "[⁠​﻿]")
        self.assertIn("👨‍👩", extract.html_to_markdown("<p>👨‍👩</p>"))  # emoji joiners stay

    def test_without_overrides_hltv_is_messy(self):
        # documents why the overrides exist: the generic extractor keeps the hover cards
        page = (FIXTURES / "hltv_page.html").read_text(encoding="utf-8")
        content, _ = extract.extract_page(page, "https://www.hltv.org/news/1/x")
        self.assertIn("Past 3 months", extract.html_to_markdown(extract.sanitize_html(content)))

    def test_sanitizer_strips_clutter(self):
        html = ('<div class="entry"><p>Real text here.</p><script>evil()</script>'
                '<div class="sharedaddy sd-sharing"><a href="/s">Share on X</a></div>'
                '<div id="cookie-banner">We use cookies</div>'
                '<img src="https://t.example/pixel.gif" width="1" height="1">'
                '<p>   </p><p></p><div><span></span></div>'
                '<pre><code class="language-py">x = 1\n</code></pre>'
                '<ul><li>one</li><li>two</li></ul>'
                '<p><img src="/pic.png" alt="a pic"> <a href="/rel">rel link</a></p></div>')
        md = extract.html_to_markdown(extract.sanitize_html(html, "https://site.example/post"))
        self.assertEqual(md.count("Real text here."), 1)
        for junk in ("evil", "Share on X", "cookies", "pixel"):
            self.assertNotIn(junk, md)
        self.assertIn("```py\nx = 1\n```", md)
        self.assertIn("- one", md)
        self.assertIn("![a pic](https://site.example/pic.png)", md)
        self.assertIn("[rel link](https://site.example/rel)", md)

    def test_line_breaks_survive(self):
        md = extract.html_to_markdown("<p>Line one<br>Line two<br/>Line three</p><p>Next</p>")
        self.assertEqual(md, "Line one\\\nLine two\\\nLine three\n\nNext")
        self.assertEqual(mposts.md_to_text(md), "Line one\nLine two\nLine three\n\nNext")

    def test_h1_in_body_is_demoted(self):
        md = extract.html_to_markdown(extract.sanitize_html("<h1>Top</h1><p>x</p><h2>Sub</h2>"))
        self.assertIn("## Top", md)
        self.assertIn("### Sub", md)

    def test_leading_title_and_banner_dropped(self):
        self.assertEqual(extract.drop_leading_title("# Some Title\n\nBody", "Some Title"), "Body")
        self.assertEqual(extract.drop_leading_title("Other\n\nBody", "Some Title"), "Other\n\nBody")
        md = "![x](https://c.example/a/pic-800x450.jpg)\n\nBody"
        self.assertEqual(extract.drop_leading_image(md, "https://c.example/b/pic-1200x675.jpg?q=1"), "Body")
        md = "A standfirst line.\n\n![](https://c.example/a/pic.jpg?w=800&s=1)\n\nBody"  # image after a dek
        self.assertEqual(extract.drop_leading_image(md, "https://c.example/a/pic.jpg?w=1600&s=2"),
                         "A standfirst line.\n\nBody")
        md = "One.\n\nTwo.\n\nThree.\n\n![](https://c.example/a/pic.jpg)"  # deep in the article: kept
        self.assertEqual(extract.drop_leading_image(md, "https://c.example/a/pic.jpg"), md)

    def test_md_to_text_and_summary(self):
        text = mposts.md_to_text("## Head\n\nSome **bold** [link](http://x) text. Second one! Third? Fourth.\n\n- a\n- b\n\n![i](http://i)")
        self.assertIn("Some bold link text.", text)
        self.assertIn("• a", text)
        self.assertNotIn("http", text)
        self.assertEqual(mposts.first_sentences(text, 3, 400), "Head Some bold link text. Second one! Third?")


class FeedConfigTest(unittest.TestCase):
    def test_repo_feeds_yml_is_valid(self):
        feeds = feedconf.load_feeds(ROOT / "feeds.yml")
        self.assertGreaterEqual(len(feeds), 11)
        self.assertEqual(len({f["url"] for f in feeds}), len(feeds))
        by = {f["url"]: f for f in feeds}
        self.assertEqual(by["https://reason.com/feed/"]["mode"], "feed")
        self.assertEqual(by["https://allenai.org/rss.xml"]["mode"], "fetch")
        self.assertEqual(by["https://www.hltv.org/rss/news"]["client"], "impersonate")

    def test_bad_entries_are_skipped_not_fatal(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "feeds.yml"
            p.write_text("feeds:\n  - url: http://a/\n    mode: bogus\n  - name: no url\n  - url: http://b/\n"
                         "    filter: {title_contains: [Epic]}\n", encoding="utf-8")
            with mock.patch.object(sys, "stderr"):
                feeds = feedconf.load_feeds(p)
        self.assertEqual([f["url"] for f in feeds], ["http://b/"])
        self.assertEqual(feeds[0]["title_contains"], ["epic"])


# --------------------------------------------------------------------------- pipeline

def rss(items):
    """items: list of (guid, title, link, html)."""
    body = "".join(
        f"<item><title>{t}</title><link>{l}</link><guid>{g}</guid>"
        f"<pubDate>Mon, {10 + i:02d} Jan 2022 00:00:00 GMT</pubDate>"
        f"<content:encoded><![CDATA[{h}]]></content:encoded></item>"
        for i, (g, t, l, h) in enumerate(items))
    return (f"<rss version='2.0' xmlns:content='http://purl.org/rss/1.0/modules/content/'><channel>"
            f"<title>Blog</title>{body}</channel></rss>").encode()


class FakeFetcher:
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get(self, url, client="plain", conditional=None, page=False):
        self.calls.append(url)
        value = self.routes[url]
        if isinstance(value, Exception):
            raise value
        return http_client.Response(200, value if isinstance(value, bytes) else value.encode(), {}, url)


FEED_URL = "https://blog.example/feed"
LONG = "<p>" + "A full sentence of article text. " * 40 + "</p>"


class PipelineTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.feeds_file = self.dir / "feeds.yml"
        self.feeds_file.write_text(f"feeds:\n  - url: {FEED_URL}\n    name: Blog\n    mode: auto\n", encoding="utf-8")
        self.sent = []
        self.calls = []
        for p in (mock.patch.object(notify, "FEEDS_FILE", self.feeds_file),
                  mock.patch.object(notify, "CONTENT_DIR", self.dir / "content" / "posts"),
                  mock.patch.object(notify, "SEEN_FILE", self.dir / "seen.json"),
                  mock.patch.object(notify, "BACKFILL", 0),
                  mock.patch.object(notify, "NEW_FEED_BACKFILL", 0),
                  mock.patch.object(notify, "DRY_RUN", False),
                  mock.patch.object(notify, "TOKEN", "t"),
                  mock.patch.object(notify, "CHAT_ID", "c"),
                  mock.patch.object(notify, "SITE_URL", "https://me.github.io/rss"),
                  mock.patch.object(notify.time, "sleep"),
                  mock.patch.object(notify, "send_message", self.fake_send),
                  mock.patch.object(notify, "tg_call", lambda m, **kw: self.calls.append((m, kw)))):
            p.start()
            self.addCleanup(p.stop)

    def fake_send(self, text, image=None, reply_markup=None):
        self.sent.append((text, image, reply_markup))
        return True, 1000 + len(self.sent)

    def feed(self, *items, extra_routes=None):
        routes = {FEED_URL: rss(list(items))}
        routes.update(extra_routes or {})
        return FakeFetcher(routes)

    def files(self):
        return sorted((self.dir / "content" / "posts").rglob("*.md"))

    def fetch(self, fetcher, seen, now=1_000_000):
        return notify.stage_fetch(seen, fetcher, now=now, log=lambda m: None)

    # -- dedup
    def test_new_item_written_once_and_never_again(self):
        seen = {"feeds": {FEED_URL: ["old"]}}
        item = ("g1", "First post", "https://blog.example/1", LONG)
        f = self.feed(("old", "Old", "https://blog.example/0", LONG), item)
        self.assertEqual(self.fetch(f, seen)["new"], 1)
        self.assertEqual(len(self.files()), 1)
        self.assertEqual(self.fetch(f, seen)["new"], 0)  # same guid again
        self.assertEqual(len(self.files()), 1)
        self.assertEqual(list(seen["posts"].values())[0]["status"], "mirrored")

    def test_first_sight_writes_nothing_without_backfill(self):
        seen = {"feeds": {}}
        self.assertEqual(self.fetch(self.feed(("a", "A", "https://blog.example/a", LONG)), seen)["new"], 0)
        self.assertEqual(seen["feeds"][FEED_URL], ["a"])

    def test_backfill_mirrors_newest_but_skips_already_mirrored(self):
        seen = {"feeds": {FEED_URL: ["a", "b"]}}
        f = self.feed(("a", "A", "https://blog.example/a", LONG), ("b", "B", "https://blog.example/b", LONG))
        with mock.patch.object(notify, "BACKFILL", 1):
            self.assertEqual(self.fetch(f, seen)["new"], 1)
            self.assertEqual(self.fetch(f, seen)["new"], 0)
        self.assertEqual(len(self.files()), 1)

    # -- modes and fallbacks
    def test_full_feed_content_means_no_page_fetch(self):
        seen = {"feeds": {FEED_URL: []}}
        f = self.feed(("g", "Full", "https://blog.example/g", LONG))
        self.fetch(f, seen)
        self.assertEqual(f.calls, [FEED_URL])

    def test_short_feed_content_fetches_the_page(self):
        seen = {"feeds": {FEED_URL: []}}
        page = ("<html><head><meta property='og:image' content='https://blog.example/og.jpg'></head><body><article><h1>Short</h1>"
                + LONG * 3 + "</article></body></html>")
        f = self.feed(("g", "Short", "https://blog.example/g", "<p>teaser</p>"), extra_routes={"https://blog.example/g": page})
        self.fetch(f, seen)
        self.assertEqual(f.calls, [FEED_URL, "https://blog.example/g"])
        fm, body = mposts.read_post(self.files()[0])
        self.assertNotIn("excerpt_only", fm)
        self.assertIn("A full sentence", body)
        self.assertEqual(fm["image"], "https://blog.example/og.jpg")

    def test_blocked_page_falls_back_to_feed_excerpt(self):
        seen = {"feeds": {FEED_URL: []}}
        blocked = http_client.FetchError("HTTP 403 (looks like bot protection)", blocked=True)
        f = self.feed(("g", "Blocked", "https://blog.example/g", "<p>just a teaser from the feed</p>"),
                      extra_routes={"https://blog.example/g": blocked})
        summary = self.fetch(f, seen)
        self.assertEqual(summary["new"], 1)
        self.assertEqual(len(summary["excerpt_only"]), 1)
        fm, body = mposts.read_post(self.files()[0])
        self.assertTrue(fm["excerpt_only"])
        self.assertIn("just a teaser", body)

    def test_one_failing_feed_does_not_abort_the_run(self):
        self.feeds_file.write_text(f"feeds:\n  - url: https://dead.example/feed\n  - url: {FEED_URL}\n", encoding="utf-8")
        seen = {"feeds": {FEED_URL: []}}
        f = self.feed(("g", "Ok", "https://blog.example/g", LONG),
                      extra_routes={"https://dead.example/feed": http_client.FetchError("boom")})
        summary = self.fetch(f, seen)
        self.assertEqual(summary["new"], 1)
        self.assertEqual(len(summary["failed_feeds"]), 1)

    def test_title_filter(self):
        self.feeds_file.write_text(f"feeds:\n  - url: {FEED_URL}\n    mode: feed\n    min_chars: 0\n"
                                   "    filter: {title_contains: [Epic]}\n", encoding="utf-8")
        seen = {"feeds": {FEED_URL: []}}
        f = self.feed(("1", "Epic freebie", "https://blog.example/1", "<p>free</p>"),
                      ("2", "Steam freebie", "https://blog.example/2", "<p>free</p>"))
        self.assertEqual(self.fetch(f, seen)["new"], 1)
        self.assertEqual(set(seen["feeds"][FEED_URL]), {"1", "2"})  # filtered one is remembered

    def test_untitled_short_post_gets_a_title_from_its_text(self):
        self.feeds_file.write_text(f"feeds:\n  - url: {FEED_URL}\n    mode: feed\n    min_chars: 0\n", encoding="utf-8")
        seen = {"feeds": {FEED_URL: []}}
        f = self.feed(("1", "", "https://blog.example/1", "<p>Hello there, a short toot.</p>"))
        self.fetch(f, seen)
        self.assertEqual(mposts.read_post(self.files()[0])[0]["title"], "Hello there, a short toot.")

    # -- notify, read button, expiry
    def test_notify_sends_once_with_read_button_and_pages_link(self):
        seen = {"feeds": {FEED_URL: []}}
        self.fetch(self.feed(("g", "Title & more", "https://blog.example/g", LONG)), seen)
        self.assertEqual(notify.stage_notify(seen, log=lambda m: None, link_check=False), 1)
        text, _, markup = self.sent[0]
        post = list(seen["posts"].values())[0]
        self.assertIn(f'https://me.github.io/rss/posts/blog/{post["slug"]}/', text)
        self.assertIn("Title &amp; more", text)
        self.assertIn("Read more", text)
        pid = next(iter(seen["posts"]))
        self.assertEqual(markup["inline_keyboard"][0][0]["callback_data"], f"r:{pid}")
        self.assertLessEqual(len(markup["inline_keyboard"][0][0]["callback_data"].encode()), 64)
        self.assertEqual(post["status"], "notified")
        self.assertEqual(post["message_id"], 1001)
        self.assertEqual(notify.stage_notify(seen, log=lambda m: None, link_check=False), 0)  # never re-notified

    def test_message_fills_but_never_exceeds_telegram_limit(self):
        body = "\n\n".join(f"Paragraph {i}. " + "Lorem ipsum dolor sit amet. " * 20 for i in range(40))
        for emoji_body in (body, body.replace("Lorem", "Lorem 😀😀😀")):
            text, _ = notify.format_mirror_message({"title": "T" * 200, "source": "S"}, emoji_body, "https://x.example/p/")
            visible = text
            for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">")):
                visible = visible.replace(a, b)
            import re
            visible = re.sub(r"<[^>]+>", "", visible)
            self.assertLessEqual(notify.utf16_len(visible), 4096)
            self.assertGreater(notify.utf16_len(visible), 3800)  # it actually uses the room

    def test_short_post_message_has_everything(self):
        text, image = notify.format_mirror_message(
            {"title": "Hi", "source": "Src", "image": "https://i.example/i.png"}, "Short body.", "https://x.example/p/")
        self.assertEqual(image, "https://i.example/i.png")
        self.assertIn("Short body.", text)
        self.assertIn('<a href="https://x.example/p/">Read more →</a>', text)

    def test_snippet_length_is_configurable(self):
        text, _ = notify.format_mirror_message({"title": "T", "source": "S"}, "word " * 400, "https://x/p/", limit=100)
        self.assertLess(len(text), 400)

    def test_read_tap_marks_post_and_updates_button(self):
        seen = {"feeds": {FEED_URL: []}}
        self.fetch(self.feed(("g", "T", "https://blog.example/g", LONG)), seen)
        notify.stage_notify(seen, log=lambda m: None, link_check=False)
        pid = next(iter(seen["posts"]))
        cq = {"id": "q1", "data": f"r:{pid}", "message": {"message_id": 1001, "chat": {"id": "c"}}}
        notify.handle_callback(cq, seen)
        self.assertTrue(seen["posts"][pid]["read_at"])
        self.assertEqual(self.calls[0][0], "editMessageReplyMarkup")
        self.assertIn("24h", json.dumps(self.calls[0][1]["reply_markup"]))
        first = seen["posts"][pid]["read_at"]
        notify.handle_callback(cq, seen)
        self.assertEqual(seen["posts"][pid]["read_at"], first)  # second tap changes nothing

    def test_read_tap_from_another_chat_is_ignored(self):
        seen = {"feeds": {}, "posts": {"abc": {"status": "notified"}}}
        notify.handle_callback({"id": "q", "data": "r:abc", "message": {"chat": {"id": "stranger"}}}, seen)
        self.assertNotIn("read_at", seen["posts"]["abc"])

    def test_expiry_read_24h_unread_72h_and_stub_cleanup(self):
        seen = {"feeds": {FEED_URL: []}}
        t0 = 1_000_000
        self.fetch(self.feed(("r", "Read me", "https://blog.example/r", LONG), ("u", "Unread", "https://blog.example/u", LONG)),
                   seen, now=t0)
        notify.stage_notify(seen, log=lambda m: None, link_check=False)
        by_title = {p["title"]: p for p in seen["posts"].values()}
        for p in by_title.values():
            p["notified_at"] = t0
        by_title["Read me"]["read_at"] = t0 + 2 * HOUR
        log = lambda m: None  # noqa: E731
        self.assertEqual(notify.expire_posts(seen, t0 + 25 * HOUR, log), 0)  # read 23h ago: not yet
        self.assertEqual(notify.expire_posts(seen, t0 + 27 * HOUR, log), 1)  # read 25h ago
        self.assertEqual(by_title["Read me"]["status"], "pruned")
        self.assertEqual(by_title["Unread"]["status"], "notified")
        stub_fm, stub_body = mposts.read_post(mposts.post_path(notify.CONTENT_DIR, by_title["Read me"]["source_slug"], by_title["Read me"]["slug"]))
        self.assertTrue(stub_fm["stub"])
        self.assertEqual(stub_fm["source_url"], "https://blog.example/r")  # stub redirects to the original
        self.assertEqual(stub_body.strip(), "")
        self.assertEqual(notify.expire_posts(seen, t0 + 71 * HOUR, log), 0)
        self.assertEqual(notify.expire_posts(seen, t0 + 73 * HOUR, log), 1)  # unread 73h after announcement
        self.assertEqual(len(self.files()), 2)  # both are stubs now
        self.assertEqual(notify.expire_posts(seen, t0 + 73 * HOUR + 31 * 86400, log), 2)  # stubs dropped later
        self.assertEqual(self.files(), [])
        self.assertEqual(seen["posts"], {})
        self.assertIn("u", seen["feeds"][FEED_URL])  # dedup memory outlives the files

    def test_refetch_regenerates_live_posts_in_place_without_reannouncing(self):
        page_v1 = "<html><body><article><p>" + "Old messy version. " * 40 + "</p></article></body></html>"
        page_v2 = ("<html><body><article><p class='dek'>The standfirst.</p><p>"
                   + "Clean new version. " * 40 + "</p></article></body></html>")
        self.feeds_file.write_text(f"feeds:\n  - url: {FEED_URL}\n    name: Blog\n    mode: fetch\n", encoding="utf-8")
        seen = {"feeds": {FEED_URL: []}}
        item = ("g", "T", "https://blog.example/g", "<p>teaser</p>")
        self.fetch(self.feed(item, extra_routes={"https://blog.example/g": page_v1}), seen, now=1000)
        notify.stage_notify(seen, log=lambda m: None, link_check=False)
        post = dict(next(iter(seen["posts"].values())))
        self.feeds_file.write_text(f"feeds:\n  - url: {FEED_URL}\n    name: Blog\n    mode: fetch\n"
                                   "    subtitle_selector: p.dek\n", encoding="utf-8")
        with mock.patch.object(notify, "REFETCH", "blog"):
            summary = self.fetch(self.feed(item, extra_routes={"https://blog.example/g": page_v2}), seen, now=5000)
        self.assertEqual((summary["refreshed"], summary["new"]), (1, 0))
        fm, body = mposts.read_post(self.files()[0])
        self.assertEqual(len(self.files()), 1)  # same file, same link
        self.assertIn("Clean new version", body)
        self.assertEqual(fm["subtitle"], "The standfirst.")
        after = next(iter(seen["posts"].values()))
        for key in ("slug", "status", "notified_at", "message_id", "fetched"):  # timer and announcement unchanged
            self.assertEqual(after[key], post[key], key)
        self.assertEqual(notify.stage_notify(seen, log=lambda m: None, link_check=False), 0)

    # -- /test
    def run_test_command(self, seen, routes_feed):
        parsed = feedparser.parse(routes_feed)
        with mock.patch.object(notify, "fetch", return_value=parsed), \
                mock.patch.object(notify, "MIRROR", True):
            return notify.cmd_test(seen)

    def test_test_command_links_to_the_mirror_page_when_mirrored(self):
        seen = {"feeds": {FEED_URL: []}}
        item = ("g", "Mirrored post", "https://blog.example/g", LONG)
        self.fetch(self.feed(item), seen)
        notify.stage_notify(seen, log=lambda m: None, link_check=False)
        text, _ = self.run_test_command(seen, rss([item]))
        slug = next(iter(seen["posts"].values()))["slug"]
        self.assertIn(f'href="https://me.github.io/rss/posts/blog/{slug}/"', text)
        self.assertNotIn("blog.example/g", text)
        self.assertNotIn("Not mirrored", text)
        self.assertEqual(len(self.sent), 1)  # /test itself didn't announce anything

    def test_test_command_says_plainly_when_it_links_to_the_original(self):
        seen = {"feeds": {FEED_URL: ["old"]}, "posts": {}}
        text, _ = self.run_test_command(seen, rss([("old", "Old post", "https://blog.example/old", LONG)]))
        self.assertIn('href="https://blog.example/old"', text)
        self.assertTrue(text.endswith(notify.NOT_MIRRORED_NOTE))
        self.assertIn("links to the original article", text)

    def test_test_command_skips_expired_and_not_yet_live_posts(self):
        seen = {"feeds": {FEED_URL: []}}
        item = ("g", "T", "https://blog.example/g", LONG)
        self.fetch(self.feed(item), seen)  # mirrored, not announced yet
        with mock.patch.object(notify, "check_link", return_value=False):
            text, _ = self.run_test_command(seen, rss([item]))
        self.assertIn("Not mirrored", text)
        next(iter(seen["posts"].values()))["status"] = "pruned"
        text, _ = self.run_test_command(seen, rss([item]))
        self.assertIn("Not mirrored", text)

    def test_unannounced_link_that_is_not_live_is_retried(self):
        seen = {"feeds": {FEED_URL: []}}
        self.fetch(self.feed(("g", "T", "https://blog.example/g", LONG)), seen)
        with mock.patch.object(notify, "check_link", return_value=False):
            self.assertEqual(notify.stage_notify(seen, log=lambda m: None), 0)
        self.assertEqual(list(seen["posts"].values())[0]["status"], "mirrored")
        self.assertEqual(self.sent, [])


# --------------------------------------------------------------------------- http layer

class HttpClientTest(unittest.TestCase):
    def fetcher(self, responses, **kw):
        f = http_client.Fetcher(delay=0, sleep=lambda s: None, **kw)
        seq = list(responses)
        f._once = lambda url, client, headers: self.step(seq)
        self.headers_seen = []
        return f

    @staticmethod
    def step(seq):
        r = seq.pop(0) if len(seq) > 1 else seq[0]
        if isinstance(r, Exception):
            raise r
        return http_client.Response(*r)

    def test_retries_then_succeeds(self):
        f = self.fetcher([(503, b"x"), (200, b"ok")])
        self.assertEqual(f.get("http://a.example/").content, b"ok")

    def test_cloudflare_block_raises_blocked_after_retries(self):
        f = self.fetcher([(403, b"<html>Just a moment...</html>")])
        with self.assertRaises(http_client.FetchError) as ctx:
            f.get("http://a.example/")
        self.assertTrue(ctx.exception.blocked)

    def test_404_fails_fast_without_retry(self):
        calls = []
        f = http_client.Fetcher(delay=0, sleep=lambda s: None)
        f._once = lambda *a: calls.append(1) or http_client.Response(404, b"")
        with self.assertRaises(http_client.FetchError) as ctx:
            f.get("http://a.example/")
        self.assertFalse(ctx.exception.blocked)
        self.assertEqual(len(calls), 1)

    def test_304_returned_for_conditional_get(self):
        f = self.fetcher([(304, b"")])
        self.assertEqual(f.get("http://a.example/", conditional={"etag": "x"}).status, 304)

    def test_network_errors_become_fetch_errors(self):
        f = self.fetcher([ConnectionError("down")])
        with self.assertRaises(http_client.FetchError):
            f.get("http://a.example/")

    def test_per_domain_delay(self):
        sleeps, now = [], [100.0]
        f = http_client.Fetcher(delay=2.0, sleep=sleeps.append, clock=lambda: now[0])
        f._once = lambda *a: http_client.Response(200, b"")
        f.get("http://a.example/1")
        f.get("http://a.example/2")  # same domain, no time passed: waits
        f.get("http://b.example/1")  # other domain: no wait
        self.assertEqual(sleeps, [2.0])


if __name__ == "__main__":
    unittest.main()
