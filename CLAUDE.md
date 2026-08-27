# CLAUDE.md — CameronMc12 profile repo

The `<username>/<username>` repo. Its README renders at the top of
`github.com/CameronMc12`. Everything visible is a generated, animated SVG.

## The one constraint that shapes everything

GitHub strips `<script>` from a README and sanitises almost all inline CSS, but
it DOES render SVGs embedded via `<img>` and DOES run their SMIL and CSS
keyframe animations. So all motion lives inside self-contained SVG files and the
README only places them. No JavaScript, anywhere, ever.

## Rebuild

```bash
python3 scripts/render_all.py          # every asset + baseline screenshots
python3 scripts/render_all.py --no-shots
python3 scripts/shoot.py heatmap --at 5    # one asset, 5s into its animation
```

Locally you need `pip install -r scripts/requirements-art.txt` (numpy + Pillow
for the wordmark). CI only installs `requirements.txt`.

## What refreshes and what does not

| Thing | How | When |
|---|---|---|
| `data/contributions.json` | public HTML scrape, no auth | daily, in Actions |
| `assets/heatmap-*`, `assets/hero-*` | re-inked from that | daily, in Actions |
| `data/stack.json` | `python3 scripts/fetch_stack.py` (needs `gh` auth) | by hand, every month or two |
| `assets/wordmark-*` | `python3 scripts/render_wordmark.py` | only when the name or geometry changes |
| `data/identity.json` | Cameron edits it | when what he is building changes |

The wordmark is committed rather than built in CI because it needs numpy and
`Futura.ttc` from macOS, neither of which a runner has.

## Rules

- Never hardcode a colour in a renderer. Tokens live in `scripts/theme.py`.
- Never put a private repo NAME in this repo. Aggregate bytes only — the private
  repos are client work.
- Never ship a change without looking at `docs/04-design/baselines/readme-*.png`
  in both themes.
- Reveals play once and freeze. Only the rain and the wordmark's rock loop.
- If the heatmap ever looks empty, check "Include private contributions on my
  profile" at github.com/settings/profile before touching any code. That single
  toggle is the difference between 21 and 193 active days.

## Docs map

| File | What it answers |
|---|---|
| `DESIGN.md` | The grammar: tokens, panel anatomy, motion, colour discipline, and every ruling Cameron has made |
| `docs/00-goals.md` | Why this exists, what done looks like, what it is not |
| `docs/01-decisions.md` | The never/always list and every dated ruling with its reason |
| `docs/02-inventory/PRODUCT-SPEC.md` | Every panel, data file and job, plus what is deliberately not built |
| `docs/03-pages/profile.md` | The page contract: what must be visible, every state, every failure branch |
| `docs/04-design/baselines/` | Screenshots of every panel and the whole assembled page, both themes |
