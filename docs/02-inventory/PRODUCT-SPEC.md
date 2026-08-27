# Inventory

## Sections (S)

| ID | Section | Renderer | Data | Status |
|---|---|---|---|---|
| S01 | Hero — Matrix rain + name | `render_hero.py` | — | shipped |
| S02 | What I do | `render_about.py` | identity | shipped |
| S03 | Building — three projects | `render_projects.py` | identity | shipped |
| S04 | Commits — 53×7 calendar | `render_heatmap.py` | contributions | shipped |
| S05 | Stack — radar + rails | `render_stack.py` | stack | shipped |
| S06 | Momentum — monthly line | `render_momentum.py` | contributions | shipped |
| S07 | Working hours — polar clock | `render_hours.py` | hours | shipped |
| S08 | Weekly rhythm — bars | `render_week.py` | contributions | shipped |
| S09 | Shipped — timeline | `render_shipped.py` | identity | shipped, **content unconfirmed** |
| S10 | Contact | `render_contact.py` | identity | shipped, **handles unconfirmed** |
| S11 | Account buttons ×5 | `render_buttons.py` | identity | shipped |
| S12 | Colophon | `render_contact.py` | — | shipped |

## Data (D)

| ID | File | Source | Refresh |
|---|---|---|---|
| D1 | `data/contributions.json` | public HTML scrape, no auth | daily, CI |
| D2 | `data/stack.json` | `gh api graphql`, needs Cameron's auth | by hand |
| D3 | `data/hours.json` | commit timestamps via `gh api`, needs auth | by hand |
| D4 | `data/identity.json` | hand-written | by hand |

## Jobs (J)

| ID | Job | Trigger |
|---|---|---|
| J1 | `refresh.yml` — rescrape + re-ink S04, S06, S08 | daily 05:17 UTC, and on push to `scripts/` |

## Open

| ID | Item | Why |
|---|---|---|
| O1 | S09 milestone content | Seeded with placeholders. Cannot be derived from any API; Cameron has to confirm the dates and wording. |
| O2 | LinkedIn / X / Instagram handles and the contact email | Placeholders. GitHub and krevio.co.za are the only verified ones. |
| O3 | S06 and S08 overlap S04 | Three cuts of the same contribution data. Worth cutting one or two once Cameron has seen the page live. |
| O4 | `hours.json` samples 100 commits per repo | 932 of ~4,300. Enough for a shape, not a census; the section says "sampled". |
