# Hermes Termux Distro

A complete working Hermes Agent setup for **unrooted Android phones** via Termux.

## Before You Start (Prerequisites)

**On the target phone (Termux):**
1. Install Termux from **F-Droid** (NOT Play Store)
2. Open Termux, run: `termux-wake-lock`
3. Have a **NVIDIA NIM key** (free tier): https://build.nvidia.com/explore/discover

**Minimum API keys needed:**
- `HERMES_NVIDIA_API_KEY` — vision + model inference (free at NVIDIA NIM)
- `API_SERVER_KEY` — any 48-char hex (`openssl rand -hex 24`)

## Install

```bash
# Clone this repo
git clone https://github.com/eo-nwanze/hermes-termux-distro.git
cd hermes-termux-distro

# Run installer
./scripts/quick-install.sh

# Set up API keys
cp config/.env.example ~/.hermes/.env
nano ~/.hermes/.env  # Fill in YOUR keys
```

## After Install

**Start Hermes:**
```bash
hermes          # CLI
hermes dashboard  # Dashboard (or sv restart hermes-dashboard)
```

**Access points (on the phone):**
| Service | URL | Auth |
|---------|-----|------|
| **Dashboard** | http://localhost:9119 | admin / CHANGE_ME (set in config.yaml) |
| **WebUI** | http://localhost:8787 | - |
| **Ollama** | http://localhost:11434 | - |
| **SearXNG** | http://localhost:8888 | - |
| **Maigret** | http://localhost:5001 | - |
| **Home Assistant** | http://localhost:8123 | - |

**From another device on same WiFi:** replace `localhost` with the phone's IP (`ifconfig` or `ip a`).

## What Gets Installed

- 7 runit services (ollama, searxng, redis, hermes-webui, maigret-web, hermes-dashboard, homeassistant)
- 50+ custom Termux/Android skills
- `agent-reach` social media research plugin
- Dashboard auth + basic LLM provider config
- Full working `hermes` CLI

## Skills Included

| Category | Skills |
|----------|--------|
| Android | `android` (calls/SMS/camera), `adb-wifi-connect`, `apk-install`, `mobile`, `android-rooting` |
| Web scraping | `scrapling-official` (patched for Termux), `domain`, `feeds` |
| Browser | `agent-browser`, `browser-act`, `browser` |
| Creative | `diagramming` (Mermaid), `gifs`, `creative` (comics, pixel art) |
| Cybersec | `maigret` (username OSINT), `godmode`, `cybersec-workstation` |
| Development | `mermaid-syntax`, `loop-breaker`, `first-principles`, `5-Whys` |
| Productivity | `find-nearby`, `local-memory`, `memory-search` |
| Social media | `agent-reach` (YouTube, Reddit, X, Instagram, Bilibili, etc.) |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Dashboard blank page | Build `web_dist` on x86 PC, copy to phone |
| `os.link` AttributeError | Use `pip install` (not git checkout) path |
| Rust crate SIGKILL | Already handled — `constraints-termux.txt` uses pre-built wheels |
| Skills not loading | Ensure `platforms: [linux, android]` in skill frontmatter |
| `psutil` fails | Pinned to `5.9.8` (last Android-compatible) |
| `faster-whisper` no wheel | `ctranslate2` has no `aarch64-linux-android` build — skip STT |
| Loopback auth broken | Dashboard binds `0.0.0.0`, not `127.0.0.1` |

## Auto-Start on Boot

```bash
cp scripts/boot-services.sh ~/.termux/boot/
chmod +x ~/.termux/boot/boot-services.sh
# Reboot phone — all services auto-start
```

## Building Dashboard `web_dist` (if blank)

The Vite/Rolldown build SIGILLs on ARM. Build on x86 Linux, copy to phone:

```bash
# On x86 PC
cd hermes-agent
npm ci && npm run build:web
scp hermes_cli/web_dist/* user@phone:~/.hermes/hermes-agent/hermes_cli/web_dist/
```

## License

MIT. Based on [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) (Apache-2.0). Custom skills retain original licenses.
