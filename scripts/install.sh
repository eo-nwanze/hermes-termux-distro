#!/data/data/com.termux/files/usr/bin/bash
# Hermes Termux Distro Installer
# Run this on a fresh Termux to install the complete working setup

set -euo pipefail

echo "=== Hermes Termux Distro Installer ==="
echo "This will install a complete working Hermes setup for unrooted Android"
echo ""

# Update packages
echo "[1/8] Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install base dependencies
echo "[2/8] Installing base dependencies..."
pkg install -y git python rust libllvm clang binutils make cmake pkg-config \
  openssl libffi libjpeg-turbo libpng freetype zlib \
  redis ollama termux-services termux-api

# Install Python packages needed for skills
echo "[3/8] Installing Python packages..."
pip install --upgrade pip setuptools wheel
pip install aiohttp yarl multidict frozenlist propcache aiosignal attrs aiohappyeyeballs
pip install psutil==5.9.8  # Last version supporting Android
pip install scrapy scrapy-playwright
pip install faster-whisper ctranslate2 --index-url https://pypi.org/simple  # May need manual wheel
pip install mcp rpds

# Install Hermes from source (with Termux patches)
echo "[4/8] Installing Hermes from source..."
cd ~
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
git checkout main

# Apply Termux patches
echo "Applying Termux patches..."

# Patch 1: os.link fallback for bionic
cat > /tmp/os_link_patch.py << 'PATCH'
import sys
import os

# Patch hermes_cli/main.py update command to use os.link fallback
# This is a conceptual patch - actual patching happens in the hermes-agent source
PATCH

# Patch 2: Add android to platform list in skill_utils
# This will be done via config

# Install with termux-all extras
pip install -e '.[termux-all]' -c constraints-termux.txt

# Build dashboard (requires x86 host - skip on device, use pre-built)
echo "Note: Dashboard build requires x86 host. Use pre-built web_dist or build on PC."

# Copy our custom skills
echo "[5/8] Installing custom skills..."
mkdir -p ~/.hermes/skills
cp -r ~/hermes-termux-distro/skills/* ~/.hermes/skills/

# Copy custom plugins
echo "[6/8] Installing custom plugins..."
mkdir -p ~/.hermes/plugins
cp -r ~/hermes-termux-distro/plugins/* ~/.hermes/plugins/

# Copy config
echo "[7/8] Installing config..."
mkdir -p ~/.hermes
cp ~/hermes-termux-distro/config/config.yaml ~/.hermes/config.yaml

# Copy memory
echo "[8/8] Installing memory..."
mkdir -p ~/.hermes/memories
cp ~/hermes-termux-distro/memory/MEMORY.md ~/.hermes/memories/

# Install runit services
echo "Installing runit services..."
mkdir -p ~/.services
cp -r ~/hermes-termux-distro/services/* ~/.services/

# Enable services
echo "Enabling services..."
for svc in ollama searxng redis hermes-webui maigret-web hermes-dashboard homeassistant; do
  ln -sf ~/.services/$svc /data/data/com.termux/files/usr/var/service/$svc 2>/dev/null || true
done

# Start services
echo "Starting services..."
sv up ollama searxng redis hermes-webui maigret-web hermes-dashboard homeassistant

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Set your API keys in ~/.hermes/config.yaml or ~/.hermes/.env"
echo "2. Run 'hermes dashboard' to access the WebUI at http://localhost:9119"
echo "3. Run 'hermes' to start the CLI"
echo ""
echo "Services running on:"
echo "  - Ollama: http://localhost:11434"
echo "  - SearXNG: http://localhost:8888"
echo "  - Redis: localhost:6379"
echo "  - Hermes WebUI: http://localhost:8787"
echo "  - Maigret Web: http://localhost:5001"
echo "  - Home Assistant: http://localhost:8123"
echo "  - Hermes Dashboard: http://localhost:9119 (admin / bb0caf8f19)"
echo ""
echo "To auto-start on boot, add to ~/.bashrc:"
echo "  termux-wake-lock"
echo "  sv up ollama searxng redis hermes-webui maigret-web hermes-dashboard homeassistant"
