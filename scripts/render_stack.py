#!/usr/bin/env python3
"""
S5 — the language mix, read two ways: a radar for the shape of it and rails for
the numbers. Both come from data/stack.json, which is measured across all 29
repos with `gh api graphql` — private ones included.

Repo NAMES never appear here. They are client work; only aggregate bytes leave
the API.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, DIM, GAP, GREEN, GREEN_DARK, GREEN_DEEP, GREEN_MID,  # noqa: E402
                   INSET, LABEL_H, MONO, MUTED, PAD, RADIUS, RULE, W, esc,
                   ground, label_row, svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "assets")

KEEP = 5
CARD_H = 236
RADAR_W = 292
R_MAX = 78


def poly(cx: float, cy: float, r: float, n: int = KEEP) -> str:
    pts = []
    for i in range(n):
        a = math.radians(-90 + i * 360 / n)
        pts.append(f"{cx + r*math.cos(a):.1f},{cy + r*math.sin(a):.1f}")
    return " ".join(pts)


def render() -> list[str]:
    with open(os.path.join(ROOT, "data", "stack.json")) as f:
        stack = json.load(f)
    langs = stack["languages"][:KEEP]
    top = langs[0]["pct"]

    h = LABEL_H + CARD_H + 38
    card_x, card_w = PAD, W - PAD * 2

    css = """
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes web{from{opacity:0;transform:scale(.7)}to{opacity:1;transform:none}}
.r{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}
.g{animation:grow .65s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:left center}
.wb{animation:web .7s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:center}
""".strip()

    parts = svg_open(W, h, "Stack signature", css)
    parts.append(ground(W, h))
    parts.append(label_row(
        "stack", f'{stack["code_bytes"]/1e6:.0f} MB · {stack["repos_total"]} repos'))
    parts.append(
        f'<rect x="{card_x + 0.5}" y="{LABEL_H + 0.5}" width="{card_w - 1}" '
        f'height="{CARD_H - 1}" rx="{RADIUS}" fill="#0C1013" stroke="{RULE}"/>'
    )
    parts.append(
        f'<line x1="{card_x + RADAR_W}" y1="{LABEL_H + 1}" x2="{card_x + RADAR_W}" '
        f'y2="{LABEL_H + CARD_H - 1}" stroke="{RULE}"/>'
    )

    cx, cy = card_x + RADAR_W / 2, LABEL_H + CARD_H / 2 + 4
    for i, frac in enumerate((0.25, 0.5, 0.75, 1.0)):
        parts.append(
            f'<polygon class="wb" points="{poly(cx, cy, R_MAX * frac)}" fill="none" '
            f'stroke="#141A1D" style="animation-delay:{0.05 + i*0.04:.2f}s"/>'
        )
    for i in range(KEEP):
        a = math.radians(-90 + i * 360 / KEEP)
        parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{cx + R_MAX*math.cos(a):.1f}" '
            f'y2="{cy + R_MAX*math.sin(a):.1f}" stroke="{RULE}"/>'
        )

    pts, dots = [], []
    for i, lang in enumerate(langs):
        a = math.radians(-90 + i * 360 / KEEP)
        r = R_MAX * (lang["pct"] / top) ** 0.72     # eased, or 4% vanishes at the hub
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        pts.append(f"{px:.1f},{py:.1f}")
        dots.append((px, py, GREEN if i == 0 else GREEN_MID if i == 1 else GREEN_DEEP))
        lr = R_MAX + 22
        lx, ly = cx + lr * math.cos(a), cy + lr * math.sin(a) + 3
        anchor = "middle" if abs(math.cos(a)) < 0.3 else ("start" if math.cos(a) > 0 else "end")
        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{CHALK if i == 0 else MUTED}" '
            f'font-family="{MONO}" font-size="10" text-anchor="{anchor}">'
            f'{esc(lang["name"])}</text>'
        )
    parts.append(
        f'<polygon class="wb" points="{" ".join(pts)}" fill="{GREEN}" '
        f'fill-opacity=".16" stroke="{GREEN}" stroke-width="1.8" '
        f'style="animation-delay:.24s"/>'
    )
    for i, (px, py, col) in enumerate(dots):
        parts.append(
            f'<circle class="wb" cx="{px:.1f}" cy="{py:.1f}" r="{4 if i == 0 else 3}" '
            f'fill="{col}" style="animation-delay:{0.3 + i*0.05:.2f}s"/>'
        )

    rx = card_x + RADAR_W + 28
    rail_w = card_w - RADAR_W - 28 - 24 - 96 - 46
    ry = LABEL_H + 46
    bar_cols = [GREEN, GREEN_MID, GREEN_DEEP, GREEN_DEEP, GREEN_DARK]
    for i, lang in enumerate(langs):
        d = 0.18 + i * 0.07
        parts.append(f'<g class="r" style="animation-delay:{d:.2f}s">')
        parts.append(
            f'<text x="{rx}" y="{ry + 4}" fill="{CHALK if i == 0 else MUTED}" '
            f'font-family="{MONO}" font-size="12">{esc(lang["name"])}</text>'
        )
        parts.append(
            f'<rect x="{rx + 96}" y="{ry - 4}" width="{rail_w:.0f}" height="8" '
            f'rx="4" fill="{INSET}"/>'
        )
        parts.append(
            f'<rect class="g" x="{rx + 96}" y="{ry - 4}" '
            f'width="{rail_w * lang["pct"] / top:.0f}" height="8" rx="4" '
            f'fill="{bar_cols[i]}" style="animation-delay:{d + 0.1:.2f}s"/>'
        )
        parts.append(
            f'<text x="{card_x + card_w - 24}" y="{ry + 4}" '
            f'fill="{GREEN if i == 0 else MUTED}" font-family="{MONO}" font-size="12" '
            f'font-weight="600" text-anchor="end">{lang["pct"]:.0f}%</text>'
        )
        parts.append("</g>")
        ry += 34
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = write(os.path.join(OUT, "05-stack.svg"), render())
    print(f"wrote assets/05-stack.svg ({n/1024:.1f} KB)")
