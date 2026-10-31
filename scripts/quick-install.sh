#!/data/data/com.termux/files/usr/bin/bash
# Quick install - minimal version for sharing with friends
# Assumes Termux is fresh, installs only what's needed to run Hermes

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="$HOME"

echo "=== Hermes Termux Quick Install ==="
echo "Repo: $REPO_DIR"
echo ""

# 1. Install base packages
echo "[1/6] Installing base packages..."
pkg update -y && pkg install -y git python rust termux-services termux-api

# 2. Install Python deps (pre-built wheels where possible)
echo "[2/6] Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install aiohttp yarl multidict frozenlist propcache aiosignal attrs aiohappyeyeballs
pip install psutil==5.9.8
pip install mcp rpds

# 3. Install Hermes from source with termux constraints
echo "[3/6] Installing Hermes..."
cd "$HOME_DIR"
if [ ! -d "hermes-agent" ]; then
  git clone https://github.com/NousResearch/hermes-agent.git
fi
cd hermes-agent
pip install -e '.[termux-all]' -c constraints-termux.txt

# 4. Deploy custom skills/plugins/config
echo "[4/6] Deploying custom skills, plugins, config..."
mkdir -p "$HOME_DIR/.hermes/skills"
mkdir -p "$HOME_DIR/.hermes/plugins"
mkdir -p "$HOME_DIR/.hermes/memories"

cp -r "$REPO_DIR/skills/"* "$HOME_DIR/.hermes/skills/"
cp -r "$REPO_DIR/plugins/"* "$HOME_DIR/.hermes/plugins/"
cp "$REPO_DIR/config/config.yaml" "$HOME_DIR/.hermes/config.yaml"
cp "$REPO_DIR/memory/MEMORY.md" "$HOME_DIR/.hermes/memories/"

# 5. Deploy and enable services
echo "[5/6] Setting up runit services..."
mkdir -p "$HOME_DIR/.services"
cp -r "$REPO_DIR/services/"* "$HOME_DIR/.services/"

# Link services to runit
for svc in ollama searxng redis hermes-webui maigret-web hermes-dashboard homeassistant; do
  ln -sf "$HOME_DIR/.services/$svc" "/data/data/com.termux/files/usr/var/service/$svc" 2>/dev/null || true
done

# 6. Start services
echo "[6/6] Starting services..."
sv up ollama searxng redis hermes-webui maigret-web hermes-dashboard homeassistant 2>/dev/null || true

echo ""
echo "=== Quick Install Complete ==="
echo ""
echo "NEXT STEPS (required):"
echo "1. Add your API keys to ~/.hermes/.env:"
echo "   HERMES_NVIDIA_API_KEY=your_nvidia_nim_key"
echo "   HERMES_CUSTOM_FDSTRATA_ENDEVOPS_NET_API_KEY=your_key"
echo "   HERMES_CUSTOM_UNSLOTH_ENDEVOPS_NET_API_KEY=your_key"
echo "   API_SERVER_KEY=$(openssl rand -hex 24 2>/dev/null || cat /dev/urandom | tr -dc 'a-f0-9' | head -c 48)"
echo ""
echo "2. Start Hermes:"
echo "   hermes dashboard --host 0.0.0.0 --port 9119 --no-open --skip-build  # Dashboard"
echo "   hermes  # CLI"
echo ""
echo "3. Access points:"
echo "   Dashboard: http://localhost:9119 (admin / bb0caf8f19)"
echo "   WebUI:     http://localhost:8787"
echo "   API:       http://localhost:8642"
echo "   Ollama:    http://localhost:11434"
echo "   SearXNG:   http://localhost:8888"
echo "   Maigret:   http://localhost:5001"
echo "   Home Asst: http://localhost:8123"
echo ""
echo "4. For auto-start on boot, run:"
echo "   cp $REPO_DIR/scripts/boot-services.sh ~/.termux/boot/"
echo "   chmod +x ~/.termux/boot/boot-services.sh"
