# Page contract — the profile README

The only page. Everything the reader sees before scrolling.

## The decision it serves

"Is this person worth replying to?" A visitor arrives from a proposal, a pitch
or a link. They need, in about four seconds: this is a real builder, this is
what he builds, this is how much.

## P1 — visible without a click

- Who: name, handle, role, country
- What he is building **right now**, in his own words
- How much: total contributions over twelve months, active days, current streak
- What in: real language mix across every repo, private included
- Proof of continuity: the twelve-month calendar, shaped, not flat

## P2 — one click away

- `krevio.co.za` — the product
- `github.com/CameronMc12` — the one public repo, and this one

## Panels and their jobs

| Panel | Job |
|---|---|
| `identity` (rain) | Sets tone in under a second. Carries no information on purpose. |
| `system` (card) | Every fact a visitor needs, in one scan. Half hand-written, half measured. |
| `wordmark` | The name, at size. Signature, not data. |
| `contributions` | The claim in the card's "commits" row, shown rather than asserted. |

## States

| State | What happens |
|---|---|
| loading | SVGs stream; panels appear with their chrome first, motion follows |
| animating | rain loops; wordmark wipes then rocks; card prints once; heatmap reveals once |
| resting | after ~4s everything but the rain and the rock is frozen |
| light theme | data panels invert; art panels stay dark by design (DESIGN.md §5) |
| stale data | if the daily job fails, the graph holds its last good state; the job goes red |
| collapsed data | if the private-contributions toggle is switched off, `fetch_contributions.py` exits non-zero and nothing is committed |
| no motion | a reader with `prefers-reduced-motion` still sees every panel — the reveals are decoration, all content is in the frozen frame |

## Actions

Two links, both in the badge row, both real. No `href="#"`, nothing that says
"coming soon". Every heatmap cell carries a `<title>` with its date and count,
so hovering a day is a real interaction.

## Failure branches

- GitHub changes the contributions markup → `fetch_contributions.py` exits with
  "GitHub markup changed, fix the selector" rather than writing an empty file.
- `gh` is not authenticated → `fetch_stack.py` says so and exits; it never
  writes a partial `stack.json`.
- A renderer is edited badly → `render_all.py` stops at the first non-zero exit,
  so a half-rendered set is never committed.
