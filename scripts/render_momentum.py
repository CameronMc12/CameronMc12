#!/usr/bin/env python3
"""
E1 — momentum. The one thing the calendar grid cannot say: the year went up.

Plotted from the real monthly totals in contributions.json, so the shape is
measured rather than drawn. The line strokes itself on with a dash animation,
once, then holds.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, DIM, GREEN, LABEL_H, MONO, MUTED, PAD, RADIUS, RULE,  # noqa: E402
                   W, WHITE_HOT, esc, ground, label_row, svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "assets")

CARD_H = 208
CARD_PAD = 24
PLOT_H = 118


def render() -> list[str]:
    with open(os.path.join(ROOT, "data", "contributions.json")) as f:
        data = json.load(f)
    monthly = data["monthly"]
    # first and last month are partial, so they understate; drop them
    months = monthly[1:-1] if len(monthly) > 3 else monthly
    vals = [m["total"] for m in months]
    top = max(vals) or 1

    card_x, card_w = PAD, W - PAD * 2
    plot_x = card_x + CARD_PAD
    plot_w = card_w - CARD_PAD * 2
    plot_y = LABEL_H + CARD_PAD + 6
    base = plot_y + PLOT_H

    step = plot_w / max(1, len(vals) - 1)
    pts = [(plot_x + i * step, base - (v / top) * (PLOT_H - 14))
           for i, v in enumerate(vals)]
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}"
                    for i, (x, y) in enumerate(pts))
    area = f"{line} L{pts[-1][0]:.1f} {base} L{pts[0][0]:.1f} {base} Z"

    h = LABEL_H + CARD_H + 38
    q = max(1, len(vals) // 4)
    first_q, last_q = sum(vals[:q]), sum(vals[-q:])

    css = """
@keyframes draw{from{stroke-dashoffset:2400}to{stroke-dashoffset:0}}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
.ln{stroke-dasharray:2400;animation:draw 1.7s cubic-bezier(.35,.1,.25,1) both}
.ar{animation:fade .9s ease-out .7s both}
.r{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
""".strip()

    parts = svg_open(W, h, "Momentum", css)
    parts.append(ground(W, h))
    parts.append(label_row("momentum", f"{first_q:,} → {last_q:,} per quarter"))
    parts.append(
        f'<rect x="{card_x + 0.5}" y="{LABEL_H + 0.5}" width="{card_w - 1}" '
        f'height="{CARD_H - 1}" rx="{RADIUS}" fill="#0C1013" stroke="{RULE}"/>'
    )
    parts.append(
        '<defs><linearGradient id="mo" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{GREEN}" stop-opacity=".28"/>'
        f'<stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient></defs>'
    )
    for frac in (0.34, 0.67):
        gy = base - (PLOT_H - 14) * frac
        parts.append(
            f'<line x1="{plot_x}" y1="{gy:.1f}" x2="{plot_x + plot_w}" '
            f'y2="{gy:.1f}" stroke="#12181B"/>'
        )
    parts.append(
        f'<line x1="{plot_x}" y1="{base}" x2="{plot_x + plot_w}" y2="{base}" '
        f'stroke="{RULE}"/>'
    )
    parts.append(f'<path class="ar" d="{area}" fill="url(#mo)"/>')
    parts.append(
        f'<path class="ln" d="{line}" fill="none" stroke="{GREEN}" '
        f'stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>'
    )
    lx, ly = pts[-1]
    parts.append(
        f'<circle class="r" cx="{lx:.1f}" cy="{ly:.1f}" r="10" fill="{GREEN}" '
        f'fill-opacity=".18" style="animation-delay:1.7s"/>'
        f'<circle class="r" cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="{WHITE_HOT}" '
        f'style="animation-delay:1.7s"/>'
    )

    fy = LABEL_H + CARD_H - 22
    parts.append(
        f'<line x1="{card_x + 1}" y1="{fy - 22}" x2="{card_x + card_w - 1}" '
        f'y2="{fy - 22}" stroke="{RULE}"/>'
    )
    parts.append(
        f'<text class="r" x="{plot_x}" y="{fy}" fill="{MUTED}" font-family="{MONO}" '
        f'font-size="12" style="animation-delay:1.8s">'
        f'first quarter <tspan fill="{CHALK}">{first_q:,}</tspan>'
        f'   ·   last quarter <tspan fill="{GREEN}">{last_q:,}</tspan></text>'
    )
    parts.append(
        f'<text class="r" x="{card_x + card_w - CARD_PAD}" y="{fy}" fill="{DIM}" '
        f'font-family="{MONO}" font-size="11" text-anchor="end" '
        f'style="animation-delay:1.86s">{last_q / max(1, first_q):.1f}× over the year</text>'
    )
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = write(os.path.join(OUT, "06-momentum.svg"), render())
    print(f"wrote assets/06-momentum.svg ({n/1024:.1f} KB)")
