#!/usr/bin/env python3
"""Fetch RSS/Atom feeds and send new items to a Telegram chat.

State lives in seen.json (committed back to the repo by the workflow).
A feed seen for the first time is "bootstrapped": its current items are
marked as seen without being sent, so adding a feed never floods your chat.
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

    pending = []  # (timestamp, feed_url, entry_id, message)
    for url in feeds:
        parsed = fetch(url)
        if parsed is None:
            continue
        feed_title = parsed.feed.get("title", "")
        known = seen["feeds"].get(url)
        ids_now = [i for i in map(entry_id, parsed.entries) if i]

        if known is None:  # new feed: remember current items, send nothing
            seen["feeds"][url] = ids_now[:MAX_IDS_PER_FEED]
            print(f"BOOTSTRAP {url}: {len(ids_now)} existing items marked as seen")
            continue

        known_set = set(known)
        for entry in parsed.entries:
            eid = entry_id(entry)
            if eid and eid not in known_set:
                pending.append((entry_time(entry), url, eid, format_message(feed_title, entry)))

    pending.sort(key=lambda p: p[0])  # oldest first
    sent = 0
    for ts, url, eid, message in pending[:MAX_PER_RUN]:
        if not send(message):
            break  # stop on failure; unsent items stay unseen for the next run
        seen["feeds"][url] = (seen["feeds"][url] + [eid])[-MAX_IDS_PER_FEED:]
        sent += 1
        time.sleep(1.1)  # stay under Telegram's per-chat rate limit

    if first_run and feeds:
        send(f"✅ RSS bot is live, tracking {len(feeds)} feeds.")

    save_seen(seen)
    left = len(pending) - sent
    print(f"Done: sent {sent}, {left} left for the next run")


if __name__ == "__main__":
    main()
