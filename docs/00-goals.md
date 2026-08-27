# Goals

**Why this exists.** `github.com/CameronMc12` was a blank profile with one
public repo. This makes the landing page say something true about a year of
work that is otherwise invisible, because 28 of 29 repos are private.

**For whom.** Anyone who lands on the profile from a proposal, a pitch, or a
link Cameron sends. Not for other developers to fork.

**What done looks like.** The profile loads, animates, states real numbers, and
the numbers stay right without anyone touching them. Cameron edits one JSON file
when what he is building changes; nothing else needs maintenance.

**How long this really is.** The build is done. Ongoing cost is a daily GitHub
Action that takes about 40 seconds, plus running `fetch_stack.py` by hand every
month or two when the language mix drifts. If it ever breaks it fails loudly
rather than silently publishing a wrong graph.

**Where it is now.** Built 2026-08-27. Four panels shipping, both themes,
daily refresh live.

**Non-goals.**

- Not a portfolio site. Links out; does not try to be a landing page.
- Not a stats service. No third-party widgets, no hosted images, no tokens.
- Not a place private repo names or client data appear.
