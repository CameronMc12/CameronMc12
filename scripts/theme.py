#!/usr/bin/env python3
"""
Shared design tokens + panel chrome for every profile SVG.

Direction: "Float instrument panel" -- the grammar from Cameron's Float finance
OS applied to a GitHub profile. Panels with labelled bars, near-monochrome
surfaces, one accent (lime) reserved for the number that matters. Not a green
hacker terminal.

The single deliberate exception is the Matrix rain panel, which runs in movie
phosphor green. It is a texture, not chrome -- see DESIGN.md section 10.

Every renderer emits a dark and a light file; the README picks between them with
<picture media="(prefers-color-scheme: dark)">, which GitHub honours.
"""
from __future__ import annotations

import html

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


class Theme:
    def __init__(self, name: str, **kw):
        self.name = name
        for k, v in kw.items():
            setattr(self, k, v)


DARK = Theme(
    "dark",
    ground="#0A0A0B",
    panel="#131315",
    panel_top="#17171A",     # top of the panel gradient
    inset="#1B1B1F",
    border="#242428",
    border_strong="#33333A",
    text="#EDEDEF",
    muted="#8A8A93",
    dim="#56565E",
    accent="#E4F222",        # lime -- the one accent
    accent_dim="#8E991A",
    ramp=["#1C1C20", "#3F450F", "#6C7714", "#9CAD16", "#C4DA1C", "#E4F222"],
    phosphor="#00FF41",      # matrix rain only
    phosphor_dim="#0B7A2C",
    phosphor_head="#D8FFE4",
    # ASCII shading floor. On black, a sparse glyph still glows, so the ramp can
    # use its whole range.
    ramp_floor=0.0,
)

LIGHT = Theme(
    "light",
    ground="#F6F6F3",
    panel="#FFFFFF",
    panel_top="#FFFFFF",
    inset="#F2F2EE",
    border="#E3E3DE",
    border_strong="#CFCFC8",
    text="#16161A",
    muted="#6C6C74",
    dim="#9C9CA4",
    accent="#6E7D00",        # lime reads as deep olive on white
    accent_dim="#A9BC12",
    ramp=["#ECECE6", "#DDE79B", "#C6D850", "#A9C000", "#85991A", "#5E6E12"],
    phosphor="#0F9D3A",
    phosphor_dim="#8FD0A4",
    phosphor_head="#04471A",
    # On white the same sparse glyph is a ghost -- ink is what you SEE, so every
    # lit cell has to sit in the dense half of the ramp or the wordmark vanishes.
    ramp_floor=0.52,
)

THEMES = {"dark": DARK, "light": LIGHT}

# --- panel geometry (Float grammar) ---------------------------------------
RADIUS = 14
BAR_H = 38
PAD = 18
FOOT_H = 40


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def svg_open(w: int, h: int, title: str, css: str = "") -> list[str]:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}" '
        f'font-family="{MONO}">',
        f"<title>{esc(title)}</title>",
    ]
    if css:
        parts.append(f"<style>{css}</style>")
    return parts


def panel(t: Theme, w: int, h: int, label: str, meta: str = "", uid: str = "p",
          ground: bool = True) -> list[str]:
    """Panel shell: rounded card + labelled top bar. `ground` paints the page
    behind it, which a composed panel must not do -- it would repaint over its
    neighbour."""
    return ([f'<rect width="{w}" height="{h}" fill="{t.ground}"/>'] if ground else []) + [
        "<defs>"
        f'<linearGradient id="{uid}g" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t.panel_top}"/>'
        f'<stop offset="1" stop-color="{t.panel}"/></linearGradient>'
        "</defs>",
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{RADIUS}" '
        f'fill="url(#{uid}g)" stroke="{t.border}" stroke-width="1"/>',
        f'<line x1="1" y1="{BAR_H}" x2="{w-1}" y2="{BAR_H}" stroke="{t.border}"/>',
        f'<text x="{PAD}" y="{BAR_H/2 + 4:.0f}" fill="{t.muted}" font-size="10" '
        f'letter-spacing="1.4" font-weight="600">{esc(label.upper())}</text>',
    ] + (
        [
            f'<text x="{w-PAD}" y="{BAR_H/2 + 4:.0f}" fill="{t.dim}" font-size="10" '
            f'letter-spacing="0.6" text-anchor="end">{esc(meta)}</text>'
        ]
        if meta
        else []
    )


# The two ART panels (rain, wordmark) keep a near-black body in BOTH themes;
# only the DATA panels (system, contributions) follow the reader's theme.
# ASCII and digital rain are photographs, not chrome: their whole read depends
# on sparse marks glowing against black, and on white the same marks are a
# ghost no amount of ink opacity rescues. Only the outer frame adapts, so on a
# white README they sit as deliberate dark cards rather than broken ones.
ART_BG = "#08090A"
ART_BAR = "#0B0C0E"
ART_RULE = "#22252A"
ART_LABEL = "#8A8A93"
ART_META = "#56565E"


def art_panel(t: Theme, w: int, h: int, label: str, meta: str, uid: str) -> list[str]:
    """Always-dark card + bar. Caller draws its content between this and
    art_frame(), clipped to url(#<uid>card)."""
    return [
        f'<defs><clipPath id="{uid}card"><rect x="0.5" y="0.5" width="{w-1}" '
        f'height="{h-1}" rx="{RADIUS}"/></clipPath></defs>',
        f'<g clip-path="url(#{uid}card)">',
        f'<rect width="{w}" height="{h}" fill="{ART_BG}"/>',
    ]


def art_bar(w: int, label: str, meta: str) -> str:
    return (
        f'<rect y="0" width="{w}" height="{BAR_H}" fill="{ART_BAR}"/>'
        f'<line x1="0" y1="{BAR_H}" x2="{w}" y2="{BAR_H}" stroke="{ART_RULE}"/>'
        f'<text x="{PAD}" y="{BAR_H/2 + 4:.0f}" fill="{ART_LABEL}" font-size="10" '
        f'letter-spacing="1.4" font-weight="600">{esc(label.upper())}</text>'
        f'<text x="{w-PAD}" y="{BAR_H/2 + 4:.0f}" fill="{ART_META}" font-size="10" '
        f'letter-spacing="0.6" text-anchor="end">{esc(meta)}</text>'
    )


def art_frame(t: Theme, w: int, h: int) -> str:
    """Closes the card clip and strokes the outer frame. On light the border has
    to work harder to separate a dark card from a white page."""
    stroke = t.border if t.name == "dark" else "#C9C9C2"
    return (
        "</g>"
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{RADIUS}" '
        f'fill="none" stroke="{stroke}" stroke-width="1"/>'
    )


def footer_rule(t: Theme, w: int, y: float) -> str:
    return f'<line x1="1" y1="{y:.1f}" x2="{w-1}" y2="{y:.1f}" stroke="{t.border}"/>'


def write(path: str, parts: list[str]) -> int:
    parts.append("</svg>")
    body = "".join(parts)
    with open(path, "w") as f:
        f.write(body)
    return len(body)
