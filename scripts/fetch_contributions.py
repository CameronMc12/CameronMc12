#!/usr/bin/env python3
"""
Scrape the real daily contribution calendar from GitHub's public,
unauthenticated fragment -- the same HTML the profile page itself renders --
and write data/contributions.json with the raw days plus derived stats.

No token, no GraphQL, no secret. Private-repo contributions are included
because "Include private contributions on my profile" is ON for this account
(github.com/settings/profile). If that toggle is ever switched off this graph
silently drops to ~5% of the real volume, so the renderer prints the active-day
ratio and the workflow fails the run when it collapses.

Run daily by .github/workflows/refresh.yml.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "CameronMc12")
URL = f"https://github.com/users/{USERNAME}/contributions"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "contributions.json")

# if fewer than this share of days are active, the private-contributions toggle
# has almost certainly been turned off -- fail loudly rather than commit a
# graph that says Cameron did nothing all year.
MIN_ACTIVE_RATIO = float(os.environ.get("MIN_ACTIVE_RATIO", "0.15"))


def fetch_days() -> list[dict]:
    r = requests.get(URL, headers={"User-Agent": "cameronmc12-profile/1.0"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        sys.exit("no calendar cells found -- GitHub markup changed, fix the selector")

    tips = {t.get("for"): t.get_text(strip=True) for t in soup.find_all("tool-tip")}

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        text = tips.get(td.get("id"), "")
        if not text or re.search(r"no contributions", text, re.I):
            count = 0
        else:
            m = re.match(r"([\d,]+)", text)
            count = int(m.group(1).replace(",", "")) if m else 0
        days.append({"date": date, "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def current_streak(days: list[dict]) -> tuple[int, str | None, str | None]:
    i = len(days) - 1
    if days[i]["count"] == 0:
        i -= 1  # today isn't over yet; don't let it break the streak
    end = i
    n = 0
    while i >= 0 and days[i]["count"] > 0:
        n += 1
        i -= 1
    if n == 0:
        return 0, None, None
    return n, days[i + 1]["date"], days[end]["date"]


def longest_streak(days: list[dict]) -> tuple[int, str | None, str | None]:
    best = run = 0
    b_start = b_end = None
    r_start = 0
    for i, d in enumerate(days):
        if d["count"] > 0:
            if run == 0:
                r_start = i
            run += 1
            if run > best:
                best, b_start, b_end = run, days[r_start]["date"], days[i]["date"]
        else:
            run = 0
    return best, b_start, b_end


def build(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    active = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"])
    cur_n, cur_s, cur_e = current_streak(days)
    lng_n, lng_s, lng_e = longest_streak(days)

    monthly: dict[str, int] = {}
    dow = [0] * 7
    for d in days:
        monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]
        dow[(dt.date.fromisoformat(d["date"]).weekday() + 1) % 7] += d["count"]

    last30 = days[-30:]
    return {
        "username": USERNAME,
        "generated_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active,
        "active_ratio": round(active / len(days), 4),
        "avg_per_active_day": round(total / active, 1) if active else 0,
        "last_30_total": sum(d["count"] for d in last30),
        "current_streak": {"length": cur_n, "start": cur_s, "end": cur_e},
        "longest_streak": {"length": lng_n, "start": lng_s, "end": lng_e},
        "best_day": {"date": best["date"], "count": best["count"]},
        "busiest_weekday": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][dow.index(max(dow))],
        "by_weekday": dow,
        "monthly": [{"month": k, "total": v} for k, v in sorted(monthly.items())],
        "days": days,
    }


if __name__ == "__main__":
    data = build(fetch_days())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    print(
        f"wrote data/contributions.json -- {data['total_contributions']:,} contributions, "
        f"{data['active_days']}/{len(data['days'])} active days "
        f"({data['active_ratio']:.0%}), streak {data['current_streak']['length']}"
    )
    if data["active_ratio"] < MIN_ACTIVE_RATIO:
        sys.exit(
            f"\nFAIL: only {data['active_ratio']:.0%} of days are active.\n"
            "Almost certainly 'Include private contributions on my profile' was\n"
            "switched off at github.com/settings/profile. Turn it back on, then\n"
            "re-run. Not committing a graph that misrepresents the year."
        )
