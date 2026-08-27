# Inventory

Small enough to fit on one page. Every panel, every script, every data file.

## Panels (P)

| ID | Panel | Renderer | Status |
|---|---|---|---|
| P1 | `identity` — Matrix digital rain | `render_matrix.py` | shipped |
| P2 | `system` — neofetch card | `render_card.py` | shipped |
| P3 | hero — P1 + P2 composed at 880 | `render_hero.py` | shipped |
| P4 | `wordmark` — 3D ASCII "CAMERON" | `render_wordmark.py` | shipped |
| P5 | `contributions` — 53×7 calendar | `render_heatmap.py` | shipped |
| P6 | `portrait` — ASCII headshot | `render_portrait.py` | **needs a photo** |

## Data (D)

| ID | File | Source | Refresh |
|---|---|---|---|
| D1 | `data/contributions.json` | public HTML scrape, no auth | daily, in CI |
| D2 | `data/stack.json` | `gh api graphql`, needs Cameron's auth | by hand |
| D3 | `data/identity.json` | hand-written | by hand |

## Jobs (J)

| ID | Job | Trigger |
|---|---|---|
| J1 | `refresh.yml` — rescrape + re-ink P3, P5 | daily 05:17 UTC, and on push to `scripts/` |

## Discovered / not built

| ID | Item | Why it is not built |
|---|---|---|
| S-new-1 | P6 ASCII portrait | Cameron's GitHub avatar is a Matrix-rain image, not a photo. Pipeline is written and unused; drop a headshot at `source-photo.jpg` and run `prep_photo.py` then `render_portrait.py`. |
| S-new-2 | Monthly sparkline in P5 | `contributions.json` already carries `monthly[]`. Left out to keep the footer to one line. |
| S-new-3 | Per-weekday rhythm strip | `by_weekday` is already computed and only the single busiest day is shown. |
