#!/usr/bin/env python3
"""
Visual gate harness. Renders each SVG the way GitHub does -- inside an <img>,
on GitHub's own README background -- and screenshots it at a fixed moment so
animated frames are comparable between runs.

    python3 scripts/shoot.py                       # every asset, both themes
    python3 scripts/shoot.py matrix --at 3.5       # one asset, 3.5s in
    python3 scripts/shoot.py --readme              # the whole assembled README

Screenshots land in docs/04-design/baselines/. An SVG loaded through <img> is
sandboxed exactly as GitHub sandboxes it, so anything that survives here
survives on the profile.
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "docs", "04-design", "baselines")

# GitHub's PROFILE README column, measured live at a 1512px viewport: 846px.
# Assets are authored at 880 and always scaled down, so the gate has to look
# at 846 or it grades a render nobody sees.
GH = {
    "dark": {"bg": "#0d1117", "fg": "#e6edf3"},
    "light": {"bg": "#ffffff", "fg": "#1f2328"},
}
PANE_W = 846
RENDER_W = 846


def page_html(theme: str, imgs: list[tuple[str, int]]) -> str:
    g = GH[theme]
    cells = "".join(
        f'<img src="{os.path.relpath(p, ROOT)}" width="{w}" '
        f'style="vertical-align:top;display:block;margin:0 auto 22px">'
        for p, w in imgs
    )
    return f"""<!doctype html><meta charset="utf-8">
<body style="margin:0;background:{g['bg']};color:{g['fg']};
  font:14px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<div style="width:{PANE_W}px;margin:0 auto;padding:32px 0;text-align:center">{cells}</div>
</body>"""


def shoot(pw, theme: str, imgs: list[tuple[str, int]], out: str, at: float) -> None:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": PANE_W + 64, "height": 900},
                    device_scale_factor=2, color_scheme=theme)
    # written into the repo root and navigated to, not set_content: an <img>
    # on an about:blank page cannot load file:// siblings, which reads as a
    # broken SVG when the SVG is fine
    tmp = os.path.join(ROOT, ".shoot.html")
    with open(tmp, "w") as f:
        f.write(page_html(theme, imgs))
    pg.goto("file://" + tmp)
    pg.wait_for_load_state("load")
    pg.wait_for_timeout(int(at * 1000))
    el = pg.query_selector("div")
    el.screenshot(path=out)
    b.close()
    os.path.exists(tmp) and os.remove(tmp)
    print(f"  {os.path.relpath(out, ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("which", nargs="?", default="all")
    ap.add_argument("--at", type=float, default=4.0, help="seconds into the animation")
    ap.add_argument("--readme", action="store_true", help="shoot the assembled hero + graph")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    widths = {"hero": RENDER_W, "wordmark": RENDER_W, "heatmap": RENDER_W,
              "portrait": int(RENDER_W * 340 / 880)}

    with sync_playwright() as pw:
        if args.readme:
            # the whole page, stacked exactly as the README lays it out, on
            # GitHub's own README background at its own column width
            for theme in ("dark", "light"):
                stack = [
                    (os.path.join(ASSETS, f"hero-{theme}.svg"), RENDER_W),
                    (os.path.join(ASSETS, f"wordmark-{theme}.svg"), RENDER_W),
                    (os.path.join(ASSETS, f"heatmap-{theme}.svg"), RENDER_W),
                ]
                shoot(pw, theme, stack, os.path.join(OUT, f"readme-{theme}.png"), args.at)
            return

        for path in sorted(glob.glob(os.path.join(ASSETS, "*.svg"))):
            base = os.path.basename(path)[:-4]
            if args.which != "all" and args.which not in base:
                continue
            theme = "light" if base.endswith("-light") else "dark"
            key = next((k for k in widths if k in base), None)
            w = widths.get(key, 480)
            shoot(pw, theme, [(path, w)], os.path.join(OUT, f"{base}.png"), args.at)


if __name__ == "__main__":
    main()
