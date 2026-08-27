#!/usr/bin/env python3
"""
S4 — the contribution calendar. 53 weeks by 7 days of real, scraped data.

Levels are cut on ABSOLUTE counts, not GitHub's per-user quartiles, so a cell's
colour means the same thing month to month and year to year. Tuned against the
real spread (193 active days, median 11, best 132): quartile-style cuts put 44
of 193 active days at maximum and the panel read as a solid wall.

The reveal is a diagonal cascade that plays once and freezes. A graph that
pulses forever is a screensaver, not a read-out.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (CHALK, DIM, DISPLAY, GREEN, LABEL_H, MONO, MUTED, PAD,  # noqa: E402
                   RADIUS, RAMP, RULE, W, esc, ground, label_row, svg_open, write)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "assets")

LEVELS = (0, 5, 15, 35, 70)
CELL = 11.0
GAP = 2.4
STEP = CELL + GAP
CARD_PAD = 24
COL_T = 0.012          # per-column delay: the left-to-right sweep
ROW_T = 0.036          # per-row delay: the top-to-bottom cascade
CELL_DUR = 0.40


def level_for(n: int) -> int:
    if n == 0:
        return 0
    for i, cut in enumerate(LEVELS[1:], start=1):
        if n <= cut:
            return i
    return 5


def build_grid(days: list[dict]) -> list[list]:
    """Sunday-first columns, left-padded so week one starts on the right day."""
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


def render() -> list[str]:
    with open(os.path.join(ROOT, "data", "contributions.json")) as f:
        data = json.load(f)
    grid = build_grid(data["days"])

    art_w = len(grid) * STEP - GAP
    art_h = 7 * STEP - GAP
    card_x, card_w = PAD, W - PAD * 2
    gx0 = card_x + (card_w - art_w) / 2
    gy0 = LABEL_H + CARD_PAD + 20
    foot_y = gy0 + art_h + 18
    card_h = foot_y + 46 - LABEL_H
    h = LABEL_H + card_h + 38

    css = f"""
@keyframes pop{{from{{opacity:0;transform:translateY(-5px) scale(.84)}}to{{opacity:1;transform:none}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.c{{animation:pop {CELL_DUR}s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:center}}
.r{{animation:rise .5s cubic-bezier(.2,.8,.2,1) both}}
""".strip()

    parts = svg_open(W, h, "Commit activity, last 365 days", css)
    parts.append(ground(W, h))
    parts.append(label_row("commits", "last 365 days · refreshed daily"))
    parts.append(
        f'<rect x="{card_x + 0.5}" y="{LABEL_H + 0.5}" width="{card_w - 1}" '
        f'height="{card_h - 1}" rx="{RADIUS}" fill="#0C1013" stroke="{RULE}"/>'
    )

    seen = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            d = dt.date.fromisoformat(cell[0])
            if (d.year, d.month) not in seen and d.day <= 7 and d.month % 2 == 1:
                seen.add((d.year, d.month))
                parts.append(
                    f'<text x="{gx0 + ci * STEP:.1f}" y="{gy0 - 8}" fill="{DIM}" '
                    f'font-family="{MONO}" font-size="9" letter-spacing="1.3">'
                    f'{d.strftime("%b").upper()}</text>'
                )
            break

    for ci, column in enumerate(grid):
        for ri, cell in enumerate(column):
            if cell is None:
                continue
            date_s, count, lvl = cell
            delay = ci * COL_T + ri * ROW_T
            plural = "" if count == 1 else "s"
            parts.append(
                f'<rect class="c" x="{gx0 + ci * STEP:.1f}" y="{gy0 + ri * STEP:.1f}" '
                f'width="{CELL}" height="{CELL}" rx="2.4" fill="{RAMP[lvl]}" '
                f'style="animation-delay:{delay:.3f}s">'
                f"<title>{esc(date_s)}: {count} contribution{plural}</title></rect>"
            )

    parts.append(
        f'<line x1="{card_x + 1}" y1="{foot_y}" x2="{card_x + card_w - 1}" '
        f'y2="{foot_y}" stroke="{RULE}"/>'
    )
    fy = foot_y + 30
    parts.append(
        f'<text class="r" x="{card_x + CARD_PAD}" y="{fy}" fill="{GREEN}" '
        f'font-family="{DISPLAY}" font-size="26" font-weight="800" '
        f'letter-spacing="-.6" style="animation-delay:1.1s">'
        f'{data["total_contributions"]:,}</text>'
    )
    tail = (f'contributions · {data["active_days"]} active days · '
            f'{data["avg_per_active_day"]:.0f} a day when active')
    parts.append(
        f'<text class="r" x="{card_x + CARD_PAD + 92}" y="{fy - 2}" fill="{MUTED}" '
        f'font-family="{MONO}" font-size="12" style="animation-delay:1.16s">'
        f"{esc(tail)}</text>"
    )

    lx = card_x + card_w - CARD_PAD - (len(RAMP) * 15) - 38
    parts.append(
        f'<text x="{lx - 8}" y="{fy - 2}" fill="{DIM}" font-family="{MONO}" '
        f'font-size="10" text-anchor="end">Less</text>'
    )
    for c in RAMP:
        parts.append(
            f'<rect x="{lx}" y="{fy - 12}" width="11" height="11" rx="2.4" fill="{c}"/>'
        )
        lx += 15
    parts.append(
        f'<text x="{lx + 2}" y="{fy - 2}" fill="{DIM}" font-family="{MONO}" '
        f'font-size="10">More</text>'
    )
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = write(os.path.join(OUT, "04-commits.svg"), render())
    print(f"wrote assets/04-commits.svg ({n/1024:.1f} KB)")
