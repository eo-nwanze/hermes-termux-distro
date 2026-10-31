---
name: apk-install-termux
description: "Install an APK from a Termux Android sandbox."
version: 1.0.0
category: devops
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [termux, apk, android, pm-install, sandbox, selinux]
    related_skills: [computer-use, systematic-debugging]
---

# Install APK from a Termux sandbox

## When to use
The user asks to download or install an Android app (APK) from within a Termux / Android terminal session, especially a sandboxed Termux instance (this device: `u0_a288`, Termux home `/data/data/com.termux/files/home`).

## Core reality (read first)
Termux runs as a **regular sandboxed app, not root** (SELinux `u:r:untrusted_app`). `pm install` from inside the sandbox fails with an SELinux permission error unless the agent has root or ADB privileges. This is a **stable environment constraint, not a transient failure** — diagnose it early instead of looping on download retries.

## Diagnose installability before trying to install
Run, in order:
1. `id` — check the SELinux context. `u:r:untrusted_app` with a `u0_a` uid (e.g. `u0_a288`) = sandboxed, non-root → `pm install` will fail.
2. `pm install -g <file.apk>` — if it errors with `Unknown class fileSystem server has no access to read file context ... /data/data/.../untrusted_app`, that confirms the sandbox blocks `pm install`. Note the error even suggests the file must live under a readable path like `/data/local/tmp/`.
3. `su -c whoami` (if `su` exists) — if it reports "No su program found" or non-root, there is no escalation path from inside Termux.

If step 1 already shows `untrusted_app`, **skip install attempts from inside Termux** and go straight to the working alternatives below.

## Downloads: watch for bot-detection, not a network failure
APK sites (APKPure, APKMirror, etc.) sit behind **Cloudflare JavaScript challenges**. `curl`/`web_extract` typically returns a challenge HTML page (`<title>Just a moment... Enable JavaScript and cookies</title>`) instead of the APK. Signature: HTTP 403, or an HTML body where a binary was expected. This is a **download** obstacle — distinct from the **install** problem. Use a browser user-agent or a working mirror; don't diagnose it as "no internet."

## Working install alternatives (verified)
1. **Manual install (works from the sandbox):** Download the APK to a user-writable path like `~/cashapp.apk`, hand it to the user to open and tap Install. Requires the "install unknown apps" permission on the user's side.
2. **ADB (reliable, needs a computer):** `adb install <file>` over USB debugging. Prep the file at a shared/known location for the user to pull.
3. **Root:** If the device is rooted, `pm install -g <file>` works directly from Termux.

## Pitfalls
- Do NOT write up the failed download attempts (APKPure/Cloudflare, `pm install` SELinux errors) as a "reliable install workflow." Frame this skill as **diagnose + escalate**, not "install works from here."
- `pm install` needs the `fileSystem` SELinux permission (FILE_ADMIN) — only ADB or root grants it. Inherent to Termux-as-sandbox; not fixable from inside.
- Prefer a user-writable path (`~` / `$HOME`) over `/tmp` — `/tmp` and `/data/local/tmp` are frequently not writable from the sandbox.

## Session transcript
- `references/session-2026-09-29.md` — full environment + error transcript from the original Cash App install attempt (reproduction recipe).
