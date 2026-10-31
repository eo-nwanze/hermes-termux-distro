# Hermes Cross-Platform Install (Mac / Windows / Linux)

Hermes runs natively on any Python platform. Use these steps to self-run in a folder:

## Prerequisites

| OS | What to install |
|----|-----------------|
| **Mac** | Python 3.11+, git, `brew install ollama` (optional) |
| **Windows** | Python 3.11+, git, [WSL recommended](https://learn.microsoft.com/en-us/windows/wsl/install) |
| **Linux** | Python 3.11+, git, `pip` |

## Step 1: Clone and install

```bash
# In any folder (e.g. ~/projects/hermes)
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
python -m venv .venv

# Activate venv
# Mac/Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -e '.[all]' -c constraints-termux.txt  # Use base constraints on non-Termux
```

## Step 2: Configure

```bash
# Create ~/.hermes/ directory
mkdir -p ~/.hermes/memories

# Copy config and memory
cp /path/to/hermes-termux-distro/config/config.yaml ~/.hermes/
cp /path/to/hermes-termux-distro/memory/MEMORY.md ~/.hermes/memories/
cp /path/to/hermes-termux-distro/config/.env.example ~/.hermes/.env
nano ~/.hermes/.env   # Fill in your API keys
```

## Step 3: Run

```bash
# Dashboard
hermes dashboard --host 0.0.0.0 --port 9119 --no-open --skip-build

# CLI
hermes

# Gateway (for relay connection)
hermes gateway run
```

## Optional Services

```bash
# Ollama (Mac: brew install ollama && ollama serve)
ollama serve

# SearXNG
pip install searxng && python -m searx.webapp

# Redis
redis-server
```

## Dashboard Web Build

If dashboard shows blank on ARM/Mac, build `web_dist` first:
```bash
npm ci && npm run build:web
# Then: hermes dashboard --skip-build
```

## Folder Structure

```
~/projects/hermes/
├── hermes-agent/         # Core Hermes source (pip install -e)
├── ~/.hermes/
│   ├── config.yaml       # Your config
│   ├── .env              # API keys
│   ├── memories/
│   │   └── MEMORY.md
│   └── skills/           # Custom skills (copy from repo)
├── ~/.services/          # Service run scripts (optional, Termux-only)
└── .venv/                # Python virtual env
```
