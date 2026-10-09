#!/usr/bin/env python3
"""Fetch RSS/Atom feeds and send new items to a Telegram chat.

State lives in seen.json (committed back to the repo by the workflow).
A feed seen for the first time is "bootstrapped": its current items are
marked as seen without being sent, so adding a feed never floods your chat.

Two optional "latest posts" settings (both 0 = off, clamped to 0-20):
  BACKFILL           send the newest N items of every feed, even if already seen
  NEW_FEED_BACKFILL  send the newest N items of a feed seen for the first time

Message text:
  EXCERPT_CHARS      how much of each post to include (default 800, 0 = link only)
  LINK_PREVIEW       set to 1 to let Telegram attach its link-preview card

Feed management from Telegram (only from your own chat, checked on every run):
  /list   /add <url> [name]   /remove <number|name|url>   /test   /help
"""

import calendar
import html
import json
import os
import random
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path

import feedparser
import requests

ROOT = Path(__file__).parent
FEEDS_FILE = ROOT / "feeds.txt"
SEEN_FILE = ROOT / "seen.json"

MAX_PER_RUN = int(os.environ.get("MAX_PER_RUN", "25"))  # cap messages per run
MAX_IDS_PER_FEED = 1000  # how many seen ids to remember per feed


def clamp_int(value, lo, hi, default=None):
    """Parse a setting: non-numbers become `default` (or `lo`), the result is clamped to lo-hi."""
    try:
        n = int(str(value).strip())
    except ValueError:
        return lo if default is None else default
    return max(lo, min(hi, n))


def clamp_count(value):
    """Parse a "latest N" setting: non-numbers become 0, the result is clamped to 0-20."""
    return clamp_int(value, 0, 20)


BACKFILL = clamp_count(os.environ.get("BACKFILL", ""))
NEW_FEED_BACKFILL = clamp_count(os.environ.get("NEW_FEED_BACKFILL", "0"))
EXCERPT_CHARS = clamp_int(os.environ.get("EXCERPT_CHARS", ""), 0, 3000, default=800)
LINK_PREVIEW = os.environ.get("LINK_PREVIEW") == "1"
DRY_RUN = os.environ.get("DRY_RUN") == "1"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; rss-telegram-bot/1.0)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
}


# --------------------------------------------------------------------------- feeds.txt

def parse_feeds_file():
    """Read feeds.txt. Returns (lines, entries).

    A feed line is `URL` or `URL  # Label`. A label can also be a single comment line
    directly above the URL (and below a blank line), which is how the file started out.
    Each entry: url, label, idx (line index) and comment_idx (that comment line, or None).
    """
    lines = FEEDS_FILE.read_text(encoding="utf-8").splitlines() if FEEDS_FILE.exists() else []
    entries = []
    for i, raw in enumerate(lines):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(\S+)(?:\s+#\s*(.*))?$", line)
        if not m:
            print(f"WARNING: ignoring unreadable line in feeds.txt: {raw!r}", file=sys.stderr)
            continue
        url, label = m.group(1), (m.group(2) or "").strip()
        comment_idx = None
        if not label and i >= 1 and lines[i - 1].lstrip().startswith("#") \
                and (i == 1 or not lines[i - 2].strip()):
            comment_idx = i - 1
            label = re.sub(r"\s*\(.*$", "", lines[i - 1].lstrip().lstrip("#")).strip()
        entries.append({"url": url, "label": label, "idx": i, "comment_idx": comment_idx})
    return lines, entries


def write_feeds_file(lines):
    """Save feeds.txt, collapsing runs of blank lines and keeping one trailing newline."""
    out, blank = [], False
    for ln in lines:
        if not ln.strip():
            if blank:
                continue
            blank = True
        else:
            blank = False
        out.append(ln.rstrip())
    FEEDS_FILE.write_text("\n".join(out).strip("\n") + "\n", encoding="utf-8")


def load_feeds():
    return [e["url"] for e in parse_feeds_file()[1]]


def load_seen():
    if SEEN_FILE.exists():
        try:
            return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("WARNING: seen.json is corrupt, starting fresh", file=sys.stderr)
    return {"feeds": {}}


def save_seen(seen):
    SEEN_FILE.write_text(json.dumps(seen, indent=1, sort_keys=True), encoding="utf-8")


# --------------------------------------------------------------------------- fetching

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


# --------------------------------------------------------------------------- message text

_SKIP_TAGS = {"script", "style", "figure", "svg", "noscript", "iframe", "button"}
_BLOCK_TAGS = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6",
               "tr", "blockquote", "pre", "hr", "table", "section", "article"}


