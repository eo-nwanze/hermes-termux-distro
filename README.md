# Hermes Termux Distro

A complete, working Hermes Agent setup for **unrooted Android phones** via Termux.

This distro packages a known-working configuration including:
- ✅ All services pre-configured (Ollama, SearXNG, Redis, Hermes WebUI, Maigret, Home Assistant, Hermes Dashboard)
- ✅ 50+ Termux/Android-specific skills (ADB, Android control, Scrapling, gstack tools, etc.)
- ✅ Custom plugins (agent-reach for social media)
- ✅ Patched for Termux/bionic compatibility (os.link fallback, android platform support)
- ✅ Pre-configured NVIDIA vision, custom LLM providers
- ✅ Dashboard with auth (admin / bb0caf8f19)
- ✅ Auto-start via runit services

## Quick Install (on target phone)

```bash
# In Termux on the target phone
pkg install -y git
git clone https://github.com/YOUR_USERNAME/hermes-termux-distro.git
cd hermes-termux-distro
./scripts/quick-install.sh
```

## What Gets Installed

| Component | Port | Purpose |
|-----------|------|---------|
| Ollama | 11434 | Local LLM inference |
| SearXNG | 8888 | Private search engine |
| Redis | 6379 | Caching/sessions |
| Hermes WebUI | 8787 | Web chat interface |
| Maigret Web | 5001 | Username reconnaissance |
| Home Assistant | 8123 | Smart home control |
| Hermes Dashboard | 9119 | Admin dashboard (admin/bb0caf8f19) |
| Hermes API Server | 8642 | REST API (needs API_SERVER_KEY) |

## Required API Keys

Edit `~/.hermes/.env` or `~/.hermes/config.yaml` with your keys:

```bash
# NVIDIA NIM (for vision models)
HERMES_NVIDIA_API_KEY=your_key

# Custom providers (Fdstrata, Strata, Unsloth)
HERMES_CUSTOM_FDSTRATA_ENDEVOPS_NET_API_KEY=your_key
HERMES_CUSTOM_UNSLOTH_ENDEVOPS_NET_API_KEY=your_key

# Dashboard API server
API_SERVER_KEY=your_48_char_hex_key
```

## Auto-Start on Boot

Add to `~/.bashrc` or `~/.profile`:

```bash
# Keep CPU awake for background services
termux-wake-lock

# Start all services
sv up ollama searxng redis hermes-webui maigret-web hermes-dashboard homeassistant
```

Or use the provided boot script:
```bash
cp scripts/boot-services.sh ~/.termux/boot/
chmod +x ~/.termux/boot/boot-services.sh
```

## Skills Included

### Android/Termux Specific
- `android` - Full phone control (calls, SMS, contacts, camera, browser)
- `adb-wifi-connect` - ADB over WiFi
- `apk-install-termux` - Install APKs from Termux
- `scrapling-official` - Web scraping (patched for Termux)
- `mobile` - Mobile device utilities

### gstack Tools
- `gstack-*` - Context save/restore, freeze/unfreeze, guard, health, retro, etc.

### Research & OSINT
- `osint-startme` - Start.me OSINT pages
- `domain` - Domain reconnaissance
- `reverse-engineer-anything` - Binary analysis
- `cybersec` - Security workstation, Maigret

### Creative & Media
- `creative` - Comics, diagrams, pixel art, image generation
- `gifs` - GIF creation/editing
- `media` - YouTube transcripts, Spotify, music generation

### Development
- `software-development` - Subagent-driven dev, debugging, planning
- `github`, `github-fetch` - GitHub integration
- `mcp` - MCP server/client tools

## Architecture

```
~/.hermes/
├── config.yaml          # Main config (sanitized in this repo)
├── .env                 # API keys (NOT in repo - add your own)
├── memories/
│   └── MEMORY.md        # Persistent memory (environment facts)
├── skills/              # 50+ custom skills
├── plugins/
│   └── agent-reach/     # Social media research plugin
└── ...

~/.services/             # Runit service definitions
├── ollama/
├── searxng/
├── redis/
├── hermes-webui/
├── maigret-web/
├── hermes-dashboard/
└── homeassistant/
```

## Building the Dashboard (web_dist)

The Vite/Rolldown build fails on Android (SIGILL). Build on x86 Linux:

```bash
# On x86 Linux host
cd hermes-agent
npm ci
npm run build:web  # Outputs to hermes_cli/web_dist/
# Copy web_dist to phone: ~/.hermes/hermes-agent/hermes_cli/web_dist/
```

Then on phone run:
```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open --skip-build
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `os.link` AttributeError | Already patched in this distro's Hermes fork |
| Skills not loading | Skills declare `platforms: [linux]` - this distro adds `android` |
| Dashboard build SIGILL | Use `--skip-build` with pre-built `web_dist` |
| Rust crates compile & SIGKILL | This distro uses pre-built wheels via `constraints-termux.txt` |
| `psutil` install fails | Pinned to 5.9.8 (last Android-compatible) |
| API server not starting | Set `API_SERVER_KEY` in `.env` (48+ hex chars) |
| Loopback auth broken | Dashboard runs on `0.0.0.0` not `127.0.0.1` |

## Upstream Issues This Distro Works Around

- [Termux is currently broken](https://hermes-agent.nousresearch.com/docs/getting-started/termux) (official docs)
- [os.link missing on bionic](https://github.com/NousResearch/hermes-agent/issues/140080)
- [Rust compilation SIGKILL](https://github.com/NousResearch/hermes-agent/issues/123860)
- [Dashboard build SIGILL](https://github.com/NousResearch/hermes-agent/issues/140004)
- [Skills filtered by sys.platform](https://github.com/NousResearch/hermes-agent/issues/139415)

## License

MIT - Based on NousResearch/hermes-agent (Apache-2.0)
Custom skills/plugins retain their original licenses.
