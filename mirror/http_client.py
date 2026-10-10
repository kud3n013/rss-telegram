"""HTTP for feeds and article pages: polite, retrying, and graceful when a site blocks us."""

import time
from dataclasses import dataclass, field
from urllib.parse import urlsplit

import requests

USER_AGENT = "rss-telegram-mirror/1.0 (+personal reading mirror; https://github.com/kud3n013/rss-telegram)"
BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Upgrade-Insecure-Requests": "1",
}
_BLOCK_MARKERS = (b"cf-chl", b"just a moment", b"attention required", b"challenge-platform")


class FetchError(Exception):
    """A fetch that failed for good. `blocked` is True for Cloudflare-style refusals."""

    def __init__(self, message, blocked=False):
        super().__init__(message)
        self.blocked = blocked


@dataclass
class Response:
    status: int
    content: bytes
    headers: dict = field(default_factory=dict)
    url: str = ""

    @property
    def text(self):
        return self.content.decode("utf-8", errors="replace")


def _looks_blocked(status, body):
    if status in (401, 403, 429, 503):
        return True
    head = body[:4000].lower()
    return status == 200 and any(m in head for m in _BLOCK_MARKERS) and b"<html" in head


class Fetcher:
    """GET with a per-domain delay, retries with backoff, and optional Chrome impersonation."""

    def __init__(self, delay=2.0, retries=3, backoff=2.0, timeout=30, sleep=time.sleep, clock=time.monotonic):
        self.delay, self.retries, self.backoff, self.timeout = delay, retries, backoff, timeout
        self._sleep, self._clock = sleep, clock
        self._last = {}  # domain -> time of the last request

    def _wait_turn(self, url):
        domain = urlsplit(url).netloc.lower()
        gap = self._clock() - self._last.get(domain, -1e9)
        if gap < self.delay:
            self._sleep(self.delay - gap)
        self._last[domain] = self._clock()

    def _once(self, url, client, headers):
        if client == "impersonate":
            from curl_cffi import requests as cffi  # imported lazily: only protected sites need it
            resp = cffi.get(url, impersonate="chrome", headers=headers, timeout=self.timeout)
        else:
            resp = requests.get(url, headers=headers, timeout=self.timeout)
        return Response(resp.status_code, resp.content, dict(resp.headers), str(resp.url))

    def get(self, url, client="plain", conditional=None, page=False):
        """Return a Response (200, or 304 when `conditional` etag/last-modified matched).

        Raises FetchError after the retries are used up; `.blocked` marks a bot-protection refusal.
        """
        headers = {"User-Agent": USER_AGENT}
        if client == "impersonate":
            headers = dict(BROWSER_HEADERS)  # curl_cffi supplies the matching browser User-Agent
        elif page:
            headers.update(BROWSER_HEADERS)
        else:
            headers["Accept"] = "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"
        for key, hdr in (("etag", "If-None-Match"), ("last_modified", "If-Modified-Since")):
            if conditional and conditional.get(key):
                headers[hdr] = conditional[key]
        last_error, blocked = "unknown error", False
        for attempt in range(self.retries):
            if attempt:
                self._sleep(self.backoff ** attempt)
            self._wait_turn(url)
            try:
                resp = self._once(url, client, headers)
            except Exception as exc:  # network errors, TLS errors, curl_cffi errors
                last_error, blocked = f"{type(exc).__name__}: {exc}", False
                continue
            if resp.status == 304:
                return resp
            if _looks_blocked(resp.status, resp.content):
                last_error, blocked = f"HTTP {resp.status} (looks like bot protection)", True
                continue
            if resp.status >= 500:
                last_error, blocked = f"HTTP {resp.status}", False
                continue
            if resp.status >= 400:
                raise FetchError(f"HTTP {resp.status}")  # 404 etc.: retrying won't help
            return resp
        raise FetchError(last_error, blocked=blocked)
