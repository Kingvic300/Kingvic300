"""Render the "Recently shipped" card: latest merged PRs and recently pushed repos.

Usage:  GITHUB_TOKEN=... python3 scripts/activity.py
Writes: assets/activity-light.svg and assets/activity-dark.svg

Standard library only. Only public repositories are shown. If the API call
fails, nothing is written, so the README keeps the last good card.
"""

import datetime as dt
import json
import os
import sys
import urllib.request
from html import escape

from theme import MONO, SANS, THEMES, kicker, shell

LOGIN = "Kingvic300"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
SKIP_REPOS = {f"{LOGIN}/{LOGIN}"}  # the profile repo itself is pushed hourly by a bot

QUERY = """
query($login: String!) {
  user(login: $login) {
    pullRequests(first: 30, states: MERGED, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes { title mergedAt repository { nameWithOwner isPrivate } }
    }
    repositories(first: 12, privacy: PUBLIC, isFork: false,
                 ownerAffiliations: [OWNER, ORGANIZATION_MEMBER],
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes { nameWithOwner description pushedAt primaryLanguage { name color } }
    }
  }
}
"""


def fetch(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-readme-activity"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors") or not payload.get("data", {}).get("user"):
        raise RuntimeError(payload.get("errors"))
    return payload["data"]["user"]


def ago(stamp, now):
    days = (now - dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))).days
    if days <= 0:
        return "today"
    if days == 1:
        return "1 day ago"
    if days < 30:
        return f"{days} days ago"
    return f"{days // 30} mo ago"


def clip(text, limit):
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def render(user, c):
    W, H, mid = 900, 372, 470
    now = dt.datetime.now(dt.timezone.utc)
    prs = [p for p in user["pullRequests"]["nodes"] if not p["repository"]["isPrivate"]]
    prs.sort(key=lambda p: p["mergedAt"], reverse=True)
    repos = [r for r in user["repositories"]["nodes"] if r["nameWithOwner"] not in SKIP_REPOS][:4]

    out = [kicker(32, 46, "Recently merged", c, color=c["accent"]),
           kicker(mid + 24, 46, "Shipping now", c, color=c["accent"]),
           kicker(W - 32, 46, f'updated {now.date().isoformat()}', c, anchor="end"),
           f'<line x1="{mid}" y1="32" x2="{mid}" y2="{H-28}" stroke="{c["border"]}"/>']

    y = 92
    for p in prs[:5]:
        out.append(f'<g transform="translate(32 {y-14})" fill="none" stroke="{c["accent"]}" stroke-width="1.6" '
                   f'stroke-linecap="round"><circle cx="4" cy="3" r="2.5"/><circle cx="4" cy="15" r="2.5"/>'
                   f'<circle cx="14" cy="15" r="2.5"/><path d="M4 5.5v7M14 12.5V8a3 3 0 0 0-3-3H8"/></g>')
        out.append(f'<text x="58" y="{y}" font-family="{SANS}" font-size="15" fill="{c["text"]}">{escape(clip(p["title"], 44))}</text>')
        out.append(f'<text x="58" y="{y+20}" font-family="{MONO}" font-size="12" fill="{c["muted"]}">'
                   f'{escape(p["repository"]["nameWithOwner"])} · {ago(p["mergedAt"], now)}</text>')
        y += 52
    if not prs:
        out.append(f'<text x="40" y="96" font-family="{SANS}" font-size="15" fill="{c["muted"]}">No public merged PRs yet.</text>')

    y = 92
    for r in repos:
        lang = r["primaryLanguage"] or {"name": "", "color": c["muted"]}
        out.append(f'<text x="{mid+24}" y="{y}" font-family="{MONO}" font-size="14.5" font-weight="700" '
                   f'fill="{c["text"]}">{escape(r["nameWithOwner"])}</text>')
        out.append(f'<text x="{W-32}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="12" '
                   f'fill="{c["muted"]}">{ago(r["pushedAt"], now)}</text>')
        meta = clip(r["description"] or "No description yet.", 40)
        out.append(f'<circle cx="{mid+29}" cy="{y+16}" r="5" fill="{lang["color"] or c["muted"]}"/>')
        out.append(f'<text x="{mid+42}" y="{y+21}" font-family="{SANS}" font-size="13.5" fill="{c["muted"]}">'
                   f'{escape(lang["name"] + " · " if lang["name"] else "")}{escape(meta)}</text>')
        y += 66

    return shell(W, H, c, "Recently merged pull requests and recently pushed repositories for " + LOGIN,
                 "".join(out), rx=18)


