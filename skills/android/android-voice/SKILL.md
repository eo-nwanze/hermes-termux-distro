---
name: android-voice
description: Voice input/output on Samsung Fold 7 via Termux — speech-to-text, text-to-speech, voice notes
triggers:
  - voice input
  - speech to text
  - text to speech
  - tts
  - stt
  - voice note
  - say
  - speak
---

# Android Voice Control (Samsung Fold 7)

Voice input and output on the Samsung Fold 7 using Termux:API speech-to-text and text-to-speech.

## Prerequisites

- Termux:API app (F-Droid) + `pkg install termux-api`
- Internet connection for STT (speech recognition)
- Runtime microphone permission for STT

## Text-to-Speech (TTS)

```bash
# Basic speak
termux-tts-speak "Hello from Samsung Fold 7"

# Adjust speech rate (words per minute)
termux-tts-speak -r 1.5 "Speaking faster now"

# Adjust pitch (0.5 = low, 2.0 = high)
termux-tts-speak -p 1.2 "Slightly higher pitch"

# Change language
termux-tts-speak -l en-US "American English"
termux-tts-speak -l fr-FR "Bonjour le monde"

# Use Hermes text_to_speech tool for higher quality
# (uses cloud TTS rather than local Android TTS)
```

## Speech-to-Text (STT)

```bash
# Start listening (opens dialog)
termux-speech-to-text

# The result is returned as JSON:
# {"code":0,"text":"recognized text here","error":""}
```

### Programmatic STT

```python
import json, subprocess

result = subprocess.run(
    ["termux-speech-to-text"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
if data.get("code") == 0:
    print(f"Heard: {data['text']}")
```

## Voice Notes Workflow

```bash
# Record a voice note
termux-speech-to-text > /storage/emulated/0/Notes/voice-note-$(date +%s).txt

# Quick voice-to-clipboard
termux-speech-to-text | jq -r '.text' | termux-clipboard-set

# Voice note with timestamp
echo "$(date): $(termux-speech-to-text | jq -r '.text')" >> ~/voice-log.txt
```

## Samsung Fold 7 Specific

- When **unfolded**: speaker/output is louder, better for TTS playback
- When **folded**: use earpiece speaker for private TTS
- Flex mode: half-folded for hands-free dictation
- Samsung Bixby can be triggered: `am start -a android.intent.action.VOICE_COMMAND`

## Pitfalls

- STT requires internet (uses Google/cloud recognition)
- TTS works offline with Samsung's built-in engine
- Microphone permission must be explicitly granted
- `termux-speech-to-text` opens a system dialog — not fully silent
- For background voice, use `termux-tts-speak` (local engine)
- For high-quality TTS, use Hermes text_to_speech tool instead
- **Samsung Recorder clips are NOT accessible from Termux** — Samsung Recorder uses app-private scoped storage. Termux cannot read `/storage/emulated/0/Recordings/Voice Recorder/`. If the user asks about finding/accessing voice clips and uses Samsung Recorder, tell them to share the clip via Telegram bot, email, or My Files to a location Termux can access. Alternatively, use Termux's own `termux-microphone-record` (if available) or `termux-speech-to-text` which saves to Termux-accessible paths.