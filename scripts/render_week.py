#!/usr/bin/env python3
"""
E3 — the weekly rhythm, from the real by-weekday totals in contributions.json.

Bars grow from the baseline on a stagger, once. The peak day is the only bar
that gets full phosphor; contrast is spent, not sprayed.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, DIM, GREEN, GREEN_DARK, GREEN_DEEP, GREEN_MID,  # noqa: E402
                   LABEL_H, MONO, MUTED, PAD, RADIUS, RULE, W, esc, ground,
                   label_row, svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "assets")

CARD_H = 220
CARD_PAD = 24
BAR_MAX = 104
NAMES = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]


def render() -> list[str]:
    with open(os.path.join(ROOT, "data", "contributions.json")) as f:
        data = json.load(f)
    dow = data["by_weekday"]                      # index 0 = Sunday
    order = [1, 2, 3, 4, 5, 6, 0]                 # show the week Monday-first
    vals = [dow[i] for i in order]
    names = [NAMES[i] for i in order]
    top = max(vals) or 1
    peak = vals.index(top)
    weekday_share = sum(vals[:5]) / max(1, sum(vals))

    card_x, card_w = PAD, W - PAD * 2
    inner = card_w - CARD_PAD * 2
    gap = 14
    bar_w = (inner - gap * 6) / 7
    base = LABEL_H + CARD_H - 74

    h = LABEL_H + CARD_H + 38
    css = """
@keyframes bar{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.b{animation:bar .6s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:bottom}
.r{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
""".strip()

    parts = svg_open(W, h, "Weekly rhythm", css)
    parts.append(ground(W, h))
    parts.append(label_row(
        "weekly rhythm",
        f"{names[peak].lower()} peaks · {weekday_share:.0%} mon–fri"))
    parts.append(
        f'<rect x="{card_x + 0.5}" y="{LABEL_H + 0.5}" width="{card_w - 1}" '
        f'height="{CARD_H - 1}" rx="{RADIUS}" fill="#0C1013" stroke="{RULE}"/>'
    )

    for i, (v, name) in enumerate(zip(vals, names)):
        x = card_x + CARD_PAD + i * (bar_w + gap)
        bh = max(6, BAR_MAX * v / top)
        d = 0.08 + i * 0.06
        is_peak = i == peak
        weekend = name in ("SAT", "SUN")
        colour = (GREEN if is_peak else GREEN_DARK if weekend
                  else GREEN_MID if v > top * 0.75 else GREEN_DEEP)
        parts.append(
            f'<text class="r" x="{x + bar_w/2:.1f}" y="{base - bh - 12:.1f}" '
            f'fill="{GREEN if is_peak else MUTED if not weekend else DIM}" '
            f'font-family="{MONO}" font-size="11" text-anchor="middle" '
            f'style="animation-delay:{d + 0.3:.2f}s">{v:,}</text>'
        )
        parts.append(
            f'<rect class="b" x="{x:.1f}" y="{base - bh:.1f}" width="{bar_w:.1f}" '
            f'height="{bh:.1f}" rx="5" fill="{colour}" '
            f'style="animation-delay:{d:.2f}s"/>'
        )
        parts.append(
            f'<text x="{x + bar_w/2:.1f}" y="{base + 22}" '
            f'fill="{CHALK if is_peak else DIM}" font-family="{MONO}" font-size="11" '
            f'letter-spacing="1.1" text-anchor="middle">{name}</text>'
        )

    fy = LABEL_H + CARD_H - 22
    parts.append(
        f'<line x1="{card_x + 1}" y1="{fy - 22}" x2="{card_x + card_w - 1}" '
        f'y2="{fy - 22}" stroke="{RULE}"/>'
    )
    parts.append(
        f'<text class="r" x="{card_x + CARD_PAD}" y="{fy}" fill="{MUTED}" '
        f'font-family="{MONO}" font-size="12" style="animation-delay:.7s">'
        f'{esc(names[peak].title())} is the heaviest day of the week, every week.</text>'
    )
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = write(os.path.join(OUT, "08-week.svg"), render())
    print(f"wrote assets/08-week.svg ({n/1024:.1f} KB)")
