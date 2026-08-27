#!/usr/bin/env python3
"""
Compose the rain and the system card into ONE 880-wide hero SVG.

Why one file instead of two images in a <table>: GitHub's README column is not
a fixed width, so two <img> tags with fixed widths get scaled by different
amounts at different viewports and the two panels stop being the same height.
Avi's reference lives with that (his two panels land "within 5px"); composing
them into a single SVG makes the alignment exact at every width, for free.

    python3 scripts/render_hero.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_card  # noqa: E402
import render_matrix  # noqa: E402
from theme import THEMES, svg_open, write  # noqa: E402

OUT_DIR = os.path.join(HERE, "..", "assets")

W, H = 880, 360
GAP = 16
LEFT_W = render_matrix.W       # 340
RIGHT_W = render_card.W        # 524

assert LEFT_W + GAP + RIGHT_W == W, (
    f"hero slots must sum to {W}: {LEFT_W} + {GAP} + {RIGHT_W} = "
    f"{LEFT_W + GAP + RIGHT_W}"
)


def render(theme_name: str) -> list[str]:
    t = THEMES[theme_name]
    parts = svg_open(W, H, "Cameron McAllister — GitHub profile")
    parts.append(f'<rect width="{W}" height="{H}" fill="{t.ground}"/>')
    parts.append("<g>")
    parts += render_matrix.body(t, "green", LEFT_W, H)
    parts.append("</g>")
    parts.append(f'<g transform="translate({LEFT_W + GAP},0)">')
    parts += render_card.body(t, RIGHT_W, H)
    parts.append("</g>")
    return parts


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in ("dark", "light"):
        n = write(os.path.join(OUT_DIR, f"hero-{name}.svg"), render(name))
        print(f"wrote assets/hero-{name}.svg ({n/1024:.0f} KB)")


if __name__ == "__main__":
    main()