OSS = [("Kingvic300", "Huntly", "Private job-hunting assistant"),
       ("Kingvic300", "Forma", "Offline desktop office suite")]

OSS_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    stargazerCount forkCount
    issues(states: OPEN) { totalCount }
    latestRelease { tagName }
    releases(first: 100) { nodes { releaseAssets(first: 50) { nodes { downloadCount } } } }
  }
}
"""


def gql(token, query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-readme-activity"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors") or not payload.get("data"):
        raise RuntimeError(payload.get("errors"))
    return payload["data"]


def fetch_oss(token):
    out = []
    for owner, name, tagline in OSS:
        r = gql(token, OSS_QUERY, {"owner": owner, "name": name})["repository"]
        downloads = sum(a["downloadCount"] for rel in r["releases"]["nodes"] for a in rel["releaseAssets"]["nodes"])
        out.append(dict(name=name, tagline=tagline, stars=r["stargazerCount"], forks=r["forkCount"],
                        issues=r["issues"]["totalCount"], downloads=downloads,
                        version=(r["latestRelease"] or {}).get("tagName") or "unreleased"))
    return out


def render_oss(projects, c):
    W, H = 880, 196
    col_w = (W - 64 - 16) / 2
    out = [kicker(32, 42, "Open source by the numbers", c, color=c["accent"]),
           kicker(W - 32, 42, "local-first · no telemetry · PRs welcome", c, anchor="end")]
    for i, p in enumerate(projects):
        x = 32 + i * (col_w + 16)
        out.append(f'<rect x="{x:.1f}" y="62" width="{col_w:.1f}" height="110" rx="12" fill="{c["bg"]}" stroke="{c["border"]}"/>')
        out.append(f'<text x="{x+18:.1f}" y="92" font-family="{SANS}" font-size="17" font-weight="700" fill="{c["text"]}">{escape(p["name"])}</text>')
        vw = len(p["version"]) * 7.4 + 16
        out.append(f'<rect x="{x+col_w-18-vw:.1f}" y="76" width="{vw:.1f}" height="22" rx="6" fill="{c["accent_soft"]}"/>')
        out.append(f'<text x="{x+col_w-18-vw/2:.1f}" y="91" text-anchor="middle" font-family="{MONO}" font-size="12" '
                   f'fill="{c["accent"]}">{escape(p["version"])}</text>')
        stats = [(p["downloads"], "downloads"), (p["stars"], "stars"), (p["forks"], "forks"), (p["issues"], "open issues")]
        sw = (col_w - 36) / 4
        for j, (val, label) in enumerate(stats):
            sx = x + 18 + j * sw
            out.append(f'<text x="{sx:.1f}" y="136" font-family="{SANS}" font-size="22" font-weight="700" '
                       f'fill="{c["accent"] if j == 0 else c["text"]}">{val:,}</text>')
            out.append(f'<text x="{sx:.1f}" y="156" font-family="{MONO}" font-size="11.5" fill="{c["muted"]}">{label}</text>')
    desc = "; ".join(f'{p["name"]} {p["version"]}: {p["downloads"]:,} downloads, {p["stars"]} stars' for p in projects)
    return shell(W, H, c, "Open source stats: " + desc, "".join(out), rx=18)


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set; leaving existing cards untouched.")
    try:
        user = fetch(token)
    except Exception as exc:  # keep the last good card on any API problem
        sys.exit(f"GitHub API unavailable ({exc}); leaving existing cards untouched.")
    for name, colors in THEMES.items():
        with open(os.path.join(OUT_DIR, f"activity-{name}.svg"), "w", encoding="utf-8") as f:
            f.write(render(user, colors))
    try:
        projects = fetch_oss(token)
    except Exception as exc:
        sys.exit(f"Open source stats unavailable ({exc}); leaving that card untouched.")
    for name, colors in THEMES.items():
        with open(os.path.join(OUT_DIR, f"oss-stats-{name}.svg"), "w", encoding="utf-8") as f:
            f.write(render_oss(projects, colors))
    print("wrote activity and open source cards")


if __name__ == "__main__":
    main()
