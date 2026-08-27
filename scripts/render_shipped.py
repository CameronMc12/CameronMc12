#!/usr/bin/env python3
"""
E4 — what actually shipped. The only section that says what the commits WERE.

Content is hand-written in data/identity.json under `shipped`. It cannot be
measured from any API, so Cameron owns every line; the file carries a note
saying the seeded entries are placeholders until he confirms them.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, DISPLAY, GREEN, GREEN_DEEP, GREEN_MID, LABEL_H,  # noqa: E402
                   MONO, MUTED, PAD, RULE, W, esc, ground, label_row,
                   svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "assets")

RAIL_X = PAD + 6
TEXT_X = PAD + 46
ROW_H = 84


def render() -> list[str]:
    with open(os.path.join(ROOT, "data", "identity.json")) as f:
        items = json.load(f)["shipped"]

    h = LABEL_H + len(items) * ROW_H + 20
    css = """
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes dot{from{opacity:0;transform:scale(0)}to{opacity:1;transform:none}}
@keyframes rail{from{transform:scaleY(0)}to{transform:scaleY(1)}}
.r{animation:rise .55s cubic-bezier(.2,.8,.2,1) both}
.d{animation:dot .45s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:center}
.rl{animation:rail .5s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:top}
""".strip()

    parts = svg_open(W, h, "What shipped", css)
    parts.append(ground(W, h))
    parts.append(label_row("shipped", "last twelve months"))

    fades = [GREEN, GREEN_MID, GREEN_DEEP, GREEN_DEEP]
    for i, item in enumerate(items):
        y = LABEL_H + 10 + i * ROW_H
        d = 0.06 + i * 0.1
        col = fades[min(i, len(fades) - 1)]
        if i < len(items) - 1:
            parts.append(
                f'<rect class="rl" x="{RAIL_X + 5}" y="{y + 12}" width="1" '
                f'height="{ROW_H - 12}" fill="{RULE}" '
                f'style="animation-delay:{d + 0.12:.2f}s"/>'
            )
        parts.append(
            f'<circle class="d" cx="{RAIL_X + 5.5}" cy="{y + 6}" r="5.5" '
            f'fill="{col}" style="animation-delay:{d:.2f}s"/>'
        )
        parts.append(f'<g class="r" style="animation-delay:{d + 0.06:.2f}s">')
        parts.append(
            f'<text x="{TEXT_X}" y="{y + 11}" fill="{col}" font-family="{MONO}" '
            f'font-size="11" letter-spacing="1.5">{esc(item["when"])}</text>'
        )
        parts.append(
            f'<text x="{TEXT_X + 92}" y="{y + 12}" fill="{CHALK}" '
            f'font-family="{DISPLAY}" font-size="20" font-weight="700" '
            f'letter-spacing="-.3">{esc(item["what"])}</text>'
        )
        parts.append(
            f'<text x="{TEXT_X}" y="{y + 38}" fill="{MUTED}" font-family="{DISPLAY}" '
            f'font-size="14" font-weight="300">{esc(item["detail"])}</text>'
        )
        parts.append("</g>")
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = write(os.path.join(OUT, "09-shipped.svg"), render())
    print(f"wrote assets/09-shipped.svg ({n/1024:.1f} KB)")
