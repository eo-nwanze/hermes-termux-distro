---
name: android-camera
description: Control the Samsung Fold 7 camera from Termux — launch camera, trigger capture, access photos via intents and Termux:API
triggers:
  - take photo
  - camera
  - take picture
  - record video
  - open camera
---

# Android Camera Control (Samsung Fold 7)

Launch and control the Samsung Fold 7 camera from Termux. Includes Flex mode support for foldable-optimized camera UI.

## Prerequisites

- Termux with `am` command
- Termux:API app for some features (`pkg install termux-api`)

## Commands

### Launch Camera

```bash
# Open still camera
am start -a android.media.action.STILL_IMAGE_CAMERA

# Open video camera
am start -a android.media.action.VIDEO_CAMERA

# Open camera in specific mode (Samsung)
am start -n com.sec.android.app.camera/.Camera --es mode "PHOTO"
am start -n com.sec.android.app.camera/.Camera --es mode "VIDEO"
am start -n com.sec.android.app.camera/.Camera --es mode "PORTRAIT"
am start -n com.sec.android.app.camera/.Camera --es mode "PRO"
```

### Capture via Intent

```bash
# Request a photo capture (launches camera for user to confirm)
am start -a android.media.action.IMAGE_CAPTURE

# Request video capture
am start -a android.media.action.VIDEO_CAPTURE
```

### Access Recent Photos

```bash
# Open gallery
am start -a android.intent.action.VIEW -t image/*

# Open specific photo
am start -a android.intent.action.VIEW -d file:///storage/emulated/0/DCIM/Camera/photo.jpg -t image/jpeg

# Scan new photos into gallery
termux-media-scan /storage/emulated/0/DCIM/Camera/
```

### Photo Storage Paths on Samsung Fold 7

```
Camera photos:  /storage/emulated/0/DCIM/Camera/
Screenshots:    /storage/emulated/0/Pictures/Screenshots/
Screen recordings: /storage/emulated/0/Screen recordings/
```

### Flex Mode (Fold 7 Specific)

```bash
# Check fold state (requires root or Samsung SDK)
# Unfolded = main inner display, camera uses full screen
# Folded = cover display, camera adapts to narrow view

# Samsung Flex Mode — camera UI splits between screens when half-folded
# Camera preview on bottom half, controls on top half
# This happens automatically when device is half-folded
```

### Batch Photo Operations

```bash
# List recent photos
ls -lt /storage/emulated/0/DCIM/Camera/ | head -20

# Count photos
ls /storage/emulated/0/DCIM/Camera/*.jpg 2>/dev/null | wc -l

# Get photo info (requires exiftool)
exiftool /storage/emulated/0/DCIM/Camera/photo.jpg
```

## Pitfalls

- Camera intents open the app but don't auto-capture without user interaction
- Samsung camera package: `com.sec.android.app.camera`
- Fold 7 has multiple cameras: wide, ultrawide, telephoto + inner selfie + cover selfie
- Cover screen selfie camera activates when phone is folded
- `termux-media-scan` is essential for gallery to see new files
- Storage permissions: `termux-setup-storage` must be run first