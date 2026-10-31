---
name: adb-wifi-connect
description: "Connect an Android device over WiFi for ADB control."
version: 1.0.0
author: Hermes Agent community
license: MIT
metadata:
  hermes:
    tags: [android, adb, wifi, tcp, connect, phone-control]
    related_skills: [android-phone-control]
---

# ADB Over WiFi Connect

## When to Use

Connect an Android device to a host over WiFi so ADB can drive it — the phone is not in `adb devices`, you need `adb connect <ip>`, or a mobile Hermes instance must reach the phone. This is the connectivity step that precedes android-phone-control (which assumes the device is already reachable). Skip it if the device already appears in `adb devices -l`.

## Purpose

Use this when an Android device (typically running a terminal app in a container that cannot reach the host's adb daemon) must be brought online for ADB control over WiFi — e.g. to drive the phone from another machine, or to let a mobile Hermes instance connect to the phone. It covers discovering the device's LAN IP, enabling TCP adb, running `adb connect`, and verifying the device is listed.

Connectivity is a prerequisite: this skill does not replace the device-control skill (android-phone-control), which assumes the device is already reachable.

## Procedure

1. **Discover the device LAN IP.**
   ```bash
   ip route get 1.1.1.1 | awk '{print $7; exit}'
   ```
   Returns the egress/LAN address. If empty, fall back to `hostname -I | awk '{print $1}'`.

2. **Enable TCP adb on the device.** A containerized adb client cannot see the host's adbd, so tcp mode must be turned on at the host level, not inside the container. From a shell that runs on the host:
   ```bash
   setprop service.adb.tcp.port 5555
   start adbd
   ```
   If `setprop`/`start` are not on PATH, use their full paths under `/system/bin` (or the build's equivalent). From inside the container this step usually fails — that is the expected blocker, not a config error.

3. **Run the connect command on the machine running Hermes.**
   ```bash
   adb connect <LAN-IP>:5555
   ```
   Use the generator to print it (see `scripts/connect-hermes.sh`):
   ```bash
   bash scripts/connect-hermes.sh        # human-readable
   bash scripts/connect-hermes.sh --cmd  # just the command
   ```

4. **Verify the connection.**
   ```bash
   adb devices -l
   ```
   It must list `<LAN-IP>:5555 device`. If it shows `unauthorized`, unlock the phone and accept the adb prompt.

5. **Hand the command to a scanning user (if needed).** Prefer a copy-paste command or a large, scannable QR over a live server — see pitfalls.

## Pitfalls

- **The connect IP changes with WiFi.** The command embeds the current LAN IP, which changes whenever the network changes. Re-run the generator (`scripts/connect-hermes.sh`) rather than editing a saved command — it reprints the current IP and writes it to `~/.hermes/adb-connect.sh`.
- **The container's adb client cannot see the host adbd.** `adb devices` returns empty even when adb is listening, because the terminal app runs in a container/proot that cannot reach the host's daemon. The fix is TCP adb mode on the host (`setprop` + `start adbd`), not reconnecting from the container.
- **`adb connect` needs adb actually listening on the host.** It only succeeds once `adbd` is listening on TCP 5555 on the device; connecting before that yields nothing.
- **A live QR page is flaky for a one-time command.** An HTTP server serving the QR dies between tool calls (its `serve_forever()` blocks and the process is killed), so the page may be unreachable when the user tries to scan it. Deliver the command as a static QR file or as copy-paste text instead.
- **Small QRs are rejected by scanners.** A QR rendered small (e.g. 330px) or with low error correction reports "invalid format" on scan. Encode with `ERROR_CORRECT_H`, a large `box_size` (~20), and a wide border — or skip the QR and give the command directly.
- **Scanners reject plain-text commands with spaces/colons.** `adb connect 10.57.109.243:5555` is not a URL/phone/contact, so many scanner apps report "invalid format." Copy-paste the command, or encode it as a `tcp://`-style URL the scanner accepts.

## Verification Checklist

- [ ] Device LAN IP was discovered (not hardcoded).
- [ ] TCP adb mode was enabled on the host before connecting.
- [ ] `adb connect <LAN-IP>:5555` was run on the Hermes host.
- [ ] `adb devices -l` lists `<LAN-IP>:5555 device`.
- [ ] If a QR was used, it is large with high error correction, or the command was copy-pasted.
