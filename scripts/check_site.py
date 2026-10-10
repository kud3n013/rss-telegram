#!/usr/bin/env python3
"""Fail (exit 1) if the built site could be indexed.

Checks every generated HTML page for the noindex robots meta tag, that robots.txt exists and
disallows everything, and that no sitemap or RSS/Atom feed was generated.
Usage: python scripts/check_site.py [public-dir]
"""

import re
import sys
from pathlib import Path

# attribute quotes are optional so a minified page would still match
NOINDEX = re.compile(r"""<meta\s+[^>]*name=["']?robots["']?[^>]*content=["']?[^"'>]*\bnoindex\b""", re.I)


def check(public):
    public = Path(public)
    problems = []
    pages = sorted(public.rglob("*.html"))
    if not pages:
        problems.append("no HTML pages found: was the site built?")
    for page in pages:
        if not NOINDEX.search(page.read_text(encoding="utf-8", errors="replace")):
            problems.append(f"missing noindex meta tag: {page.relative_to(public)}")
    robots = public / "robots.txt"
    if not robots.exists():
        problems.append("robots.txt is missing")
    else:
        lines = [ln.split("#")[0].strip().lower() for ln in robots.read_text(encoding="utf-8").splitlines()]
        if "user-agent: *" not in lines or "disallow: /" not in lines:
            problems.append("robots.txt must contain 'User-agent: *' and 'Disallow: /'")
        if any(ln.startswith("allow:") and ln != "allow:" for ln in lines):
            problems.append("robots.txt must not contain Allow rules")
    for name in ("sitemap.xml", "sitemap_index.xml"):
        if (public / name).exists():
            problems.append(f"{name} must not be generated")
    for feed in list(public.rglob("index.xml")) + list(public.rglob("*.rss")) + list(public.rglob("*.atom")):
        problems.append(f"feed output must not be generated: {feed.relative_to(public)}")
    return problems


def main(argv):
    public = argv[1] if len(argv) > 1 else "public"
    problems = check(public)
    for p in problems:
        print(f"FAIL {p}", file=sys.stderr)
    if problems:
        return 1
    print(f"OK: every page in {public} is noindex, robots.txt disallows all")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
