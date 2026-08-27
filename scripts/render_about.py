#!/usr/bin/env python3
"""
S2 — who he is, in two lines and four bullets.

Deliberately has NO section label and no headline. It is the first thing under
the hero, so it introduces itself; a label row here would be the third piece of
chrome in 400px. Everything below it carries a label instead.

Copy comes from data/identity.json so Cameron owns every word.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, DISPLAY, GREEN, MONO, MUTED, PAD, REVEAL_CSS, RULE,  # noqa: E402
                   W, esc, ground, svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "assets")

LEFT_W = 440
DIVIDER = PAD + LEFT_W
RIGHT_X = DIVIDER + 34


def wrap(text: str, per_line: int) -> list[str]:
    """Greedy wrap. SVG has no flow layout, so the line breaks are decided here
    rather than by the renderer."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if len(trial) > per_line and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def render() -> list[str]:
    with open(os.path.join(ROOT, "data", "identity.json")) as f:
        idn = json.load(f)

    sub_lines = wrap(idn["summary"], 52)
    caps = idn["capabilities"]

    top = 38
    h = top + 36 + 10 + len(sub_lines) * 27 + 36
    h = max(h, top + 6 + len(caps) * 25 + 30)

    parts = svg_open(W, h, "What I do", REVEAL_CSS)
    parts.append(ground(W, h))

    y = top + 28
    parts.append(
        f'<text class="r" x="{PAD}" y="{y}" fill="{CHALK}" font-family="{DISPLAY}" '
        f'font-size="27" font-weight="700" letter-spacing="-.6">{esc(idn["role"])}</text>'
    )
    y += 20
    for i, line in enumerate(sub_lines):
        y += 27
        parts.append(
            f'<text class="r" x="{PAD}" y="{y}" fill="{MUTED}" font-family="{DISPLAY}" '
            f'font-size="17" font-weight="300" style="animation-delay:{.08 + i*.05:.2f}s">'
            f"{esc(line)}</text>"
        )

    parts.append(
        f'<line x1="{DIVIDER}" y1="{top + 2}" x2="{DIVIDER}" y2="{h - 26}" stroke="{RULE}"/>'
    )

    cy = top + 22
    for i, cap in enumerate(caps):
        d = 0.16 + i * 0.06
        parts.append(f'<g class="w" style="animation-delay:{d:.2f}s">')
        parts.append(
            f'<text x="{RIGHT_X}" y="{cy}" fill="{GREEN}" font-family="{MONO}" '
            f'font-size="11">›</text>'
        )
        parts.append(
            f'<text x="{RIGHT_X + 20}" y="{cy}" fill="{CHALK}" font-family="{MONO}" '
            f'font-size="12.5">{esc(cap)}</text>'
        )
        parts.append("</g>")
        cy += 25
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = write(os.path.join(OUT, "02-about.svg"), render())
    print(f"wrote assets/02-about.svg ({n/1024:.1f} KB)")