class _TextExtractor(HTMLParser):
    """Turns HTML into plain text: paragraphs become line breaks, images/figures vanish."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self.skip += 1
        elif tag in _BLOCK_TAGS:
            self.parts.append("\n• " if tag == "li" else "\n")

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
        elif tag in _BLOCK_TAGS and tag != "li":  # <li> already starts its own line
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_text(markup):
    parser = _TextExtractor()
    try:
        parser.feed(markup or "")
        parser.close()
    except Exception:  # malformed markup must never break a run
        return ""
    text = "".join(parser.parts).replace("\xa0", " ")
    lines = [re.sub(r"[ \t\r\f\v]+", " ", ln).strip() for ln in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


# a trailing "… Continue reading <title>" / "Read more" line left by feed summaries
_MORE_RE = re.compile(r"\s*(?:…|\.{3})?\s*(?:continue reading|read more)\b[^\n]{0,200}\Z", re.I)


def entry_text(entry):
    """Plain text of an item's body: the full content if the feed has it, else its summary."""
    candidates = [c.get("value", "") for c in (entry.get("content") or [])]
    candidates.append(entry.get("summary", ""))
    for markup in candidates:
        text = html_to_text(markup)
        if text:
            return _MORE_RE.sub("", text).strip()
    return ""


def truncate(text, limit):
    """Cut to about `limit` characters, preferring the end of a sentence, then a word."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(m) for m in (". ", "! ", "? ", ".\n", "\n\n"))
    if end >= limit * 0.6:
        return cut[:end + 1].rstrip() + " …"
    if re.search(r"\s", cut):
        cut = cut.rsplit(None, 1)[0]
    return cut.rstrip(" ,;:–—-") + " …"


def make_excerpt(entry, limit):
    if limit <= 0:
        return ""
    text = entry_text(entry)
    title = (entry.get("title") or "").strip()
    if title and text.lower().startswith(title.lower()):  # body that repeats the title
        text = text[len(title):].lstrip(" \n:–—-")
    return truncate(text, limit)


def format_message(feed_title, entry):
    title = html.escape(entry.get("title") or "(no title)")
    link = html.escape(entry.get("link") or "", quote=True)
    source = html.escape(feed_title or "")
    msg = f'<b><a href="{link}">{title}</a></b>' if link else f"<b>{title}</b>"
    if source:
        msg += f"\n<i>{source}</i>"
    excerpt = make_excerpt(entry, EXCERPT_CHARS)
    if excerpt:
        msg += f"\n\n{html.escape(excerpt)}"
        if link:
            msg += f'\n\n<a href="{link}">Read more →</a>'
    return msg


# --------------------------------------------------------------------------- telegram

def send(text):
    if DRY_RUN:
        print("DRY RUN >>", text.replace("\n", " | "))
        return True
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    if not LINK_PREVIEW:
        payload["link_preview_options"] = json.dumps({"is_disabled": True})
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


def send_long(text, limit=3800):
    """Send a multi-line reply, splitting between lines if it is too long for one message."""
    chunk = ""
    for line in text.split("\n"):
        if chunk and len(chunk) + len(line) + 1 > limit:
            send(chunk)
            chunk = ""
        chunk = f"{chunk}\n{line}" if chunk else line
    if chunk:
        send(chunk)


def get_updates(offset):
    data = {"timeout": 0, "allowed_updates": json.dumps(["message"])}
    if offset is not None:
        data["offset"] = offset
    try:
        resp = requests.post(f"https://api.telegram.org/bot{TOKEN}/getUpdates", data=data, timeout=30)
        body = resp.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"getUpdates failed: {exc}", file=sys.stderr)
        return []
    if not body.get("ok"):
        print(f"getUpdates error: {body}", file=sys.stderr)
        return []
    result = body.get("result")
    return result if isinstance(result, list) else []


# --------------------------------------------------------------------------- commands

HELP = (
    "<b>Feed commands</b>\n"
    "/list - show your feeds\n"
    "/add &lt;url&gt; [name] - add a feed\n"
    "/remove &lt;number|name|url&gt; - remove a feed\n"
    "/test - send the newest post of a random feed\n"
    "/help - this message\n\n"
    "I check for commands on every run (every few minutes), so replies are not instant."
)


def norm_url(url):
    return url.strip().rstrip("/").lower()


def feed_name(entry):
    return entry["label"] or entry["url"]


def cmd_test():
    """Returns the newest post of a random feed (as a message); nothing is marked as seen."""
    feeds = load_feeds()
    random.shuffle(feeds)
    for url in feeds:  # skip feeds that fail or are empty
        parsed = fetch(url)
        if parsed is None or not parsed.entries:
            continue
        # newest by date; undated items fall back to feed order (newest first)
        newest = min(enumerate(parsed.entries), key=lambda p: (-entry_time(p[1]), p[0]))[1]
        return format_message(parsed.feed.get("title", ""), newest)
    return "I couldn't get a post from any feed. Check /list and the Actions log."


def cmd_list():
    _, entries = parse_feeds_file()
    if not entries:
        return "No feeds yet. Add one with /add &lt;url&gt;."
    rows = [f"📚 Tracking {len(entries)} feeds:"]
    for n, e in enumerate(entries, 1):
        name = html.escape(feed_name(e))
        rows.append(f'{n}. <a href="{html.escape(e["url"], quote=True)}">{name}</a>' if e["label"]
                    else f"{n}. {name}")
    return "\n".join(rows)


def cmd_add(arg):
    """Returns the reply text."""
    parts = arg.split(None, 1)
    if not parts:
        return "Usage: /add &lt;url&gt; [name]"
    url = parts[0]
    if not re.match(r"^https?://\S+$", url, re.I):
        return "That doesn't look like a link. Usage: /add &lt;url&gt; [name]"
    lines, entries = parse_feeds_file()
    if any(norm_url(e["url"]) == norm_url(url) for e in entries):
        return "I'm already tracking that feed."
    parsed = fetch(url)
    if parsed is None or (not parsed.entries and not parsed.feed.get("title")):
        return ("I couldn't read that as an RSS/Atom feed, so I didn't add it. "
                "Check the link, or look for the site's feed URL.")
    label = parts[1] if len(parts) > 1 else (parsed.feed.get("title") or "")
    label = re.sub(r"[#\s]+", " ", label).strip()
    if lines and lines[-1].strip():
        lines.append("")
    lines.append(f"{url}  # {label}" if label else url)
    write_feeds_file(lines)
    n = len(parsed.entries)
    if NEW_FEED_BACKFILL and n:
        extra = f" I'll send its newest {min(NEW_FEED_BACKFILL, n)} post(s) now."
    else:
        extra = " You'll get new posts from now on."
    return f"✅ Added <b>{html.escape(label or url)}</b> ({n} posts found).{extra}"


def cmd_remove(arg, seen):
    """Returns the reply text; drops the feed's state from `seen` when it removes one."""
    if not arg:
        return "Usage: /remove &lt;number|name|url&gt;. See /list for the numbers."
    lines, entries = parse_feeds_file()
    if arg.isdigit():
        n = int(arg)
        match = [entries[n - 1]] if 1 <= n <= len(entries) else []
    else:
        exact = [e for e in entries if norm_url(e["url"]) == norm_url(arg)]
        q = arg.lower()
        match = exact or [e for e in entries if q in e["url"].lower() or q in e["label"].lower()]
    if not match:
        return "No feed matches that. Use /list to see the numbers."
    if len(match) > 1:
        rows = [f"{entries.index(e) + 1}. {html.escape(feed_name(e))}" for e in match]
        return "More than one feed matches:\n" + "\n".join(rows) + "\nUse the number, e.g. /remove 2."
    e = match[0]
    drop = {e["idx"]} | ({e["comment_idx"]} if e["comment_idx"] is not None else set())
    write_feeds_file([ln for i, ln in enumerate(lines) if i not in drop])
    seen["feeds"].pop(e["url"], None)
    return f"🗑 Removed <b>{html.escape(feed_name(e))}</b>."


