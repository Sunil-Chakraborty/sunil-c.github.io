#!/usr/bin/env python3
"""
Builds the Annaprashan Story gallery page from template.html + the
photos in ./images, the videos in ./videos, and the music in ./audio.

Requires Pillow:
    pip install Pillow

Optional: ffmpeg, for auto-generating a thumbnail frame for each video.
"""

import base64
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    from PIL import Image
except ImportError:
    sys.exit(
        "This script needs Pillow to compress photos.\n"
        "Install it with:  pip install Pillow"
    )


# ==============================================================
# 0) FOLDERS AND COMPRESSION SETTINGS
# ==============================================================

IMAGES_DIR = "images"

LOGO_SOURCE = os.path.join(IMAGES_DIR, "Logo.PNG")
LOGO_OUTPUT = "logo.png"

# --------------------------------------------------------------
# Landing-page profile images
# --------------------------------------------------------------

PROFILE_DIR = "profile"
PROFILE_OUTPUT_DIR = "profile"

PROFILE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".avif",
    ".bmp",
    ".tif",
    ".tiff",
}

VIDEOS_DIR = "videos"

TEMPLATE_FILE = "template.html"

AUDIO_FILE = "audio/background.mp3"
AUDIO_EXTENSIONS = (".mp3", ".m4a", ".wav", ".ogg", ".webm", ".aac", ".flac")

# Optional manual captions for files shown under More > Audio Files.
# Use the exact audio filename as the key and enter your caption as the value.
# Example: "0001_My recording 55.m4a": "স্মৃতির কথা — প্রথম পর্ব",
AUDIO_CAPTIONS = {
    "আমার-ইচ্ছা.m4a": "অধীরের কবিতা - সুনীলের পাঠ ",
    "ছোটোবড়ো.mp3": "কবি - রবীন্দ্রনাথ ঠাকুর - সুনীলের পাঠ",
    "স্বাধীনতা.mp3": "কবি - শামসুর রহমান  - সুনীলের পাঠ",
    "হারিয়ে.m4a": "কবি -  প্রেমেন্দ্র মিত্র   - সুনীলের পাঠ",
    "তুই ফেলে এসেছিস কারে.m4a": "রবীন্দ্রসঙ্গীত - সুনীলের গানের চেষ্টা",
    
}

DOCUMENTS_DIR = "documents"

DOCUMENT_ORDER = []

OUR_STORY = ""

OUTPUT_DIR = "dist"

MAX_DIMENSION = 800
JPEG_QUALITY = 62


# ==============================================================
# 1) PHOTO ORDER
# ==============================================================

ORDER = [
    "Harinavi_School.avif",
    "0001_01.jpg",
    "0002_01.jpg",
    "0003_01.jpg",
    "0004_01.jpg",
]


# ==============================================================
# 2) PHOTO CAPTIONS
# ==============================================================

CAPTIONS = {
    "0001_01.jpg": (
        "The Indian Driverless Vehicle",
        "Uses *AI* (Animal Intelligence)",
    ),
    "0002_01.jpg": (
        "রবীনের ছেলে - আমাদের গর্ব",
        "",
    ),
    "0003_01.jpg": (
        "এইতো হচ্ছে কত কথা",
        "",
    ),
    "0004_01.jpg": (
        "আমি আছিতো ভাল আছে",
        "",
    ),
    
}


# ==============================================================
# 2b) VIDEOS
# ==============================================================

VIDEO_ORDER = [
    "0001_01.mp4",
    "0002_01.mp4",
    "0003_01.mp4",
]


VIDEO_CAPTIONS = {
    "0001_01.mp4": (
        "ভগবান যা করেন মঙ্গলের জন্য",
        "স্বামীজীর উপদেশমূলক গল্প",
    ),

    "0002_01.mp4": (
        "TRAUMA detected",
        "Emergency requirement",
    ),
    "0003_01.mp4": (
        "কৈলাসেতে ঝর্ণা বরফ",
        "মাছে  ভাতে  মামা বাড়ী ",
    ),
}


# ==============================================================
# 2c) MORE
# ==============================================================

