#!/usr/bin/env python3
"""
Tokens and shared chrome for every section SVG.

Direction: "Matrix mainframe". Near-black ground, one phosphor-green accent, mono
labels, generous negative space. Every section is a compact band you glance at
rather than a landing-page slab you read — one small caps label on the left, its
context on the right, then the content. No section headlines.

DARK ONLY, on purpose. Digital rain and ASCII shading only read against black,
and the page is designed as one continuous dark surface. There is no light pair;
a GitHub reader in light mode gets a deliberate dark page, the way a photograph
does not invert.

The page is authored at 846px, which is GitHub's profile README column at a
1512px viewport, and scales down from there.
"""
from __future__ import annotations

import html

W = 846                    # GitHub's profile README column, measured
PAD = 44                   # page gutter
GAP = 12                   # gap between cards inside a section
RADIUS = 10

MONO = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")
DISPLAY = ("'Archivo', ui-sans-serif, system-ui, -apple-system, "
           "'Helvetica Neue', Arial, sans-serif")

GROUND = "#07090A"
PANEL = "#0C1013"
INSET = "#111619"
RULE = "#1A2226"
RULE_STRONG = "#26333A"
CHALK = "#E7F0EA"
MUTED = "#7E9188"
DIM = "#495D54"

GREEN = "#00FF41"          # phosphor, the accent
GREEN_MID = "#12B24A"
GREEN_DEEP = "#0B7A2C"
GREEN_DARK = "#0A3D1B"
WHITE_HOT = "#D8FFE4"      # the bright head of a rain drop

# heatmap ramp, empty -> max
RAMP = ["#141A1D", GREEN_DARK, GREEN_DEEP, GREEN_MID, GREEN, WHITE_HOT]

LABEL_H = 50               # the compact section label row


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def svg_open(w: int, h: int, title: str, css: str = "") -> list[str]:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">',
        f"<title>{esc(title)}</title>",
    ]
    if css:
        parts.append(f"<style>{css}</style>")
    return parts


def ground(w: int = W, h: int = 0) -> str:
    return f'<rect width="{w}" height="{h}" fill="{GROUND}"/>'


def label_row(left: str, right: str, y: int = 0, w: int = W) -> str:
    """The one piece of chrome every section shares: small caps label on the
    left, context on the right. Replaces the eyebrow + 34px headline pattern,
    which added ~90px a section and made the page read as a pitch."""
    return (
        f'<text x="{PAD}" y="{y + 34}" fill="{DIM}" font-family="{MONO}" '
        f'font-size="11" font-weight="600" letter-spacing="2.2">{esc(left.upper())}</text>'
        f'<text x="{w - PAD}" y="{y + 34}" fill="{DIM}" font-family="{MONO}" '
        f'font-size="11" letter-spacing="1.1" text-anchor="end">{esc(right.upper())}</text>'
    )


def card(x: float, y: float, w: float, h: float, uid: str = "",
         fill: str = PANEL) -> str:
    return (
        f'<rect x="{x + 0.5:.1f}" y="{y + 0.5:.1f}" width="{w - 1:.1f}" '
        f'height="{h - 1:.1f}" rx="{RADIUS}" fill="{fill}" stroke="{RULE}"/>'
    )


def write(path: str, parts: list[str]) -> int:
    parts.append("</svg>")
    body = "".join(parts)
    with open(path, "w") as f:
        f.write(body)
    return len(body)


# --- shared motion ---------------------------------------------------------
# Reveals play ONCE and freeze (`both`, no repeatCount). The only things that
# loop are textures: the rain, and the nudge on a button arrow. A read-out that
# pulses forever is a screensaver.
REVEAL_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes wipe{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes pop{from{opacity:0;transform:translateY(-5px) scale(.86)}to{opacity:1;transform:none}}
.r{animation:rise .52s cubic-bezier(.2,.8,.2,1) both}
.w{animation:wipe .5s cubic-bezier(.2,.8,.2,1) both}
.g{transform-origin:left center;animation:grow .7s cubic-bezier(.2,.8,.2,1) both}
""".strip()
