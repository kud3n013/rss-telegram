"""feeds.yml: loading, and comment-preserving add/remove for the Telegram commands."""

from pathlib import Path

from ruamel.yaml import YAML

MODES = ("auto", "feed", "fetch")
CLIENTS = ("plain", "impersonate")


def _yaml():
    y = YAML()
    y.preserve_quotes = True
    y.width = 200
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def _load(path):
    path = Path(path)
    y = _yaml()
    data = y.load(path.read_text(encoding="utf-8")) if path.exists() else None
    if not isinstance(data, dict):
        data = y.load("feeds: []\n")
    if not isinstance(data.get("feeds"), list):
        data["feeds"] = []
    return y, data


def _save(y, data, path):
    with Path(path).open("w", encoding="utf-8", newline="\n") as fh:
        y.dump(data, fh)


def _entry(raw):
    """Normalise one feeds.yml item; raises ValueError for a bad one."""
    if not isinstance(raw, dict) or not raw.get("url"):
        raise ValueError(f"feed entry without a url: {raw!r}")
    mode = str(raw.get("mode") or "auto").lower()
    client = str(raw.get("client") or "plain").lower()
    if mode not in MODES:
        raise ValueError(f"{raw['url']}: mode must be one of {MODES}, not {mode!r}")
    if client not in CLIENTS:
        raise ValueError(f"{raw['url']}: client must be one of {CLIENTS}, not {client!r}")
    flt = raw.get("filter") or {}
    words = flt.get("title_contains") or []
    if isinstance(words, str):
        words = [words]
    min_chars = raw.get("min_chars")
    remove = raw.get("remove") or []
    if isinstance(remove, str):
        remove = [remove]
    return {
        "subtitle_selector": str(raw["subtitle_selector"]).strip() if raw.get("subtitle_selector") else None,
        "remove": [str(r).strip() for r in remove if str(r).strip()],
        "url": str(raw["url"]).strip(),
        "label": str(raw.get("name") or "").strip(),
        "mode": mode,
        "client": client,
        "selector": (str(raw["selector"]).strip() or None) if raw.get("selector") else None,
        "title_contains": [str(w).lower() for w in words if str(w).strip()],
        "min_chars": 600 if min_chars is None else int(min_chars),
    }


def load_feeds(path):
    """All feeds as dicts (url, label, mode, client, selector, title_contains, min_chars).

    A malformed entry is skipped with a warning on stderr rather than breaking the run.
    """
    import sys
    out = []
    for raw in _load(path)[1]["feeds"]:
        try:
            out.append(_entry(raw))
        except (ValueError, TypeError) as exc:
            print(f"WARNING: ignoring feeds.yml entry: {exc}", file=sys.stderr)
    return out


def add_feed(path, url, name=""):
    y, data = _load(path)
    item = {"url": url}
    if name:
        item["name"] = name
    data["feeds"].append(item)
    _save(y, data, path)


def remove_feed(path, url):
    y, data = _load(path)
    feeds = data["feeds"]
    for i in range(len(feeds) - 1, -1, -1):  # delete in place so ruamel keeps the other comments
        if isinstance(feeds[i], dict) and feeds[i].get("url") == url:
            del feeds[i]
    _save(y, data, path)
