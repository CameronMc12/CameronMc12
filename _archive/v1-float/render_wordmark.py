#!/usr/bin/env python3
"""
"CAMERON" as an extruded 3D wordmark, rasterised to ASCII, emitted as an SVG
that animates on GitHub (SMIL and CSS keyframes run inside an <img>; JS never
does).

Pipeline
    bold TTF -> binary mask -> extrude the mask along +z into a SURFACE voxel
    shell (front cap, back cap, boundary side walls) -> per frame: rotate,
    project, z-buffer splat into a character grid, glyph chosen by Lambert
    shading of the rotated surface normal.

Only the surface is kept -- filling the solid interior would multiply the voxel
count by the depth for pixels that are never visible.

The rotation is a pre-rendered ASCII flipbook: one <g> per frame, cycled with a
discrete SMIL opacity animation. Rows are emitted as whole strings rather than
per-character elements, which is what keeps a 24-frame flipbook inside ~100KB.

    python3 scripts/render_wordmark.py                 # rock, both themes
    python3 scripts/render_wordmark.py --mode static   # frame 0 only, for eyeballing
    WORDMARK_TEXT=APEX python3 scripts/render_wordmark.py
"""
from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from theme import (BAR_H, PAD, RADIUS, THEMES, art_bar, art_frame, art_panel,
                   esc, svg_open, write)  # noqa: E402

OUT_DIR = os.path.join(HERE, "..", "assets")

TEXT = os.environ.get("WORDMARK_TEXT", "CAMERON")
# Futura Condensed ExtraBold: seven letters have to share the grid, and a
# condensed face keeps ~11 columns per letter instead of 8. A normal-width
# heavy face (Impact, Arial Black) collapses the counters below one cell and
# the word rasterises to a slab.
FONT_PATH = os.environ.get("WORDMARK_FONT", "/System/Library/Fonts/Supplemental/Futura.ttc")
FONT_INDEX = int(os.environ.get("WORDMARK_FONT_INDEX", "4"))

# full width, short band. "CAMERON" is seven letters: at 490px the grid gives
# each letter ~11 columns and the whole word only 6 rows, which is below the
# resolution any letterform survives. Across the full 880 it reads properly.
# (Avi's reference used three letters, which is why his fits a half panel.)
#
# The HEIGHT is derived from the art, not fixed. A hardcoded height made the
# vertical fit binding, so the word shrank to 169 of 247 columns and sat in the
# middle of a band it did not fill. Now the width binds and the panel is cut to
# the word -- which also means WORDMARK_TEXT can change without a relayout.
W = 880
TOP_PAD_ROWS = 0.9
BOT_PAD_ROWS = 0.7
COLS = int(os.environ.get("WORDMARK_COLS", "247"))
CELL_W = 3.55
CELL_H = 6.2

MASK_H = 210          # glyph raster height in px -- drives voxel density
TRACKING = 0.30       # extra letter-spacing in em. at 0.06 the extruded side
                      # walls closed every counter and inter-letter gap and the
                      # word rasterised to one unreadable slab. seven letters
                      # need roughly double the tracking three would.
DEPTH_FRAC = 0.42     # extrusion depth as a fraction of cap height. shallow
                      # extrusions (0.15-0.26) project to under two grid columns
                      # at this yaw and vanish -- the word goes back to being a
                      # flat stencil. depth and tracking have to rise together.
TILT_DEG = 7.0        # fixed X tilt so the top wall stays visible
CAM_DIST = 6.2        # long lens: a near camera foreshortens the far letters
FOCAL = 4.3           # ~20% at the ends of the swing and reads as a bug
FIT_X = 0.955          # fraction of the grid width the widest pose may occupy
FIT_Y = 0.88          # ...and of its height. fitting on width alone let the
                      # cap height run past the panel and clipped every letter.

FRAMES = 18
ROCK_DEG = 9.0        # amplitude of the oscillation, either side of rest
REST_DEG = -28.0      # resting three-quarter pose. near-frontal (-6) hid the
                      # extruded walls behind the front caps and the word read
                      # as a flat stencil -- the yaw IS the 3D.

# sparse -> dense. index 0 is blank, so the background clears to spaces.
RAMP = " .`:-=+*csS#%@"
# keyed near the view axis and lifted: the letter faces stay dense, the extruded
# walls fall away to a dimmer glyph, and that gap is the whole 3D read. a
# side-heavy key makes the walls out-shine the faces and the word dissolves.
def key_light() -> np.ndarray:
    """Key derived FROM the rest pose, not hardcoded. A fixed world-space key
    stops pointing at the letter faces the moment REST_DEG changes, and the
    faces then shade the same as the walls -- which is the entire 3D read. The
    offset keeps it off-axis so the walls do not all collapse to ambient."""
    face = np.array([0.0, 0.0, -1.0]) @ rot(REST_DEG, TILT_DEG).T
    L = face + np.array([-0.30, -0.34, 0.0])
    return L / np.linalg.norm(L)
