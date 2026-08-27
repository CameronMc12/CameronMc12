#!/usr/bin/env python3
"""
The neofetch-style system card: who Cameron is on the left, what the code
actually says on the right.

Half of it is hand-written (data/identity.json — his words, his call) and half
is measured (data/stack.json — real language bytes across all 29 repos,
private included). Avi's reference hand-authors the whole card, which means the
numbers on it are true on the day they are typed and drift from then on. The
split here is deliberate: opinions are edited, facts are computed.

Lines fade and slide in on a short stagger so the panel prints itself next to
the rain, then freezes. No looping.

    python3 scripts/render_card.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import BAR_H, PAD, RADIUS, THEMES, esc, footer_rule, panel, svg_open, write  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT_DIR = os.path.join(ROOT, "assets")

W, H = 524, 360       # hero-right slot; render_hero.py composes it with the rain
KEY_W = 74            # the key column, so every value starts on one line
ROW_H = 19.4
FOOT_H = 40           # streak strip, so the panel floor is not dead space
STAGGER = 0.055       # per-line reveal delay
DUR = 0.5

# languages worth naming on a card this size; the rest collapse into "other"
BAR_KEEP = 5


def load(name: str) -> dict:
    with open(os.path.join(ROOT, "data", name)) as f:
        return json.load(f)


def body(t, W: int, H: int) -> list[str]:
    idn = load("identity.json")
    stack = load("stack.json")
    contrib = load("contributions.json")

    langs = stack["languages"][:BAR_KEEP]
    other = round(100 - sum(l["pct"] for l in langs), 1)

    rows = [
        ("host", f"{idn['handle']} @ github"),
        ("name", idn["name"]),
        ("role", idn["role"]),
        ("locale", idn["location"]),
        (None, None),
        ("now", idn["now"]),
        ("also", idn["also"]),
        ("clients", idn["prev"]),
        (None, None),
        ("repos", f"{stack['repos_total']} ({stack['repos_public']} public, "
                  f"{stack['repos_private']} private)"),
        ("uptime", f"since {stack['member_since']}, {stack['code_bytes']/1e6:.0f} MB tracked"),
        ("commits", f"{contrib['total_contributions']:,} in the last year"),
    ]

    css = f"""
@keyframes in{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:translateY(0)}}}}
.r{{opacity:0;animation:in {DUR}s cubic-bezier(.2,.8,.2,1) both}}
.k{{fill:{t.dim};font-size:11px}}
.v{{fill:{t.text};fill-opacity:.92;font-size:11.5px}}
.vd{{fill:{t.muted};font-size:11.5px}}
.lbl{{fill:{t.muted};font-size:9.5px;letter-spacing:1.2px;font-weight:600}}
""".strip()

    parts = [f"<style>{css}</style>"]
    parts += panel(t, W, H, "system", "neofetch", uid="cd")

    y = BAR_H + PAD + 4
    step = 0
    for key, val in rows:
        if key is None:
            y += ROW_H * 0.45
            continue
        d = step * STAGGER
        step += 1
        parts.append(f'<g class="r" style="animation-delay:{d:.2f}s">')
        parts.append(f'<text class="k" x="{PAD}" y="{y:.1f}">{esc(key)}</text>')
        cls = "v" if key in ("host", "name", "now", "commits") else "vd"
        parts.append(f'<text class="{cls}" x="{PAD + KEY_W}" y="{y:.1f}">{esc(val)}</text>')
        parts.append("</g>")
        y += ROW_H

    # --- language bar: measured, not claimed --------------------------------
    y += 4
    bar_y = y + 11
    bar_w = W - PAD * 2
    parts.append(f'<g class="r" style="animation-delay:{step*STAGGER:.2f}s">')
    parts.append(f'<text class="lbl" x="{PAD}" y="{y:.1f}">LANGUAGE MIX</text>')
    parts.append(
        f'<text class="k" x="{W-PAD}" y="{y:.1f}" text-anchor="end">'
        f'{stack["repos_total"]} repos</text>'
    )
    parts.append(
        f'<rect x="{PAD}" y="{bar_y:.1f}" width="{bar_w}" height="9" rx="4.5" '
        f'fill="{t.inset}"/>'
    )
    # clip the fills to the pill so the ends stay round without per-segment radii
    parts.append(
        f'<defs><clipPath id="cdbar"><rect x="{PAD}" y="{bar_y:.1f}" '
        f'width="{bar_w}" height="9" rx="4.5"/></clipPath></defs>'
        f'<g clip-path="url(#cdbar)">'
    )
    x = PAD
    shades = [t.accent, t.accent_dim, t.muted, t.dim, t.border_strong]
    for i, l in enumerate(langs):
        seg = bar_w * l["pct"] / 100
        parts.append(
            f'<rect x="{x:.1f}" y="{bar_y:.1f}" width="{seg:.1f}" height="9" '
            f'fill="{shades[i]}"/>'
        )
        x += seg
    parts.append("</g>")

    ly = bar_y + 24
    lx = PAD
    # advance measured from the glyph count at 10.5px mono (6.31px/char), not
    # guessed: the first pass ran "63%" straight into the next legend dot
    for i, l in enumerate(langs):
        label = f'{l["name"]} {l["pct"]:.0f}%'
        parts.append(f'<circle cx="{lx+3.5:.1f}" cy="{ly-3.5:.1f}" r="3.5" fill="{shades[i]}"/>')
        parts.append(
            f'<text class="vd" x="{lx+12:.1f}" y="{ly:.1f}" font-size="10.5">'
            f'{esc(l["name"])} <tspan fill="{t.dim}">{l["pct"]:.0f}%</tspan></text>'
        )
        lx += 12 + len(label) * 6.31 + 13
    parts.append("</g>")

    # --- footer: the cadence numbers, one accent among them -----------------
    fy = H - FOOT_H
    cs = contrib["current_streak"]["length"]
    ls = contrib["longest_streak"]["length"]
    parts.append(footer_rule(t, W, fy))
    parts.append(f'<g class="r" style="animation-delay:{(step+1)*STAGGER:.2f}s">')
    parts.append(
        f'<text x="{PAD}" y="{fy + 24:.0f}" font-size="11" fill="{t.muted}">'
        f'streak <tspan fill="{t.accent}" font-weight="700">{cs}d</tspan>'
        f'<tspan fill="{t.dim}">   ·   longest </tspan>'
        f'<tspan fill="{t.text}" fill-opacity=".9">{ls}d</tspan>'
        f'<tspan fill="{t.dim}">   ·   busiest </tspan>'
        f'<tspan fill="{t.text}" fill-opacity=".9">{esc(contrib["busiest_weekday"])}</tspan></text>'
    )
    parts.append(
        f'<text x="{W-PAD}" y="{fy + 24:.0f}" font-size="10.5" fill="{t.dim}" '
        f'text-anchor="end">{contrib["last_30_total"]:,} in the last 30 days</text>'
    )
    parts.append("</g>")

    return parts


def render(theme_name: str) -> list[str]:
    t = THEMES[theme_name]
    parts = svg_open(W, H, "System card")
    parts.append(f'<rect width="{W}" height="{H}" fill="{t.ground}"/>')
    return parts + body(t, W, H)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in ("dark", "light"):
        n = write(os.path.join(OUT_DIR, f"card-{name}.svg"), render(name))
        print(f"wrote assets/card-{name}.svg ({n/1024:.1f} KB)")


if __name__ == "__main__":
    main()
