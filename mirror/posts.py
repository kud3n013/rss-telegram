"""Mirrored posts on disk: slugs, frontmatter, reading/writing, plain-text snippets and expiry."""

import hashlib
import io
import re
import unicodedata
from pathlib import Path

from ruamel.yaml import YAML

FIELDS = ("title", "subtitle", "source", "source_url", "author", "date", "fetched", "image",
          "summary", "tags", "guid")


# ---------------------------------------------------------------------------- identity

def slugify(text, max_len=60):
    """URL-safe lowercase ASCII slug, cut at a word boundary."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = re.sub(r"['’]", "", text)  # "Anna's" -> "annas", not "anna-s"
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(text) > max_len:
        text = text[:max_len].rsplit("-", 1)[0] if "-" in text[:max_len] else text[:max_len]
    return text or "post"


def guid_hash(guid):
    """Stable 10-hex-digit id for a feed item (used as the state key and in button data)."""
    return hashlib.sha1((guid or "").encode("utf-8")).hexdigest()[:10]


def make_slug(title, guid):
    """Title slug plus a short guid hash, so equal titles never collide."""
    return f"{slugify(title)}-{guid_hash(guid)[:6]}"


def post_path(content_dir, source_slug, slug):
    return Path(content_dir) / source_slug / f"{slug}.md"


# ---------------------------------------------------------------------------- frontmatter

def _yaml():
    y = YAML(typ="safe")
    y.default_flow_style = False
    y.allow_unicode = True
    y.width = 10_000
    return y


def build_frontmatter(fields, extra=None):
    """YAML frontmatter block (with the --- fences) in the documented field order."""
    data = {k: fields.get(k) if fields.get(k) is not None else ("" if k != "tags" else []) for k in FIELDS}
    data["tags"] = [str(t) for t in (fields.get("tags") or [])]
    for k, v in (extra or {}).items():
        data[k] = v
    for k in ("title", "subtitle", "summary", "author"):
        data[k] = re.sub(r"\s+", " ", str(data[k])).strip()
    buf = io.StringIO()
    y = _yaml()
    for key, value in data.items():  # one key at a time: the safe dumper would sort them
        y.dump({key: value}, buf)
    return f"---\n{buf.getvalue()}---\n"


def split_frontmatter(text):
    """(frontmatter dict, body) of a post file; ({}, text) when it has none."""
    m = re.match(r"\A---\n(.*?\n)---\n?(.*)\Z", text, re.S)
    if not m:
        return {}, text
    data = _yaml().load(m.group(1))
    return (data if isinstance(data, dict) else {}), m.group(2)


def neutralize_shortcodes(body):
    """Hugo parses {{< and {{% anywhere in content, even in code fences; one article about
    templates would fail the whole site build. A zero-width space defuses them."""
    return re.sub(r"\{\{(?=[<%])", "{{​", body)


def write_post(path, fields, body, extra=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = neutralize_shortcodes(body)
    path.write_text(build_frontmatter(fields, extra) + "\n" + body.strip() + "\n", encoding="utf-8", newline="\n")


def read_post(path):
    return split_frontmatter(Path(path).read_text(encoding="utf-8"))


def write_stub(path, fields):
    """Replace a post with a tiny redirect page so old Telegram links still lead somewhere."""
    keep = {k: fields.get(k) for k in ("title", "source", "source_url", "date", "guid")}
    write_post(path, keep, "", extra={"stub": True})


# ---------------------------------------------------------------------------- text helpers

def md_to_text(md):
    """Plain text of a Markdown body (paragraph breaks kept), for Telegram snippets."""
    md = md.replace("{{​", "{{")  # undo neutralize_shortcodes
    text = re.sub(r"```[^\n]*\n(.*?)```", r"\1", md, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "• ", text, flags=re.M)
    text = re.sub(r"(\*\*|__)(.+?)\1", r"\2", text, flags=re.S)
    text = re.sub(r"(?<![\w*])[*_]([^*_\n]+)[*_](?![\w*])", r"\1", text)
    text = re.sub(r"`([^`\n]+)`", r"\1", text)
    text = re.sub(r"^\s*([-*_]\s*){3,}$", "", text, flags=re.M)
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!>|])", r"\1", text)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def first_sentences(text, count=3, limit=400):
    """The first `count` sentences, at most `limit` characters (cut at a word if one is longer)."""
    flat = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'“(])", flat)
    out = ""
    for part in parts[:count]:
        if out and len(out) + len(part) + 1 > limit:
            break
        out = f"{out} {part}".strip()
    if len(out) > limit:
        out = out[:limit].rsplit(" ", 1)[0].rstrip(" ,;:–—-") + " …"
    return out


# ---------------------------------------------------------------------------- expiry

def expires_at(post, read_ttl_h, unread_ttl_h):
    """Epoch second when a mirrored post should be removed.

    Read posts go `read_ttl_h` after being marked read; unread ones `unread_ttl_h` after
    they were announced (or fetched, if never announced). The earlier of the two wins.
    """
    started = post.get("notified_at") or post.get("fetched") or 0
    unread_deadline = started + unread_ttl_h * 3600
    if post.get("read_at"):
        return min(unread_deadline, post["read_at"] + read_ttl_h * 3600)
    return unread_deadline
