---
name: qrcode-toolkit
description: Decode and generate QR codes. Use when the user wants to scan/read QR codes from images, generate QR codes for URLs/WiFi/contacts, or work with any barcode/QR code related tasks. Triggers on "QR code", "二维码", "scan QR", "generate QR", "decode barcode", "read barcode", or when handling QR code images.
---

# QR Code Toolkit (二维码工具包)

Comprehensive QR code decoding and generation tools.

## Installation

```bash
pip install qrcode[pil] pyzbar opencv-python Pillow

# On macOS, also install:
brew install zbar
```

## Part 1: Decode QR Codes (解码二维码)

Decode QR codes from images, URLs, screenshots, or clipboard.

### Basic Usage

```bash
# Decode from image file
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py ~/Downloads/qrcode.png

# Decode from URL
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py "https://example.com/qr.png"

# Decode from clipboard (screenshot or copied image)
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py --clipboard

# Decode from current screen
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py --screenshot
```

### Output Formats

```bash
# Pretty table (default)
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py image.png

# JSON format
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py image.png --format json

# Raw data only
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py image.png --format raw

# Save to file
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py image.png --output result.txt
```

### Supported QR Code Types

| Type | Description | Example |
|------|-------------|---------|
| URL | Web links | `https://example.com` |
| WiFi | Network credentials | `WIFI:T:WPA;S:network;P:pass;;` |
| vCard | Contact information | `BEGIN:VCARD...` |
| Email | Email address/message | `mailto:user@example.com` |
| Phone | Telephone number | `tel:+1234567890` |
| SMS | Text message | `SMSTO:12345:Hello` |
| Plain Text | Any text content | `Hello World` |

---

## Part 2: Generate QR Codes (生成二维码)

### Basic QR Code

```bash
# Simple text/URL
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py "Hello World" --output hello.png

# URL
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py "https://example.com" --output link.png

# Print as ASCII art (terminal)
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py "Test" --ascii

# Copy to clipboard
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py "Hello" --clipboard
```

### WiFi QR Code

Generate QR codes for WiFi networks (scan to connect):

```bash
# Basic WiFi
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --wifi "MyNetwork" "password123" \
  --output wifi.png

# Hidden network with WPA2
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --wifi "MyNetwork" "password123" \
  --type WPA --hidden \
  --output wifi.png

# Open network (no password)
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --wifi "GuestWiFi" "" \
  --type nopass \
  --output guest-wifi.png
```

### Contact Card (vCard)

```bash
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --vcard \
  --name "John Doe" \
  --phone "+1 234 567 8900" \
  --email "john@example.com" \
  --org "Example Inc" \
  --title "Software Engineer" \
  --output contact.png
```

### Email QR Code

```bash
# Simple email
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --email "contact@example.com" \
  --output email.png

# Email with pre-filled subject and body
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --email "support@example.com" \
  --subject "Help Request" \
  --body "I need assistance with..." \
  --output support-qr.png
```

### Phone & SMS

```bash
# Phone number
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --phone "+1234567890" \
  --output phone.png

# SMS with pre-filled message
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --sms "+1234567890" "Hello, I'm interested in your product" \
  --output sms.png
```

### Advanced Options

```bash
# High quality with custom colors
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  "https://example.com" \
  --size 20 \
  --border 4 \
  --error-correction H \
  --fg-color "#1a1a1a" \
  --bg-color "#f5f5f5" \
  --output high-quality.png

# With logo in center
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  "https://mybrand.com" \
  --logo ~/logo.png \
  --output branded.png

# Open after generation
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  "Hello" --output test.png --display
```

---

## Common Use Cases

### Use Case 1: Scan QR from Screenshot

When user shares a QR code screenshot:

```bash
# Save the image and decode
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py /path/to/screenshot.png

# Or if image is in clipboard
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py --clipboard
```

### Use Case 2: Create WiFi Access Card

For guests or office visitors:

```bash
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --wifi "Office-Guest" "Welcome2024" \
  --type WPA \
  --size 15 \
  --output guest-wifi.png \
  --display
```

### Use Case 3: Share Contact Information

Create a digital business card:

```bash
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  --vcard \
  --name "Denny Chui" \
  --phone "+86 138-xxxx-xxxx" \
  --email "denny@example.com" \
  --url "https://github.com/DennyChui" \
  --org "Tech Corp" \
  --output business-card.png
```

### Use Case 4: URL Shortener Alternative

```bash
# Generate QR for any URL
python3 .claude/skills/qrcode-toolkit/scripts/generate_qr.py \
  "https://docs.qq.com/sheet/DV2RHaXR5cGJERkRJ?tab=BB08J2" \
  --output doc-qr.png

# Verify by decoding
python3 .claude/skills/qrcode-toolkit/scripts/decode_qr.py doc-qr.png
```

---

## Python API Usage

### Decode in Python

```python
import sys
sys.path.insert(0, '.claude/skills/qrcode-toolkit/scripts')
from decode_qr import load_image, decode_qr_codes

# Load and decode
image = load_image('qrcode.png')
results = decode_qr_codes(image)

for result in results:
    print(f"Data: {result['data']}")
    print(f"Type: {result['type']}")
```

### Generate in Python

```python
import sys
sys.path.insert(0, '.claude/skills/qrcode-toolkit/scripts')
from generate_qr import generate_qr_code, generate_wifi_qr

# Generate WiFi QR
wifi_data = generate_wifi_qr("MyNetwork", "password", "WPA")
path = generate_qr_code(wifi_data, output_path='wifi.png', size=15)
print(f"Generated: {path}")
```

---

## Troubleshooting

### "No QR codes found"

- Image quality too low
- QR code partially cropped
- Try with higher resolution image
- Check if it's actually a QR code (not Data Matrix or other format)

### Import errors

```bash
# Reinstall dependencies
pip install --force-reinstall qrcode[pil] pyzbar opencv-python Pillow

# On macOS
brew reinstall zbar
```

### Clipboard not working

- **macOS**: Use `Cmd+Ctrl+Shift+4` to screenshot to clipboard
- **Alternative**: Save screenshot to file, then use file path

### pyzbar errors on macOS

```bash
# If you get "zbar shared library not found"
brew install zbar
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
```

---

## Technical Notes

### Error Correction Levels

| Level | Recovery Capacity | Use Case |
|-------|------------------|----------|
| L | ~7% | Clean environments |
| M | ~15% | Default |
| Q | ~25% | Somewhat dirty |
| H | ~30% | With logo overlay |

### QR Code Capacity

| Version | Max Chars (Alphanumeric) | Max Chars (Binary) |
|---------|-------------------------|-------------------|
| 1 | 25 | 17 |
| 10 | 174 | 119 |
| 40 | 4,296 | 2,953 |

Version is auto-detected based on content length.
