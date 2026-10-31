---
name: android-rooting
description: Root Pixel and Android devices from Termux with Magisk.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [android, pixel, termux, magisk, root, fastboot, adb, bootloader]
  related_skills: [apk-install-termux]
---

# Android Rooting Skill

## Overview

Establishes root on a Pixel / Android device by patching the boot image with
Magisk and flashing it via fastboot. Runs the orchestration from a Termux
Android sandbox (which already ships `adb`), but uses a laptop over USB where
fastboot is reliable. Covers device identification, locating and downloading the
matching factory image, and patching/flash — not the OS-level root setup.

## When to Use

- User wants root on a Pixel or Android phone and asks you to find the firmware,
  tools, or Magisk, or to walk the root flow.
- User has already enabled OEM Unlocking / USB debugging and needs the download
  + command steps.
- You need the correct factory-image URL for a specific build number.

## Prerequisites

- The device must be in Developer Options with **OEM unlocking** (and, for the
  USB method, **USB debugging**) enabled. Confirm `getprop ro.boot.verifiedbootstate`
  and `getprop service.adb.root` before starting.
- A laptop with the extracted `platform-tools` (adb + fastboot) for the USB path,
  or working wireless debugging for the phone-only path.
- Free storage on the device (factory images are ~3 GB; keep the extracted
  `boot.img`/`init_boot.img` + Magisk APK handy).

## Procedure

1. **Identify the device** — read `getprop` for model, codename, build, and
   boot state:
   `getprop | grep -iE 'ro.product.model|ro.product.codename|ro.build.version.release|ro.boot.verifiedbootstate|service.adb.root'`
   Log the exact build fingerprint (e.g. `google/bluejay/bluejay:16/CP1A.260405.005/...`).
2. **Locate the matching factory image** — go to
   `https://developers.google.com/android/images` and find the row for the
   device + matching build. If the page is JS-rendered and empty, fall back to
   the Pixel Factory Images Telegram tracker (see references) and confirm the
   exact factory hash.
3. **Download the factory image** — pull it from the official
   `https://dl.google.com/dl/android/aosp/<codename>-<build>-factory-<hash>.zip`.
   It is ~3 GB; run it in the background (`terminal background=true`) so it does
   not hit the foreground timeout.
4. **Extract and inspect** — `unzip` the factory zip, then `unzip` the nested
   `image-<codename>-<build>.zip`. List the `.img` files. **Check whether the
   build ships `boot.img` or only `init_boot.img`** before patching (Android 16
   Pixel builds often ship only `init_boot.img`).
5. **Patch with Magisk** — download the latest Magisk APK from the official
   GitHub releases (`https://github.com/topjohnwu/Magisk/releases/latest`),
   install it on the phone, open Magisk → **Create patched boot image**, and
   select the extracted `boot.img` (or `init_boot.img`).
6. **Flash** — reboot to bootloader (`fastboot flashing unlock` if the bootloader
   is still locked — this wipes the device), then flash the patched image:
   `fastboot flash boot <patched>.img` (or `fastboot flash init_boot <patched>.img`).
   Then `fastboot reboot`.

## Pitfalls

- **Wrong image file breaks the flash.** On Android 16 Pixel builds only
  `init_boot.img` may exist; flashing the nonexistent `boot.img` fails. Always
  list the extracted `.img` files first and flash what is present.
- **The factory image is huge (~3 GB).** Foreground downloads hit the 600 s tool
  timeout; use `background=true` and poll the process.
- **adb/fastboot binaries are host arch, not device arch.** The bundled
  `platform-tools` adb/fastboot are x86_64 (laptop) and will not run on the ARM
  phone; the phone's own system `adb` is what runs on-device. Use the laptop
  binaries for the USB fastboot path.
- **Locked bootloader wipes the device.** `fastboot flashing unlock` erases all
  data; confirm OEM Unlocking is enabled first.
- **Google's factory-image pages are JS-rendered.** `web_extract` on
  `developers.google.com/android/images` often returns only prose with no links;
  resolve the exact URL via the tracker in references, then verify with a HEAD
  probe before downloading.

## Verification

- The downloaded factory zip extracts to `image-<codename>-<build>.zip`, which
  extracts to a `.img` set; confirm the patch target file (`boot.img` or
  `init_boot.img`) is present.
- After `fastboot reboot`, confirm root: open Magisk and it shows **Installed**,
  or run a root checker / `adb shell su -c id`.

## References

- `references/factory-image-urls.md` — exact factory-image URL formats, the
  proven working `dl.google.com/dl/android/aosp/` form, the 404 forms to avoid,
  the Telegram tracker, platform-tools and Magisk download sources, and the
  JS-rendering limitation of Google's pages.
