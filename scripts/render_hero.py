#!/usr/bin/env python3
"""
S1 — the hero. A full-bleed Matrix rain viewport with HUD corner brackets and
the name over it.

How the rain loops seamlessly: each column holds 2R glyphs whose bottom half is
an exact copy of the top half, and the column translates down by exactly R rows,
forever. Because the content is periodic over R rows the wrap point is invisible,
so there is no restart flash.

How the drops are made: the trail is BAKED INTO the strip rather than animated.
Every L glyphs the opacity resets to 1 (the head, near-white like the film) and
decays upward into the tail. Scrolling that fixed pattern past a clip window is
indistinguishable from individually falling drops, and it costs one CSS
animation per column instead of one per glyph.
"""
from __future__ import annotations

import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, DIM, GREEN, GREEN_DEEP, GROUND, MONO, MUTED,  # noqa: E402
                   PAD, W, WHITE_HOT, DISPLAY, esc, svg_open, write)

OUT = os.path.join(HERE, "..", "assets")

H = 360
FIELD_BG = "#050607"
FONT = 15.0
CELL_W = 17.2         # column pitch; a wider pitch than the field reads as rain
                      # rather than as a wall of text
LINE_H = 20.0
ROWS = 36             # half-strip height in glyphs; the strip is doubled
SEED = 20260827       # fixed, so a re-render is not a diff

GLYPHS = ("ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ"
          "0123456789ｦｨｩｪｫｬｭｮｯｰｱｲｳｴｵ:=*+-<>|")

# drop lengths must divide ROWS or the strip stops being periodic and the loop
# develops a visible seam
DROP_LENGTHS = [12, 18, 36]
FLICKER_SHARE = 0.08
STEPS = 12            # baked trail resolution, emitted as CSS classes


def build_column(rng: random.Random) -> list[tuple[str, int, bool]]:
    length = rng.choice(DROP_LENGTHS)
    phase = rng.randrange(length)
    out = []
    for i in range(ROWS):
        pos = (i + phase) % length          # 0 = tail end, length-1 = head
        t = pos / (length - 1)
        # eased so the head reads as a point of light and the tail dissolves,
        # instead of a flat linear wedge
        step = max(1, min(STEPS, round((t ** 2.4) * STEPS)))
        out.append((rng.choice(GLYPHS), step, rng.random() < FLICKER_SHARE))
    return out


def render() -> list[str]:
    rng = random.Random(SEED)
    strip_h = ROWS * LINE_H
    cols = int(W // CELL_W) + 1

    ladder = []
    for s in range(1, STEPS + 1):
        o = 0.05 + 0.95 * (s / STEPS)
        col = GREEN_DEEP if s <= STEPS * 0.45 else GREEN
        ladder.append(f".o{s}{{fill:{col};fill-opacity:{o:.2f}}}")

    css = f"""
@keyframes fall{{from{{transform:translateY(-{strip_h:.0f}px)}}to{{transform:translateY(0)}}}}
@keyframes flick{{0%,86%{{opacity:1}}88%{{opacity:.18}}90%{{opacity:1}}95%{{opacity:.45}}100%{{opacity:1}}}}
@keyframes bracket{{from{{opacity:0;transform:scale(.82)}}to{{opacity:1;transform:none}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
.col{{animation:fall linear infinite;will-change:transform}}
.f{{animation:flick steps(1,end) infinite}}
.bk{{animation:bracket .5s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:center}}
.r{{animation:rise .6s cubic-bezier(.2,.8,.2,1) both}}
{''.join(ladder)}
.hd{{fill:{WHITE_HOT};fill-opacity:1}}
.gl{{font-size:{FONT}px;font-family:'Hiragino Kaku Gothic ProN','Yu Gothic','MS Gothic',{MONO}}}
""".strip()

    parts = svg_open(W, H, "Cameron McAllister — GitHub profile", css)
    parts.append(
        "<defs>"
        f'<clipPath id="hv"><rect width="{W}" height="{H}"/></clipPath>'
        f'<radialGradient id="wash" cx="50%" cy="48%" r="72%">'
        f'<stop offset="0" stop-color="{FIELD_BG}" stop-opacity="0.62"/>'
        f'<stop offset="0.56" stop-color="{FIELD_BG}" stop-opacity="0.88"/>'
        f'<stop offset="1" stop-color="{GROUND}" stop-opacity="1"/>'
        "</radialGradient></defs>"
    )
    parts.append(f'<rect width="{W}" height="{H}" fill="{FIELD_BG}"/>')
    parts.append('<g clip-path="url(#hv)">')

    x0 = (W - (cols - 1) * CELL_W) / 2
    for c in range(cols):
        strip = build_column(rng)
        dur = rng.uniform(6.0, 16.0)
        offset = -rng.uniform(0, dur)        # negative delay = start mid-fall
        x = x0 + c * CELL_W
        parts.append(
            f'<g class="col" style="animation-duration:{dur:.2f}s;'
            f'animation-delay:{offset:.2f}s">'
        )
        parts.append(f'<text class="gl" x="{x:.1f}" y="{-strip_h + LINE_H:.1f}">')
        first = True
        for _rep in range(2):
            for g, step, flick in strip:
                is_head = step == STEPS
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

    # the wash sits on the rain so the type has something to sit on
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#wash)"/>')

    # HUD corner brackets, popping in on a stagger
    b, t_, s = 34, 3, 26      # bracket arm, stroke, inset
    for i, (bx, by, sx, sy) in enumerate([
        (s, s, 1, 1), (W - s, s, -1, 1), (s, H - s, 1, -1), (W - s, H - s, -1, -1)
    ]):
        d = (f"M{bx} {by + sy * b} L{bx} {by} L{bx + sx * b} {by}")
        parts.append(
            f'<path class="bk" d="{d}" stroke="{GREEN}" stroke-width="{t_}" '
            f'fill="none" style="animation-delay:{0.1 + i * 0.07:.2f}s"/>'
        )

    # name block
    cx = W / 2
    parts.append(
        f'<text class="r" x="{cx}" y="118" fill="{GREEN}" font-family="{MONO}" '
        f'font-size="10" letter-spacing="4" text-anchor="middle" '
        f'style="animation-delay:.28s">OPERATOR</text>'
    )
    parts.append(
        f'<text class="r" x="{cx}" y="196" fill="#FFFFFF" font-family="{DISPLAY}" '
        f'font-size="76" font-weight="900" letter-spacing="-3" text-anchor="middle" '
        f'style="animation-delay:.36s">CAMERON</text>'
    )
    parts.append(
        f'<text class="r" x="{cx}" y="240" fill="{CHALK}" font-family="{DISPLAY}" '
        f'font-size="30" font-weight="300" letter-spacing="10.8" text-anchor="middle" '
        f'style="animation-delay:.44s">McALLISTER</text>'
    )
    parts.append(
        f'<text class="r" x="{cx}" y="278" fill="{MUTED}" font-family="{MONO}" '
        f'font-size="11" letter-spacing="2.2" text-anchor="middle" '
        f'style="animation-delay:.52s">BUILDER · SOUTH AFRICA · REMOTE</text>'
    )
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = write(os.path.join(OUT, "01-hero.svg"), render())
    print(f"wrote assets/01-hero.svg ({n/1024:.0f} KB)")
