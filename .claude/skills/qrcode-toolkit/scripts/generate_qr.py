#!/usr/bin/env python3
"""
Generate QR codes with various options and formats.

Usage:
    python generate_qr.py "Hello World" --output qr.png
    python generate_qr.py "https://example.com" --size 10 --border 2
    python generate_qr.py "WIFI:T:WPA;S:MyNetwork;P:password;;" --output wifi.png
    python generate_qr.py "Hello" --ascii  # Print to terminal

Advanced examples:
    # WiFi QR code
    python generate_qr.py --wifi "MyNetwork" "password123" --type WPA
    
    # Contact card (vCard)
    python generate_qr.py --vcard --name "John Doe" --phone "+1234567890" --email "john@example.com"
    
    # Copy to clipboard (macOS)
    python generate_qr.py "Hello" --clipboard
"""

import argparse
import io
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote


def install_dependencies():
    """Check and guide installation of required packages."""
    missing = []
    
    try:
        import qrcode
    except ImportError:
        missing.append("qrcode[pil]")
    
    try:
        import PIL.Image
    except ImportError:
        missing.append("Pillow")
    
    if missing:
        print("Missing dependencies. Please install:", file=sys.stderr)
        print(f"  pip install {' '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def generate_wifi_qr(ssid: str, password: str, security: str = "WPA", hidden: bool = False) -> str:
    """Generate WiFi configuration QR code data."""
    # Format: WIFI:T:WPA;S:network;P:password;H:true;;
    hidden_str = "true" if hidden else "false"
    return f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden_str};;"


def generate_vcard_qr(
    name: str,
    phone: str = "",
    email: str = "",
    org: str = "",
    title: str = "",
    url: str = "",
    address: str = ""
) -> str:
    """Generate vCard QR code data."""
    lines = ["BEGIN:VCARD", "VERSION:3.0"]
    lines.append(f"FN:{name}")
    lines.append(f"N:{name};;;")
    
    if phone:
        lines.append(f"TEL:{phone}")
    if email:
        lines.append(f"EMAIL:{email}")
    if org:
        lines.append(f"ORG:{org}")
    if title:
        lines.append(f"TITLE:{title}")
    if url:
        lines.append(f"URL:{url}")
    if address:
        lines.append(f"ADR:;;{address};;;;")
    
    lines.append("END:VCARD")
    return "\n".join(lines)


def generate_email_qr(email: str, subject: str = "", body: str = "") -> str:
    """Generate email QR code data (MATMSG format for better compatibility)."""
    if subject or body:
        return f"MATMSG:TO:{email};SUB:{subject};BODY:{body};;"
    return f"mailto:{email}"


def generate_phone_qr(phone: str) -> str:
    """Generate phone number QR code data."""
    return f"tel:{phone}"


def generate_sms_qr(phone: str, message: str = "") -> str:
    """Generate SMS QR code data."""
    return f"SMSTO:{phone}:{message}"