AMBIENT = 0.13
FOG = 0.30            # how far the back of the EXTRUSION dims. must be measured
                      # against the extrusion depth, not the observed z range:
                      # normalising to the range fogged a nearly-frontal word
                      # from end to end and dimmed the last three letters.
# The wordmark carries NO accent. Every attempt to pick a "brightest" tier
# painted most of the word lime, because the front caps of a flat-ish extrusion
# all shade within a couple of ramp steps of each other. Float's rule is that
# contrast is spent, not sprayed: the lime belongs to the heatmap and the one
# headline number, so this panel is two tiers of ink and the density ramp does
# the work. WALL_AT splits the dim extruded walls from the lit faces.
WALL_AT = 0.55


def build_mask() -> np.ndarray:
    size = MASK_H * 2
    font = ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX)
    track = int(size * TRACKING)
    widths = [font.getbbox(ch)[2] - font.getbbox(ch)[0] for ch in TEXT]
    total_w = sum(widths) + track * (len(TEXT) - 1)
    img = Image.new("L", (total_w + size, size * 2), 0)
    d = ImageDraw.Draw(img)
    x = size // 2
    for ch, wch in zip(TEXT, widths):
        bb = font.getbbox(ch)
        d.text((x - bb[0], size // 2 - bb[1]), ch, font=font, fill=255)
        x += wch + track
    a = np.array(img) > 127
    rows = np.any(a, axis=1)
    cols = np.any(a, axis=0)
    a = a[rows.argmax(): len(rows) - rows[::-1].argmax(),
          cols.argmax(): len(cols) - cols[::-1].argmax()]
    scale = MASK_H / a.shape[0]
    im = Image.fromarray((a * 255).astype(np.uint8)).resize(
        (max(1, int(a.shape[1] * scale)), MASK_H), Image.LANCZOS)
    return np.array(im) > 127


def build_voxels(mask: np.ndarray):
    """Surface shell only: front cap, back cap, and the extruded side walls."""
    h, w = mask.shape
    depth_px = max(2, int(h * DEPTH_FRAC))

    ys, xs = np.nonzero(mask)
    pts, nrms = [], []

    # front cap (facing the camera) and back cap
    front = np.stack([xs, ys, np.zeros_like(xs)], 1).astype(np.float32)
    pts.append(front)
    nrms.append(np.tile([0, 0, -1.0], (len(xs), 1)))
    back = front.copy()
    back[:, 2] = depth_px
    pts.append(back)
    nrms.append(np.tile([0, 0, 1.0], (len(xs), 1)))

    # boundary pixels -> side walls, normal = outward 2D gradient
    pad = np.pad(mask, 1)
    nb = (pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    by, bx = np.nonzero(mask & ~nb)
    gx = (pad[by + 1, bx + 2].astype(np.int8) - pad[by + 1, bx].astype(np.int8))
    gy = (pad[by + 2, bx + 1].astype(np.int8) - pad[by, bx + 1].astype(np.int8))
    n2 = np.stack([-gx, -gy], 1).astype(np.float32)
    mag = np.linalg.norm(n2, axis=1, keepdims=True)
    mag[mag == 0] = 1
    n2 /= mag
    # every 2nd z slice is enough: the grid is coarser than the voxel pitch
    zs = np.arange(0, depth_px + 1, 2, dtype=np.float32)
    wall = np.concatenate([np.stack([bx, by, np.full_like(bx, z, dtype=np.float32)], 1)
                           for z in zs])
    wall_n = np.concatenate([np.stack([n2[:, 0], n2[:, 1], np.zeros(len(bx))], 1)
                             for _ in zs])
    pts.append(wall.astype(np.float32))
    nrms.append(wall_n.astype(np.float32))

    P = np.concatenate(pts).astype(np.float32)
    N = np.concatenate(nrms).astype(np.float32)

    # centre on the origin, scale so the word is 1.0 unit wide
    P[:, 0] -= w / 2
    P[:, 1] -= h / 2
    P[:, 2] -= depth_px / 2
    P /= w
    return P, N, depth_px / w


def rot(yaw_deg: float, tilt_deg: float) -> np.ndarray:
    a, b = math.radians(yaw_deg), math.radians(tilt_deg)
    ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
    return (rx @ ry).astype(np.float32)





LIGHT = key_light()


def project(P: np.ndarray, N: np.ndarray, M: np.ndarray):
    Q = P @ M.T
    Nr = N @ M.T
    z = Q[:, 2] + CAM_DIST
    k = FOCAL / z
    return Q[:, 0] * k, Q[:, 1] * k, z, Nr


def fit_width(P, N, yaws):
    """Scale and horizontal centre from the union bbox, fitted on WIDTH only.
    The panel height is then cut to whatever that scale needs."""
    boxes = []
    for y in yaws:
        sx, _sy, _z, _n = project(P, N, rot(y, TILT_DEG))
        boxes.append((sx.min(), sx.max()))
    x0 = min(b[0] for b in boxes)
    x1 = max(b[1] for b in boxes)
    return (COLS * FIT_X) / (x1 - x0), (x0 + x1) / 2


def art_rows(P, N, yaws, scale) -> tuple[float, float]:
    """Union vertical extent of every pose, in rows, at the fitted scale."""
    aspect = CELL_W / CELL_H
    lo = hi = None
    for y in yaws:
        _sx, sy, _z, _n = project(P, N, rot(y, TILT_DEG))
        a, b = sy.min() * scale * aspect, sy.max() * scale * aspect
        lo = a if lo is None else min(lo, a)
        hi = b if hi is None else max(hi, b)
    return lo, hi


def fit_view(P, N, yaws, rows):
    """One scale AND one centre for every frame, from the union bounding box of
    all poses. Fitting on max|x| assumed the projection was symmetric about the
    origin; perspective plus a 24-degree yaw makes it anything but, and the C
    walked off the left edge. Centring per frame instead would make the word
    jitter through the rock."""
    aspect = CELL_W / CELL_H
    boxes = []
    for y in yaws:
        sx, sy, _z, _n = project(P, N, rot(y, TILT_DEG))
        boxes.append((sx.min(), sx.max(), sy.min(), sy.max()))
    x0 = min(b[0] for b in boxes); x1 = max(b[1] for b in boxes)
    y0 = min(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    scale = min((COLS * FIT_X) / (x1 - x0), (rows * FIT_Y) / ((y1 - y0) * aspect))
    return scale, (x0 + x1) / 2, (y0 + y1) / 2


def frame_grid(P, N, yaw, view, rows, depth_w):
    M = rot(yaw, TILT_DEG)
    sx, sy, z, Nr = project(P, N, M)
    oz = P[:, 2]                          # object-space depth, for the fog

    scale, cx, cy = view
    col = np.rint((sx - cx) * scale + COLS / 2).astype(np.int32)
    row = np.rint((sy - cy) * scale * (CELL_W / CELL_H) + rows / 2).astype(np.int32)

    ok = (col >= 0) & (col < COLS) & (row >= 0) & (row < rows)
    col, row, z, Nr, oz = col[ok], row[ok], z[ok], Nr[ok], oz[ok]

    idx = row * COLS + col
    order = np.lexsort((z, idx))          # nearest voxel first within each cell
    idx_s, N_s, oz_s = idx[order], Nr[order], oz[order]
    keep = np.empty(len(idx_s), bool)
    keep[0] = True
    keep[1:] = idx_s[1:] != idx_s[:-1]
    idx_k, N_k, oz_k = idx_s[keep], N_s[keep], oz_s[keep]

    # the front cap normal is -z and the key is on -z, so the dot is already
    # positive for the faces. negating it lit the BACK of the word and every
    # visible cell fell to the sparse end of the ramp.
    lam = np.clip(N_k @ LIGHT, 0, 1)
    shade = AMBIENT + (1 - AMBIENT) * lam
    # fog on OBJECT-space depth, not camera depth. camera depth also varies
    # along the word once it is yawed, which fogged "CAMERON" left-to-right and
    # flattened the last four letters into one grey mass.
    shade *= 1 - FOG * np.clip((oz_k + depth_w / 2) / max(depth_w, 1e-6), 0, 1)

    grid = np.zeros(rows * COLS, np.float32)
    grid[idx_k] = shade
    return grid.reshape(rows, COLS)


def to_rows(grid: np.ndarray, floor: float) -> list[tuple[str, str]]:
    """Each row becomes (wall_string, face_string). Two ink tiers: the extruded
    side walls sit well back from the lit front caps, which is what carries the
    3D at this glyph size. Both strings are laid at the same x so the layers
    stay in register."""
    out = []
    n = len(RAMP) - 1
    for r in grid:
        wall, face = [], []
        for v in r:
            if v <= 0.02:
                wall.append(" ")
                face.append(" ")
                continue
            vf = floor + (1 - floor) * v
            g = RAMP[max(1, min(n, int(round(vf * n))))]
            if v < WALL_AT:
                wall.append(g)
                face.append(" ")
            else:
                wall.append(" ")
                face.append(g)
        out.append(("".join(wall).rstrip(), "".join(face).rstrip()))
    return out


def build_frames(mode: str):
    """Returns (frames, rows, panel_height). The widest pose sets the scale for
    every frame, so the word never grows past the panel mid-swing."""
    mask = build_mask()
    P, N, depth_w = build_voxels(mask)

    yaws = [REST_DEG + ROCK_DEG * math.sin(2 * math.pi * i / FRAMES) for i in range(FRAMES)]
    if mode == "static":
        yaws = [REST_DEG]
    poses = sorted(set(yaws) | {REST_DEG})

    scale, cx = fit_width(P, N, poses)
    lo, hi = art_rows(P, N, poses, scale)
    rows = int(math.ceil(hi - lo) + TOP_PAD_ROWS + BOT_PAD_ROWS)
    cy = (lo + hi) / 2 / (scale * (CELL_W / CELL_H))
    view = (scale, cx, cy)

    # the rock is symmetric, so sin() revisits every yaw exactly twice per
    # cycle. rasterise each distinct pose ONCE and play it back in both slots:
    # 18 frames of flipbook for the file size of 10.
    slots = [round(y, 4) for y in yaws]
    uniq = sorted(set(slots))
    # raw shade grids, not glyphs: the ramp floor is per-theme, so the two
    # themes ink the SAME raster differently
    grids = [frame_grid(P, N, y, view, rows, depth_w) for y in uniq]
    schedule = [uniq.index(y) for y in slots]

    height = int(round(BAR_H + PAD * 0.55 + rows * CELL_H + PAD * 0.7))
    return grids, schedule, rows, height


def render(theme_name: str, mode: str, built) -> list[str]:
    t = THEMES[theme_name]
    grids, schedule, rows, H = built
    # the card is dark in both themes, so the dark ramp floor applies to both
    frames = [to_rows(g, 0.0) for g in grids]

    total = 3.6
    art_top = BAR_H + PAD * 0.55 + CELL_H
    x0 = (W - COLS * CELL_W) / 2

    css = (
        # 0.94 of the cell, not 0.86: GitHub's profile README column is 846px, so
        # an 880-wide asset is ALWAYS scaled down, and at 0.86 the glyphs thinned
        # to a smudge on the live page even though the baseline looked fine at 1:1.
        f"text{{font-size:{CELL_H*0.94:.1f}px;letter-spacing:{CELL_W - CELL_H*0.94*0.6:.2f}px;"
        f"white-space:pre;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}"
        ".wall{fill:#CDD0D6;fill-opacity:.62}.face{fill:#FAFBFC;fill-opacity:1}"
    )
    parts = svg_open(W, H, f"{TEXT} — 3D ASCII wordmark", css)
    parts.append(f'<rect width="{W}" height="{H}" fill="{t.ground}"/>')
    parts += art_panel(t, W, H, "wordmark", f"{TEXT.lower()}.3d", uid="wm")

    # opening wipe: the word prints in left to right, once, then holds
    parts.append(
        f'<defs><clipPath id="wmwipe"><rect x="0" y="0" width="0" height="{H}">'
        f'<animate attributeName="width" from="0" to="{W}" dur="1.05s" '
        f'begin="0s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" '
        f'keyTimes="0;1" values="0;{W}"/></rect></clipPath></defs>'
    )
    parts.append('<g clip-path="url(#wmwipe)">')

    for fi, rows_txt in enumerate(frames):
        if len(schedule) > 1:
            vals = ";".join("1" if k == fi else "0" for k in schedule)
            anim = (
                f'<animate attributeName="opacity" values="{vals}" '
                f'dur="{total}s" calcMode="discrete" repeatCount="indefinite"/>'
            )
            op = ' opacity="0"'
        else:
            anim, op = "", ""
        parts.append(f"<g{op}>{anim}")
        for ri, (wall, face) in enumerate(rows_txt):
            y = art_top + ri * CELL_H
            for cls, txt in (("wall", wall), ("face", face)):
                if txt:
                    parts.append(
                        f'<text class="{cls}" x="{x0:.1f}" y="{y:.1f}" '
                        f'xml:space="preserve">{esc(txt)}</text>'
                    )
        parts.append("</g>")

    parts.append("</g>")          # close the wipe clip
    parts.append(art_bar(W, "wordmark", f"{TEXT.lower()}.3d"))
    parts.append(art_frame(t, W, H))
    return parts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["rock", "static"], default="rock")
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    built = build_frames(args.mode)          # rasterise once, ink twice
    print(f"grid {COLS}x{built[2]}, panel {W}x{built[3]}, "
          f"{len(built[0])} distinct poses over {len(built[1])} slots")
    for name in ("dark", "light"):
        path = os.path.join(OUT_DIR, f"wordmark-{name}.svg")
        n = write(path, render(name, args.mode, built))
        print(f"wrote assets/wordmark-{name}.svg ({n/1024:.0f} KB)")


if __name__ == "__main__":
    main()
