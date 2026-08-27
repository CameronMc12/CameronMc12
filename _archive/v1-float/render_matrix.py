#!/usr/bin/env python3
"""
Animated Matrix digital-rain panel, as pure SVG (no JS -- GitHub strips it).

How it loops seamlessly: each column holds a strip of 2R glyphs whose bottom
half is an exact copy of the top half, and the whole column translates down by
exactly R rows, forever. Because the content is periodic over R rows the wrap
point is invisible, so there is no restart flash.

How the falling drops are made: the trail is BAKED INTO the strip rather than
animated. Every L glyphs the opacity resets to 1 (the head, rendered near-white
like the film) and decays upward into the tail. Scrolling that fixed pattern
past a clip window is indistinguishable from individually falling drops, and it
costs one CSS animation per column instead of one per glyph.

Glyph mutation (the shimmer) is a short opacity flicker on ~9% of glyphs. It
multiplies with the baked fill-opacity rather than replacing it, which is why
the trail gradient survives the flicker.

Palette: this panel is the ONE place phosphor green is allowed. Cameron asked
for the film look and it is a texture, not chrome -- everything else in the
profile is monochrome with a single lime accent. See DESIGN.md section 10.

    python3 scripts/render_matrix.py            # writes assets/matrix-{dark,light}.svg
    python3 scripts/render_matrix.py --palette lime   # accent-coloured variant
"""
from __future__ import annotations

import argparse
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (ART_BG, BAR_H, DARK, PAD, RADIUS, THEMES, art_bar, art_frame,
                   art_panel, esc, svg_open, write)  # noqa: E402

OUT_DIR = os.path.join(HERE, "..", "assets")

W, H = 340, 360       # hero-left slot; render_hero.py composes it with the card
FONT = 15.5
CELL_W = 8.6          # advance width of the half-width katakana at this size
LINE_H = 17.0
SEED = 20260827       # fixed so re-renders don't churn the diff

# the half-width katakana the film used, plus the digits and rules that break
# up the texture. no full-width glyphs -- they double the advance and the
# columns stop lining up.
GLYPHS = (
    "ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ"
    "0123456789"
    "ｦｨｩｪｫｬｭｮｯｰｱｲｳｴｵ"
    ":=*+-<>|╌"
)

# drop lengths must divide R or the strip stops being periodic and the loop
# develops a visible seam.
DROP_LENGTHS = [12, 18, 24, 36]
FLICKER_SHARE = 0.09
OPACITY_STEPS = 12    # baked trail resolution, emitted as CSS classes


def build_column(rng: random.Random, rows: int) -> list[tuple[str, int, bool]]:
    """One half-strip: (glyph, opacity_step, flickers). Doubled by the caller."""
    length = rng.choice([d for d in DROP_LENGTHS if rows % d == 0])
    phase = rng.randrange(length)
    out = []
    for i in range(rows):
        pos = (i + phase) % length          # 0 = tail end, length-1 = head
        t = pos / (length - 1)
        # ease the trail so the head reads as a point of light and the tail
        # dissolves, instead of a flat linear wedge
        step = max(1, min(OPACITY_STEPS, round((t ** 2.4) * OPACITY_STEPS)))
        out.append((rng.choice(GLYPHS), step, rng.random() < FLICKER_SHARE))
    return out


