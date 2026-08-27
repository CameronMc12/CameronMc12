#!/usr/bin/env python3
"""
The account buttons — one small SVG each, so the README can wrap them in real
<a href> tags.

Why one file per button and not one strip: GitHub renders a README SVG inside an
<img>, which kills every link INSIDE the SVG. An <a> in the markdown wrapping an
<img> is the only thing that actually clicks through. So each button is its own
image and the anchor lives in the README.

That same sandbox is why there is no hover state. Pointer events never reach the
image, so :hover, transitions and cursor changes are all inert — anything
depending on them would be a control that looks alive and is not. What does run
is declarative animation, so each button gets an entry slide and its arrow keeps
a slow diagonal nudge. The nudge is the affordance: it is the only honest way to
say "this goes somewhere" inside an image.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, GREEN, MONO, PANEL, RULE, RULE_STRONG, GROUND,  # noqa: E402
                   esc, svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "assets")

H = 46
PAD_L = 22
PAD_R = 18
GAP = 14
ARROW = 11
FONT = 13
CHAR_W = 7.82        # JetBrains-ish mono advance at 13px, measured
RADIUS = 23


def render(label: str, accent: bool, delay: float) -> tuple[list[str], int]:
    text_w = len(label) * CHAR_W
    w = int(PAD_L + text_w + GAP + ARROW + PAD_R)

    fg = GROUND if accent else CHALK
    arrow_fg = GROUND if accent else GREEN
    bg = GREEN if accent else PANEL
    border = GREEN if accent else RULE_STRONG

    css = f"""
@keyframes inn{{from{{opacity:0;transform:translateY(7px)}}to{{opacity:1;transform:none}}}}
@keyframes nudge{{0%,72%{{transform:none}}80%{{transform:translate(2.4px,-2.4px)}}100%{{transform:none}}}}
.btn{{animation:inn .5s cubic-bezier(.2,.8,.2,1) {delay:.2f}s both}}
.ar{{animation:nudge 2.6s ease-in-out {delay + 0.9:.2f}s infinite}}
""".strip()

    # NO background rect. The buttons sit inline in the README, on whatever
    # ground GitHub is painting; a ground of our own shows as a darker patch
    # against #0d1117 and the row reads as a mis-tinted band.
    parts = svg_open(w, H, f"{label} — opens in a new tab", css)
    parts.append('<g class="btn">')
    parts.append(
        f'<rect x="1" y="1" width="{w - 2}" height="{H - 2}" rx="{RADIUS}" '
        f'fill="{bg}" stroke="{border}" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{PAD_L}" y="{H/2 + 4.5:.0f}" fill="{fg}" font-family="{MONO}" '
        f'font-size="{FONT}" font-weight="{700 if accent else 500}" '
        f'letter-spacing=".3">{esc(label)}</text>'
    )
    ax = PAD_L + text_w + GAP
    ay = H / 2
    # The positioning transform lives on the OUTER group and the animation on an
    # inner one. A CSS `transform` in a keyframe replaces the element's
    # transform ATTRIBUTE outright rather than composing with it, so animating
    # the positioned group teleports the arrow to the origin the moment the
    # animation starts.
    parts.append(
        f'<g transform="translate({ax:.1f},{ay:.1f})"><g class="ar">'
        f'<path d="M-4 4 L4 -4" stroke="{arrow_fg}" stroke-width="1.7" '
        f'stroke-linecap="round"/>'
        f'<path d="M-0.6 -4 L4 -4 L4 0.6" stroke="{arrow_fg}" stroke-width="1.7" '
        f'stroke-linecap="round" stroke-linejoin="round" fill="none"/></g></g>'
    )
    parts.append("</g>")
    return parts, w


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(ROOT, "data", "identity.json")) as f:
        accounts = json.load(f)["accounts"]
    total = 0
    for i, acct in enumerate(accounts):
        slug = acct["label"].lower().replace(" ", "-")
        parts, w = render(acct["label"], accent=(i == 0), delay=0.06 + i * 0.08)
        n = write(os.path.join(OUT, f"btn-{slug}.svg"), parts)
        total += w
        print(f"  btn-{slug}.svg  {w}px  {n/1024:.1f} KB")
    print(f"{len(accounts)} buttons, {total}px wide before gaps")
