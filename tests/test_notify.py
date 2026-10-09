"""Offline tests for notify.py (no network): run with `python -m unittest tests.test_notify`."""

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from xml.sax.saxutils import escape

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import notify  # noqa: E402

FEED = "https://example.com/feed"


def rss(ids, summary=None, content=None, title="Blog"):
    """RSS with the given ids, newest first; 'a' is the oldest, one day per item.

    `summary` / `content` are HTML strings put in <description> / <content:encoded>.
    """
    def item(i):
        extra = ""
        if summary is not None:
            extra += f"<description>{escape(summary)}</description>"
        if content is not None:
            extra += f"<content:encoded>{escape(content)}</content:encoded>"
        return (f"<item><title>T{i}</title><link>https://example.com/{i}</link><guid>{i}</guid>"
                f"<pubDate>Mon, {10 + ord(i) - ord('a'):02d} Jan 2022 00:00:00 GMT</pubDate>{extra}</item>")

    items = "".join(item(i) for i in ids)
    return (f"<rss version='2.0' xmlns:content='http://purl.org/rss/1.0/modules/content/'>"
            f"<channel><title>{title}</title>{items}</channel></rss>").encode()


class NotifyTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.feeds = {FEED: rss("edcba")}  # a oldest ... e newest
        self.post_ok = []  # per-call success flags; default True
        self.posts = []
        self.payloads = []
        self.updates = []  # what getUpdates returns on the next call
        self.update_calls = []  # data dicts sent to getUpdates
        self.updates_ok = True
        patches = [
            mock.patch.object(notify, "SEEN_FILE", self.dir / "seen.json"),
            mock.patch.object(notify, "FEEDS_FILE", self.dir / "feeds.txt"),
            mock.patch.object(notify, "DRY_RUN", False),
            mock.patch.object(notify, "TOKEN", "t"),
            mock.patch.object(notify, "CHAT_ID", "c"),
            mock.patch.object(notify, "MAX_PER_RUN", 25),
            mock.patch.object(notify, "BACKFILL", 0),
            mock.patch.object(notify, "NEW_FEED_BACKFILL", 0),
            mock.patch.object(notify, "EXCERPT_CHARS", 800),
            mock.patch.object(notify, "LINK_PREVIEW", False),
            mock.patch.object(notify.time, "sleep"),
            mock.patch.object(notify.requests, "get", self.fake_get),
            mock.patch.object(notify.requests, "post", self.fake_post),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def fake_get(self, url, **kw):
        body = self.feeds.get(url)
        if body is None:
            raise requests.ConnectionError("boom")
        return mock.Mock(content=body, raise_for_status=lambda: None)

    def fake_post(self, url, data=None, **kw):
        if url.endswith("/getUpdates"):
            self.update_calls.append(dict(data))
            if not self.updates_ok:
                raise requests.ConnectionError("telegram down")
            result, self.updates = self.updates, []
            return mock.Mock(json=lambda: {"ok": True, "result": result})
        ok = self.post_ok.pop(0) if self.post_ok else True
        self.posts.append(data["text"])
        self.payloads.append(data)
        return mock.Mock(status_code=200 if ok else 500, ok=ok, text="err")

    def run_main(self, seen=None, feeds=(FEED,), feeds_text=None):
        text = feeds_text if feeds_text is not None else "\n".join(feeds)
        (self.dir / "feeds.txt").write_text(text, encoding="utf-8")
        # a pre-existing seen.json avoids the one-off "bot is live" message
        (self.dir / "seen.json").write_text(json.dumps(seen or {"feeds": {}}), encoding="utf-8")
        self.posts.clear()
        notify.main()
        return json.loads((self.dir / "seen.json").read_text(encoding="utf-8"))

    def titles(self):
        return [re.search(r">([^<]+)</a>", t).group(1) for t in self.posts]

    def feeds_text(self):
        return (self.dir / "feeds.txt").read_text(encoding="utf-8")

    def say(self, text, chat="c", uid=None):
        """Queue an incoming Telegram message for the next getUpdates call."""
        uid = uid if uid is not None else 100 + len(self.updates)
        self.updates.append({"update_id": uid, "message": {"chat": {"id": chat}, "text": text}})

    def test_normal_run_sends_only_new_oldest_first(self):
        seen = self.run_main({"feeds": {FEED: ["a", "b"]}})
        self.assertEqual(self.titles(), ["Tc", "Td", "Te"])
        self.assertEqual(seen["feeds"][FEED], ["a", "b", "c", "d", "e"])

    def test_first_sight_without_backfill_sends_nothing(self):
        seen = self.run_main()
        self.assertEqual(self.posts, [])
        self.assertEqual(sorted(seen["feeds"][FEED]), list("abcde"))

    def test_first_sight_with_new_feed_backfill(self):
        with mock.patch.object(notify, "NEW_FEED_BACKFILL", 2):
            seen = self.run_main()
        self.assertEqual(self.titles(), ["Td", "Te"])
        self.assertEqual(sorted(seen["feeds"][FEED]), list("abcde"))

    def test_manual_backfill_resends_without_duplicate_ids(self):
        with mock.patch.object(notify, "BACKFILL", 2):
            seen = self.run_main({"feeds": {FEED: list("abcde")}})
        self.assertEqual(self.titles(), ["Td", "Te"])
        self.assertEqual(seen["feeds"][FEED], list("abcde"))

    def test_overlap_is_sent_once(self):
        with mock.patch.object(notify, "BACKFILL", 3):
            seen = self.run_main({"feeds": {FEED: list("abd")}})  # c, e new; newest 3 = c,d,e
        self.assertEqual(self.titles(), ["Tc", "Td", "Te"])
        self.assertEqual(sorted(seen["feeds"][FEED]), list("abcde"))
        self.assertEqual(len(seen["feeds"][FEED]), 5)

    def test_backfill_may_exceed_max_per_run(self):
        with mock.patch.object(notify, "BACKFILL", 3), mock.patch.object(notify, "MAX_PER_RUN", 1):
            self.run_main({"feeds": {FEED: list("abcde")}})
        self.assertEqual(self.titles(), ["Tc", "Td", "Te"])

    def test_telegram_failure_leaves_items_unseen(self):
        self.post_ok = [True, False]
        seen = self.run_main({"feeds": {FEED: ["a", "b"]}})
        self.assertEqual(self.titles(), ["Tc", "Td"])  # stopped after the failure
        self.assertEqual(seen["feeds"][FEED], ["a", "b", "c"])

    def test_telegram_failure_on_new_feed_backfill_keeps_unsent_unseen(self):
        self.post_ok = [True, False]
        with mock.patch.object(notify, "NEW_FEED_BACKFILL", 3):
            seen = self.run_main()  # newest 3 = c, d, e; d fails
        self.assertEqual(sorted(seen["feeds"][FEED]), ["a", "b", "c"])

    def test_failed_feed_is_skipped_and_not_marked_seen(self):
        bad = "https://example.com/bad"
        with mock.patch.object(notify, "BACKFILL", 2):
            seen = self.run_main({"feeds": {FEED: list("abcde")}}, feeds=(FEED, bad))
        self.assertNotIn(bad, seen["feeds"])
        self.assertEqual(self.titles(), ["Td", "Te"])

    def test_clamp_count(self):
        c = notify.clamp_count
        self.assertEqual([c(""), c("abc"), c("-3"), c("5"), c("99"), c(" 2 ")], [0, 0, 0, 5, 20, 2])

    def test_dry_run_prints_and_does_not_post(self):
        with mock.patch.object(notify, "DRY_RUN", True), mock.patch.object(notify, "BACKFILL", 1), \
                mock.patch("builtins.print") as pr:
            self.run_main({"feeds": {FEED: list("abcde")}})
        self.assertEqual(self.posts, [])
        self.assertTrue(any("DRY RUN >>" in str(c.args[0]) for c in pr.call_args_list))

    # ------------------------------------------------------------------ excerpts

    def msg_for(self, **feed_kw):
        self.feeds = {FEED: rss("ab", **feed_kw)}
        self.run_main({"feeds": {FEED: ["a"]}})
        self.assertEqual(len(self.posts), 1)
        return self.posts[0]

    def test_message_has_title_source_excerpt_and_read_more(self):
        m = self.msg_for(summary="<p>Hello <b>world</b>.</p>")
        self.assertTrue(m.startswith('<b><a href="https://example.com/b">Tb</a></b>\n<i>Blog</i>\n\nHello world.'))
        self.assertTrue(m.endswith('<a href="https://example.com/b">Read more →</a>'))

    def test_content_preferred_over_summary_and_figures_dropped(self):
        m = self.msg_for(summary="short summary",
                         content="<p>Full text.</p><figure><img src='x'><figcaption>CAPTION</figcaption></figure><p>More.</p>")
        self.assertIn("Full text.\n\nMore.", m)
        self.assertNotIn("short summary", m)
        self.assertNotIn("CAPTION", m)

    def test_continue_reading_tail_removed(self):
        m = self.msg_for(summary="<p>Body here.</p><p>… Continue reading Tb</p>")
        self.assertIn("Body here.", m)
        self.assertNotIn("Continue reading", m)

    def test_excerpt_is_html_escaped(self):
        m = self.msg_for(summary="<p>1 &lt; 2 &amp; <script>bad()</script>3</p>")
        self.assertIn("1 &lt; 2 &amp; 3", m)
        self.assertNotIn("bad()", m)

    def test_excerpt_chars_zero_is_link_only(self):
        with mock.patch.object(notify, "EXCERPT_CHARS", 0):
            m = self.msg_for(summary="<p>Hello world.</p>")
        self.assertEqual(m, '<b><a href="https://example.com/b">Tb</a></b>\n<i>Blog</i>')

    def test_no_body_means_no_read_more(self):
        m = self.msg_for()
        self.assertNotIn("Read more", m)

    def test_long_excerpt_truncated_at_sentence(self):
        body = " ".join(f"Sentence number {n} is here." for n in range(100))
        with mock.patch.object(notify, "EXCERPT_CHARS", 200):
            m = self.msg_for(summary=body)
        excerpt = m.split("\n\n")[1]
        self.assertLessEqual(len(excerpt), 205)
        self.assertTrue(excerpt.endswith(". …"))

    def test_truncate_falls_back_to_word_boundary(self):
        out = notify.truncate("word " * 100, 22)
        self.assertEqual(out, "word word word word …")

    def test_leading_title_repeat_removed(self):
        m = self.msg_for(summary="<p>Tb: the actual text.</p>")
        self.assertIn("\n\nthe actual text.", m)

    def test_link_preview_disabled_unless_enabled(self):
        self.msg_for(summary="x")
        self.assertEqual(json.loads(self.payloads[0]["link_preview_options"]), {"is_disabled": True})
        self.payloads.clear()
        with mock.patch.object(notify, "LINK_PREVIEW", True):
            self.msg_for(summary="x")
        self.assertNotIn("link_preview_options", self.payloads[0])

    def test_html_to_text_lists_and_entities(self):
        out = notify.html_to_text("<ul><li>one</li><li>two&nbsp;x</li></ul><p>a<br>b</p>")
        self.assertEqual(out, "• one\n• two x\n\na\nb")

    # ------------------------------------------------------------------ commands

    def test_list_numbers_feeds_with_labels(self):
        text = "# header\n\n# Alpha (note)\nhttp://a.test/feed\n\nhttp://b.test/feed  # Beta\n\nhttp://c.test/feed\n"
        self.feeds = {u: rss("a") for u in ("http://a.test/feed", "http://b.test/feed", "http://c.test/feed")}
        self.say("/list")
        self.run_main({"feeds": {}}, feeds_text=text)
        reply = self.posts[0]
        self.assertIn("Tracking 3 feeds", reply)
        self.assertIn('1. <a href="http://a.test/feed">Alpha</a>', reply)
        self.assertIn('2. <a href="http://b.test/feed">Beta</a>', reply)
        self.assertIn("3. http://c.test/feed", reply)

    def test_add_valid_feed_labels_it_and_bootstraps_same_run(self):
        new = "http://new.test/feed"
        self.feeds[new] = rss("ab", title="New Blog")
        self.say(f"/add {new}")
        seen = self.run_main({"feeds": {FEED: list("abcde")}})
        self.assertIn("Added <b>New Blog</b>", self.posts[0])
        self.assertIn(f"{new}  # New Blog", self.feeds_text())
        self.assertEqual(len(self.posts), 1)  # nothing from the new feed itself
        self.assertEqual(sorted(seen["feeds"][new]), ["a", "b"])

    def test_add_with_custom_name_and_new_feed_backfill(self):
        new = "http://new.test/feed"
        self.feeds[new] = rss("abc")
        self.say(f"/add {new} My # Name")
        with mock.patch.object(notify, "NEW_FEED_BACKFILL", 2):
            seen = self.run_main({"feeds": {FEED: list("abcde")}})
        self.assertIn(f"{new}  # My Name", self.feeds_text())
        self.assertEqual(len(self.posts), 3)  # reply + 2 backfilled posts
        self.posts.pop(0)  # the /add reply
        self.assertEqual(self.titles(), ["Tb", "Tc"])
        self.assertEqual(sorted(seen["feeds"][new]), ["a", "b", "c"])

    def test_add_rejects_bad_url_unreadable_and_duplicate(self):
        self.say("/add notaurl")
        self.say("/add http://dead.test/feed")  # fetch fails
        self.say(f"/add {FEED}/")  # same feed, trailing slash
        self.say("/add")
        before = "https://example.com/feed\n"
        self.run_main({"feeds": {FEED: list("abcde")}}, feeds_text=before)
        self.assertEqual(len(self.posts), 4)
        self.assertIn("doesn't look like a link", self.posts[0])
        self.assertIn("couldn't read", self.posts[1])
        self.assertIn("already tracking", self.posts[2])
        self.assertIn("Usage", self.posts[3])
        self.assertEqual(self.feeds_text(), before)

    def test_remove_by_number_drops_feed_comment_and_state(self):
        a, b = "http://a.test/feed", "http://b.test/feed"
        self.feeds = {a: rss("a"), b: rss("a")}
        text = "# top\n\n# Alpha\n" + a + "\n\n# Beta (x)\n" + b + "\n"
        self.say("/remove 1")
        seen = self.run_main({"feeds": {a: ["a"], b: ["a"]}}, feeds_text=text)
        self.assertIn("Removed <b>Alpha</b>", self.posts[0])
        self.assertEqual(self.feeds_text(), "# top\n\n# Beta (x)\n" + b + "\n")
        self.assertNotIn(a, seen["feeds"])
        self.assertIn(b, seen["feeds"])

    def test_remove_by_substring_and_ambiguous(self):
        a, b = "http://x.test/feed", "http://x.test/other"
        self.feeds = {a: rss("a"), b: rss("a")}
        text = f"{a}  # One\n{b}  # Two\n"
        self.say("/remove x.test")  # ambiguous
        self.say("/remove two")  # unique via label
        self.say("/remove 9")  # out of range
        seen = self.run_main({"feeds": {a: ["a"], b: ["a"]}}, feeds_text=text)
        self.assertIn("More than one", self.posts[0])
        self.assertIn("Removed <b>Two</b>", self.posts[1])
        self.assertIn("No feed matches", self.posts[2])
        self.assertEqual(self.feeds_text(), f"{a}  # One\n")
        self.assertEqual(list(seen["feeds"]), [a])

    def test_commands_from_other_chats_and_plain_text_are_ignored(self):
        self.say("/remove 1", chat="stranger")
        self.say("hello there")
        seen = self.run_main({"feeds": {FEED: list("abcde")}})
        self.assertEqual(self.posts, [])
        self.assertIn(FEED, self.feeds_text())
        self.assertEqual(seen["tg_offset"], 102)  # both updates consumed

    def test_help_start_and_unknown_commands(self):
        self.say("/start")
        self.say("/help@MyBot")
        self.say("/wat")
        self.run_main({"feeds": {FEED: list("abcde")}})
        self.assertEqual(len(self.posts), 3)
        self.assertTrue(all("Feed commands" in p for p in self.posts))

    def test_offset_saved_and_sent_next_run(self):
        self.say("/help", uid=500)
        seen = self.run_main({"feeds": {FEED: list("abcde")}})
        self.assertEqual(seen["tg_offset"], 501)
        self.assertNotIn("offset", self.update_calls[0])
        self.run_main(seen)
        self.assertEqual(self.update_calls[-1]["offset"], 501)

    def test_getupdates_failure_does_not_break_run(self):
        self.updates_ok = False
        self.run_main({"feeds": {FEED: ["a", "b"]}})
        self.assertEqual(self.titles(), ["Tc", "Td", "Te"])

    def test_dry_run_skips_commands(self):
        self.say("/remove 1")
        with mock.patch.object(notify, "DRY_RUN", True), mock.patch("builtins.print"):
            self.run_main({"feeds": {FEED: list("abcde")}})
        self.assertEqual(self.update_calls, [])
        self.assertIn(FEED, self.feeds_text())

    def test_first_run_message_mentions_help(self):
        (self.dir / "feeds.txt").write_text(FEED + "\n", encoding="utf-8")
        notify.main()
        self.assertIn("Send /help", self.posts[-1])

    def test_test_command_sends_newest_post_of_a_feed_without_marking_seen(self):
        self.say("/test")
        seen = self.run_main({"feeds": {FEED: list("abcde")}})
        self.assertEqual(self.titles(), ["Te"])  # newest of "edcba"; nothing else is sent
        self.assertEqual(seen["feeds"][FEED], list("abcde"))

    def test_test_command_skips_broken_and_empty_feeds(self):
        dead, empty = "http://dead.test/feed", "http://empty.test/feed"
        self.feeds[empty] = rss("")
        self.say("/test")
        self.run_main({"feeds": {FEED: list("abcde")}}, feeds=(dead, empty, FEED))
        self.assertEqual(self.titles(), ["Te"])

    def test_test_command_with_no_working_feed_says_so(self):
        self.say("/test")
        self.run_main({"feeds": {}}, feeds=("http://dead.test/feed",))
        self.assertIn("couldn't get a post", self.posts[0])

    def test_send_long_splits_on_lines(self):
        notify.send_long("\n".join(["x" * 1000] * 5))
        self.assertEqual(len(self.posts), 2)
        self.assertTrue(all(len(p) <= 3800 for p in self.posts))


if __name__ == "__main__":
    unittest.main()
