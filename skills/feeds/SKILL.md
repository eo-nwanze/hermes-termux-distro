---
name: feeds
description: RSS/Atom feed management and monitoring on Termux/Android. Subscribe to blogs, podcasts, YouTube channels, and news sources. Aggregate and filter content from the terminal.
tags: [rss, atom, feeds, news, podcasts, termux, monitoring]
version: 1.0.0
---

# Feed Management on Termux/Android

## Overview
Read, manage, and monitor RSS/Atom feeds from Termux. Covers feed readers, YouTube RSS, podcast feeds, and custom aggregation pipelines.

## Feed Reader Installation

### Newsboat (CLI Feed Reader)
```bash
pkg install newsboat

# Create config
mkdir -p ~/.config/newsboat
cat > ~/.config/newsboat/config << 'EOF'
auto-reload yes
reload-time 30
browser "termux-open-url"
save-path ~/feeds/saved/
text-width 80
show-read-feeds no
show-read-articles no
article-sort-order date-asc
EOF

# Add feeds
mkdir -p ~/.config/newsboat
cat > ~/.config/newsboat/urls << 'EOF'
https://news.ycombinator.com/rss "Tech" "HN"
https://www.reddit.com/r/termux/.rss "Tech" "Reddit Termux"
https://www.reddit.com/r/android/.rss "Tech" "Reddit Android"
https://lwn.net/headlines/rss "Tech" "LWN"
https://feeds.feedburner.com/TheHackersNews "Security" "THN"
EOF
```

### Using Newsboat
```bash
# Start reading
newsboat

# Reload all feeds
newsboat -x reload

# Export articles
newsboat -e > opml-export.xml

# Import OPML
newsboat -i subscriptions.opml
```

### Miniflux (Self-Hosted)
```bash
# Install with Go
pkg install golang
go install github.com/miniflux/miniflux@latest

# Or use Docker if available
# Access via http://localhost:8080
```

## YouTube Channel Feeds

### Get YouTube RSS Feed URL
```bash
# From channel ID
# https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID

# From channel URL, extract channel ID
channel_url="https://www.youtube.com/@example"
# Use the YouTube channel page source
# Search for "channelId" in page source
```

### YouTube Feed Processing
```python
import feedparser

def get_latest_videos(channel_id, max_videos=5):
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    
    videos = []
    for entry in feed.entries[:max_videos]:
        videos.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "video_id": entry.yt_videoid,
        })
    return videos
```

## Podcast Feed Management

### Download Podcasts
```bash
# Install podfox (podcast client)
pip install podfox

# Configure
cat > ~/.podfox.cfg << 'EOF'
{
  "podcast_dir": "~/podcasts",
  "max_episodes": 5,
  "download_count": 3
}
EOF

# Import feed
podfox import https://feeds.example.com/podcast.rss

# Download new episodes
podfox update
podfox download NEW
```

### Play Podcasts
```bash
# Install mpv or ffplay
pkg install mpv

# Play latest episode
mpv ~/podcasts/show_name/latest_episode.mp3
```

## Feed Aggregation with Python

### Custom Feed Aggregator
```python
import feedparser
import json
from datetime import datetime

def aggregate_feeds(feed_urls, keyword_filter=None):
    """Aggregate multiple feeds and optionally filter by keyword."""
    all_entries = []
    
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            published = entry.get("published", "")
            
            if keyword_filter:
                text = f"{title} {summary}".lower()
                if keyword_filter.lower() not in text:
                    continue
            
            all_entries.append({
                "feed": feed.feed.get("title", "Unknown"),
                "title": title,
                "link": link,
                "summary": summary[:500],
                "published": published,
            })
    
    # Sort by date (newest first)
    all_entries.sort(key=lambda x: x.get("published", ""), reverse=True)
    return all_entries

# Example
feeds = [
    "https://news.ycombinator.com/rss",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.reddit.com/r/termux/.rss",
]

results = aggregate_feeds(feeds, keyword_filter="android")
for r in results[:20]:
    print(f"[{r['feed']}] {r['title']}")
    print(f"  {r['link']}")
```

### OPML Processing
```python
import xml.etree.ElementTree as ET

def parse_opml(opml_file):
    """Extract feed URLs from OPML export."""
    tree = ET.parse(opml_file)
    root = tree.getroot()
    
    feeds = []
    for outline in root.iter("outline"):
        xml_url = outline.get("xmlUrl")
        if xml_url:
            feeds.append({
                "title": outline.get("title", ""),
                "url": xml_url,
                "category": outline.get("category", ""),
            })
    return feeds
```

## Feed Monitoring Pipeline

### Continuous Feed Watcher
```bash
cat > ~/bin/feed-watch.sh << 'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
# Feed watcher with Termux notifications
FEEDS_FILE="$HOME/.config/newsboat/urls"
SEEN_FILE="$HOME/.config/feed-watch-seen.txt"
touch "$SEEN_FILE"

python3 << 'PYEOF'
import feedparser, json, os, subprocess

feeds_file = os.environ.get("FEEDS_FILE", os.path.expanduser("~/.config/newsboat/urls"))
seen_file = os.environ.get("SEEN_FILE", os.path.expanduser("~/.config/feed-watch-seen.txt"))

with open(seen_file) as f:
    seen = set(line.strip() for line in f)

with open(feeds_file) as f:
    for line in f:
        url = line.split()[0] if line.strip() else ""
        if not url or not url.startswith("http"):
            continue
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            entry_id = entry.get("id", entry.get("link", ""))
            if entry_id not in seen:
                title = entry.get("title", "New post")
                feed_title = feed.feed.get("title", "Feed")
                subprocess.run([
                    "termux-notification",
                    "--title", feed_title,
                    "--content", title
                ])
                with open(seen_file, "a") as sf:
                    sf.write(entry_id + "\n")
PYEOF
SCRIPT
chmod +x ~/bin/feed-watch.sh
```

### Schedule with Termux:Job
```bash
# Run feed watcher every 30 minutes
termux-job-scheduler --schedule \
  --script ~/bin/feed-watch.sh \
  --period-ms 1800000 \
  --network-true
```

## Common Feed URLs
```bash
# Hacker News
https://news.ycombinator.com/rss

# Reddit (any subreddit)
https://www.reddit.com/r/SUBREDDIT/.rss

# GitHub releases (any repo)
https://github.com/OWNER/REPO/releases.atom

# ArXiv (any category)
https://arxiv.org/rss/cs.AI

# LWN.net
https://lwn.net/headlines/rss
```

## Pitfalls
- Feedparser needs installation: `pip install feedparser`
- Some sites do not publish RSS — use RSS bridge services (rss-bridge)
- YouTube RSS feeds only show the last 15 videos
- Newsboat config must have both `config` and `urls` files
- Termux may kill background processes — use `termux-wake-lock` for long operations
- OPML imports may contain dead feeds — validate periodically