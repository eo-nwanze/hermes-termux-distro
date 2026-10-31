---
name: home-assistant
description: Install, configure, and control Home Assistant Core on Termux/Samsung Fold 7 — service management, API control, and Termux-specific workarounds
triggers:
  - home assistant
  - hass
  - smart home
  - ha dashboard
  - home automation
  - ha-cli
---

# Home Assistant Core on Termux (Samsung Fold 7)

Run Home Assistant Core (pip install) on Termux with runit auto-start and REST API control.

## Installation

### Step 1: Install HA and Dependencies

**CRITICAL: `uv` package (Rust/maturin) CANNOT compile on Termux.** Create a dummy package first:

```bash
# Create dummy uv package
mkdir -p ~/workspace/dummy-uv/uv
cat > ~/workspace/dummy-uv/uv/__init__.py << 'EOF'
"""Dummy uv package for Termux — satisfies Home Assistant dependency."""
__version__ = "0.9.26"
EOF

cat > ~/workspace/dummy-uv/uv/__main__.py << 'EOF'
"""Stub uv CLI — does nothing on Termux."""
import sys
print("uv: stub implementation on Termux (not functional)")
sys.exit(1)
EOF

cat > ~/workspace/dummy-uv/pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "uv"
version = "0.9.26"
description = "Dummy uv package for Termux/Home Assistant compatibility"
requires-python = ">=3.8"

[tool.setuptools.packages.find]
where = ["."]
include = ["uv*"]
EOF

# Install dummy uv FIRST
pip install ~/workspace/dummy-uv/

# Now install Home Assistant
pip install homeassistant
```

### Step 2: Pre-install Critical Dependencies

HA's internal pip installer uses `uv` (broken), so use `--skip-pip` and pre-install core deps:

```bash
pip install hassil home-assistant-intents mutagen ha-ffmpeg pyotp pyqrcode home-assistant-frontend
```

### Step 3: Create Minimal Configuration

**DO NOT use `default_config:`** — it pulls in too many deps (bluetooth, dhcp, ssdp, stream, etc.) that fail on Termux.

```yaml
# ~/.homeassistant/configuration.yaml
homeassistant:
  name: Home
  latitude: 0
  longitude: 0
  elevation: 0
  unit_system: metric
  time_zone: UTC

frontend:
http:
  server_port: 8123
api:
websocket_api:
system_health:
logger:
  default: warning
lovelace:
  mode: storage
```

### Step 4: Create Runit Service

```bash
mkdir -p ~/.services/homeassistant/log

cat > ~/.services/homeassistant/run << 'EOF'
#!/data/data/com.termux/files/usr/bin/sh
# Home Assistant service — skip-pip (uv broken), ignore-os-check (Android)
exec hass --config ~/.homeassistant --skip-pip --ignore-os-check 2>&1
EOF

cat > ~/.services/homeassistant/log/run << 'EOF'
#!/data/data/com.termux/files/usr/bin/sh
export LOGDIR=${LOGDIR:-/data/data/com.termux/files/usr/var/log}
mkdir -p "$LOGDIR/sv/homeassistant"
exec svlogd -tt "$LOGDIR/sv/homeassistant"
EOF

chmod +x ~/.services/homeassistant/run ~/.services/homeassistant/log/run
ln -sf ~/.services/homeassistant $PREFIX/var/service/homeassistant
```

### Step 5: Complete Onboarding via API

```bash
python3 ~/workspace/complete_ha_onboarding.py
# OR use the ha-cli tool:
python3 ~/workspace/ha-cli.py token admin <password>
```

Onboarding creates user account and completes 4 steps: user, core_config, analytics, integration.

## Service Management

```bash
sv start $PREFIX/var/service/homeassistant     # Start
sv stop $PREFIX/var/service/homeassistant      # Stop
sv restart $PREFIX/var/service/homeassistant   # Restart
sv status $PREFIX/var/service/homeassistant    # Check status
```

Logs: `$PREFIX/var/log/sv/homeassistant/current`
Web UI: `http://localhost:8123/`

## HA CLI Tool

Located at `~/workspace/ha-cli.py` — control HA from the terminal:

```bash
# List all entity states
python3 ~/workspace/ha-cli.py states

# Get specific entity state
python3 ~/workspace/ha-cli.py state light.living_room

# Call a service
python3 ~/workspace/ha-cli.py call light toggle '{"entity_id":"light.living_room"}'

# Get HA config
python3 ~/workspace/ha-cli.py config

# List all entity IDs
python3 ~/workspace/ha-cli.py entities

# Refresh access token
python3 ~/workspace/ha-cli.py token admin <password>
```

## REST API Direct Usage

```bash
# Get fresh token (they expire in 30 min)
# See ~/workspace/ha_get_tokens.py for automated refresh

# List states
curl -s http://localhost:8123/api/states \
  -H "Authorization: Bearer <TOKEN>"

# Get specific entity
curl -s http://localhost:8123/api/states/light.living_room \
  -H "Authorization: Bearer <TOKEN>"

# Call service
curl -s -X POST http://localhost:8123/api/services/light/toggle \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"light.living_room"}'

# Get config
curl -s http://localhost:8123/api/config \
  -H "Authorization: Bearer <TOKEN>"
```

## Adding Integrations

To add integrations beyond the minimal config, add them one at a time to `~/.homeassistant/configuration.yaml`. Each integration may require additional pip packages. Install them manually BEFORE restarting HA:

```bash
# Example: adding a sensor integration
pip install <required-package>
# Then add to configuration.yaml and restart
sv restart $PREFIX/var/service/homeassistant
```

## Pitfalls

1. **`uv` package is UNBUILDABLE on Termux** — Rust/maturin compilation fails. MUST use the dummy package workaround. Without it, `pip install homeassistant` fails.

2. **`--skip-pip` is mandatory** — HA's internal package installer calls `uv` to install integration deps. Since our `uv` is a stub, internal pip will fail. Pre-install all needed packages manually.

3. **`--ignore-os-check` is mandatory** — Android (Bionic libc) is not in HA's supported OS list. Without this flag, HA prints "only supports Linux, OSX and Windows WSL" and loops.

4. **`default_config:` causes cascading failures** — It auto-enables bluetooth, cloud, dhcp, ssdp, stream, usb, mobile_app, assist_pipeline, and go2rtc. Most of these fail on Termux. Use a minimal config instead and add integrations individually.

5. **Access tokens expire in 30 minutes** — HA issues short-lived JWT tokens. Use the refresh token flow (saved in `~/.homeassistant/.hermes_credentials.json`) to get fresh tokens. For persistent access, create a long-lived token via HA web UI (Settings > Security > Create Token).

6. **Onboarding must be completed before API is fully functional** — During onboarding, most API endpoints return 401. Complete all 4 onboarding steps (user, core_config, analytics, integration) before using the API.

7. **Missing dependencies cause silent import failures** — If HA fails to start but shows no clear error in the log, check for `ModuleNotFoundError` lines. Each missing module needs `pip install <package>` and a restart.

8. **Flask dev server equivalent** — HA uses aiohttp internally, which is fine for personal/local use. Not for public exposure.

## Credentials

Saved at: `~/.homeassistant/.hermes_credentials.json`
- Default username: `admin`
- Default password: `admin123!` (change via web UI)
- Contains access_token and refresh_token for API access