def generate_qr_code(
    data: str,
    output_path: str = None,
    size: int = 10,
    border: int = 2,
    error_correction: str = "H",
    fg_color: str = "black",
    bg_color: str = "white",
    logo_path: str = None,
    ascii_output: bool = False,
    clipboard: bool = False
) -> str:
    """
    Generate QR code with various options.
    
    Args:
        data: Content to encode
        output_path: Output file path (PNG/SVG/JPG)
        size: Box size in pixels
        border: Border width in boxes
        error_correction: L/M/Q/H (Low/Medium/Quartile/High)
        fg_color: Foreground color
        bg_color: Background color
        logo_path: Optional logo image to embed
        ascii_output: Print ASCII art to terminal
        clipboard: Copy to clipboard (macOS)
    
    Returns:
        Path to generated file or None if printed to terminal
    """
    import qrcode
    from PIL import Image
    
    # Error correction levels
    ec_levels = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H,
    }
    
    # Create QR code
    qr = qrcode.QRCode(
        version=None,  # Auto-fit
        error_correction=ec_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_H),
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    if ascii_output:
        # Print ASCII art
        qr.print_ascii(invert=False)
        return None
    
    # Generate image
    img = qr.make_image(fill_color=fg_color, back_color=bg_color)
    
    # Add logo if specified
    if logo_path and Path(logo_path).exists():
        logo = Image.open(logo_path)
        
        # Calculate logo size (max 20% of QR code)
        qr_width, qr_height = img.size
        logo_max_size = min(qr_width, qr_height) // 5
        
        # Resize logo
        logo_width, logo_height = logo.size
        if logo_width > logo_max_size or logo_height > logo_max_size:
            ratio = min(logo_max_size / logo_width, logo_max_size / logo_height)
            new_size = (int(logo_width * ratio), int(logo_height * ratio))
            logo = logo.resize(new_size, Image.Resampling.LANCZOS)
        
        # Paste logo in center
        logo_pos = ((qr_width - logo.width) // 2, (qr_height - logo.height) // 2)
        
        # Handle transparency
        if logo.mode == 'RGBA':
            img.paste(logo, logo_pos, logo)
        else:
            img.paste(logo, logo_pos)
    
    # Determine output
    if clipboard:
        # Save to temp file and copy to clipboard
        temp_path = tempfile.mktemp(suffix='.png')
        img.save(temp_path)
        
        if sys.platform == 'darwin':
            import subprocess
            subprocess.run(['osascript', '-e', f'set the clipboard to (read (POSIX file "{temp_path}") as PNG picture)'])
            print("✓ QR code copied to clipboard")
        else:
            print(f"✓ QR code saved to {temp_path} (clipboard copy not supported on this platform)")
        
        return temp_path
    
    if output_path:
        img.save(output_path)
        return output_path
    
    # Default: save to temp and return path
    temp_path = tempfile.mktemp(suffix='.png')
    img.save(temp_path)
    return temp_path


def main():
    parser = argparse.ArgumentParser(
        description='Generate QR codes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Hello World" --output hello.png
  %(prog)s "https://example.com" --size 10 --border 4
  %(prog)s --wifi "MyNetwork" "mypassword" --type WPA
  %(prog)s --vcard --name "John" --phone "+1234567890"
  %(prog)s "Test" --ascii
        """
    )
    
    # Content options
    content_group = parser.add_mutually_exclusive_group()
    content_group.add_argument('text', nargs='?', help='Text/URL to encode')
    content_group.add_argument('--wifi', nargs=2, metavar=('SSID', 'PASSWORD'),
                               help='Generate WiFi QR code')
    content_group.add_argument('--vcard', action='store_true',
                               help='Generate vCard QR code')
    content_group.add_argument('--email', metavar='EMAIL',
                               help='Generate email QR code')
    content_group.add_argument('--phone', metavar='PHONE',
                               help='Generate phone QR code')
    content_group.add_argument('--sms', nargs=2, metavar=('PHONE', 'MESSAGE'),
                               help='Generate SMS QR code')
    
    # WiFi options
    parser.add_argument('--type', choices=['WEP', 'WPA', 'nopass'], default='WPA',
                       help='WiFi security type (default: WPA)')
    parser.add_argument('--hidden', action='store_true',
                       help='Hidden WiFi network')
    
    # vCard options
    parser.add_argument('--name', help='Contact name')
    parser.add_argument('--org', help='Organization')
    parser.add_argument('--title', help='Job title')
    parser.add_argument('--url', help='Website URL')
    parser.add_argument('--address', help='Physical address')
    
    # Email options
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')
    
    # QR code appearance
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--size', type=int, default=10,
                       help='Box size in pixels (default: 10)')
    parser.add_argument('--border', '-b', type=int, default=2,
                       help='Border width in boxes (default: 2)')
    parser.add_argument('--error-correction', '-e', choices=['L', 'M', 'Q', 'H'],
                       default='H', help='Error correction level (default: H)')
    parser.add_argument('--fg-color', default='black', help='Foreground color')
    parser.add_argument('--bg-color', default='white', help='Background color')
    parser.add_argument('--logo', help='Logo image to embed in center')
    
    # Output options
    parser.add_argument('--ascii', '-a', action='store_true',
                       help='Print ASCII art to terminal')
    parser.add_argument('--clipboard', '-c', action='store_true',
                       help='Copy to clipboard (macOS)')
    parser.add_argument('--display', '-d', action='store_true',
                       help='Open image after generation')
    
    args = parser.parse_args()
    
    # Check dependencies
    install_dependencies()
    
    # Generate data based on type
    data = None
    
    if args.wifi:
        ssid, password = args.wifi
        data = generate_wifi_qr(ssid, password, args.type, args.hidden)
    elif args.vcard:
        if not args.name:
            print("Error: --name is required for vCard", file=sys.stderr)
            sys.exit(1)
        data = generate_vcard_qr(
            name=args.name,
            phone=args.phone or "",
            email=args.email or "",
            org=args.org or "",
            title=args.title or "",
            url=args.url or "",
            address=args.address or ""
        )
    elif args.email:
        data = generate_email_qr(args.email, args.subject or "", args.body or "")
    elif args.phone:
        data = generate_phone_qr(args.phone)
    elif args.sms:
        phone, message = args.sms
        data = generate_sms_qr(phone, message)
    elif args.text:
        data = args.text
    else:
        parser.print_help()
        sys.exit(1)
    
    # Generate QR code
    result = generate_qr_code(
        data=data,
        output_path=args.output,
        size=args.size,
        border=args.border,
        error_correction=args.error_correction,
        fg_color=args.fg_color,
        bg_color=args.bg_color,
        logo_path=args.logo,
        ascii_output=args.ascii,
        clipboard=args.clipboard
    )
    
    if result:
        print(f"✓ QR code generated: {result}")
        print(f"  Content preview: {data[:100]}{'...' if len(data) > 100 else ''}")
        
        if args.display:
            import subprocess
            if sys.platform == 'darwin':
                subprocess.run(['open', result])
            elif sys.platform == 'linux':
                subprocess.run(['xdg-open', result])
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
