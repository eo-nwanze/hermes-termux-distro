---
name: gifs
description: Create and edit GIFs on Samsung Fold 7 — generate, resize, optimize, and convert animated GIFs from video or images
triggers:
  - create gif
  - make gif
  - convert to gif
  - gif optimization
  - animated gif
  - resize gif
---

# GIF Creation & Editing (Samsung Fold 7)

Create, resize, optimize, and convert animated GIFs from video or images on Termux.

## Install

```bash
pkg install ffmpeg imagemagick
```

## Video to GIF

```bash
# Basic conversion (adjust quality with -filter_complex)
ffmpeg -i input.mp4 -vf "fps=15,scale=480:-1:flags=lanczos" -loop 0 output.gif

# High quality GIF (slower, better palette)
ffmpeg -i input.mp4 -filter_complex "[0:v] fps=15,scale=480:-1:flags=lanczos,split [a][b];[a] palettegen [p];[b][p] paletteuse" output.gif

# Specific time range
ffmpeg -ss 00:00:05 -to 00:00:10 -i input.mp4 -vf "fps=15,scale=480:-1" output.gif

# From screen recording
ffmpeg -i /storage/emulated/0/Screen\ recordings/recording.mp4 -vf "fps=10,scale=640:-1" -loop 0 output.gif
```

## Images to GIF

```bash
# Combine images into animated GIF
convert -delay 50 -loop 0 frame*.png output.gif

# With specific ordering
convert -delay 100 -loop 0 frame01.png frame02.png frame03.png output.gif

# Resize images during GIF creation
convert -delay 50 -loop 0 -resize 480x480 frame*.png output.gif
```

## GIF Optimization

```bash
# Reduce colors (smaller file)
convert input.gif -colors 64 -fuzz 10% output.gif

# Reduce size
convert input.gif -resize 320x240 output.gif

# Coalesce (fix frame timing issues)
convert input.gif -coalesce output.gif

# Optimize (remove duplicate pixels between frames)
convert input.gif -layers Optimize output.gif

# Strip metadata
convert input.gif -strip output.gif
```

## GIF Info

```bash
# Get GIF details
 identify input.gif

# Get frame count
 identify input.gif | wc -l

# File size
 ls -lh input.gif
```

## Samsung Fold 7 Tips

- Use `scale=480:-1` for cover screen (narrow)
- Use `scale=768:-1` for inner screen unfolded (wide)
- Use `scale=640:-1` for good balance
- Keep FPS at 10-15 for smooth playback without huge files
- Save GIFs to `/storage/emulated/0/Pictures/` for gallery access

## Pitfalls

- GIF files can be very large — always optimize with palette generation
- `convert` is CPU-intensive on ARM — be patient with large files
- Use `fps=10` minimum for decent animation quality
- Screen recordings on Fold 7 are in `/storage/emulated/0/Screen recordings/`
- ImageMagick `convert` syntax order matters: options before input