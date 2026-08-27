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

**2026-08-27 — Rebuilt as ten sections in Matrix green; v1 archived.**
The first build used the Float grammar (lime accent, ASCII wordmark, light and
dark pairs). Cameron rejected the register as too austere and too much like a
landing page. The replacement is one dark surface, one phosphor accent, and
compact bands with no section headlines. v1 is in `_archive/v1-float/` rather
than deleted.

**2026-08-27 — Dark only, no light pair.**
Halves the asset count and matches the intent. A reader in GitHub's light theme
gets a deliberate dark page.

**2026-08-27 — Account buttons are separate SVGs wrapped in markdown anchors.**
A link inside an `<img>`-embedded SVG never fires, so a single accounts strip
could not be clicked. Five small images with the `<a>` in the README is the only
thing that works. The same sandbox rules out hover, so the affordance is a
looping arrow nudge.

**2026-08-27 — Never rest an element at `opacity:0`.**
Chromium does not run animations in an offscreen `<img>`-embedded SVG. During
the full-page gate the contact card and every button rendered blank because
their resting state was invisible. `animation-fill-mode: both` back-fills the
from-state anyway, so the invisible state belongs in the keyframe and the base
style must be visible.

**2026-08-27 — Never put a CSS `transform` on an element with a `transform`
attribute.** The CSS one replaces the attribute rather than composing with it.
The button arrows teleported to the top-left corner the moment their nudge
animation started. Position on an outer group, animate an inner one.

**2026-08-27 — Working hours are measured, not assumed.**
The section was mocked as a night owl peaking at 22:00. `fetch_hours.py` walks
real commit timestamps: 93% between 08:00 and 18:00, peak at midday, nothing
after 21:00. The data rewrote the copy. A made-up number on a public profile is
a lie with a nice chart around it.
