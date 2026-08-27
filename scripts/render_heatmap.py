#!/usr/bin/env python3
"""
The contribution calendar: 53 weeks x 7 days of rounded cells, revealed once in
a diagonal cascade and then frozen. No looping glow -- a graph that pulses
forever is a screensaver, not a read-out.

The ramp is LIME, not GitHub green. That is the point of the whole profile:
one accent, and it belongs to the number that matters. On light the same hue
runs the other way, pale to deep olive, because on white "more" has to mean
darker.

Levels are cut on absolute counts rather than GitHub's per-user quartiles, so
the colour of a day means the same thing month to month. Cameron's days run
high (4,292 over the year), hence the wide top bands.

    python3 scripts/render_heatmap.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import BAR_H, PAD, RADIUS, THEMES, esc, footer_rule, panel, svg_open, write  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, ".."))
IN_PATH = os.path.join(ROOT, "data", "contributions.json")
OUT_DIR = os.path.join(ROOT, "assets")

W = 880
CELL = 12
GAP = 3
STEP = CELL + GAP
LEFT_LABEL_W = 26
MONTH_H = 17
LEGEND_H = 32
FOOT_H = 44

# Absolute cut points, not GitHub's per-user quartiles, so a cell's colour means
# the same thing month to month and year to year. Tuned against the real spread
# (193 active days, median 11, best 132): these put 74/45/25/34/15 days in the
# five bands, which keeps the top of the ramp rare enough to mean something.
# Quartile-style cuts (3/9/20/38) pushed 44 days to maximum and the panel read
# as a solid wall of lime.
LEVELS = (0, 5, 15, 35, 70)

COL_T = 0.013         # per-column delay: the left-to-right sweep
ROW_T = 0.040         # per-row delay: the top-to-bottom cascade
CELL_DUR = 0.40


def level_for(n: int) -> int:
    if n == 0:
        return 0
    for i, cut in enumerate(LEVELS[1:], start=1):
        if n <= cut:
            return i
    return 5


def build_grid(days: list[dict]) -> list[list]:
    """Sunday-first columns, left-padded so week one starts on the right weekday."""
    first = dt.date.fromisoformat(days[0]["date"])
    col: list = [None] * ((first.weekday() + 1) % 7)
    grid = []
    for d in days:
        wd = (dt.date.fromisoformat(d["date"]).weekday() + 1) % 7
        while len(col) < wd:
            col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"])))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        grid.append(col + [None] * (7 - len(col)))
    return grid


def render(theme_name: str, data: dict) -> list[str]:
    t = THEMES[theme_name]
    grid = build_grid(data["days"])
    art_w = len(grid) * STEP - GAP
    art_h = 7 * STEP - GAP

    grid_top = BAR_H + MONTH_H + 8
    grid_left = int((W - art_w + LEFT_LABEL_W) / 2)
    H = grid_top + art_h + LEGEND_H + FOOT_H + 8

    css = f"""
@keyframes pop{{from{{opacity:0;transform:translateY(-5px) scale(.86)}}to{{opacity:1;transform:none}}}}
.c{{opacity:0;animation:pop {CELL_DUR}s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:center}}
.lab{{fill:{t.dim};font-size:9.5px}}
""".strip()

    parts = svg_open(W, H, "GitHub contributions", css)
    parts += panel(
        t, W, H, "contributions",
        f'{data["range"]["start"]} → {data["range"]["end"]} · refreshed daily',
        uid="hm",
    )

    # month labels, one per month, placed on the column its 1st-week falls in
    seen = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            d = dt.date.fromisoformat(cell[0])
            if (d.year, d.month) not in seen and d.day <= 7:
                seen.add((d.year, d.month))
                parts.append(
                    f'<text class="lab" x="{grid_left + ci*STEP}" '
                    f'y="{BAR_H + MONTH_H:.0f}">{d.strftime("%b")}</text>'
                )
            break

    for wi, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(
            f'<text class="lab" x="{grid_left - LEFT_LABEL_W}" '
            f'y="{grid_top + wi*STEP + CELL*0.8:.1f}">{name}</text>'
        )

    for ci, column in enumerate(grid):
        for ri, cell in enumerate(column):
            if cell is None:
                continue
            date_s, count, lvl = cell
            delay = ci * COL_T + ri * ROW_T
            plural = "" if count == 1 else "s"
            parts.append(
                f'<rect class="c" x="{grid_left + ci*STEP}" y="{grid_top + ri*STEP}" '
                f'width="{CELL}" height="{CELL}" rx="2.5" fill="{t.ramp[lvl]}" '
                f'style="animation-delay:{delay:.3f}s">'
                f"<title>{esc(date_s)}: {count} contribution{plural}</title></rect>"
            )

    # legend, right-aligned under the grid
    leg_y = grid_top + art_h + 15
    leg_w = len(t.ramp) * (CELL - 2) + 2 * (len(t.ramp) - 1)
    lx = W - PAD - leg_w - 34
    parts.append(
        f'<text class="lab" x="{lx - 6}" y="{leg_y + CELL*0.72:.1f}" '
        f'text-anchor="end">Less</text>'
    )
    for c in t.ramp:
        parts.append(
            f'<rect x="{lx}" y="{leg_y}" width="{CELL-2}" height="{CELL-2}" '
            f'rx="2.2" fill="{c}"/>'
        )
        lx += CELL
    parts.append(f'<text class="lab" x="{lx - 2}" y="{leg_y + CELL*0.72:.1f}">More</text>')

    # footer: the one accent number on the page
    fy = H - FOOT_H
    parts.append(footer_rule(t, W, fy))
    ty = fy + 27
    parts.append(
        f'<text x="{PAD}" y="{ty:.0f}" font-size="13">'
        f'<tspan fill="{t.accent}" font-weight="700">{data["total_contributions"]:,}</tspan>'
        f'<tspan fill="{t.muted}"> contributions in the last year</tspan>'
        f'<tspan fill="{t.dim}">   ·   {data["active_days"]} active days</tspan>'
        f'<tspan fill="{t.dim}">   ·   {data["avg_per_active_day"]:.0f}/day when active</tspan>'
        f"</text>"
    )
    parts.append(
        f'<text x="{W-PAD}" y="{ty:.0f}" font-size="11" fill="{t.dim}" text-anchor="end">'
        f'best day {data["best_day"]["count"]} on {esc(data["best_day"]["date"])}</text>'
    )
    return parts


def main() -> None:
    with open(IN_PATH) as f:
        data = json.load(f)
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in ("dark", "light"):
        n = write(os.path.join(OUT_DIR, f"heatmap-{name}.svg"), render(name, data))
        print(f"wrote assets/heatmap-{name}.svg ({n/1024:.1f} KB)")


if __name__ == "__main__":
    main()
