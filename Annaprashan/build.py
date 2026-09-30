#!/usr/bin/env python3
# https://tinyurl.com/Agastya-First-Rice-Ceremony
"""
Builds annaprashan-story.html from template.html + the photos in ./images

Requires Pillow (for resizing/compressing photos before embedding):
    pip install Pillow

HOW TO CHANGE THE ORDER OF SLIDES
---------------------------------
Only edit the ORDER list below. Move a filename up or down and run:

    python3 build.py

Each photo's title/subtitle is stored separately in CAPTIONS (keyed by
filename), so it always travels with its photo. You never need to touch
CAPTIONS just to reorder.

To add a photo: copy it into ./images (or wherever IMAGES_DIR points),
add one line in CAPTIONS, and add its filename to ORDER where you want it.

KEEPING THE FILE LIGHTWEIGHT
-----------------------------
Photos are resized and re-compressed at build time (originals in
IMAGES_DIR are never modified) using the settings below:

    MAX_DIMENSION  - longest side, in pixels, after resizing
    JPEG_QUALITY   - 1-95; lower = smaller file, more compression artifacts

The defaults (1100px, quality 78) bring an 18-photo story from roughly
4.7 MB down to about 2-3 MB with very little visible difference. Raise
MAX_DIMENSION / JPEG_QUALITY if you want higher quality at a larger
file size, or lower them for an even smaller file.
"""

import base64
import io
import json
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit(
        "This script needs Pillow to compress photos.\n"
        "Install it with:  pip install Pillow"
    )

# ----------------------------------------------------------------------
# 0) FOLDERS AND COMPRESSION SETTINGS
# ----------------------------------------------------------------------
IMAGES_DIR = "images"          # <-- point this at your local photo folder
TEMPLATE_FILE = "template.html"
OUTPUT_FILE = "annaprashan-story.html"

MAX_DIMENSION = 1100            # longest side in pixels after resizing
JPEG_QUALITY = 78               # 1-95, lower = smaller file

# ----------------------------------------------------------------------
# 1) ORDER  <-- edit this list to change the presentation sequence
# ----------------------------------------------------------------------
ORDER = [
    "IMG-20260903-WA0011.jpg",   # invitation (landing page)
    "0001_01.jpg",
    "0003_01.jpg",
    "0005_01.jpg",
    "0006_01.jpg",
    "0009_01.jpg",
    "0010_01.jpg",
    "0012_01.jpg",
    "0014_01.jpg",
    "0015_01.jpg",
    "0016_01.jpg",
    "0018_01.jpg",
    "0023_01.jpg",
    "0024_01.jpg",
    "0026_01.jpg",
    "0028_01.jpg",
    "0031_01.jpg",
    "0032_01.jpg",
    "0033_01.jpg",
]

# ----------------------------------------------------------------------
# 2) CAPTIONS  <-- one entry per photo: (title, subtitle, pan-x, pan-y)
#    pan-x / pan-y = direction of the slow zoom drift, e.g. "-3%", "2%"
# ----------------------------------------------------------------------
CAPTIONS = {
    "0001_01.jpg": ("The First Bite", "Baba offers the ceremonial rice", "-3%", "-2%"),
    "0003_01.jpg": ("The Little Prince", "Crowned in the traditional mukut", "2%", "-2%"),
    "0005_01.jpg": ("Gifts of Gold", "Jewellery laid out to bless the day", "-2%", "2%"),
    "0006_01.jpg": ("A Quiet Moment", "Ma cradles her sleepy little one", "3%", "1%"),
    "0009_01.jpg": ("Golden Keepsakes", "More precious gifts for the occasion", "-3%", "2%"),
    "0010_01.jpg": ("The Ritual Begins", "Elders performing the floor rites", "2%", "3%"),
    "0012_01.jpg": ("The Sacred Thala", "Rice, turmeric, and diya for the puja", "-2%", "-3%"),
    "0014_01.jpg": ("Two Doting Grandmothers", "Showering the little one with love", "3%", "-1%"),
    "0015_01.jpg": ("Offering Blessings", "A handful of rice and good wishes", "-3%", "1%"),
    "0016_01.jpg": ("Gathered in Prayer", "Family and friends join the rituals", "2%", "-2%"),
    "0018_01.jpg": ("Blessings Begin", "Wrapped in the ceremonial red cloth", "-2%", "3%"),
    "0023_01.jpg": ("Wide-Eyed Wonder", "A curious little face", "3%", "2%"),
    "0024_01.jpg": ("In Ma's Arms", "Held close through it all", "-3%", "-2%"),
    "0026_01.jpg": ("Family Portrait", "Three generations, one smile", "2%", "1%"),
    "0028_01.jpg": ("Garlanded with Love", "Dida's blessings, wrapped in flowers", "-2%", "-1%"),
    "0031_01.jpg": ("Up in the Air", "Baba lifts his little one high", "3%", "3%"),
    "0032_01.jpg": ("Celebration Time", "Family gathers for the party", "-3%", "2%"),
    "0033_01.jpg": ("One Big Happy Family", "Celebrating together", "2%", "-3%"),
}

# ----------------------------------------------------------------------
# 3) SPECIAL SLIDES  <-- per-photo overrides (hold time, hide caption)
#    duration    = milliseconds to hold the slide (default 4200)
#    showCaption = False hides the bottom caption box for that slide
# ----------------------------------------------------------------------
SPECIAL = {
    "IMG-20260903-WA0011.jpg": {
        "title": "Invitation", "sub": "",
        "kx": "1%", "ky": "-1%",
        "duration": 7000,
        "showCaption": False,
    },
}


def encode_image(path):
    """Resize + re-compress a photo in memory and return it as a data URI.
    The original file on disk is never touched."""
    img = Image.open(path)
    img = img.convert("RGB") if img.mode not in ("RGB", "L") else img
    w, h = img.size
    longest = max(w, h)
    if longest > MAX_DIMENSION:
        scale = MAX_DIMENSION / longest
        img = img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def check():
    problems = []
    seen = set()
    for name in ORDER:
        if name in seen:
            problems.append(f"Listed twice in ORDER: {name}")
        seen.add(name)
        if name not in CAPTIONS and name not in SPECIAL:
            problems.append(f"No caption defined for: {name}")
        if not os.path.exists(os.path.join(IMAGES_DIR, name)):
            problems.append(f"Image file not found in {IMAGES_DIR}/: {name}")
    for name in CAPTIONS:
        if name not in ORDER:
            print(f"Note: '{name}' has a caption but is not in ORDER (skipped).")
    if problems:
        print("Please fix these first:")
        for p in problems:
            print("  -", p)
        sys.exit(1)


def build():
    check()
    slides = []
    total_original = 0
    total_compressed = 0
    for name in ORDER:
        if name in SPECIAL:
            entry = dict(SPECIAL[name])
        else:
            title, sub, kx, ky = CAPTIONS[name]
            entry = {"title": title, "sub": sub, "kx": kx, "ky": ky}
        path = os.path.join(IMAGES_DIR, name)
        total_original += os.path.getsize(path)
        src = encode_image(path)
        total_compressed += len(src)
        entry["src"] = src
        slides.append(entry)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    output = template.replace("__SLIDES_JSON__", json.dumps(slides))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Photos: {total_original/1_048_576:.1f} MB original -> "
          f"{total_compressed/1_048_576:.1f} MB embedded "
          f"(resized to {MAX_DIMENSION}px, quality {JPEG_QUALITY})")
    print(f"Wrote {OUTPUT_FILE} ({len(output):,} bytes, {len(slides)} slides)")


if __name__ == "__main__":
    build()