def handle_commands(seen):
    """Answer commands sent to the bot since the last run. Only your own chat is obeyed."""
    for upd in get_updates(seen.get("tg_offset")):
        seen["tg_offset"] = max(seen.get("tg_offset") or 0, upd.get("update_id", 0) + 1)
        msg = upd.get("message") or {}
        if str((msg.get("chat") or {}).get("id")) != str(CHAT_ID):
            continue  # not from you: ignore silently
        parts = (msg.get("text") or "").split(None, 1)
        if not parts or not parts[0].startswith("/"):
            continue
        cmd, arg = parts[0].split("@")[0].lower(), (parts[1].strip() if len(parts) > 1 else "")
        if cmd == "/list":
            reply = cmd_list()
        elif cmd == "/add":
            reply = cmd_add(arg)
        elif cmd == "/test":
            reply = cmd_test()
        elif cmd == "/remove":
            reply = cmd_remove(arg, seen)
        else:  # /start, /help and anything unknown
            reply = HELP
        send_long(reply)


# --------------------------------------------------------------------------- main

def main():
    if not DRY_RUN and not (TOKEN and CHAT_ID):
        sys.exit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (or DRY_RUN=1).")

    first_run = not SEEN_FILE.exists()
    seen = load_seen()
    seen.setdefault("feeds", {})

    if not DRY_RUN:
        handle_commands(seen)  # may edit feeds.txt, so it runs before the feeds are loaded
    feeds = load_feeds()

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
        send(f"✅ RSS bot is live, tracking {len(feeds)} feeds. Send /help for commands.")

    save_seen(seen)
    left = len(pending) - sent
    print(f"Done: sent {sent}, {left} left for the next run")


if __name__ == "__main__":
    main()
