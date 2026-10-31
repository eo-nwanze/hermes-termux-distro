---
name: maigret
description: Username reconnaissance across 2000+ sites using Maigret — OSINT account discovery and profiling
triggers:
  - username search
  - account search
  - osint username
  - maigret
  - find accounts
  - username recon
---

# Maigret — Username OSINT Reconnaissance

Search 2000+ sites for a username's presence. Generates HTML/PDF reports of account findings.

## Install

```bash
pip install maigret
```

## Basic Usage

```bash
# Search all sites for username
maigret USERNAME

# Search specific sites
maigret USERNAME --site reddit --site github --site twitter

# Generate HTML report
maigret USERNAME --html -p ~/reports/

# Generate PDF report
maigret USERNAME --pdf -p ~/reports/

# Limit to top N sites by rank (faster)
maigret USERNAME --top 100

# Search multiple usernames
maigret user1 user2 user3

# From a file of usernames
maigret -f ~/usernames.txt
```

## Advanced Options

```bash
# Timeout per site (seconds)
maigret USERNAME --timeout 15

# Use cookies for authenticated checks
maigret USERNAME --cookies

# Proxy support
maigret USERNAME --proxy socks5://127.0.0.1:9050

# Tor support (requires tor running)
maigret USERNAME --tor

# Verbose output
maigret USERNAME -v

# Check only sites that definitely exist (filter certainty)
maigret USERNAME --filter-claimed
```

## Samsung Fold 7 Performance Tips

```bash
# On ARM64, limit concurrent connections (8 is safe)
maigret USERNAME -t 8

# Use top 50 sites for quick checks on mobile data
maigret USERNAME --top 50

# Redirect output to file for later review
maigret USERNAME --html -p /storage/emulated/0/reports/
```

## Web UI

Maigret includes a built-in Flask web interface for browser-based username searches.

```bash
# Launch web UI (default port 5000)
maigret --web

# Custom port
maigret --web 5001
```

### Runit Service (auto-start on boot)

Maigret Web UI runs as an sv service on port 5001:

```bash
# Service at ~/.services/maigret-web/
# Symlinked to /data/data/com.termux/files/usr/var/service/maigret-web

sv start /data/data/com.termux/files/usr/var/service/maigret-web
sv stop /data/data/com.termux/files/usr/var/service/maigret-web
sv restart /data/data/com.termux/files/usr/var/service/maigret-web
sv status /data/data/com.termux/files/usr/var/service/maigret-web
```

Access at: `http://localhost:5001/`

**Note:** Uses Flask development server — not production-grade but functional for personal use.

## Termux DNS Fix (CRITICAL)

On Termux/Android, `aiodns` cannot auto-detect DNS servers (no `/etc/resolv.conf`). This causes **all Maigret searches to fail with "Could not contact DNS servers"**. Two patches are required:

### Patch 1: `checking.py` — TCPConnector DNS resolver
File: `$PREFIX/lib/python3.13/site-packages/maigret/checking.py`

Around line 149, change the `TCPConnector` to include explicit DNS nameservers:
```python
# Before (BROKEN on Termux):
connector = (
    ProxyConnector.from_url(self.proxy)
    if self.proxy
    else TCPConnector(ssl=ssl_context)
)

# After (FIXED):
from aiohttp.resolver import AsyncResolver
resolver = AsyncResolver(nameservers=['8.8.8.8', '8.8.4.4', '1.1.1.1'])
connector = (
    ProxyConnector.from_url(self.proxy)
    if self.proxy
    else TCPConnector(ssl=ssl_context, resolver=resolver)
)
```

### Patch 2: `app.py` — Reports directory
File: `$PREFIX/lib/python3.13/site-packages/maigret/web/app.py`

Line 34, change the hardcoded `/tmp` path (not writable on Termux):
```python
# Before (BROKEN on Termux):
app.config["REPORTS_FOLDER"] = os.path.abspath('/tmp/maigret_reports')

# After (FIXED):
app.config["REPORTS_FOLDER"] = os.path.abspath(os.path.join(os.path.expanduser('~'), 'maigret_reports'))
```

**⚠️ These patches are lost on `pip install --upgrade maigret`. Re-apply after upgrades.**

## Pitfalls

- **Termux DNS**: Maigret's `aiodns` can't find DNS servers on Android — must patch `checking.py` with explicit nameservers. See "Termux DNS Fix" above.
- **Termux /tmp**: Web UI hardcodes `/tmp/maigret_reports` which is not writable on Termux — must patch `app.py`. See "Termux DNS Fix" above.
- **Full-scan proxy bug**: When running `maigret -a` (all sites), the code calls `ProxyConnector.from_url(self.proxy)` with an empty string when no proxy is set, raising `ValueError: Invalid scheme component:` and causing massive worker failures. Top-N scans (`--top N`) work because they use a different code path. Workaround: use `--top 100` or `--top 500` instead of `-a` for full database scans.
- Large scans take 10+ minutes — use `--top` for quick checks
- Some sites block Tor/VPN connections or return Cloudflare bot challenges
- Rate limiting may trigger captchas on some sites
- Results show claim probability, not guaranteed accounts
- `pip install maigret` pulls many dependencies
- Flask dev server warning — fine for personal/local use, not for public exposure
- `-n` flag controls parallel connections; use `-n 5` or `-n 10` on mobile to avoid overwhelming the network