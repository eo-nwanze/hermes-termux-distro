---
name: android-browser
description: Control the Android browser on Samsung Fold 7 from Termux — open URLs, search, share pages, clear cache using am intents
triggers:
  - open browser
  - browse url
  - open website
  - web search
  - chrome
  - samsung internet
---

# Android Browser Control (Samsung Fold 7)

Control the Android browser from Termux using `am` intents. Optimized for Samsung Fold 7's foldable display.

## Prerequisites

- Termux with `am` command (available by default)
- No Termux:API needed for basic browser intents

## Commands

### Open a URL

```bash
# Open in default browser
am start -a android.intent.action.VIEW -d "https://example.com"

# Open in Chrome specifically
am start -a android.intent.action.VIEW -d "https://example.com" -n com.android.chrome/com.android.chrome.Main

# Open in Samsung Internet
am start -a android.intent.action.VIEW -d "https://example.com" -n com.sec.android.app.sbrowser/.MainActivity
```

### Web Search

```bash
# Search using default browser
am start -a android.intent.action.WEB_SEARCH --es query "search terms"

# Search via Chrome
am start -a android.intent.action.VIEW -d "https://www.google.com/search?q=search+terms" -n com.android.chrome/com.android.chrome.Main
```

### Share a URL

```bash
am start -a android.intent.action.SEND --es android.intent.extra.TEXT "https://example.com" -t text/plain
```

### Open Bookmarks

```bash
# Chrome bookmarks
am start -n com.android.chrome/com.android.chrome.Main --ez bookmarks true
```

### Clear Browser Cache

```bash
# Clear Chrome cache (requires root or `pm clear` which also clears data)
pm clear com.android.chrome  # WARNING: removes all Chrome data
```

### Fold 7 Specific Tips

- When **unfolded**, the browser uses the wide inner screen layout
- When **folded**, it uses the cover screen (narrow viewport)
- Use DeX mode for desktop-like browsing: `settings put global force_desktop_mode 1`
- Split screen browsing with two tabs side-by-side works great unfolded

## Advanced Browser Automation

For full browser automation (crawling, archiving, CDP control), use the **autobrowser** skill:
- Provides Chrome DevTools Protocol (CDP) access via ADB forwarding
- High-fidelity web crawling with behavior execution
- Control via `autobrowserctl` CLI

> Full browser skill ecosystem, non-interactive install patterns, and Bionic/glibc compatibility notes: `references/browser-automation.md`

Quick setup:
```bash
# Enable USB Debugging, then:
adb tcpip 5555 && adb connect localhost:5555
adb forward tcp:9222 localabstract:chrome_devtools_remote
autobrowserctl tabs    # list Chrome tabs
autobrowserctl crawl https://example.com --setup
```

## Pitfalls

- `am start` with `-n` (component) can break if the browser package name changes
- Samsung Internet package is `com.sec.android.app.sbrowser`
- Chrome package is `com.android.chrome`
- Some intents require the browser to already be running
- On Fold 7, cover screen browsing is limited — unfold for best experience
- Android Chrome does not support `--remote-debugging-port` via intent; use ADB forwarding instead