def body(t, palette: str, W: int, H: int) -> list[str]:
    """
    The rain field keeps a near-black ground in BOTH themes. Digital rain is a
    photograph, not chrome -- the trail only reads because it fades into black,
    and inverting it for light mode produced a washed-out ghost with no drama
    (see docs/04-design/baselines/matrix-light-rejected.png). Only the panel
    frame and label adapt, so on a white README it sits as a deliberate dark
    card rather than a broken one.
    """
    theme_name = t.name
    rng = random.Random(SEED)

    field_bg = ART_BG
    content_top = BAR_H
    content_h = H - content_top
    inner_w = W - 2
    cols = int(inner_w // CELL_W) + 1
    rows = 36
    strip_h = rows * LINE_H

    if palette == "lime":
        head, hot, cold = "#FFFFFF", "#E4F222", "#6E7A12"
    else:
        head, hot, cold = DARK.phosphor_head, DARK.phosphor, DARK.phosphor_dim

    ladder = []
    for s_ in range(1, OPACITY_STEPS + 1):
        o = 0.05 + 0.95 * (s_ / OPACITY_STEPS)
        col = cold if s_ <= OPACITY_STEPS * 0.45 else hot
        ladder.append(f".o{s_}{{fill:{col};fill-opacity:{o:.2f}}}")

    css = f"""
@keyframes fall{{from{{transform:translateY(-{strip_h:.0f}px)}}to{{transform:translateY(0)}}}}
@keyframes flick{{0%,86%{{opacity:1}}88%{{opacity:.18}}90%{{opacity:1}}95%{{opacity:.45}}100%{{opacity:1}}}}
.col{{animation:fall linear infinite;will-change:transform}}
.f{{animation:flick steps(1,end) infinite}}
{''.join(ladder)}
.hd{{fill:{head};fill-opacity:1}}
text{{font-size:{FONT}px;font-family:'Hiragino Kaku Gothic ProN','Yu Gothic','MS Gothic',ui-monospace,monospace}}
""".strip()

    parts = [f"<style>{css}</style>"]
    parts.append(
        "<defs>"
        f'<clipPath id="mxclip"><rect x="1" y="{content_top}" '
        f'width="{inner_w}" height="{content_h - 1}"/></clipPath>'
        f'<linearGradient id="mxfade" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{field_bg}" stop-opacity="1"/>'
        f'<stop offset="0.10" stop-color="{field_bg}" stop-opacity="0"/>'
        f'<stop offset="0.88" stop-color="{field_bg}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{field_bg}" stop-opacity="0.92"/>'
        "</linearGradient></defs>"
    )

    parts += art_panel(t, W, H, "identity", "matrix.sh", uid="mx")

    # the rain, edge to edge under the bar
    parts.append('<g clip-path="url(#mxclip)">')
    x0 = 1 + (inner_w - (cols - 1) * CELL_W) / 2
    for c in range(cols):
        strip = build_column(rng, rows)
        dur = rng.uniform(5.5, 15.0)
        offset = -rng.uniform(0, dur)
        x = x0 + c * CELL_W
        parts.append(
            f'<g class="col" style="animation-duration:{dur:.2f}s;'
            f'animation-delay:{offset:.2f}s">'
        )
        parts.append(f'<text x="{x:.1f}" y="{content_top - strip_h + LINE_H:.1f}">')
        first = True
        for _rep in range(2):
            for g, step, flick in strip:
                is_head = step == OPACITY_STEPS
                cls = "hd" if is_head else f"o{step}"
                extra = ""
                if flick and not is_head:
                    cls += " f"
                    extra = (
                        f' style="animation-duration:{rng.uniform(1.4, 4.2):.2f}s;'
                        f'animation-delay:-{rng.uniform(0, 4):.2f}s"'
                    )
                dy = "0" if first else f"{LINE_H:.0f}"
                first = False
                parts.append(
                    f'<tspan x="{x:.1f}" dy="{dy}" class="{cls}"{extra}>{esc(g)}</tspan>'
                )
        parts.append("</text></g>")
    parts.append("</g>")

    # feather the top and bottom so the rain enters and leaves the window
    parts.append(
        f'<rect x="1" y="{content_top}" width="{inner_w}" height="{content_h - 1}" '
        f'fill="url(#mxfade)"/>'
    )

    parts.append(art_bar(W, "identity", "matrix.sh"))
    parts.append(art_frame(t, W, H))
    return parts


def render(theme_name: str, palette: str) -> list[str]:
    t = THEMES[theme_name]
    parts = svg_open(W, H, "Matrix digital rain")
    parts.append(f'<rect width="{W}" height="{H}" fill="{t.ground}"/>')
    return parts + body(t, palette, W, H)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--palette", choices=["green", "lime"], default="green",
                    help="green = film phosphor (default); lime = the profile accent")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    suffix = "" if args.palette == "green" else "-lime"
    for name in ("dark", "light"):
        path = os.path.join(OUT_DIR, f"matrix{suffix}-{name}.svg")
        n = write(path, render(name, args.palette))
        print(f"wrote assets/matrix{suffix}-{name}.svg ({n/1024:.0f} KB)")


if __name__ == "__main__":
    main()
