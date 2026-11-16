#!/usr/bin/env python3
"""Generate original PseudOS wallpaper and logo using Pillow."""
from __future__ import annotations

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)


def font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
]
FONT_REGULAR = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",
]


def make_wallpaper() -> None:
    width, height = 1920, 1080
    top = (7, 15, 30)
    bottom = (12, 27, 47)
    image = Image.new("RGB", (width, height))
    pixels = image.load()

    # Deep navy vertical gradient with a restrained teal glow at the right.
    for y in range(height):
        t = y / (height - 1)
        base = tuple(round(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(width):
            dx = (x - 1390) / 950
            dy = (y - 435) / 680
            glow = max(0.0, 1.0 - math.sqrt(dx * dx + dy * dy)) ** 2
            pixels[x, y] = (
                min(255, round(base[0] + 3 * glow)),
                min(255, round(base[1] + 34 * glow)),
                min(255, round(base[2] + 44 * glow)),
            )

    art = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(art, "RGBA")

    # Large cropped orbital paths create depth without making the desktop busy.
    center = (1450, 470)
    for i, color in enumerate(((41, 214, 197, 48), (106, 105, 255, 40), (41, 214, 197, 25))):
        inset = i * 90
        d.ellipse(
            (center[0] - 610 + inset, center[1] - 390 + inset,
             center[0] + 610 - inset, center[1] + 390 - inset),
            outline=color, width=3 if i == 0 else 2,
        )

    # A quiet technical grid, strongest around the right-hand motif.
    for x in range(880, width, 64):
        d.line((x, 0, x, height), fill=(150, 190, 215, 14), width=1)
    for y in range(40, height, 64):
        d.line((850, y, width, y), fill=(150, 190, 215, 14), width=1)

    # Glowing geometric nodes and diagonal links.
    nodes = [(1130, 210), (1460, 160), (1710, 365), (1510, 690), (1195, 650), (1770, 835)]
    links = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (3, 5)]
    for a, b in links:
        d.line((nodes[a], nodes[b]), fill=(65, 211, 202, 35), width=2)
    for index, (x, y) in enumerate(nodes):
        c = (41, 214, 197, 190) if index % 2 == 0 else (139, 120, 255, 170)
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=c)
        d.ellipse((x - 24, y - 24, x + 24, y + 24), outline=(*c[:3], 55), width=2)

    # A broad translucent crescent-like panel anchors the right-side motif.
    d.rounded_rectangle((1210, 255, 1740, 785), radius=150,
                        fill=(7, 18, 34, 80), outline=(41, 214, 197, 70), width=3)
    d.ellipse((1305, 350, 1645, 690), outline=(41, 214, 197, 210), width=12)
    d.arc((1342, 386, 1608, 652), start=30, end=310, fill=(150, 124, 255, 220), width=9)
    d.ellipse((1452, 304, 1500, 352), fill=(41, 214, 197, 230))
    d.ellipse((1607, 525, 1643, 561), fill=(150, 124, 255, 230))

    # Brand lettering on the left, with generous negative space for icons.
    title_font = font(FONT_BOLD, 112)
    subtitle_font = font(FONT_REGULAR, 33)
    eyebrow_font = font(FONT_BOLD, 21)
    d.rounded_rectangle((145, 340, 244, 350), radius=5, fill=(41, 214, 197, 255))
    d.text((145, 390), "PORTABLE LINUX DESKTOP", font=eyebrow_font, fill=(117, 203, 205, 255))
    d.text((138, 445), "PseudOS", font=title_font, fill=(240, 247, 250, 255), stroke_width=1, stroke_fill=(240, 247, 250, 255))
    d.text((148, 590), "A desktop that travels with you.", font=subtitle_font, fill=(172, 190, 207, 255))
    d.text((148, 955), "PSEUDOS  /  0.1.0", font=eyebrow_font, fill=(99, 133, 157, 220))

    # Add a very subtle bottom vignette.
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 900, width, height), fill=(2, 8, 16, 34))
    art = Image.alpha_composite(art, overlay)
    image = Image.alpha_composite(image.convert("RGBA"), art).convert("RGB")
    image.save(ASSETS / "pseudos-wallpaper.png", optimize=True)


def make_logo() -> None:
    size = 512
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(image, "RGBA")
    d.rounded_rectangle((12, 12, 500, 500), radius=116, fill=(10, 24, 42, 255), outline=(61, 212, 202, 220), width=7)
    d.ellipse((78, 78, 434, 434), outline=(41, 214, 197, 120), width=5)
    d.arc((106, 106, 406, 406), start=212, end=30, fill=(144, 119, 255, 255), width=15)
    d.arc((106, 106, 406, 406), start=40, end=205, fill=(41, 214, 197, 255), width=15)
    letter = font(FONT_BOLD, 250)
    bbox = d.textbbox((0, 0), "P", font=letter, stroke_width=0)
    x = (size - (bbox[2] - bbox[0])) / 2 - bbox[0] - 6
    y = (size - (bbox[3] - bbox[1])) / 2 - bbox[1] - 12
    d.text((x, y), "P", font=letter, fill=(240, 247, 250, 255))
    d.ellipse((362, 111, 401, 150), fill=(41, 214, 197, 255))
    image.save(ASSETS / "pseudos-logo.png", optimize=True)


if __name__ == "__main__":
    make_wallpaper()
    make_logo()
    print("Generated assets/pseudos-wallpaper.png (1920x1080) and assets/pseudos-logo.png (512x512).")
