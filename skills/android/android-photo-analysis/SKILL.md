---
name: android-photo-analysis
description: Analyze photos on Samsung Fold 7 using EXIF extraction, batch processing, and AI vision analysis
triggers:
  - analyze photo
  - photo analysis
  - exif data
  - image metadata
  - photo info
---

# Android Photo Analysis (Samsung Fold 7)

Analyze photos stored on the Samsung Fold 7 — extract EXIF data, batch process, and use AI vision for description.

## Prerequisites

```bash
pkg install python pillow exiftool
pip install Pillow
```

## EXIF Extraction

```bash
# Single photo EXIF
exiftool /storage/emulated/0/DCIM/Camera/IMG_20260418_120000.jpg

# Quick summary
exiftool -s -DateTimeOriginal -Make -Model -ExposureTime -FNumber -ISO -FocalLength photo.jpg

# Samsung Fold 7 specific: detects which camera sensor was used
exiftool -Model -LensModel -FocalLengthIn35mmFormat photo.jpg
```

## Batch Photo Operations

```bash
# List all photos sorted by date
ls -lt /storage/emulated/0/DCIM/Camera/ | head -30

# Find photos from specific date
find /storage/emulated/0/DCIM/Camera/ -name "IMG_20260418*.jpg"

# Count photos by month
ls /storage/emulated/0/DCIM/Camera/ | cut -c5-10 | sort | uniq -c

# Disk usage of camera folder
du -sh /storage/emulated/0/DCIM/Camera/
du -sh /storage/emulated/0/Pictures/Screenshots/
```

## Python EXIF Reader

```python
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif(image_path):
    img = Image.open(image_path)
    exif = img._getexif()
    if exif:
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            print(f"{tag}: {value}")
    return exif
```

## AI Vision Analysis

Use the `vision_analyze` tool to get AI descriptions of photos:

```
# Provide the local file path to vision_analyze
vision_analyze(
    image_url="/storage/emulated/0/DCIM/Camera/photo.jpg",
    question="Describe this photo in detail"
)
```

## Photo Organization Script

```bash
# Organize photos by date into folders
for f in /storage/emulated/0/DCIM/Camera/IMG_*.jpg; do
    date=$(exiftool -DateTimeOriginal -d "%Y-%m-%d" "$f" | cut -d: -f2 | tr -d ' ')
    mkdir -p "/storage/emulated/0/DCIM/Sorted/$date"
    mv "$f" "/storage/emulated/0/DCIM/Sorted/$date/"
done
```

## Pitfalls

- `termux-media-scan` needed after moving files so gallery updates
- Samsung Fold 7 stores 50MP photos — these are very large files
- HEIF format (.heic) may need `pip install pyheif` or conversion
- Screenshots go to `/storage/emulated/0/Pictures/Screenshots/`
- Screen recordings go to `/storage/emulated/0/Screen recordings/`