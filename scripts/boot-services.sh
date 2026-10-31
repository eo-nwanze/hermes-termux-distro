#!/data/data/com.termux/files/usr/bin/bash
# Termux boot script - auto-starts all Hermes services on device boot
# Place in ~/.termux/boot/boot-services.sh and chmod +x

# Acquire wake lock to keep CPU alive for background services
termux-wake-lock

# Wait for filesystem to be ready
sleep 3

# Start runit services in dependency order
sv up redis
sleep 1
sv up ollama
sv up searxng
sv up hermes-webui
sv up maigret-web
sv up hermes-dashboard
sv up homeassistant

# Optional: Start Hermes gateway if not running via dashboard
# hermes gateway run --daemon &

echo "[$(date)] Hermes Termux services started" >> ~/.hermes/boot.log
