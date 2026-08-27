# CLAUDE.md — CameronMc12 profile repo

The `<username>/<username>` repo. Its README renders at the top of
`github.com/CameronMc12`. Everything visible is a generated, animated SVG.

## The constraints that shape everything

GitHub strips `<script>` from a README and from an SVG loaded through `<img>`,
but it DOES run SMIL and CSS keyframe animations inside one. So all motion lives
in the files and the README only places them. No JavaScript, anywhere, ever.

That same `<img>` sandbox means **links inside an SVG never fire** and **there is
no hover**. The account buttons are therefore separate small SVGs, each wrapped
in an `<a href>` in the markdown, with a looping arrow nudge instead of a hover
state.

## Rebuild

```bash
python3 scripts/render_all.py             # every section + baselines
python3 scripts/render_all.py --no-shots
python3 scripts/shoot.py 04 --at 5        # one section, 5s into its animation
```

## What refreshes and what does not

| Thing | How | When |
|---|---|---|
| `data/contributions.json` | public HTML scrape, no auth | daily, in Actions |
| `assets/04`, `06`, `08` | re-inked from that | daily, in Actions |
| `data/stack.json` | `python3 scripts/fetch_stack.py` (needs `gh` auth) | by hand, monthly |
| `data/hours.json` | `python3 scripts/fetch_hours.py` (needs `gh` auth) | by hand, monthly |
| `data/identity.json` | Cameron edits it | when anything he says changes |
| everything else | `python3 scripts/render_all.py` | after a data or code change |

`fetch_stack.py` and `fetch_hours.py` run locally because `GITHUB_TOKEN` inside
this repo's own Actions run can only read this repo, and both need to see the 28
private ones.

## Rules

- Never hardcode a colour in a renderer. Tokens live in `scripts/theme.py`.
- Never put a private repo NAME in this repo. Aggregate numbers only — the
  private repos are client work.
- Never rest an element at `opacity:0`. See DESIGN.md §5; it can stay invisible.
- Never put a CSS `transform` on an element that already has a `transform`
  attribute. See DESIGN.md §5.
- Never write a claim you have not measured. If a section needs a number that no
  API gives you, either fetch it properly or do not ship the section.
- Never ship without looking at `docs/04-design/baselines/_page.png`.
- If the heatmap ever looks empty, check "Include private contributions on my
  profile" at github.com/settings/profile before touching any code. That single
  toggle is the difference between 21 and 193 active days.

## Docs map

| File | What it answers |
|---|---|
| `DESIGN.md` | Tokens, section anatomy, motion rules, colour discipline, every ruling |
| `docs/00-goals.md` | Why this exists, what done looks like, what it is not |
| `docs/01-decisions.md` | The never/always list and every dated ruling with its reason |
| `docs/02-inventory/PRODUCT-SPEC.md` | Every section, data file and job, and what is deliberately not built |
| `docs/03-pages/profile.md` | The page contract: what must be visible, every state, every failure branch |
| `docs/04-design/baselines/` | Screenshots of every section and the whole page |
| `_archive/v1-float/` | The first build (Float grammar, ASCII wordmark, portrait pipeline) |
