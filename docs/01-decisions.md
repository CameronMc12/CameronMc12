# Decisions

## Never

- Never hardcode a colour in a renderer. Tokens live in `scripts/theme.py`.
- Never name a private repo anywhere in this repo. Aggregate bytes only.
- Never publish a heatmap that has collapsed — `fetch_contributions.py` exits
  non-zero below a 15% active-day ratio rather than commit it.
- Never use a hosted stats widget (`github-readme-stats` and friends). They
  render on someone else's server, rate-limit, and eventually show a broken
  image on the profile.
- Never rely on JavaScript. GitHub strips `<script>` from a README and from an
  SVG loaded through `<img>`.

## Always

- Always emit a dark and a light file together, and select with `<picture>`.
- Always re-run `python3 scripts/render_all.py` after touching a renderer, and
  look at `docs/04-design/baselines/readme-*.png` before committing.
- Always keep reveals one-shot. Only textures loop.

## Rulings

**2026-08-27 — Private contributions toggle is load-bearing.**
Before this build the public calendar showed 21 active days out of 365 and
`totalCommitContributions` attributed exactly one repo. The commits were
correctly linked (`author_login: CameronMc12`, default branch, non-fork); the
cause was "Include private contributions on my profile" being off in
`github.com/settings/profile`. Turning it on took the calendar from 21 to 193
active days and 185 to 4,292 contributions. If that toggle is ever switched
back off, the daily workflow will fail rather than publish the collapsed graph.

**2026-08-27 — Scrape the public HTML, do not mint a PAT.**
With the toggle on, `github.com/users/<user>/contributions` already serves the
real numbers unauthenticated. A fine-grained token would have to be created,
stored as a secret and rotated before expiry, to produce the same figures.

**2026-08-27 — `fetch_stack.py` runs locally, not in CI.**
`GITHUB_TOKEN` inside this repo's own Actions run can only read this repo, so
the language mix across 29 private repos cannot be computed in CI without a PAT.
It changes by a few percent a month, so it is committed by hand.

**2026-08-27 — The hero is one SVG, not two images in a table.**
GitHub's README column is not a fixed width, so two `<img>` tags with fixed
widths scale by different amounts at different viewports and stop being the same
height. Compositing them into a single 880-wide file makes the alignment exact
at every width.

**2026-08-27 — Heatmap levels are absolute, not quartiles.**
Cut at 5 / 15 / 35 / 70 so a cell's colour means the same thing month to month.
Quartile-style cuts put 44 of 193 active days at maximum and the panel read as a
solid wall of lime.

**2026-08-27 — Seven letters, so the wordmark is a full-width band.**
At 490px "CAMERON" got 11 grid columns per letter and 6 rows of cap height,
which is below the resolution any letterform survives. Across the full 880 it
gets 30 columns and 21 rows. The reference profile uses three letters, which is
why a half-width panel works there.
