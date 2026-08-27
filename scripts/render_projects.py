#!/usr/bin/env python3
"""
S3 — the three things he is building, as compact cards.

An earlier pass gave each project a full-width row with its own chart and ran to
~700px. This is the same three projects in ~240px: name, one line, the number
that matters, and a ramp that reads at a glance. The page is meant to be
scanned, not read.

The ramp bars grow from the baseline on a per-bar stagger, once, then hold.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, DISPLAY, GAP, GREEN, GREEN_DEEP, GREEN_MID, LABEL_H,  # noqa: E402
                   MONO, MUTED, PAD, RADIUS, RULE, W, esc, ground, label_row,
                   svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "assets")

CARD_H = 132
BARS = 10
BAR_GAP = 3
CARD_PAD = 18
SPARK_H = 30


def render() -> list[str]:
    with open(os.path.join(ROOT, "data", "identity.json")) as f:
        projects = json.load(f)["projects"]

    n = len(projects)
    card_w = (W - PAD * 2 - GAP * (n - 1)) / n
    h = LABEL_H + CARD_H + 38

    css = """
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes bar{from{transform:scaleY(0)}to{transform:scaleY(1)}}
.c{animation:rise .55s cubic-bezier(.2,.8,.2,1) both}
.b{animation:bar .5s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:bottom}
""".strip()

    parts = svg_open(W, h, "What I'm building", css)
    parts.append(ground(W, h))
    parts.append(label_row("building", f"{n} active · all private"))

    bar_w = (card_w - CARD_PAD * 2 - BAR_GAP * (BARS - 1)) / BARS
    ramp_colours = [GREEN_DEEP] * 4 + [GREEN_MID] * 3 + [GREEN] * 3

    for i, p in enumerate(projects):
        x = PAD + i * (card_w + GAP)
        y = LABEL_H
        d = 0.06 + i * 0.09
        parts.append(f'<g class="c" style="animation-delay:{d:.2f}s">')
        parts.append(
            f'<rect x="{x + 0.5:.1f}" y="{y + 0.5}" width="{card_w - 1:.1f}" '
            f'height="{CARD_H - 1}" rx="{RADIUS}" fill="#0C1013" stroke="{RULE}"/>'
        )
        parts.append(
            f'<text x="{x + CARD_PAD:.1f}" y="{y + 40}" fill="{CHALK}" '
            f'font-family="{DISPLAY}" font-size="21" font-weight="700" '
            f'letter-spacing="-.42">{esc(p["name"])}</text>'
        )
        parts.append(
            f'<text x="{x + card_w - CARD_PAD:.1f}" y="{y + 39}" fill="{GREEN}" '
            f'font-family="{DISPLAY}" font-size="15" font-weight="700" '
            f'text-anchor="end">{esc(p["metric"])}</text>'
        )
        parts.append(
            f'<text x="{x + CARD_PAD:.1f}" y="{y + 63}" fill="{MUTED}" '
            f'font-family="{MONO}" font-size="11.5">{esc(p["blurb"])}</text>'
        )

        base = y + CARD_H - CARD_PAD
        for bi, val in enumerate(p["ramp"][:BARS]):
            bx = x + CARD_PAD + bi * (bar_w + BAR_GAP)
            bh = max(3, val)
            parts.append(
                f'<rect class="b" x="{bx:.1f}" y="{base - bh:.1f}" '
                f'width="{bar_w:.1f}" height="{bh}" rx="2" '
                f'fill="{ramp_colours[bi]}" '
                f'style="animation-delay:{d + 0.18 + bi * 0.035:.2f}s"/>'
            )
        parts.append("</g>")
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = write(os.path.join(OUT, "03-projects.svg"), render())
    print(f"wrote assets/03-projects.svg ({n/1024:.1f} KB)")
