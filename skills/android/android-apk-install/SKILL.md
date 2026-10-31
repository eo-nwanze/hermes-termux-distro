---
name: android-apk-install
description: Install Android APK files from Termux on Samsung Fold 7 — download, install, and auto-launch on boot
triggers:
  - install apk
  - install android app
  - sideload apk
  - install app from github
  - apk install
  - auto launch app
---

# Android APK Installation from Termux

Install Android apps (APKs) from Termux command line on Samsung Fold 7. Covers downloading, installing, and setting up auto-launch on boot.

## Step 1: Download the APK

For GitHub releases, find the correct APK for arm64 (`uname -m` returns `aarch64`):

```bash
# List latest release assets to find the right APK
# Use the GitHub API endpoint: https://api.github.com/repos/OWNER/REPO/releases/latest
# Look for: *-android-arm64v8.apk or *-android-arm64.apk
# Download the arm64 variant using curl -L -o FILENAME URL
```

Place APKs in `/storage/emulated/0/Download/` — accessible by the Android content provider.

## Step 2: Find the Package Name

Extract the Android package name from the APK before installing:

```python
import zipfile, re
with zipfile.ZipFile('/storage/emulated/0/Download/AppName.apk') as z:
    data = z.read('AndroidManifest.xml')
    text = data.decode('utf-16le', errors='ignore')
    matches = re.findall(r'(?:com|org|net|io)\.[.\w]+', text)
    print(matches[0])  # e.g., org.localsend.localsend_app
```

Also find the main activity name (usually `MainActivity`).

## Step 3: Install the APK

**Without root, silent install is impossible.** The user MUST tap "Install" on screen.

Open the installer dialog:
```bash
# Simplest method — opens system installer dialog
termux-open /storage/emulated/0/Download/AppName.apk

# Alternative: content URI via am intent
am start -a android.intent.action.VIEW \
  -d "content://com.termux.files/storage/emulated/0/Download/AppName.apk" \
  -t application/vnd.android.package-archive

# Alternative: Google package installer explicitly (Samsung)
am start -a android.intent.action.MAIN \
  -n com.google.android.packageinstaller/com.android.packageinstaller.InstallStart \
  -d "content://com.termux.files/storage/emulated/0/Download/AppName.apk" \
  -t application/vnd.android.package-archive
```

**FAILED METHODS** (don't waste time trying — all blocked by SELinux/permissions):
- `pm install /path/apk` — system_server can't read Termux private storage
- `cmd package install-create` — requires `INTERACT_ACROSS_USERS_FULL`
- `cat apk | cmd package install -S $SIZE` — same permission error
- `cp ~/file.apk /data/local/tmp/` — permission denied
- `pm grant com.termux android.permission.REQUEST_INSTALL_PACKAGES` — needs `GRANT_RUNTIME_PERMISSIONS`

## Step 4: Verify Installation

```bash
pm list packages | grep PACKAGENAME
```

## Step 5: Auto-Launch on Boot

For GUI apps (NOT daemons), add a one-shot launcher to the boot script:

```bash
# Add to ~/.termux/boot/start-services.sh (after the network wait loop)
if pm list packages 2>/dev/null | grep -q "PACKAGENAME"; then
    (sleep 5 && am start -n PACKAGENAME/.MainActivity) &
fi
```

Important:
- Use `(sleep N && am start ...)` with `&` — backgrounded with delay
- The 5s sleep lets the home screen settle after boot
- `pm list packages` check ensures it only launches if installed
- **Do NOT put GUI apps under runit/sv** — they exit immediately and runit respawns endlessly

For actual daemons (servers), use the runit/sv system per the `termux-boot-services` skill.

## Step 6: Launch Immediately

```bash
am start -n PACKAGENAME/.MainActivity
```

## Pitfalls

1. **No silent install without root** — Android requires user confirmation for sideloaded APKs. All programmatic install methods fail from Termux's unprivileged UID.
2. **File URI vs Content URI** — `file:///` URIs may be blocked on API 24+. Use `content://com.termux.files/` prefix or `termux-open`.
3. **arm64 vs arm32** — Samsung Fold 7 uses arm64-v8a. Download the arm64 variant of APKs.
4. **Samsung package installer** — Component is `com.google.android.packageinstaller` (Google) not `com.android.packageinstaller`.
5. **GUI apps are NOT daemons** — Don't add them to runit/sv. Use boot script one-shot launchers instead.
6. **Termux:Boot must match Termux source** — F-Droid Termux needs F-Droid Termux:Boot.