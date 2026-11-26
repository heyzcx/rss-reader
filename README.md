# rss-reader

Fetch an RSS or Atom feed and list its latest entries — a zero-dependency Python CLI.

## Install

No dependencies, Python 3.8+:

```bash
git clone https://github.com/heyzcx/rss-reader.git
cd rss-reader
```

## Usage

```bash
python3 rss_reader.py <FEED_URL> [--limit N] [--show-desc]
```

| Option | Default | Meaning |
| --- | --- | --- |
| `FEED_URL` | — | Feed URL, or a local XML file path |
| `--limit N` | `10` | How many entries to show |
| `--show-desc` | off | Also print each entry's description |

## Examples

```bash
# Latest Hacker News front page entries
python3 rss_reader.py https://hnrss.org/frontpage --limit 5

# Try it offline with the bundled sample feed
python3 rss_reader.py sample-feed.xml --show-desc
```

## Notes

- Supports RSS 2.0 and Atom, including Atom links stored in `href` attributes.
- A bad URL, network error, or unparsable feed exits with code 2 and a clear message.
- `sample-feed.xml` is a tiny local feed for testing without network access.
