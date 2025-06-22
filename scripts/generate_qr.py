#!/usr/bin/env python3
"""
Generate QR code for evidence dashboard access.
Useful for printed documents and presentations.
"""

import os
from pathlib import Path


def generate_evidence_qr():
    """Generate QR code linking to evidence dashboard."""

    # Evidence dashboard URL (replace with actual URL)
    dashboard_url = (
        "https://github.com/example/oversight_curriculum/"
        "actions/workflows/evidence.yml"
    )

    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(dashboard_url)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to results directory
    output_path = Path("results/evidence_dashboard_qr.png")
    output_path.parent.mkdir(exist_ok=True)
    img.save(output_path)

    print(f"QR code saved to: {output_path}")
    print(f"Links to: {dashboard_url}")
    print("\nAdd this QR code to your memo for easy access to live evidence!")


if __name__ == "__main__":
    try:
        import qrcode

        generate_evidence_qr()
    except ImportError:
        print("Installing qrcode...")
        os.system("pip install qrcode[pil]")
        import qrcode

        generate_evidence_qr()
