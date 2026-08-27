#!/usr/bin/env python3
"""
E5 — contact, and the colophon.

The account BUTTONS are not in here: they are separate SVGs so the README can
wrap each one in a real <a href>. See render_buttons.py. This file is the label
row, the one-line ask with the email as the section's single accent, and the
colophon strip that closes the page.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, DIM, DISPLAY, GREEN, GROUND, MONO, PAD, RADIUS,  # noqa: E402
                   RULE, W, esc, ground, svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "assets")

LABEL_H = 50
CARD_H = 88


def render_ask() -> list[str]:
    with open(os.path.join(ROOT, "data", "identity.json")) as f:
        idn = json.load(f)
    email = idn["email"]

    h = LABEL_H + CARD_H + 16
    card_x, card_w = PAD, W - PAD * 2

    css = """
@keyframes rise{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}
@keyframes blip{0%,100%{opacity:1}50%{opacity:.25}}
.r{animation:rise .55s cubic-bezier(.2,.8,.2,1) both}
.lv{animation:blip 2.4s ease-in-out infinite}
""".strip()

    parts = svg_open(W, h, "Contact", css)
    parts.append(ground(W, h))
    parts.append(
        f'<text x="{PAD}" y="34" fill="{DIM}" font-family="{MONO}" font-size="11" '
        f'font-weight="600" letter-spacing="2.2">CONTACT</text>'
    )
    parts.append(
        f'<circle class="lv" cx="{W - PAD - 118}" cy="30" r="3.5" fill="{GREEN}"/>'
    )
    parts.append(
        f'<text x="{W - PAD}" y="34" fill="{GREEN}" font-family="{MONO}" '
        f'font-size="11" letter-spacing="1.5" text-anchor="end">TAKING ON WORK</text>'
    )

    parts.append(
        f'<rect class="r" x="{card_x + 0.5}" y="{LABEL_H + 0.5}" '
        f'width="{card_w - 1}" height="{CARD_H - 1}" rx="{RADIUS}" fill="#0C1013" '
        f'stroke="{RULE}"/>'
    )
    parts.append(
        f'<text class="r" x="{card_x + 24}" y="{LABEL_H + 52}" fill="{CHALK}" '
        f'font-family="{DISPLAY}" font-size="24" font-weight="600" '
        f'letter-spacing="-.48" style="animation-delay:.08s">'
        f'Design, build, and the ads. Get in touch.</text>'
    )
    pill_w = 22 + len(email) * 7.82 + 22
    pill_x = card_x + card_w - 24 - pill_w
    parts.append(
        f'<g class="r" style="animation-delay:.16s">'
        f'<rect x="{pill_x:.1f}" y="{LABEL_H + 22}" width="{pill_w:.0f}" height="44" '
        f'rx="22" fill="{GREEN}"/>'
        f'<text x="{pill_x + pill_w/2:.1f}" y="{LABEL_H + 49}" fill="{GROUND}" '
        f'font-family="{MONO}" font-size="13" font-weight="700" '
        f'text-anchor="middle">{esc(email)}</text></g>'
    )
    return parts


def render_colophon() -> list[str]:
    h = 62
    parts = svg_open(W, h, "Colophon")
    parts.append(ground(W, h))
    parts.append(f'<line x1="{PAD}" y1="16" x2="{W - PAD}" y2="16" stroke="{RULE}"/>')
    parts.append(
        f'<text x="{PAD}" y="45" fill="{DIM}" font-family="{MONO}" font-size="10" '
        f'letter-spacing="1.6">GENERATED SVG · NO JAVASCRIPT · NO THIRD-PARTY WIDGETS</text>'
    )
    parts.append(
        f'<text x="{W - PAD}" y="45" fill="{DIM}" font-family="{MONO}" font-size="10" '
        f'letter-spacing="1.6" text-anchor="end">REFRESHED DAILY FROM PUBLIC DATA</text>'
    )
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    a = write(os.path.join(OUT, "10-contact.svg"), render_ask())
    b = write(os.path.join(OUT, "12-colophon.svg"), render_colophon())
    print(f"wrote assets/10-contact.svg ({a/1024:.1f} KB)")
    print(f"wrote assets/12-colophon.svg ({b/1024:.1f} KB)")
