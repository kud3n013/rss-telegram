#!/usr/bin/env python3
"""Fetch RSS/Atom feeds and send new items to a Telegram chat.

State lives in seen.json (committed back to the repo by the workflow).
A feed seen for the first time is "bootstrapped": its current items are
marked as seen without being sent, so adding a feed never floods your chat.

Two optional "latest posts" settings (both 0 = off, clamped to 0-20):
  BACKFILL           send the newest N items of every feed, even if already seen
  NEW_FEED_BACKFILL  send the newest N items of a feed seen for the first time
"""

import calendar
import html
import json
import os
import sys
import time
from pathlib import Path

import feedparser
import requests

ROOT = Path(__file__).parent
FEEDS_FILE = ROOT / "feeds.txt"
SEEN_FILE = ROOT / "seen.json"

MAX_PER_RUN = int(os.environ.get("MAX_PER_RUN", "25"))  # cap messages per run
MAX_IDS_PER_FEED = 1000  # how many seen ids to remember per feed


def clamp_count(value):
    """Parse a "latest N" setting: non-numbers become 0, the result is clamped to 0-20."""
    try:
        n = int(str(value).strip())
    except ValueError:
        return 0
    return max(0, min(20, n))


BACKFILL = clamp_count(os.environ.get("BACKFILL", ""))
NEW_FEED_BACKFILL = clamp_count(os.environ.get("NEW_FEED_BACKFILL", "0"))
DRY_RUN = os.environ.get("DRY_RUN") == "1"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; rss-telegram-bot/1.0)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
}


def load_feeds():
    feeds = []
    for line in FEEDS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            feeds.append(line)
    return feeds


def load_seen():
    if SEEN_FILE.exists():
        try:
            return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("WARNING: seen.json is corrupt, starting fresh", file=sys.stderr)
    return {"feeds": {}}


def save_seen(seen):
    SEEN_FILE.write_text(json.dumps(seen, indent=1, sort_keys=True), encoding="utf-8")


def fetch(url):
    """Return a parsed feed, or None if the fetch/parse failed."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"FAILED  {url}: {exc}", file=sys.stderr)
        return None
    parsed = feedparser.parse(resp.content)
    if not parsed.entries and parsed.bozo:
        print(f"FAILED  {url}: unparseable feed ({parsed.bozo_exception})", file=sys.stderr)
        return None
    return parsed


def entry_id(entry):
    return entry.get("id") or entry.get("link") or entry.get("title")


def entry_time(entry):
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    return calendar.timegm(t) if t else 0


def send(text):
    if DRY_RUN:
        print("DRY RUN >>", text.replace("\n", " | "))
        return True
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    for _ in range(3):
        try:
            resp = requests.post(url, data=payload, timeout=30)
        except requests.RequestException as exc:
            print(f"Telegram request failed: {exc}", file=sys.stderr)
            return False
        if resp.status_code == 429:  # rate limited
            wait = resp.json().get("parameters", {}).get("retry_after", 5)
            time.sleep(wait + 1)
            continue
        if resp.ok:
            return True
        print(f"Telegram error {resp.status_code}: {resp.text}", file=sys.stderr)
        return False
    return False


def format_message(feed_title, entry):
    title = html.escape(entry.get("title") or "(no title)")
    link = html.escape(entry.get("link") or "", quote=True)
    source = html.escape(feed_title or "")
    msg = f'<a href="{link}">{title}</a>' if link else f"<b>{title}</b>"
    if source:
        msg += f"\n<i>{source}</i>"
    return msg


def main():
    if not DRY_RUN and not (TOKEN and CHAT_ID):
        sys.exit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (or DRY_RUN=1).")

    feeds = load_feeds()
    first_run = not SEEN_FILE.exists()
    seen = load_seen()
    seen.setdefault("feeds", {})

    pending = {}  # (feed_url, entry_id) -> [timestamp, order, message, is_backfill]

    def queue(url, eid, entry, feed_title, is_backfill):
        item = pending.get((url, eid))
        if item:  # already queued this run: never send twice
            item[3] = item[3] or is_backfill
        else:
            pending[(url, eid)] = [entry_time(entry), len(pending),
                                   format_message(feed_title, entry), is_backfill]

    for url in feeds:
        parsed = fetch(url)
        if parsed is None:
            continue
        feed_title = parsed.feed.get("title", "")
        known = seen["feeds"].get(url)
        ids_now = [i for i in map(entry_id, parsed.entries) if i]

        # newest N by date; undated items fall back to feed order (newest first)
        n = BACKFILL if known is not None else max(BACKFILL, NEW_FEED_BACKFILL)
        dated = [(i, e) for i, e in enumerate(parsed.entries) if entry_id(e)]
        newest = sorted(dated, key=lambda p: (-entry_time(p[1]), p[0]))[:n]

        if known is None:  # new feed: remember current items, send only the backfill
            backfilled = {entry_id(e) for _, e in newest}
            # backfilled ids are added to seen only once actually sent
            seen["feeds"][url] = [i for i in ids_now if i not in backfilled][:MAX_IDS_PER_FEED]
            if newest:
                print(f"BOOTSTRAP {url}: {len(ids_now)} existing items, sending newest {len(newest)}")
            else:
                print(f"BOOTSTRAP {url}: {len(ids_now)} existing items marked as seen")
        else:
            known_set = set(known)
            for entry in parsed.entries:
                eid = entry_id(entry)
                if eid and eid not in known_set:
                    queue(url, eid, entry, feed_title, False)

        for _, entry in newest:
            queue(url, entry_id(entry), entry, feed_title, True)

    # Oldest first (undated ties keep reverse feed order). Backfilled items that were
    # already seen would not be retried next run, so the cap only limits ordinary new
    # items: a backfill run may send more than MAX_PER_RUN.
    def order(kv):
        return (kv[1][0], -kv[1][1])

    backfill_items = [kv for kv in pending.items() if kv[1][3]]
    new_items = sorted((kv for kv in pending.items() if not kv[1][3]), key=order)
    to_send = sorted(backfill_items + new_items[:MAX_PER_RUN], key=order)
    sent = 0
    for (url, eid), (_, _, message, _) in to_send:
        if not send(message):
            break  # stop on failure; unsent items stay unseen for the next run
        ids = seen["feeds"][url]
        if eid not in ids:  # backfilled items may already be remembered
            seen["feeds"][url] = (ids + [eid])[-MAX_IDS_PER_FEED:]
        sent += 1
        time.sleep(1.1)  # stay under Telegram's per-chat rate limit

    if first_run and feeds:
        send(f"✅ RSS bot is live, tracking {len(feeds)} feeds.")

    save_seen(seen)
    left = len(pending) - sent
    print(f"Done: sent {sent}, {left} left for the next run")


if __name__ == "__main__":
    main()
