#!/usr/bin/env python3
"""rss-reader: fetch an RSS or Atom feed and list its latest entries.

Zero-dependency Python CLI (urllib + xml.etree only). Usage:
    python3 rss_reader.py <FEED_URL> [--limit N] [--show-desc]
Examples:
    python3 rss_reader.py https://example.com/feed.xml
    python3 rss_reader.py https://hnrss.org/frontpage --limit 5
    python3 rss_reader.py sample-feed.xml --show-desc
"""
import argparse
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET


def fetch(url, timeout=15):
    """Download a feed; accepts http(s) URLs and local file paths."""
    if "://" not in url:
        with open(url, "rb") as f:
            return f.read()
    req = urllib.request.Request(url, headers={"User-Agent": "rss-reader/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def strip_ns(tag):
    return tag.rsplit("}", 1)[-1]


def entry_text(item, *names):
    for name in names:
        el = next((c for c in item if strip_ns(c.tag) == name), None)
        if el is not None and el.text:
            return el.text.strip()
    return ""


def parse(data):
    """Parse RSS 2.0 or Atom XML into (feed_title, [entries])."""
    root = ET.fromstring(data)
    kind = strip_ns(root.tag)
    entries = []
    if kind == "rss":
        channel = next(c for c in root if strip_ns(c.tag) == "channel")
        title = entry_text(channel, "title")
        items = [c for c in channel if strip_ns(c.tag) == "item"]
    elif kind == "feed":  # Atom
        title = entry_text(root, "title")
        items = [c for c in root if strip_ns(c.tag) == "entry"]
    else:
        raise ValueError(f"unsupported feed format: {kind!r}")
    for item in items:
        link = entry_text(item, "link")
        if not link:  # Atom links live in href attributes
            link_el = next((c for c in item if strip_ns(c.tag) == "link"), None)
            if link_el is not None:
                link = link_el.get("href", "")
        entries.append({
            "title": entry_text(item, "title") or "(no title)",
            "link": link,
            "date": entry_text(item, "pubDate", "published", "updated"),
            "desc": entry_text(item, "description", "summary"),
        })
    return title, entries


def main(argv=None):
    parser = argparse.ArgumentParser(description="List the latest entries of an RSS or Atom feed.")
    parser.add_argument("feed", help="feed URL or local XML file path")
    parser.add_argument("--limit", type=int, default=10, help="how many entries to show (default: 10)")
    parser.add_argument("--show-desc", action="store_true", help="also print each entry's description")
    args = parser.parse_args(argv)

    try:
        data = fetch(args.feed)
    except (OSError, urllib.error.URLError) as exc:
        print(f"error: cannot fetch feed: {exc}", file=sys.stderr)
        return 2
    try:
        title, entries = parse(data)
    except (ET.ParseError, ValueError) as exc:
        print(f"error: cannot parse feed: {exc}", file=sys.stderr)
        return 2

    print(f"{title or args.feed}  ({len(entries)} entries)")
    for i, entry in enumerate(entries[: args.limit], 1):
        line = f"{i}. {entry['title']}"
        if entry["date"]:
            line += f"  [{entry['date']}]"
        print(line)
        if entry["link"]:
            print(f"   {entry['link']}")
        if args.show_desc and entry["desc"]:
            print(f"   {entry['desc'][:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
