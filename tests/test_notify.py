"""Offline tests for notify.py (no network): run with `python -m unittest tests.test_notify`."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import notify  # noqa: E402

FEED = "https://example.com/feed"


def rss(ids):
    """RSS with the given ids, newest first; 'a' is the oldest, one day per item."""
    items = "".join(
        f"<item><title>T{i}</title><link>https://example.com/{i}</link><guid>{i}</guid>"
        f"<pubDate>Mon, {10 + ord(i) - ord('a'):02d} Jan 2022 00:00:00 GMT</pubDate></item>"
        for i in ids
    )
    return f"<rss version='2.0'><channel><title>Blog</title>{items}</channel></rss>".encode()


class NotifyTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.feeds = {FEED: rss("edcba")}  # a oldest ... e newest
        self.post_ok = []  # per-call success flags; default True
        self.posts = []
        patches = [
            mock.patch.object(notify, "SEEN_FILE", self.dir / "seen.json"),
            mock.patch.object(notify, "FEEDS_FILE", self.dir / "feeds.txt"),
            mock.patch.object(notify, "DRY_RUN", False),
            mock.patch.object(notify, "TOKEN", "t"),
            mock.patch.object(notify, "CHAT_ID", "c"),
            mock.patch.object(notify, "MAX_PER_RUN", 25),
            mock.patch.object(notify, "BACKFILL", 0),
            mock.patch.object(notify, "NEW_FEED_BACKFILL", 0),
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
        ok = self.post_ok.pop(0) if self.post_ok else True
        self.posts.append(data["text"])
        return mock.Mock(status_code=200 if ok else 500, ok=ok, text="err")

    def run_main(self, seen=None, feeds=(FEED,)):
        (self.dir / "feeds.txt").write_text("\n".join(feeds), encoding="utf-8")
        # a pre-existing seen.json avoids the one-off "bot is live" message
        (self.dir / "seen.json").write_text(json.dumps(seen or {"feeds": {}}), encoding="utf-8")
        self.posts.clear()
        notify.main()
        return json.loads((self.dir / "seen.json").read_text(encoding="utf-8"))

    def titles(self):
        return [t.split(">")[1].split("<")[0] for t in self.posts]

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


if __name__ == "__main__":
    unittest.main()
