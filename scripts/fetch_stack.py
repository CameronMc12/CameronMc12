#!/usr/bin/env python3
"""
Aggregate the real language mix across every repo -- private included -- into
data/stack.json.

Runs LOCALLY, not in CI. It needs Cameron's `gh` auth (repo scope) to see the
private repos, and GITHUB_TOKEN inside the profile repo's own Actions run can
only ever see that one repo. Rather than mint and rotate a fine-grained PAT for
a number that moves by a few percent a month, this is committed by hand:

    python3 scripts/fetch_stack.py && python3 scripts/render_all.py

PRIVACY: repo NAMES are never written to this file. Cameron's private repos are
client work (Ikonik, Mezzanine, Shelving SA) and a public profile has no
business listing them. Only aggregate byte counts leave the API. The
"currently building" lines on the info card come from data/identity.json,
which he edits by hand and controls completely.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "stack.json")

# languages GitHub reports that say nothing about what someone can build
IGNORE = {"HTML", "CSS", "SCSS", "Dockerfile", "Makefile", "Shell", "Batchfile",
          "Procfile", "Nix", "Roff", "MDX"}

GQL = """
query($cursor: String) {
  viewer {
    login
    name
    createdAt
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
      pageInfo { hasNextPage endCursor }
      nodes {
        isPrivate
        isArchived
        pushedAt
        stargazerCount
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def gh_graphql(cursor: str | None) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={GQL}"]
    if cursor:
        args += ["-f", f"cursor={cursor}"]
    else:
        args += ["-F", "cursor="]
    res = subprocess.run(args, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"gh api failed -- is `gh auth status` green?\n{res.stderr.strip()}")
    return json.loads(res.stdout)["data"]["viewer"]


def main() -> None:
    cursor = None
    nodes: list[dict] = []
    login = name = created = ""
    while True:
        v = gh_graphql(cursor)
        login, name, created = v["login"], v["name"], v["createdAt"]
        page = v["repositories"]
        nodes += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    sizes: dict[str, int] = {}
    colors: dict[str, str] = {}
    for repo in nodes:
        for edge in repo["languages"]["edges"]:
            lang = edge["node"]["name"]
            if lang in IGNORE:
                continue
            sizes[lang] = sizes.get(lang, 0) + edge["size"]
            colors[lang] = edge["node"]["color"] or "#8A8A93"

    total = sum(sizes.values()) or 1
    ranked = sorted(sizes.items(), key=lambda kv: -kv[1])
    langs = [
        {"name": k, "bytes": v, "pct": round(100 * v / total, 1), "color": colors[k]}
        for k, v in ranked
    ]

    data = {
        "login": login,
        "name": name,
        "member_since": created[:10],
        "repos_total": len(nodes),
        "repos_public": sum(1 for r in nodes if not r["isPrivate"]),
        "repos_private": sum(1 for r in nodes if r["isPrivate"]),
        "repos_active_90d": sum(1 for r in nodes if not r["isArchived"]),
        "code_bytes": total,
        "languages": langs,
    }
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    top = ", ".join(f"{l['name']} {l['pct']}%" for l in langs[:5])
    print(f"wrote data/stack.json -- {len(nodes)} repos, {total/1e6:.1f}MB of code\n  {top}")


if __name__ == "__main__":
    main()
