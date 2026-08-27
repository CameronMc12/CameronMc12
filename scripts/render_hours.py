#!/usr/bin/env python3
"""
E2 — the working day, as a 24-hour polar chart of real commit timestamps.

Every number here is measured by fetch_hours.py, not drawn. The first mock of
this section assumed a night owl and put the peak at 22:00; the actual data says
93% between 08:00 and 18:00 and nothing after 21:00. The measurement changed the
copy, which is the whole point of measuring.

Spokes sweep in clockwise from midnight, once, then hold.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, DIM, DISPLAY, GREEN, GREEN_DARK, GREEN_DEEP,  # noqa: E402
                   GREEN_MID, LABEL_H, MONO, MUTED, PAD, RADIUS, RULE, W,
                   esc, ground, label_row, svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "assets")

CARD_H = 268
DIAL_W = 300
R_IN, R_OUT = 34, 108


def render() -> list[str]:
    with open(os.path.join(ROOT, "data", "hours.json")) as f:
        d = json.load(f)
    by_hour = d["by_hour"]
    total = d["commits_sampled"]
    top = max(by_hour) or 1
    peak = d["peak_hour"]
    core = sum(by_hour[8:18]) / total
    after_21 = sum(by_hour[21:]) / total
    q0, q1 = d["quiet_window"]

    card_x, card_w = PAD, W - PAD * 2
    h = LABEL_H + CARD_H + 38
    cx = card_x + DIAL_W / 2
    cy = LABEL_H + CARD_H / 2

    css = """
@keyframes spoke{from{opacity:0;transform:scale(.35)}to{opacity:1;transform:none}}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.s{animation:spoke .5s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:center}
.r{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
""".strip()

    parts = svg_open(W, h, "Working hours", css)
    parts.append(ground(W, h))
    parts.append(label_row(
        "working hours",
        f'{total:,} commits sampled · {d["timezone"].split("/")[-1].lower()}'))
    parts.append(
        f'<rect x="{card_x + 0.5}" y="{LABEL_H + 0.5}" width="{card_w - 1}" '
        f'height="{CARD_H - 1}" rx="{RADIUS}" fill="#0C1013" stroke="{RULE}"/>'
    )
    parts.append(
        f'<line x1="{card_x + DIAL_W}" y1="{LABEL_H + 1}" x2="{card_x + DIAL_W}" '
        f'y2="{LABEL_H + CARD_H - 1}" stroke="{RULE}"/>'
    )

    for r, col in ((R_OUT, "#141A1D"), ((R_IN + R_OUT) / 2, "#11161A"), (R_IN, RULE)):
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="none" stroke="{col}"/>'
        )

    for hr, v in enumerate(by_hour):
        a = math.radians(hr * 15 - 90)
        length = (R_OUT - R_IN) * (v / top)
        if v == 0:
            length = 2
        x1, y1 = cx + R_IN * math.cos(a), cy + R_IN * math.sin(a)
        x2 = cx + (R_IN + length) * math.cos(a)
        y2 = cy + (R_IN + length) * math.sin(a)
        frac = v / top
        col = (GREEN if hr == peak else GREEN_MID if frac > 0.7
               else GREEN_DEEP if frac > 0.3 else GREEN_DARK)
        parts.append(
            f'<line class="s" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{col}" stroke-width="6" stroke-linecap="round" '
            f'style="animation-delay:{0.05 + hr * 0.026:.2f}s"><title>'
            f'{hr:02d}:00 — {v} commits</title></line>'
        )

    for hr, label in ((0, "00"), (6, "06"), (12, "12"), (18, "18")):
        a = math.radians(hr * 15 - 90)
        lx, ly = cx + (R_OUT + 16) * math.cos(a), cy + (R_OUT + 16) * math.sin(a) + 3.5
        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{DIM}" font-family="{MONO}" '
            f'font-size="9" text-anchor="middle">{label}</text>'
        )

    tx = card_x + DIAL_W + 30
    parts.append(
        f'<text class="r" x="{tx}" y="{LABEL_H + 52}" fill="{DIM}" '
        f'font-family="{MONO}" font-size="10" letter-spacing="1.8" '
        f'style="animation-delay:.5s">PEAK HOUR</text>'
    )
    parts.append(
        f'<text class="r" x="{tx}" y="{LABEL_H + 88}" fill="{GREEN}" '
        f'font-family="{DISPLAY}" font-size="30" font-weight="800" '
        f'letter-spacing="-.6" style="animation-delay:.56s">{peak:02d}:00</text>'
    )
    parts.append(
        f'<text class="r" x="{tx}" y="{LABEL_H + 118}" fill="{MUTED}" '
        f'font-family="{DISPLAY}" font-size="14" font-weight="300" '
        f'style="animation-delay:.62s">A working day, not a night shift. Nothing</text>'
    )
    parts.append(
        f'<text class="r" x="{tx}" y="{LABEL_H + 138}" fill="{MUTED}" '
        f'font-family="{DISPLAY}" font-size="14" font-weight="300" '
        f'style="animation-delay:.62s">lands between {q0:02d}:00 and {q1:02d}:00.</text>'
    )

    fy = LABEL_H + CARD_H - 46
    parts.append(
        f'<line x1="{card_x + DIAL_W + 1}" y1="{fy - 26}" '
        f'x2="{card_x + card_w - 1}" y2="{fy - 26}" stroke="{RULE}"/>'
    )
    stats = [(f"{core:.0%}", "08:00 — 18:00"),
             (f"{after_21:.0%}", "AFTER 21:00"),
             (f"{d['repos_scanned']}", "REPOS SAMPLED")]
    sx = tx
    for i, (big, small) in enumerate(stats):
        parts.append(f'<g class="r" style="animation-delay:{0.7 + i*0.06:.2f}s">')
        parts.append(
            f'<text x="{sx}" y="{fy}" fill="{CHALK}" font-family="{DISPLAY}" '
            f'font-size="20" font-weight="700">{esc(big)}</text>'
        )
        parts.append(
            f'<text x="{sx}" y="{fy + 18}" fill="{DIM}" font-family="{MONO}" '
            f'font-size="10" letter-spacing="1.3">{esc(small)}</text>'
        )
        parts.append("</g>")
        sx += 152
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = write(os.path.join(OUT, "07-hours.svg"), render())
    print(f"wrote assets/07-hours.svg ({n/1024:.1f} KB)")
