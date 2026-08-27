#!/usr/bin/env python3
"""
Visual gate. Renders each section the way GitHub does — inside an <img>, on
GitHub's dark README ground, at the width the profile column actually is — and
screenshots it at a fixed moment so animated frames are comparable run to run.

    python3 scripts/shoot.py               # every section, plus the whole page
    python3 scripts/shoot.py 01 --at 3.5   # one section, 3.5s into its animation

GitHub's PROFILE README column measures 846px at a 1512px viewport and 766px at
1200px, so assets authored at 846 are always scaled down a little. The gate
renders at 846 rather than 1:1 for that reason — anything that only reads at
full size does not read.
"""
from __future__ import annotations

import argparse
import glob
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "docs", "04-design", "baselines")
PANE_W = 846
GH_BG = "#0d1117"


def page_html(imgs: list[str]) -> str:
    cells = "".join(
        f'<img src="{os.path.relpath(p, ROOT)}" width="{PANE_W}" '
        f'style="display:block;margin:0 auto">' for p in imgs
    )
    return (f'<!doctype html><meta charset="utf-8"><body style="margin:0;'
            f'background:{GH_BG}"><div style="width:{PANE_W}px;margin:0 auto">'
            f"{cells}</div></body>")


def shoot(pw, imgs: list[str], out: str, at: float) -> None:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": PANE_W + 60, "height": 900},
                    device_scale_factor=2, color_scheme="dark")
    # written into the repo root and navigated to, not set_content: an <img> on
    # an about:blank page cannot load file:// siblings, which reads as a broken
    # SVG when the SVG is fine
    tmp = os.path.join(ROOT, ".shoot.html")
    with open(tmp, "w") as f:
        f.write(page_html(imgs))
    pg.goto("file://" + tmp)
    pg.wait_for_load_state("load")
    pg.wait_for_timeout(int(at * 1000))
    pg.query_selector("div").screenshot(path=out, animations="allow")
    b.close()
    os.remove(tmp)
    print(f"  {os.path.relpath(out, ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("which", nargs="?", default="all")
    ap.add_argument("--at", type=float, default=4.0)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    files = sorted(glob.glob(os.path.join(ASSETS, "*.svg")))
    page = [f for f in files if not os.path.basename(f).startswith("btn-")]

    with sync_playwright() as pw:
        if args.which == "all":
            for f in files:
                base = os.path.basename(f)[:-4]
                shoot(pw, [f], os.path.join(OUT, f"{base}.png"), args.at)
            shoot(pw, page, os.path.join(OUT, "_page.png"), args.at)
        else:
            for f in files:
                if args.which in os.path.basename(f):
                    base = os.path.basename(f)[:-4]
                    shoot(pw, [f], os.path.join(OUT, f"{base}.png"), args.at)


if __name__ == "__main__":
    main()
