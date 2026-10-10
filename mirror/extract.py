"""Turn feed items and article pages into clean Markdown."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment
from markdownify import MarkdownConverter

# elements that never belong in an article body
_DROP_TAGS = ("script", "style", "noscript", "iframe", "form", "button", "svg", "canvas", "object",
              "embed", "input", "select", "textarea", "nav", "aside", "footer", "link", "meta", "template")
# class/id words of share widgets, cookie banners, newsletter boxes and similar clutter
_JUNK_RE = re.compile(
    r"(^|[-_\s])(share|sharing|shares|sharedaddy|social|addtoany|a2a|cookie|cookies|consent|gdpr|"
    r"newsletter|subscribe|subscription|signup|sign-up|advert|ad-slot|promo|related|"
    r"comments?|sidebar|breadcrumbs?|skip-link|screen-reader-text|visually-hidden)($|[-_\s])", re.I)
_TRACKER_RE = re.compile(r"(feeds\.feedburner\.com/~|stats\.wp\.com|pixel|beacon|/track(ing)?[/?]|doubleclick|"
                         r"analytics|1x1\.|/wp-includes/images/smilies/)", re.I)
_BOILERPLATE_START = ("share this", "like this", "related posts", "related:", "read more", "continue reading")
_KEEP_EMPTY = {"img", "br", "hr", "video", "audio", "source", "picture", "td", "th", "tr"}


def _is_boilerplate(tag):
    text = tag.get_text(" ", strip=True)
    if not text or tag.find(["img", "pre", "code", "table"]):
        return False
    low = text.lower()
    if "appeared first on" in low and len(text) < 300:  # WordPress "The post X appeared first on Y."
        return True
    return len(text) < 120 and low.startswith(_BOILERPLATE_START)


def sanitize_html(markup, base_url=""):
    """Strip clutter, make URLs absolute, and demote headings when the body has its own <h1>."""
    soup = BeautifulSoup(markup or "", "lxml")
    root = soup.body or soup
    for node in root.find_all(string=lambda s: isinstance(s, Comment)):
        node.extract()
    for tag in root.find_all(_DROP_TAGS):
        tag.decompose()
    for tag in list(root.find_all(True)):
        if tag.parent is None:  # already removed along with an ancestor
            continue
        ident = " ".join([*(tag.get("class") or []), tag.get("id") or "", tag.get("role") or ""])
        if ident.strip() and _JUNK_RE.search(ident) and tag.name not in ("body", "article", "main"):
            tag.decompose()
    for img in root.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or ""
        sizes = [int(img[k]) for k in ("width", "height") if str(img.get(k, "")).isdigit()]
        if not src or src.startswith("data:") or _TRACKER_RE.search(src) or (sizes and min(sizes) <= 2):
            img.decompose()
        else:
            img.attrs = {"src": urljoin(base_url, src), "alt": img.get("alt", "")}
    for a in root.find_all("a"):
        href = a.get("href", "")
        if not href or href.startswith(("javascript:", "#")):
            a.unwrap()
        else:
            a.attrs = {"href": urljoin(base_url, href)}
    for tag in root.find_all(["p", "div", "li"]):
        if tag.parent is not None and _is_boilerplate(tag):
            tag.decompose()
    for _ in range(4):  # removing an empty child can empty its parent
        for tag in root.find_all(True):
            if tag.parent is None or tag.name in _KEEP_EMPTY:
                continue
            if not tag.get_text(strip=True) and not tag.find(list(_KEEP_EMPTY)):
                tag.decompose()
    if root.find("h1"):  # the page template already shows the post title as the h1
        for level in range(5, 0, -1):
            for h in root.find_all(f"h{level}"):
                h.name = f"h{level + 1}"
    return "".join(str(c) for c in root.children)


class _Converter(MarkdownConverter):
    def convert_pre(self, el, text, parent_tags=None, **kwargs):
        code = el.find("code")
        lang = ""
        for cls in ((code.get("class") if code else None) or el.get("class") or []):
            m = re.match(r"(?:language|lang)-(\w+)", cls)
            if m:
                lang = m.group(1)
        body = (code or el).get_text().strip("\n")
        return f"\n\n```{lang}\n{body}\n```\n\n"


def html_to_markdown(markup):
    md = _Converter(heading_style="ATX", bullets="-", strip=["script", "style"]).convert(markup or "")
    md = re.sub(r"[ \t]+\n", "\n", md.replace("\xa0", " "))
    return re.sub(r"\n{3,}", "\n\n", md).strip()


def drop_leading_title(md, title):
    """Remove a first line that only repeats the post title (the page prints the title itself)."""
    lines = md.split("\n")
    first = re.sub(r"^#+\s*", "", lines[0]).strip().lower().rstrip(".…")
    t = (title or "").strip().lower().rstrip(".…")
    if first and t and (first == t or (len(first) > 20 and t.startswith(first))
                        or (len(t) > 20 and first.startswith(t))):
        return "\n".join(lines[1:]).strip()
    return md


def drop_leading_image(md, image):
    """Remove the first image if it is the banner image the page template already shows."""
    if not image:
        return md
    m = re.match(r"\s*(?:\[\s*)?!\[[^\]]*\]\(([^)\s]+)[^)]*\)(?:\]\([^)]*\))?\s*", md)
    if m and _image_key(m.group(1)) == _image_key(image):
        return md[m.end():].strip()
    return md


def _image_key(url):
    """The image file name without query string, extension or a -800x450 size suffix."""
    name = url.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
    return re.sub(r"[-_]\d+x\d+$", "", name.rsplit(".", 1)[0]).lower()


# ---------------------------------------------------------------------------- sources

def text_len(markup):
    return len(BeautifulSoup(markup or "", "lxml").get_text(" ", strip=True))


def feed_html(entry):
    """The richest HTML the feed itself offers for an item (longest of content/summary)."""
    candidates = [c.get("value", "") for c in (entry.get("content") or [])]
    candidates.append(entry.get("summary", "") or "")
    return max(candidates, key=text_len, default="")


def choose_mode(feed_cfg, entry):
    """'feed' (convert the feed's HTML) or 'fetch' (download the page), from the feed's config."""
    mode = feed_cfg.get("mode", "auto")
    if mode in ("feed", "fetch"):
        return mode
    return "feed" if text_len(feed_html(entry)) >= feed_cfg.get("min_chars", 600) else "fetch"


def extract_page(page_html, url, selector=None):
    """Main content of an article page -> (html, metadata dict). Raises ValueError if nothing usable."""
    meta = {"image": None, "author": None}
    try:
        import trafilatura
        md = trafilatura.extract_metadata(page_html)
        if md:
            meta = {"image": md.image or None, "author": md.author or None}
    except Exception:
        pass
    if selector:
        node = BeautifulSoup(page_html, "lxml").select_one(selector)
        if node is None or not node.get_text(strip=True):
            raise ValueError(f"selector {selector!r} matched nothing")
        return str(node), meta
    content = None
    try:
        import trafilatura
        content = trafilatura.extract(page_html, url=url, output_format="html", include_images=True,
                                      include_links=True, include_formatting=True, include_tables=True,
                                      favor_recall=True)
    except Exception:
        content = None
    if not content or text_len(content) < 200:  # trafilatura found little: try readability
        try:
            from readability import Document
            alt = Document(page_html).summary(html_partial=True)
            if text_len(alt) > text_len(content or ""):
                content = alt
        except Exception:
            pass
    if not content or not text_len(content):
        raise ValueError("no article content found")
    return content, meta
