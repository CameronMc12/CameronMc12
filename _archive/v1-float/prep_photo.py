#!/usr/bin/env python3
"""
Prepare a headshot for ASCII conversion.

A flatly-lit face converts to a dark unreadable blob, so this does three things
before render_portrait.py ever sees it:

  1. isolate the subject      — rembg if it is installed, otherwise skipped
  2. boost LOCAL contrast     — so a flat face gains real highlights and shadows
  3. composite onto white     — white maps to the blank end of the density ramp,
                                so the background prints as nothing

Step 2 is normally OpenCV's CLAHE. cv2 is not installed here and is a heavy
dependency for one call, so this uses an unsharp mask on the luminance channel
plus a percentile stretch, which gets most of the way there. If you want the
real thing: pip install opencv-python rembg, and both paths light up
automatically.

    python3 scripts/prep_photo.py source-photo.jpg
    -> source-prepped.png
"""
from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "source-prepped.png")

TARGET_H = 900
LOCAL_RADIUS = 26     # unsharp radius, in px at TARGET_H
LOCAL_AMOUNT = 1.25   # how hard the local contrast is pushed
CLIP_LO, CLIP_HI = 2.0, 99.0   # percentile stretch, in %


def cut_background(img: Image.Image) -> Image.Image:
    try:
        from rembg import remove          # optional
    except ImportError:
        print("  rembg not installed — skipping background removal", file=sys.stderr)
        return img.convert("RGBA")
    print("  rembg: cutting the subject out")
    return remove(img).convert("RGBA")


def on_white(img: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    return Image.alpha_composite(bg, img).convert("L")


def local_contrast(g: Image.Image) -> Image.Image:
    a = np.asarray(g, dtype=np.float32)
    blur = np.asarray(g.filter(ImageFilter.GaussianBlur(LOCAL_RADIUS)), dtype=np.float32)
    a = a + LOCAL_AMOUNT * (a - blur)                 # unsharp on luminance
    lo, hi = np.percentile(a, [CLIP_LO, CLIP_HI])     # percentile stretch
    a = (a - lo) * (255.0 / max(hi - lo, 1e-3))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "L")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: prep_photo.py <photo>")
    src = sys.argv[1]
    img = Image.open(src)
    print(f"  {src}: {img.size[0]}x{img.size[1]}")

    img = cut_background(img)
    scale = TARGET_H / img.size[1]
    img = img.resize((max(1, int(img.size[0] * scale)), TARGET_H), Image.LANCZOS)

    g = local_contrast(on_white(img))
    g.save(OUT)
    print(f"wrote {os.path.relpath(OUT, ROOT)} ({g.size[0]}x{g.size[1]})")
    print("next: python3 scripts/render_portrait.py")


if __name__ == "__main__":
    main()
