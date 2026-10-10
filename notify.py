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
  BANNERS            set to 0 to stop showing each post's banner image above the text

Feed management from Telegram (only from your own chat, checked on every run):
  /list   /add <url> [name]   /remove <number|name|url>   /test   /help

Article mirror (MIRROR=1): instead of sending in one go, the run is split in two stages that
the workflow separates with a site build + deploy, so a "Read more" link never 404s:
  python notify.py fetch    commands, feeds -> content/posts/*.md, expiry of old posts
  python notify.py notify   Telegram messages for posts that are mirrored but not yet announced
Without MIRROR=1 the original single-stage behaviour is unchanged. See the README.
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
from urllib.parse import urljoin

import feedparser
import requests

from mirror import extract, feedconf, http_client
from mirror import posts as mposts

ROOT = Path(__file__).parent
FEEDS_FILE = Path(os.environ.get("FEEDS_FILE") or ROOT / "feeds.yml")
SEEN_FILE = Path(os.environ.get("SEEN_FILE") or ROOT / "seen.json")
CONTENT_DIR = Path(os.environ.get("CONTENT_DIR") or ROOT / "content" / "posts")

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
BANNERS = os.environ.get("BANNERS") != "0"
DRY_RUN = os.environ.get("DRY_RUN") == "1"
MIRROR = os.environ.get("MIRROR") == "1"
TELEGRAM_LIMIT = 4096  # characters of visible text per message
MIRROR_EXCERPT_CHARS = clamp_int(os.environ.get("MIRROR_EXCERPT_CHARS", ""), 0, TELEGRAM_LIMIT, default=TELEGRAM_LIMIT)
READ_TTL_HOURS = clamp_int(os.environ.get("READ_TTL_HOURS", ""), 1, 24 * 365, default=24)
UNREAD_TTL_HOURS = clamp_int(os.environ.get("UNREAD_TTL_HOURS", ""), 1, 24 * 365, default=72)
STUB_DAYS = clamp_int(os.environ.get("STUB_DAYS", ""), 0, 3650, default=30)
SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")
DOMAIN_DELAY = float(os.environ.get("DOMAIN_DELAY", "2"))
# re-extract already-mirrored posts of feeds whose url or name contains this text (manual runs only)
REFETCH = os.environ.get("REFETCH", "").strip().lower()
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; rss-telegram-bot/1.0)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
}


# --------------------------------------------------------------------------- feeds.yml

def feed_entries():
    """Every feed in feeds.yml as a dict (url, label, mode, client, selector, ...)."""
    return feedconf.load_feeds(FEEDS_FILE) if FEEDS_FILE.exists() else []


def load_feeds():
    return [e["url"] for e in feed_entries()]


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


def _big_enough(item):
    """False for tiny images (avatars, icons, tracking pixels) whose size the feed states."""
    for key in ("width", "height"):
        try:
            if int(item.get(key)) < 200:
                return False
        except (TypeError, ValueError):
            pass
    return True


_AVATAR_RE = re.compile(r"gravatar\.com/avatar|/avatars?/", re.I)


def entry_image(entry):
    """URL of the post's banner image: media tags, an image enclosure, or the first <img> in the body."""
    candidates = [m for m in (entry.get("media_content") or [])
                  if m.get("medium") == "image" or str(m.get("type", "")).startswith("image/")]
    candidates += entry.get("media_thumbnail") or []
    for link in entry.get("links") or []:
        if link.get("rel") == "enclosure" and str(link.get("type", "")).startswith("image/"):
            candidates.append({"url": link.get("href")})
    for item in candidates:
        if item.get("url") and _big_enough(item) and not _AVATAR_RE.search(item["url"]):
            return urljoin(entry.get("link") or "", item["url"])
    bodies = [c.get("value", "") for c in (entry.get("content") or [])] + [entry.get("summary", "")]
    for markup in bodies:
        for tag in re.findall(r"<img\b[^>]*>", markup or "", re.I):
            src = re.search(r"""\bsrc\s*=\s*["']([^"']+)["']""", tag, re.I)
            size = {k.lower(): v for k, v in re.findall(r"""\b(width|height)\s*=\s*["']?(\d+)""", tag, re.I)}
            if src and not src.group(1).startswith("data:") and _big_enough(size) \
                    and not _AVATAR_RE.search(src.group(1)):
                return urljoin(entry.get("link") or "", html.unescape(src.group(1)))
    return None


def format_message(feed_title, entry):
    """Returns (text, banner image URL or None)."""
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
    return msg, (entry_image(entry) if BANNERS else None)


# --------------------------------------------------------------------------- telegram

def send_message(text, image=None, reply_markup=None):
    """Post one message. Returns (ok, message_id); the id is None in a dry run or if unreadable."""
    if DRY_RUN:
        print("DRY RUN >>", text.replace("\n", " | "))
        return True, None
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    if image:  # the image URL becomes a large preview above the text
        payload["link_preview_options"] = json.dumps(
            {"url": image, "show_above_text": True, "prefer_large_media": True})
    elif not LINK_PREVIEW:
        payload["link_preview_options"] = json.dumps({"is_disabled": True})
    for _ in range(3):
        try:
            resp = requests.post(url, data=payload, timeout=30)
        except requests.RequestException as exc:
            print(f"Telegram request failed: {exc}", file=sys.stderr)
            return False, None
        if resp.status_code == 429:  # rate limited
            wait = resp.json().get("parameters", {}).get("retry_after", 5)
            time.sleep(wait + 1)
            continue
        if resp.ok:
            try:
                message_id = resp.json()["result"]["message_id"]
            except Exception:
                message_id = None
            return True, message_id if isinstance(message_id, int) else None
        print(f"Telegram error {resp.status_code}: {resp.text}", file=sys.stderr)
        return False, None
    return False, None


def send(text, image=None):
    return send_message(text, image)[0]


def tg_call(method, **params):
    """Best-effort Telegram API call (button edits, callback answers). Never raises."""
    if DRY_RUN:
        return None
    try:
        resp = requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}",
                             data={k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
                                   for k, v in params.items()}, timeout=30)
        return resp.json() if resp.ok else None
    except (requests.RequestException, ValueError) as exc:
        print(f"Telegram {method} failed: {exc}", file=sys.stderr)
        return None


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
    allowed = ["message", "callback_query"] if MIRROR else ["message"]
    data = {"timeout": 0, "allowed_updates": json.dumps(allowed)}
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


NOT_MIRRORED_NOTE = "<i>Not mirrored: this links to the original article.</i>"


def mirrored_test_message(seen, entry):
    """The mirror-page message for a /test post that is mirrored and live, else None."""
    if not (MIRROR and SITE_URL and seen):
        return None
    post = seen.get("posts", {}).get(mposts.guid_hash(entry_id(entry) or ""))
    if not post or post["status"] == "pruned":
        return None
    path = mposts.post_path(CONTENT_DIR, post["source_slug"], post["slug"])
    url = site_post_url(post)
    # announced posts were checked live; one still waiting may not be deployed yet
    if not path.exists() or (post["status"] != "notified" and not check_link(url, tries=1)):
        return None
    fm, body = mposts.read_post(path)
    return format_mirror_message(fm, body, url)


def cmd_test(seen=None):
    """Returns the newest post of a random feed (as a message); nothing is marked as seen.

    It links to the mirror page when that post is mirrored, otherwise to the original and says so.
    """
    feeds = load_feeds()
    random.shuffle(feeds)
    for url in feeds:  # skip feeds that fail or are empty
        parsed = fetch(url)
        if parsed is None or not parsed.entries:
            continue
        # newest by date; undated items fall back to feed order (newest first)
        newest = min(enumerate(parsed.entries), key=lambda p: (-entry_time(p[1]), p[0]))[1]
        mirrored = mirrored_test_message(seen, newest)
        if mirrored:
            return mirrored
        text, image = format_message(parsed.feed.get("title", ""), newest)
        return f"{text}\n\n{NOT_MIRRORED_NOTE}", image
    return "I couldn't get a post from any feed. Check /list and the Actions log."


def cmd_list():
    entries = feed_entries()
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
    entries = feed_entries()
    if any(norm_url(e["url"]) == norm_url(url) for e in entries):
        return "I'm already tracking that feed."
    parsed = fetch(url)
    if parsed is None or (not parsed.entries and not parsed.feed.get("title")):
        return ("I couldn't read that as an RSS/Atom feed, so I didn't add it. "
                "Check the link, or look for the site's feed URL.")
    label = parts[1] if len(parts) > 1 else (parsed.feed.get("title") or "")
    label = re.sub(r"[#\s]+", " ", label).strip()
    feedconf.add_feed(FEEDS_FILE, url, label)
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
    entries = feed_entries()
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
    feedconf.remove_feed(FEEDS_FILE, e["url"])
    seen["feeds"].pop(e["url"], None)
    return f"🗑 Removed <b>{html.escape(feed_name(e))}</b>."


READ_BUTTON = "✓ Read"
READ_DONE = "✓ Read · mirror removed within {h}h"


def read_markup(done=False):
    if done:
        return {"inline_keyboard": [[{"text": READ_DONE.format(h=READ_TTL_HOURS), "callback_data": "noop"}]]}
    return None


def handle_callback(cq, seen):
    """A tap on a message button. "r:<id>" marks that mirrored post as read (starts its delete timer)."""
    msg = cq.get("message") or {}
    if str((msg.get("chat") or {}).get("id")) != str(CHAT_ID):
        return  # not from you: ignore silently
    data = cq.get("data") or ""
    if data.startswith("r:"):
        post = seen.get("posts", {}).get(data[2:])
        if post and post.get("status") != "pruned" and not post.get("read_at"):
            post["read_at"] = int(time.time())
            tg_call("editMessageReplyMarkup", chat_id=CHAT_ID, message_id=msg.get("message_id"),
                    reply_markup=read_markup(done=True))
    # the callback is usually too old to answer by now (runs are minutes apart): errors are ignored
    tg_call("answerCallbackQuery", callback_query_id=cq.get("id"))


def handle_commands(seen):
    """Answer commands sent to the bot since the last run. Only your own chat is obeyed."""
    for upd in get_updates(seen.get("tg_offset")):
        seen["tg_offset"] = max(seen.get("tg_offset") or 0, upd.get("update_id", 0) + 1)
        if upd.get("callback_query"):
            handle_callback(upd["callback_query"], seen)
            continue
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
            reply = cmd_test(seen)
        elif cmd == "/remove":
            reply = cmd_remove(arg, seen)
        else:  # /start, /help and anything unknown
            reply = HELP
        if isinstance(reply, tuple):  # (text, banner image) from /test
            send(*reply)
        else:
            send_long(reply)


# --------------------------------------------------------------------------- article mirror

def utf16_len(text):
    """Telegram counts message length in UTF-16 code units (emoji count twice)."""
    return len(text.encode("utf-16-le")) // 2


def site_post_url(post):
    return f"{SITE_URL}/posts/{post['source_slug']}/{post['slug']}/"


def format_mirror_message(fm, body, url, limit=None):
    """Telegram HTML for a mirrored post: title, source, as much text as fits, Read more.

    The visible text (what Telegram counts, after entity parsing) stays within TELEGRAM_LIMIT.
    Returns (text, banner image URL or None).
    """
    title = (fm.get("title") or "(no title)").strip()
    source = (fm.get("source") or "").strip()
    limit = MIRROR_EXCERPT_CHARS if limit is None else limit
    head_plain = title + (f"\n{source}" if source else "")
    foot_plain = "Read more →"
    # visible text = head + "\n\n" + excerpt + "\n\n" + foot; keep a small safety margin
    budget = TELEGRAM_LIMIT - 8 - utf16_len(head_plain) - utf16_len(foot_plain) - 4
    excerpt = ""
    if limit > 0 and budget > 0:
        full = mposts.md_to_text(body) or (fm.get("summary") or "")
        cut = min(limit, budget)
        excerpt = truncate(full, cut)
        while excerpt and utf16_len(excerpt) > budget:  # emoji-heavy text or the " …" tail: shrink
            cut = max(0, cut - max(1, utf16_len(excerpt) - budget))
            excerpt = truncate(full, cut) if cut else ""
    link = html.escape(url, quote=True)
    msg = f'<b><a href="{link}">{html.escape(title)}</a></b>'
    if source:
        msg += f"\n<i>{html.escape(source)}</i>"
    if excerpt:
        msg += f"\n\n{html.escape(excerpt)}"
    msg += f'\n\n<a href="{link}">Read more →</a>'
    return msg, ((fm.get("image") or None) if BANNERS else None)


def feed_cfg_for(entries, url):
    return next((e for e in entries if e["url"] == url), None)


def entry_date_iso(entry, fallback):
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", t) if t else fallback


def iso_now(now):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))


def mirror_entry(fc, parsed_feed, entry, fetcher, now, log, slug=None):
    """Build and write the Markdown file for one feed item. Returns its state record.

    Never raises for content problems: a page that can't be fetched or parsed falls back to
    the feed's own data and the post is marked excerpt_only. Only I/O errors propagate.
    `slug` keeps an existing file name when a post is regenerated (its link must not change).
    """
    guid = entry_id(entry)
    link = entry.get("link") or ""
    title = html.unescape(entry.get("title") or "").strip()
    source = fc["label"] or parsed_feed.feed.get("title") or fc["url"]
    image = entry_image(entry)
    author = (entry.get("author") or "").strip()
    excerpt_only = False
    page_meta = {}
    base = link or fc["url"]

    html_body = extract.feed_html(entry)
    mode = extract.choose_mode(fc, entry)
    if mode == "fetch" and link:
        try:
            resp = fetcher.get(link, client=fc["client"], page=True)
            html_body, page_meta = extract.extract_page(resp.text, link, fc["selector"], fc.get("remove") or (),
                                                        fc.get("subtitle_selector"))
            base = link
        except http_client.FetchError as exc:
            kind = "BLOCKED" if exc.blocked else "FETCH FAILED"
            log(f"{kind} {link}: {exc} - saving feed excerpt only")
            excerpt_only = True
        except ValueError as exc:
            log(f"EXTRACT FAILED {link}: {exc} - saving feed excerpt only")
            excerpt_only = True
    elif mode == "fetch":
        excerpt_only = True  # nothing to fetch without a link

    md = extract.html_to_markdown(extract.sanitize_html(html_body, base))
    if not title:  # e.g. Mastodon posts: use the start of the text
        first = (mposts.md_to_text(md).split("\n") or [""])[0]
        title = truncate(first, 80).replace(" …", "…") if first else "(no title)"
    image = page_meta.get("image") or image  # the page's og:image is usually larger than a feed thumbnail
    md = extract.drop_leading_image(extract.drop_leading_title(md, title), image)
    if not md:  # the feed had nothing readable either: keep at least the title and link
        excerpt_only = True
    author = author or (page_meta.get("author") or "")

    fetched = iso_now(now)
    source_slug = mposts.slugify(source)
    slug = slug or mposts.make_slug(title, guid)
    summary = mposts.first_sentences(mposts.md_to_text(md), 3, 400)
    tags = [t.get("term") for t in (entry.get("tags") or []) if t.get("term")]
    fields = {"title": title, "subtitle": page_meta.get("subtitle") or "", "source": source, "source_url": link, "author": author,
              "date": entry_date_iso(entry, fetched), "fetched": fetched, "image": image or "",
              "summary": summary, "tags": tags, "guid": guid}
    extra = {"excerpt_only": True} if excerpt_only else None
    mposts.write_post(mposts.post_path(CONTENT_DIR, source_slug, slug), fields, md, extra)
    return {"guid": guid, "feed": fc["url"], "source": source, "source_slug": source_slug, "slug": slug,
            "title": title, "fetched": int(now), "status": "mirrored", "excerpt_only": excerpt_only,
            "date": entry_time(entry) or int(now)}


def expire_posts(seen, now, log):
    """Replace expired posts with redirect stubs and drop old stubs. Returns how many changed."""
    changed = 0
    for pid, post in list(seen.get("posts", {}).items()):
        path = mposts.post_path(CONTENT_DIR, post["source_slug"], post["slug"])
        if post["status"] == "pruned":
            if STUB_DAYS * 86400 + post.get("pruned_at", now) <= now:
                path.unlink(missing_ok=True)
                del seen["posts"][pid]
                changed += 1
            continue
        if mposts.expires_at(post, READ_TTL_HOURS, UNREAD_TTL_HOURS) > now:
            continue
        try:
            fm = mposts.read_post(path)[0] if path.exists() else {}
            mposts.write_stub(path, {**fm, "title": post["title"], "source": post["source"],
                                     "source_url": fm.get("source_url", ""), "guid": post["guid"]})
        except OSError as exc:
            log(f"PRUNE FAILED {path}: {exc}")
            continue
        post["status"], post["pruned_at"] = "pruned", int(now)
        changed += 1
        log(f"PRUNED {post['source_slug']}/{post['slug']} ({'read' if post.get('read_at') else 'unread'})")
    return changed


def refresh_posts(seen, fc, parsed, fetcher, now, log, summary):
    """Re-extract this feed's live (not yet expired) posts in place, e.g. after changing its
    feeds.yml overrides. Same file name and link, same delete timer, never re-announced."""
    count = 0
    for entry in parsed.entries:
        old = seen["posts"].get(mposts.guid_hash(entry_id(entry) or ""))
        if not old or old["status"] == "pruned" or old["feed"] != fc["url"]:
            continue
        try:
            rec = mirror_entry(fc, parsed, entry, fetcher, now, log, slug=old["slug"])
        except Exception as exc:
            log(f"REFRESH FAILED {entry.get('link')}: {type(exc).__name__}: {exc}")
            summary["failed_items"].append(f"{fc['label'] or fc['url']}: {entry.get('title')}: refresh: {exc}")
            continue
        if rec["source_slug"] != old["source_slug"]:  # feed renamed since: keep the old path
            mposts.post_path(CONTENT_DIR, rec["source_slug"], rec["slug"]).replace(
                mposts.post_path(CONTENT_DIR, old["source_slug"], old["slug"]))
        old.update(title=rec["title"], excerpt_only=rec["excerpt_only"])
        count += 1
        log(f"REFRESHED {old['source_slug']}/{old['slug']}")
    return count


def stage_fetch(seen, fetcher=None, now=None, log=print):
    """Feeds -> Markdown files + state. Returns a summary dict (also written for the workflow)."""
    now = now if now is not None else time.time()
    fetcher = fetcher or http_client.Fetcher(delay=DOMAIN_DELAY)
    seen.setdefault("posts", {})
    seen.setdefault("http", {})
    summary = {"new": 0, "pruned": 0, "refreshed": 0, "failed_feeds": [], "failed_items": [], "excerpt_only": []}
    summary["pruned"] = expire_posts(seen, now, log)

    entries = feed_entries()
    new_posts = []  # (date, id, feed config, parsed feed, entry, is_backfill)
    http_cache = {}  # url -> validators, kept only for feeds fully processed this run
    incomplete = set()  # feed urls with items skipped by the cap or failed: no 304 shortcut next time
    for fc in entries:
        url = fc["url"]
        cache = seen["http"].get(url) or {}
        refetch = bool(REFETCH) and (REFETCH in url.lower() or REFETCH in fc["label"].lower())
        try:
            resp = fetcher.get(url, client=fc["client"], conditional=None if (BACKFILL or refetch) else cache)
            if resp.status == 304:
                log(f"UNCHANGED {url}")
                continue
            parsed = feedparser.parse(resp.content)
            if not parsed.entries and parsed.bozo:
                raise http_client.FetchError(f"unparseable feed ({parsed.bozo_exception})")
        except http_client.FetchError as exc:
            kind = "BLOCKED" if exc.blocked else "FAILED"
            log(f"{kind}  {url}: {exc}")
            summary["failed_feeds"].append(f"{fc['label'] or url}: {exc}")
            continue
        except Exception as exc:  # a broken feed must never abort the run
            log(f"FAILED  {url}: {type(exc).__name__}: {exc}")
            summary["failed_feeds"].append(f"{fc['label'] or url}: {exc}")
            continue

        if refetch:
            summary["refreshed"] += refresh_posts(seen, fc, parsed, fetcher, now, log, summary)

        known = seen["feeds"].get(url)
        ids_now = [i for i in map(entry_id, parsed.entries) if i]
        dated = [(i, e) for i, e in enumerate(parsed.entries) if entry_id(e)]
        n = BACKFILL if known is not None else max(BACKFILL, NEW_FEED_BACKFILL)
        newest = sorted(dated, key=lambda p: (-entry_time(p[1]), p[0]))[:n]
        todo = []  # (entry, is_backfill)
        if known is None:
            backfilled = {entry_id(e) for _, e in newest}
            seen["feeds"][url] = [i for i in ids_now if i not in backfilled][:MAX_IDS_PER_FEED]
            log(f"BOOTSTRAP {url}: {len(ids_now)} existing items, mirroring newest {len(newest)}")
        else:
            known_set = set(known)
            todo = [(e, False) for e in parsed.entries if entry_id(e) and entry_id(e) not in known_set]
        todo += [(e, True) for _, e in newest]
        if not BACKFILL:
            hdrs = {k.lower(): v for k, v in resp.headers.items()}
            http_cache[url] = {"etag": hdrs.get("etag"), "last_modified": hdrs.get("last-modified")}

        done_here = set()
        for entry, is_backfill in todo:
            guid = entry_id(entry)
            pid = mposts.guid_hash(guid)
            old = seen["posts"].get(pid)
            if guid in done_here or (old and old["status"] != "pruned"):
                continue  # never write or announce the same article twice
            done_here.add(guid)
            title = entry.get("title") or ""
            if fc["title_contains"] and not any(w in title.lower() for w in fc["title_contains"]):
                if guid not in seen["feeds"][url]:
                    seen["feeds"][url].append(guid)  # filtered out: remembered, not mirrored
                continue
            new_posts.append((entry_time(entry), pid, fc, parsed, entry, is_backfill))

    # oldest first; ordinary new items are capped per run, backfilled ones are not
    new_posts.sort(key=lambda t: t[0])
    ordinary_left = MAX_PER_RUN
    for t in new_posts:
        _, pid, fc, parsed, entry, is_backfill = t
        if not is_backfill:
            if ordinary_left <= 0:
                incomplete.add(fc["url"])
                continue  # stays unseen: picked up on the next run
            ordinary_left -= 1
        guid = entry_id(entry)
        try:
            rec = mirror_entry(fc, parsed, entry, fetcher, now, log)
        except Exception as exc:
            log(f"ITEM FAILED {entry.get('link') or guid}: {type(exc).__name__}: {exc}")
            summary["failed_items"].append(f"{fc['label'] or fc['url']}: {entry.get('title')}: {exc}")
            incomplete.add(fc["url"])
            continue  # not marked seen: retried on the next run
        seen["posts"][pid] = rec
        ids = seen["feeds"][fc["url"]]
        if guid not in ids:
            seen["feeds"][fc["url"]] = (ids + [guid])[-MAX_IDS_PER_FEED:]
        summary["new"] += 1
        if rec["excerpt_only"]:
            summary["excerpt_only"].append(f"{rec['source']}: {rec['title']}")
        log(f"MIRRORED {rec['source_slug']}/{rec['slug']}" + (" (excerpt only)" if rec["excerpt_only"] else ""))

    for url, validators in http_cache.items():
        if url not in incomplete:
            seen["http"][url] = validators
    summary["pending"] = sum(1 for p in seen["posts"].values() if p["status"] == "mirrored")
    return summary


def check_link(url, tries=6, wait=10):
    """True once the mirrored page answers 200 (Pages can lag a few seconds after a deploy)."""
    if DRY_RUN:
        return True
    for attempt in range(tries):
        try:
            if requests.get(url, headers={"User-Agent": http_client.USER_AGENT}, timeout=20).status_code == 200:
                return True
        except requests.RequestException:
            pass
        if attempt < tries - 1:
            time.sleep(wait)
    return False


def stage_notify(seen, log=print, link_check=True):
    """Send Telegram messages for mirrored-but-unannounced posts, oldest first."""
    if not SITE_URL and not DRY_RUN:
        sys.exit("Set SITE_URL (the GitHub Pages address) for the notify stage.")
    posts = seen.setdefault("posts", {})
    pending = sorted(((pid, p) for pid, p in posts.items() if p["status"] == "mirrored"),
                     key=lambda kv: (kv[1].get("date", 0), kv[1]["fetched"]))
    sent = 0
    for pid, post in pending:
        path = mposts.post_path(CONTENT_DIR, post["source_slug"], post["slug"])
        if not path.exists():
            log(f"MISSING {path}: marking as pruned")
            post["status"], post["pruned_at"] = "pruned", int(time.time())
            continue
        fm, body = mposts.read_post(path)
        url = site_post_url(post) if SITE_URL else f"https://example.invalid/posts/{post['source_slug']}/{post['slug']}/"
        if link_check and not check_link(url):
            log(f"NOT LIVE YET {url}: will retry next run")
            continue
        text, image = format_mirror_message(fm, body, url)
        ok, message_id = send_message(text, image, {"inline_keyboard": [[{"text": READ_BUTTON, "callback_data": f"r:{pid}"}]]})
        if not ok:
            break  # stop on failure; the rest stay pending for the next run
        post.update(status="notified", notified_at=int(time.time()), message_id=message_id)
        sent += 1
        time.sleep(1.1)  # stay under Telegram's per-chat rate limit
    log(f"Notify: sent {sent}, {len(pending) - sent} still pending")
    return sent


def write_github_output(values):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            for k, v in values.items():
                fh.write(f"{k}={v}\n")


def write_step_summary(lines):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")


def run_fetch_stage():
    if not DRY_RUN and not (TOKEN and CHAT_ID):
        sys.exit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (or DRY_RUN=1).")
    seen = load_seen()
    seen.setdefault("feeds", {})
    if not DRY_RUN:
        handle_commands(seen)  # may edit feeds.yml and mark posts read, so it runs first
    summary = stage_fetch(seen)
    save_seen(seen)
    changed = summary["new"] > 0 or summary["pruned"] > 0 or summary["refreshed"] > 0
    print(f"Fetch done: {summary['new']} new, {summary['pruned']} expired, {summary['refreshed']} refreshed, "
          f"{len(summary['failed_feeds'])} feed failures, {len(summary['failed_items'])} item failures")
    write_github_output({"changed": str(changed).lower(), "new_count": summary["new"],
                         "pruned": summary["pruned"], "pending": summary["pending"]})
    lines = ["### Mirror fetch", f"- new posts: {summary['new']}", f"- expired posts: {summary['pruned']}",
             f"- refreshed posts: {summary['refreshed']}",
             f"- pending announcement: {summary['pending']}"]
    for key, label in (("failed_feeds", "feed failures"), ("failed_items", "item failures"),
                       ("excerpt_only", "excerpt-only posts")):
        if summary[key]:
            lines += [f"- {label}:"] + [f"  - {x}" for x in summary[key]]
    write_step_summary(lines)


def run_notify_stage():
    if not DRY_RUN and not (TOKEN and CHAT_ID):
        sys.exit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (or DRY_RUN=1).")
    seen = load_seen()
    seen.setdefault("feeds", {})
    sent = stage_notify(seen)
    save_seen(seen)
    write_step_summary(["### Mirror notify", f"- messages sent: {sent}"])


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
        if not send(*message):
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
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252
        stream.reconfigure(encoding="utf-8", errors="replace")
    stage = sys.argv[1] if len(sys.argv) > 1 else ("all" if MIRROR else "legacy")
    if stage == "fetch":
        run_fetch_stage()
    elif stage == "notify":
        run_notify_stage()
    elif stage == "all":  # both stages in one go: for local DRY_RUN checks
        run_fetch_stage()
        run_notify_stage()
    else:
        main()