# OUR_STORY is shown only when it contains text.


# ==============================================================
# 3) SPECIAL SLIDES
# ==============================================================

SPECIAL = {
    "Harinavi_School.avif": {
        "title": "Harinavi School",
        "sub": "",
        "hero": True,
    },
}


# ==============================================================
# IMAGE PROCESSING
# ==============================================================

def _resize_and_encode(img):

    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    w, h = img.size

    longest = max(w, h)

    if longest > MAX_DIMENSION:

        scale = MAX_DIMENSION / longest

        img = img.resize(
            (
                round(w * scale),
                round(h * scale),
            ),
            Image.LANCZOS,
        )

    buf = io.BytesIO()

    img.save(
        buf,
        format="JPEG",
        quality=JPEG_QUALITY,
        optimize=True,
        progressive=True,
    )

    return buf.getvalue()


def compress_image_bytes(path):
    """
    Resize + re-compress a photo in memory.

    The original file on disk is never modified.
    """

    return _resize_and_encode(Image.open(path))


# ==============================================================
# FFMPEG
# ==============================================================

_FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None


def make_video_poster_bytes(video_path):
    """
    Grab a frame from the video using ffmpeg.
    """

    if not _FFMPEG_AVAILABLE:
        return None

    with tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False,
    ) as tmp:

        output_path = tmp.name

    try:

        command = [
            "ffmpeg",
            "-y",
            "-ss",
            "1",
            "-i",
            video_path,
            "-frames:v",
            "1",
            "-q:v",
            "3",
            output_path,
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            return None

        if not os.path.exists(output_path):
            return None

        with open(output_path, "rb") as f:
            return f.read()

    finally:

        if os.path.exists(output_path):
            os.remove(output_path)


# ==============================================================
# VALIDATION
# ==============================================================

def check():

    problems = []

    seen = set()

    for name in ORDER:

        if name in seen:
            problems.append(
                f"Listed twice in ORDER: {name}"
            )

        seen.add(name)

        if (
            name not in CAPTIONS
            and name not in SPECIAL
        ):
            problems.append(
                f"No caption defined for: {name}"
            )

        if not os.path.exists(
            os.path.join(IMAGES_DIR, name)
        ):
            problems.append(
                f"Image file not found in "
                f"{IMAGES_DIR}/: {name}"
            )

    for name in CAPTIONS:

        if name not in ORDER:

            print(
                f"Note: '{name}' has a caption "
                f"but is not in ORDER (skipped)."
            )

    seen_video = set()

    for name in VIDEO_ORDER:

        if name in seen_video:

            problems.append(
                f"Listed twice in VIDEO_ORDER: {name}"
            )

        seen_video.add(name)

        if name not in VIDEO_CAPTIONS:

            problems.append(
                f"No caption defined in "
                f"VIDEO_CAPTIONS for: {name}"
            )

        if not os.path.exists(
            os.path.join(VIDEOS_DIR, name)
        ):

            problems.append(
                f"Video file not found in "
                f"{VIDEOS_DIR}/: {name}"
            )

    for name in VIDEO_CAPTIONS:

        if name not in VIDEO_ORDER:

            print(
                f"Note: '{name}' has a video caption "
                f"but is not in VIDEO_ORDER (skipped)."
            )

    if DOCUMENT_ORDER:

        for name in DOCUMENT_ORDER:

            if not name.lower().endswith(
                (".pdf", ".txt")
            ):

                problems.append(
                    f"Document must be PDF or TXT: {name}"
                )

            if not os.path.exists(
                os.path.join(DOCUMENTS_DIR, name)
            ):

                problems.append(
                    f"Document file not found in "
                    f"{DOCUMENTS_DIR}/: {name}"
                )

    if problems:

        print("Please fix these first:")

        for problem in problems:
            print("  -", problem)

        sys.exit(1)

    if VIDEO_ORDER and not _FFMPEG_AVAILABLE:

        print(
            "Note: ffmpeg not found — video cards will "
            "use the browser's default preview frame."
        )


# ==============================================================
# CAPTION HELPER
# ==============================================================

def _caption_entry(name):

    title, sub = CAPTIONS[name]

    return {
        "title": title,
        "sub": sub,
    }


# ==============================================================
# BUILD
# ==============================================================

def build():

    check()

    out_images = os.path.join(
        OUTPUT_DIR,
        "images",
    )

    os.makedirs(
        out_images,
        exist_ok=True,
    )


    # ----------------------------------------------------------
    # LOGO
    # ----------------------------------------------------------

    if os.path.isfile(LOGO_SOURCE):

        shutil.copyfile(
            LOGO_SOURCE,
            os.path.join(
                out_images,
                LOGO_OUTPUT,
            ),
        )


    # ----------------------------------------------------------
    # MAIN PHOTO GALLERY
    # ----------------------------------------------------------

    slides = []

    total_original = 0
    total_written = 0

    for name in ORDER:

        entry = (
            dict(SPECIAL[name])
            if name in SPECIAL
            else _caption_entry(name)
        )

        path = os.path.join(
            IMAGES_DIR,
            name,
        )

        total_original += os.path.getsize(path)

        jpeg_bytes = compress_image_bytes(path)

        total_written += len(jpeg_bytes)

        out_name = (
            os.path.splitext(name)[0]
            + ".jpg"
        )

        with open(
            os.path.join(
                out_images,
                out_name,
            ),
            "wb",
        ) as f:

            f.write(jpeg_bytes)

        entry["src"] = (
            f"images/{out_name}"
        )

        entry["file"] = name

        slides.append(entry)


    # ----------------------------------------------------------
    # VIDEOS
    # ----------------------------------------------------------

    out_videos = os.path.join(
        OUTPUT_DIR,
        "videos",
    )

    total_video_bytes = 0
    posters_made = 0

    if VIDEO_ORDER:

        os.makedirs(
            out_videos,
            exist_ok=True,
        )

    for name in VIDEO_ORDER:

        title, sub = VIDEO_CAPTIONS[name]

        src_path = os.path.join(
            VIDEOS_DIR,
            name,
        )

        total_video_bytes += os.path.getsize(
            src_path
        )

        shutil.copyfile(
            src_path,
            os.path.join(
                out_videos,
                name,
            ),
        )

        entry = {
            "title": title,
            "sub": sub,
            "type": "video",
            "src": f"videos/{name}",
            "file": name,
        }

        poster_bytes = make_video_poster_bytes(
            src_path
        )

        if poster_bytes:

            poster_name = (
                os.path.splitext(name)[0]
                + "_poster.jpg"
            )

            with open(
                os.path.join(
                    out_images,
                    poster_name,
                ),
                "wb",
            ) as f:

                f.write(poster_bytes)

            entry["poster"] = (
                f"images/{poster_name}"
            )

            posters_made += 1

        slides.append(entry)


    # ----------------------------------------------------------
    # DOCUMENTS
    # ----------------------------------------------------------

    document_names = []

    if os.path.isdir(DOCUMENTS_DIR):

        if DOCUMENT_ORDER:

            document_names = list(
                DOCUMENT_ORDER
            )

        else:

            document_names = sorted(
                name
                for name in os.listdir(
                    DOCUMENTS_DIR
                )
                if name.lower().endswith(
                    (".pdf", ".txt")
                )
            )


    documents = []

    total_document_bytes = 0

    if document_names:

        out_documents = os.path.join(
            OUTPUT_DIR,
            "documents",
        )

        os.makedirs(
            out_documents,
            exist_ok=True,
        )

        for name in document_names:

            src_path = os.path.join(
                DOCUMENTS_DIR,
                name,
            )

            if not os.path.isfile(src_path):
                continue

            shutil.copyfile(
                src_path,
                os.path.join(
                    out_documents,
                    name,
                ),
            )

            total_document_bytes += os.path.getsize(
                src_path
            )

            ext = os.path.splitext(
                name
            )[1].lower()

            is_text = ext == ".txt"

            entry = {
                "title": os.path.splitext(
                    name
                )[0].replace("_", " "),

                "sub": (
                    "Text Document"
                    if is_text
                    else "PDF Document"
                ),

                "type": "document",

                "document_type": (
                    "text"
                    if is_text
                    else "pdf"
                ),

                "file": name,

                "src": (
                    f"documents/{name}"
                ),
            }

            # Use a same-basename JPG as the card cover for either TXT or PDF.
            # Example: documents/story.txt + documents/story.jpg.
            cover_name = None
            source_stem = os.path.splitext(name)[0].casefold()
            for candidate in os.listdir(DOCUMENTS_DIR):
                candidate_path = os.path.join(DOCUMENTS_DIR, candidate)
                if (
                    os.path.isfile(candidate_path)
                    and os.path.splitext(candidate)[1].lower() in (".jpg", ".jpeg")
                    and os.path.splitext(candidate)[0].casefold() == source_stem
                ):
                    cover_name = candidate
                    break

            if cover_name:
                shutil.copyfile(
                    os.path.join(DOCUMENTS_DIR, cover_name),
                    os.path.join(out_documents, cover_name),
                )
                entry["thumbnail"] = f"documents/{cover_name}"

            if is_text:

                with open(
                    src_path,
                    "r",
                    encoding="utf-8-sig",
                ) as f:

                    entry["text"] = f.read()

            documents.append(entry)

        slides.extend(documents)


    # ==========================================================
    # PROFILE IMAGES
    #
    # Every image inside ./profile is automatically included
    # on the landing page.
    # ==========================================================

    profile_images = []

    if os.path.isdir(PROFILE_DIR):

        out_profile_dir = os.path.join(
            OUTPUT_DIR,
            PROFILE_OUTPUT_DIR,
        )

        os.makedirs(
            out_profile_dir,
            exist_ok=True,
        )

        for filename in sorted(
            os.listdir(PROFILE_DIR),
            key=str.lower,
        ):

            src_path = os.path.join(
                PROFILE_DIR,
                filename,
            )

            # Ignore directories
            if not os.path.isfile(src_path):
                continue

            extension = os.path.splitext(
                filename
            )[1].lower()

            # Ignore unsupported files
            if extension not in PROFILE_EXTENSIONS:
                continue

            try:

                with Image.open(src_path) as im:

                    im = im.convert("RGB")

                    im.thumbnail(
                        (
                            MAX_DIMENSION,
                            MAX_DIMENSION,
                        ),
                        Image.LANCZOS,
                    )

                    output_name = (
                        os.path.splitext(
                            filename
                        )[0]
                        + ".jpg"
                    )

                    output_path = os.path.join(
                        out_profile_dir,
                        output_name,
                    )

                    im.save(
                        output_path,
                        "JPEG",
                        quality=JPEG_QUALITY,
                        optimize=True,
                    )

                profile_images.append(
                    {
                        "src": (
                            f"{PROFILE_OUTPUT_DIR}/"
                            f"{output_name}"
                        ),

                        "title": (
                            os.path.splitext(
                                filename
                            )[0]
                            .replace("_", " ")
                        ),
                    }
                )

            except Exception as exc:

                print(
                    f"Warning: could not process "
                    f"profile image {filename}: {exc}"
                )


    # ==========================================================
    # TEMPLATE
    # ==========================================================

    with open(
        TEMPLATE_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        template = f.read()


    output = template.replace(
        "__SLIDES_JSON__",
        json.dumps(slides),
    )

    output = output.replace(
        "__PROFILE_IMAGES_JSON__",
        json.dumps(profile_images),
    )

    output = output.replace(
        "__OUR_STORY__",
        json.dumps(
            OUR_STORY or ""
        ),
    )

    output = output.replace(
        "__DOCUMENTS_JSON__",
        json.dumps(documents),
    )

    # ==========================================================
    # AUDIO FILES (excluding the dedicated background track)
    # ==========================================================

    audio_items = []
    out_audio_dir = os.path.join(OUTPUT_DIR, "audio")
    background_rel = os.path.normcase(os.path.normpath(AUDIO_FILE)) if AUDIO_FILE else None

    if os.path.isdir("audio"):
        os.makedirs(out_audio_dir, exist_ok=True)
        for name in sorted(os.listdir("audio"), key=str.lower):
            src_path = os.path.join("audio", name)
            if not os.path.isfile(src_path):
                continue
            if os.path.splitext(name)[1].lower() not in AUDIO_EXTENSIONS:
                continue
            rel_path = os.path.normcase(os.path.normpath(src_path))
            if background_rel and rel_path == background_rel:
                continue
            shutil.copyfile(src_path, os.path.join(out_audio_dir, name))
            audio_items.append({
                "title": os.path.splitext(name)[0].replace("_", " "),
                "caption": AUDIO_CAPTIONS.get(name, "").strip(),
                "sub": "Audio File",
                "type": "audio",
                "file": name,
                "src": f"audio/{name}",
            })

    output = output.replace(
        "__AUDIO_LIST_JSON__",
        json.dumps(audio_items, ensure_ascii=False),
    )

    # ==========================================================
    # AUDIO
    # ==========================================================

    if AUDIO_FILE:

        if not os.path.exists(AUDIO_FILE):

            sys.exit(
                f"AUDIO_FILE is set but not found: "
                f"{AUDIO_FILE}"
            )

        out_audio_dir = os.path.join(
            OUTPUT_DIR,
            "audio",
        )

        os.makedirs(
            out_audio_dir,
            exist_ok=True,
        )

        audio_name = os.path.basename(
            AUDIO_FILE
        )

        shutil.copyfile(
            AUDIO_FILE,
            os.path.join(
                out_audio_dir,
                audio_name,
            ),
        )

        output = output.replace(
            "__AUDIO_SRC__",
            f"audio/{audio_name}",
        )

        audio_note = (
            f", + "
            f"{os.path.getsize(AUDIO_FILE)/1024:.0f}"
            f" KB audio"
        )

    else:

        output = re.sub(
            r'\s*<audio id="bgAudio".*?</audio>',
            "",
            output,
            flags=re.S,
        )

        audio_note = " (no audio)"


    # ==========================================================
    # WRITE INDEX
    # ==========================================================

    index_path = os.path.join(
        OUTPUT_DIR,
        "index.html",
    )

    with open(
        index_path,
        "w",
        encoding="utf-8",
    ) as f:

        f.write(output)


    # ==========================================================
    # BUILD SUMMARY
    # ==========================================================

    print(
        f"Photos: "
        f"{total_original/1_048_576:.1f} MB original "
        f"-> "
        f"{total_written/1_048_576:.1f} MB "
        f"in {out_images}/ "
        f"(resized to {MAX_DIMENSION}px, "
        f"quality {JPEG_QUALITY})"
        f"{audio_note}"
    )

    if VIDEO_ORDER:

        print(
            f"Videos: "
            f"{len(VIDEO_ORDER)} file(s), "
            f"{total_video_bytes/1_048_576:.1f} MB "
            f"copied as-is to {out_videos}/ "
            f"({posters_made}/"
            f"{len(VIDEO_ORDER)} got an "
            f"auto thumbnail)"
        )

    if documents:

        print(
            f"Documents: "
            f"{len(documents)} PDF(s), "
            f"{total_document_bytes/1_048_576:.1f} MB "
            f"copied to "
            f"{os.path.join(OUTPUT_DIR, 'documents')}/"
        )

    print(
        f"Profile images: "
        f"{len(profile_images)} copied to "
        f"{os.path.join(OUTPUT_DIR, PROFILE_OUTPUT_DIR)}/"
    )

    print(
        "Our Story: included"
        if OUR_STORY.strip()
        else
        "Our Story: hidden "
        "(OUR_STORY is empty)"
    )

    print(
        f"Wrote {index_path} "
        f"({os.path.getsize(index_path):,} bytes)"
    )

    print(
        f"Upload the whole "
        f"'{OUTPUT_DIR}/' folder to GitHub Pages."
    )


# ==============================================================
# MAIN
# ==============================================================

if __name__ == "__main__":
    build()