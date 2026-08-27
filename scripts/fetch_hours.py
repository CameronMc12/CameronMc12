#!/usr/bin/env python3
"""
Aggregate the hour-of-day of real commits into data/hours.json.

Runs LOCALLY, not in CI: it needs Cameron's `gh` auth to see the private repos,
and GITHUB_TOKEN inside the profile repo's own Actions run can only see that one
repo. The shape of a working day moves slowly, so this is committed by hand.

The public contributions endpoint is daily-only — it carries no clock — so this
walks the commit list of every repo and reads the author timestamps. Without it
the "working hours" section would be a drawing rather than a measurement, and a
made-up number on a public profile is just a lie with a nice chart around it.

PRIVACY: repo NAMES never reach the output. Only the 24 hour buckets do.

    python3 scripts/fetch_hours.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "hours.json")

USER = os.environ.get("GH_PROFILE_USER", "CameronMc12")
TZ = ZoneInfo(os.environ.get("GH_PROFILE_TZ", "Africa/Johannesburg"))
PER_REPO = 100          # most recent N commits per repo


def gh(args: list[str]) -> object:
    res = subprocess.run(["gh", *args], capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"gh failed — is `gh auth status` green?\n{res.stderr.strip()}")
    return json.loads(res.stdout)


def main() -> None:
    repos = gh(["repo", "list", USER, "--limit", "200", "--no-archived",
                "--source", "--json", "nameWithOwner,defaultBranchRef"])
    buckets = [0] * 24
    total = 0
    scanned = 0

    for repo in repos:
        name = repo["nameWithOwner"]
        try:
            commits = gh(["api", f"repos/{name}/commits",
                          "-X", "GET", "-f", f"author={USER}",
                          "-f", f"per_page={PER_REPO}",
                          "--jq", "[.[].commit.author.date]"])
        except SystemExit:
            continue                       # empty repo, or no default branch
        scanned += 1
        for stamp in commits:
            when = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            buckets[when.astimezone(TZ).hour] += 1
            total += 1

    if not total:
        sys.exit("no commits found — nothing written")

    peak = buckets.index(max(buckets))
    quiet_start = min(range(24), key=lambda i: sum(buckets[(i + k) % 24] for k in range(4)))
    late = sum(buckets[21:] + buckets[:2]) / total
    quiet = sum(buckets[(quiet_start + k) % 24] for k in range(4)) / total

    data = {
        "generated_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "timezone": str(TZ),
        "repos_scanned": scanned,
        "commits_sampled": total,
        "by_hour": buckets,
        "peak_hour": peak,
        "late_share": round(late, 4),
        "quiet_window": [quiet_start, (quiet_start + 4) % 24],
        "quiet_share": round(quiet, 4),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote data/hours.json — {total:,} commits across {scanned} repos, "
          f"peak {peak:02d}:00, {late:.0%} after 21:00")


if __name__ == "__main__":
    main()
