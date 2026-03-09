#!/usr/bin/env python3
"""
Decode QR codes from images.
Supports multiple QR codes in one image, various formats, and error handling.

Usage:
    python decode_qr.py <image_path> [--format table|json|raw]
    python decode_qr.py --clipboard [--format table|json|raw]
    python decode_qr.py --screenshot [--format table|json|raw]

Examples:
    python decode_qr.py ~/Downloads/qrcode.png
    python decode_qr.py https://example.com/qr.png
    python decode_qr.py --clipboard
    python decode_qr.py --screenshot --format json
"""

import argparse
import base64
import io
import json
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import List, Optional, Tuple


def install_dependencies():
    """Check and guide installation of required packages."""
    missing = []
    
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    
    try:
        from pyzbar import pyzbar
    except ImportError:
        missing.append("pyzbar")
    
    try:
        import PIL.Image
    except ImportError:
        missing.append("Pillow")
    
    if missing:
        print("Missing dependencies. Please install:", file=sys.stderr)
        print(f"  pip install {' '.join(missing)}", file=sys.stderr)
        print("\nNote: On macOS, you may also need:", file=sys.stderr)
        print("  brew install zbar", file=sys.stderr)
        sys.exit(1)


def load_image(source: str) -> Optional["cv2.Mat"]:
    """
    Load image from various sources:
    - Local file path
    - HTTP/HTTPS URL
    - Base64 data URI
    """
    import cv2
    import numpy as np
    
    # Check if it's a URL
    if source.startswith(('http://', 'https://')):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        req = urllib.request.Request(source, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            image_data = response.read()
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    # Check if it's a base64 data URI
    if source.startswith('data:image'):
        # Extract base64 data
        base64_data = source.split(',')[1]
        image_data = base64.b64decode(base64_data)
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    # Local file
    path = Path(source).expanduser()
    if not path.exists():
        return None
    
    return cv2.imread(str(path))


def load_from_clipboard() -> Optional["cv2.Mat"]:
    """Load image from system clipboard."""
    import cv2
    import numpy as np
    
    try:
        import pyperclip
        # Try to get image from clipboard
        # Note: pyperclip doesn't support images directly on all platforms
        # So we use PIL for cross-platform clipboard image access
        
        try:
            from PIL import ImageGrab
            # macOS specific
            if sys.platform == 'darwin':
                img = ImageGrab.grabclipboard()
                if img is None:
                    return None
                # Convert PIL to OpenCV
                import numpy as np
                return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except ImportError:
            pass
        
        # Fallback: try using pbpaste on macOS
        import subprocess
        result = subprocess.run(['pbpaste'], capture_output=True)
        # If it's a file path, load it
        path = result.stdout.decode('utf-8').strip()
        if Path(path).exists():
            return cv2.imread(path)
        
        return None
    except Exception as e:
        print(f"Clipboard error: {e}", file=sys.stderr)
        return None


def take_screenshot() -> "cv2.Mat":
    """Take a screenshot of the entire screen."""
    import cv2
    import numpy as np
    
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    except ImportError:
        print("PIL not available for screenshot", file=sys.stderr)
        sys.exit(1)


def decode_qr_codes(image: "cv2.Mat") -> List[dict]:
    """
    Decode all QR codes in an image.
    Returns list of dicts with: data, type, rect, polygon
    """
    from pyzbar import pyzbar
    
    # Decode barcodes and QR codes
    decoded_objects = pyzbar.decode(image)
    
    results = []
    for obj in decoded_objects:
        result = {
            'data': obj.data.decode('utf-8'),
            'type': obj.type,
            'rect': {
                'x': obj.rect.left,
                'y': obj.rect.top,
                'width': obj.rect.width,
                'height': obj.rect.height
            },
            'polygon': [(p.x, p.y) for p in obj.polygon]
        }
        results.append(result)
    
    return results


def format_output(results: List[dict], format_type: str) -> str:
    """Format results according to specified format."""
    if not results:
        return "No QR codes found."
    
    if format_type == 'json':
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    if format_type == 'raw':
        return '\n'.join(r['data'] for r in results)
    
    # table format (default)
    lines = []
    lines.append(f"Found {len(results)} code(s):\n")
    lines.append("-" * 60)
    
    for i, result in enumerate(results, 1):
        lines.append(f"\n[{i}] Type: {result['type']}")
        lines.append(f"    Data: {result['data']}")
        lines.append(f"    Position: ({result['rect']['x']}, {result['rect']['y']}) "
                    f"{result['rect']['width']}x{result['rect']['height']}")
        
        # Try to detect content type
        data = result['data']
        if data.startswith('http://') or data.startswith('https://'):
            lines.append(f"    Content: URL")
        elif data.startswith('WIFI:') or data.startswith('wifi:'):
            lines.append(f"    Content: WiFi Configuration")
        elif data.startswith('tel:') or data.startswith('TEL:'):
            lines.append(f"    Content: Phone Number")
        elif data.startswith('mailto:') or data.startswith('MATMSG:'):
            lines.append(f"    Content: Email")
        elif data.startswith('BEGIN:VCARD'):
            lines.append(f"    Content: Contact Card (vCard)")
        elif data.startswith('BEGIN:VEVENT'):
            lines.append(f"    Content: Calendar Event")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Decode QR codes from images'
    )
    parser.add_argument(
        'source',
        nargs='?',
        help='Image file path, URL, or base64 data'
    )
    parser.add_argument(
        '--clipboard', '-c',
        action='store_true',
        help='Read image from clipboard'
    )
    parser.add_argument(
        '--screenshot', '-s',
        action='store_true',
        help='Take screenshot and decode QR codes from it'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['table', 'json', 'raw'],
        default='table',
        help='Output format (default: table)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    install_dependencies()
    
    # Determine image source
    image = None
    
    if args.screenshot:
        print("Taking screenshot...", file=sys.stderr)
        image = take_screenshot()
    elif args.clipboard:
        print("Reading from clipboard...", file=sys.stderr)
        image = load_from_clipboard()
        if image is None:
            print("Error: No image found in clipboard", file=sys.stderr)
            print("Try copying an image first (Cmd+Ctrl+Shift+4 on macOS)", file=sys.stderr)
            sys.exit(1)
    elif args.source:
        image = load_image(args.source)
        if image is None:
            print(f"Error: Could not load image from {args.source}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Decode QR codes
    print("Decoding QR codes...", file=sys.stderr)
    results = decode_qr_codes(image)
    
    # Format output
    output = format_output(results, args.format)
    
    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\nOutput saved to: {args.output}", file=sys.stderr)
    else:
        print(output)
    
    # Return exit code based on results
    sys.exit(0 if results else 1)


if __name__ == '__main__':
    main()
