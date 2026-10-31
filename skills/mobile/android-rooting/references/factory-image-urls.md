# Factory-Image & Tool Download Sources

Condensed from a working root session on a **Pixel 6a (`bluejay`)**, build
`CP1A.260405.005` (Android 16). These are the exact forms that resolve; the 404
forms are the ones that do not.

## Google's official pages (often JS-rendered)

- Factory images (list): `https://developers.google.com/android/images`
- Full OTA images: `https://developers.google.com/android/ota`
- Android 16 download hub: `https://developer.android.com/about/versions/16/download`

`web_extract` on these frequently returns only prose with no working download
links, because the pages render their device lists client-side. Do not rely on
the extractor to give you the URL — use it for the prose, then resolve the exact
URL via the tracker below.

## Exact factory-image download URL (verified working)

```
https://dl.google.com/dl/android/aosp/<codename>-<build>-factory-<hash>.zip
```

Examples confirmed during this session:

- `bluejay-cp1a.260405.005-factory-1267628c.zip` → **200 OK**, 3.28 GB (this is
  the Pixel 6a build matching Android 16 `CP1A.260405.005`).

Forms that returned **404** (do not use):

- `https://dl.google.com/android/repository/image/bluejay_beta-cp1a.260405.005-factory-015d7e2d.zip`
- `https://dl.google.com/android/repository/image/bluejay_beta-cp1a.260405.005.b1-factory-015d7e2d.zip`
- `https://dl.google.com/developers/android/bluejay/images/factory/bluejay_beta-cp1a.260405.005-factory-015d7e2d.zip`

Note the factory zip is ~3 GB and is slow (~9 MB/s typical). Run it in the
**background** (`terminal background=true`) so it survives past the foreground
timeout, then poll the process.

## The reliable discovery source: Pixel Factory Images tracker

The Telegram channel **Pixel Factory Images Tracker** posts each build's exact
download link as soon as it is detected. Its public post list page parses cleanly
where Google's pages do not:

```
https://t.me/s/pixelfactoryimagestracker?before=<last_seen_post_id>
```

Fetch that page and grep for `<codename>-<build>-factory-<hash>.zip`. This is how
the working `bluejay-cp1a.260405.005-factory-1267628c.zip` URL was found.

## Platform tools (adb + fastboot)

Official standalone archive (x86_64 — for the laptop, not the phone):

```
https://dl.google.com/android/repository/platform-tools-latest-linux.zip
```

(also `-darwin.zip` and `-windows.zip`). Extract into a working folder; keep
`adb` and `fastboot` from there for the USB flash path.

## Magisk (root patcher)

Download the latest APK from the official GitHub releases:

```
https://github.com/topjohnwu/Magisk/releases/latest
```

The asset name is `Magisk-v<version>.apk` (e.g. `Magisk-v30.7.apk`). Install it on
the phone and use **Create patched boot image**.

## Boot image caveat for Android 16 Pixel builds

Many Android 16 Pixel factory images ship **only `init_boot.img`**, not
`boot.img`. Always list the extracted `.img` files before patching, and flash the
partition that actually exists:

- present `boot.img` → `fastboot flash boot <patched>.img`
- present `init_boot.img` → `fastboot flash init_boot <patched>.img`

This session's `bluejay` `CP1A.260405.005` build ships `boot.img` (64 MB) and no
`init_boot.img`.
