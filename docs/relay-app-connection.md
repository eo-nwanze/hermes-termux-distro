# Hermes Android Relay App — Connection Guide

The **Hermes Relay App** connects a phone Hermes agent to your hosted Hermes backend via a relay gateway. The phone app acts as a **client** to your gateway, receiving responses over an outbound WebSocket — no inbound ports needed on the phone.

## How It Works

```
┌────────────────────────┐       HTTPS/WS        ┌────────────────────────┐
│  Hermes Android Relay  │ ◄──────────────────► │  Your Hermes Gateway   │
│  App (phone)           │   Outbound-only       │  (Mac/Windows/Server)  │
└────────────────────────┘                        └────────────────────────┘
```

- **Phone** → connects to your gateway's dashboard API over WiFi or relay
- **Gateway** → responds via WebSocket, no inbound port on phone needed

## Step 1: Start the Gateway on Desktop

On your Mac/Windows host:

```bash
# Start gateway with relay enabled
export GATEWAY_RELAY_URL="wss://relay.nousresearch.com/relay"
export GATEWAY_RELAY_ID="gw-your-unique-id"
export GATEWAY_RELAY_SECRET="<generate a base64 secret>"
export API_SERVER_KEY="your-48-hex-key"

hermes gateway run
```

## Step 2: Enroll for Relay (one-time)

```bash
hermes gateway enroll \
  --relay-url wss://relay.nousresearch.com/relay \
  --platform telegram \
  --endpoint https://your-server.example.com
```

This writes `GATEWAY_RELAY_ID` and `GATEWAY_RELAY_SECRET` to `~/.hermes/.env`.

## Step 3: Install Hermes Relay App on Phone

1. Install **Hermes Relay App** from F-Droid:
   - https://f-droid.org/packages/com.nousresearch.hermes_relay/
2. Open the app → enter your gateway info:
   - Gateway URL: `wss://relay.nousresearch.com/relay`
   - Gateway ID: `gw-your-unique-id`
   - Secret: your base64 secret

## Step 4: Connect to Local Dashboard (Loopback)

If the gateway runs on the same phone:
```bash
# App connects to local dashboard on loopback
http://127.0.0.1:9119
```

If the gateway runs on a **different machine** on the same WiFi:
```bash
# Get phone IP
ifconfig  # or ip a on phone

# Set dashboard bind to 0.0.0.0 for LAN access
hermes dashboard --host 0.0.0.0 --port 9119 --no-open --skip-build
```

Then on the phone app, enter: `http://YOUR_MAC_IP:9119`

## Step 5: API Server (Phone → Gateway Communication)

Ensure `API_SERVER_KEY` is set in `~/.hermes/.env` on the gateway:
```bash
API_SERVER_KEY=your_48_char_hex_key  # openssl rand -hex 24
```

Phone app connects to `http://YOUR_HOST_IP:8642` for API calls.

## Quick Connection Test

```bash
# From phone Termux, test connectivity to your desktop gateway:
curl http://YOUR_DESKTOP_IP:8642/health
# Should return: {"ok": true, ...}

# Dashboard test:
curl http://YOUR_DESKTOP_IP:9119/api/auth/me
# Should return: {"detail": "Unauthorized"} (auth gate active)
```

## Relay Config Reference

```yaml
gateway:
  relay_url: "wss://relay.nousresearch.com/relay"
  relay_id: "gw-your-id"
  relay_secret: "your-base64-secret"
  relay_endpoint: "https://your-server.example.com"
  relay_platforms: "telegram"
  api_server:
    enabled: true
    host: 0.0.0.0
    port: 8642
```

## Self-Hosted Relay (No Nous Portal)

If you don't want to use `relay.nousresearch.com`, run your own connector:

```bash
# Clone connector
git clone https://github.com/NousResearch/gateway-gateway.git
cd gateway-gateway
pip install -e .

# Start relay server
python relay_server.py \
  --port 8080 \
  --secret "your-shared-secret" \
  --platforms discord,telegram
```

Then set `GATEWAY_RELAY_URL="ws://your-server:8080/relay"`.

## Android-Specific Notes

- **Loopback (127.0.0.1) is NOT a trust boundary** on Android — any app with network permission can access it
- Dashboard must bind `0.0.0.0` for LAN access (not `127.0.0.1`)
- `termux-wake-lock` keeps services alive in background
- Battery optimization may kill background processes — disable for Termux in Android settings
