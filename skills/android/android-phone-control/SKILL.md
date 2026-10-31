---
name: android-phone-control
description: Control Samsung Fold 7 phone functions — calls, SMS, contacts — from Termux using Termux:API
triggers:
  - make call
  - send sms
  - phone call
  - call phone
  - contacts
  - phone control
---

# Android Phone Control (Samsung Fold 7)

Control phone, SMS, and contacts from Termux using the Termux:API companion app.

## Prerequisites

1. Install Termux:API app from F-Droid (must match Termux source)
2. `pkg install termux-api`
3. Grant runtime permissions (Phone, Contacts, SMS)

## Phone Calls

```bash
# Make a call
termux-telephony-call +1234567890

# Check call/phone state
termux-telephony-deviceinfo

# Open dialer with number pre-filled
am start -a android.intent.action.DIAL -d tel:+1234567890
```

## SMS

```bash
# Send SMS
termux-sms-send -n +1234567890 "Hello from Fold 7"

# Send to multiple recipients
termux-sms-send -n +1234567890,+1098765432 "Group message"

# Read SMS inbox (recent messages)
termux-sms-list

# Read SMS with filters
termux-sms-list -l 50 -n +1234567890
```

## Contacts

```bash
# List all contacts
termux-contact-list

# Search contacts (pipe through grep)
termux-contact-list | grep -i "name"

# Open contacts app
am start -a android.intent.action.VIEW -t vnd.android.cursor.dir/contact
```

## Notifications

```bash
# Post a notification
termux-notification --title "Alert" --content "Something happened"

# Post with action buttons
termux-notification --title "Task Done" --content "Build completed" --id build-notify

# Remove notification
termux-notification --id build-notify --cancel
```

## Clipboard & Device

```bash
# Get/set clipboard
termux-clipboard-get
termux-clipboard-set "Copied text"

# Vibrate
termux-vibrate -d 500

# Torch/flashlight
termux-torch on
termux-torch off

# Battery (Fold 7 has dual batteries)
termux-battery-status

# Screen state (folded vs unfolded)
dumpsys display | grep -E "mBaseDisplayInfo|ScreenState"
```

## Pitfalls

- Termux:API F-Droid and Play Store versions are incompatible — use same source
- SMS permissions require explicit user grant on Android 13+
- `termux-telephony-call` only initiates calls, doesn't auto-dial silently
- Samsung Dual SIM: use correct slot for SMS/calls