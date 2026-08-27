#!/usr/bin/env python3
"""
Turn source-prepped.png into a monochrome ASCII portrait that types itself in,
row by row, once, then holds.

Monochrome on purpose: per-character rainbow colouring is exactly what makes
most ASCII portraits look like television static. One ink, and the density ramp
does all the work.

The reveal is a per-row horizontal wipe — each row lives in its own clip whose
width animates left to right, staggered top to bottom, with a small block
riding the wipe edge as a cursor.

Renders on the always-dark art card (see DESIGN.md §5), so there is no light
variant of the ink.

    python3 scripts/prep_photo.py <photo> && python3 scripts/render_portrait.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (BAR_H, PAD, THEMES, art_bar, art_frame, art_panel, esc,  # noqa: E402
                   svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.path.join(ROOT, "source-prepped.png")
OUT_DIR = os.path.join(ROOT, "assets")

W, H = 340, 360        # the hero-left slot, so it can swap in for the rain
CELL_W = 3.55
CELL_H = 6.2
# leading space clears the background to nothing: white -> blank
RAMP = " .`:-=+*csS#%@"

ROW_T = 0.045          # per-row stagger
WIPE = 0.32            # how long one row takes to print


def main() -> None:
    if not os.path.exists(SRC):
        sys.exit(
            f"{os.path.relpath(SRC, ROOT)} not found.\n"
            "Drop a headshot in the repo root and run:\n"
            "  python3 scripts/prep_photo.py <photo>"
        )
    cols = int((W - PAD * 2) // CELL_W)
    rows = int((H - BAR_H - PAD * 1.4) // CELL_H)

    img = Image.open(SRC).convert("L")
    # fit inside the grid without distorting the face
    src_aspect = img.size[0] / img.size[1]
    grid_aspect = (cols * CELL_W) / (rows * CELL_H)
    if src_aspect > grid_aspect:
        w, h = cols, max(1, int(cols / src_aspect * (CELL_W / CELL_H)))
    else:
        h, w = rows, max(1, int(rows * src_aspect * (CELL_H / CELL_W)))
    a = np.asarray(img.resize((w, h), Image.LANCZOS), dtype=np.float32) / 255.0

    n = len(RAMP) - 1
    lines = ["".join(RAMP[int(round((1 - v) * n))] for v in row).rstrip() for row in a]

    x0 = PAD + (W - PAD * 2 - w * CELL_W) / 2
    y0 = BAR_H + PAD * 0.7 + (H - BAR_H - PAD * 1.4 - h * CELL_H) / 2 + CELL_H
    art_w = w * CELL_W

    css = (
        f"text{{font-size:{CELL_H*0.86:.1f}px;letter-spacing:"
        f"{CELL_W - CELL_H*0.86*0.6:.2f}px;white-space:pre;"
        "font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;"
        "fill:#E7E8EA;fill-opacity:.9}"
    )

    for theme_name in ("dark", "light"):
        t = THEMES[theme_name]
        parts = svg_open(W, H, "ASCII portrait", css)
        parts.append(f'<rect width="{W}" height="{H}" fill="{t.ground}"/>')
        parts += art_panel(t, W, H, "identity", "portrait", uid="pt")

        defs = ["<defs>"]
        for i in range(len(lines)):
            begin = i * ROW_T
            defs.append(
                f'<clipPath id="pw{i}"><rect x="{x0:.1f}" '
                f'y="{y0 + i*CELL_H - CELL_H:.1f}" width="0" height="{CELL_H*1.4:.1f}">'
                f'<animate attributeName="width" values="0;{art_w:.0f}" dur="{WIPE}s" '
                f'begin="{begin:.2f}s" fill="freeze"/></rect></clipPath>'
            )
        defs.append("</defs>")
        parts.append("".join(defs))

        for i, line in enumerate(lines):
            if not line:
                continue
            y = y0 + i * CELL_H
            parts.append(
                f'<text clip-path="url(#pw{i})" x="{x0:.1f}" y="{y:.1f}" '
                f'xml:space="preserve">{esc(line)}</text>'
            )
            # the cursor block riding the wipe edge
            parts.append(
                f'<rect x="{x0:.1f}" y="{y - CELL_H*0.78:.1f}" width="{CELL_W*1.6:.1f}" '
                f'height="{CELL_H*0.86:.1f}" fill="#E4F222" opacity="0">'
                f'<animate attributeName="x" values="{x0:.1f};{x0+art_w:.0f}" '
                f'dur="{WIPE}s" begin="{i*ROW_T:.2f}s" fill="freeze"/>'
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.02;.98;1" '
                f'dur="{WIPE}s" begin="{i*ROW_T:.2f}s" fill="freeze"/></rect>'
            )

        parts.append(art_bar(W, "identity", "portrait"))
        parts.append(art_frame(t, W, H))
        nbytes = write(os.path.join(OUT_DIR, f"portrait-{theme_name}.svg"), parts)
        print(f"wrote assets/portrait-{theme_name}.svg ({nbytes/1024:.0f} KB, {w}x{h} chars)")

    print("\nto use it instead of the rain, in scripts/render_hero.py swap")
    print("  render_matrix.body(t, 'green', LEFT_W, H)  ->  a portrait <image>/<use>,")
    print("or just point the README's hero <picture> at portrait-*.svg.")


if __name__ == "__main__":
    main()
