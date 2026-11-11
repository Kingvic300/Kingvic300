"""Render the "Behind the Commits" activity card from real GitHub data.

Usage:  GITHUB_TOKEN=... python scripts/stats.py
Writes: assets/stats-light.svg and assets/stats-dark.svg

Standard library only. If the API call fails, nothing is written, so the
README keeps showing the last good card.

The contribution total matches the profile graph, so it includes private
contributions while "Include private contributions" is on in GitHub settings.
"""

import datetime as dt
import json
import os
import sys
import urllib.request
from html import escape

LOGIN = "Kingvic300"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    pullRequests { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC,
                 isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""

from theme import MONO, SANS, THEMES


def fetch(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-readme-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors") or not payload.get("data", {}).get("user"):
        raise RuntimeError(payload.get("errors"))
    return payload["data"]["user"]


def summarize(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    today = dt.date.today().isoformat()
    days = [d for d in days if d["date"] <= today]

    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    # today may have no contributions yet; start counting from yesterday then
    tail = days[:-1] if days and not days[-1]["contributionCount"] else days
    for d in reversed(tail):
        if not d["contributionCount"]:
            break
        current += 1

    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]

    langs = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            langs[name] = langs.get(name, 0) + edge["size"]
    for skip in ("HTML", "CSS", "Jupyter Notebook", "Dockerfile", "Shell", "Makefile"):
        langs.pop(skip, None)
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    top = [(n, s / total) for n, s in top]

    return dict(
        total=cal["totalContributions"],
        weekly=weekly,
        first=days[0]["date"] if days else today,
        current=current,
        longest=longest,
        prs=user["pullRequests"]["totalCount"],
        repos=user["repositories"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in user["repositories"]["nodes"]),
        langs=top,
        updated=today,
    )


def fmt(n):
    return f"{n:,}"


def render(s, c):
    W, H = 1200, 460
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="t d">',
        '<title id="t">Behind the commits</title>',
        f'<desc id="d">GitHub activity for {LOGIN}: {fmt(s["total"])} contributions in the last year, '
        f'longest streak {s["longest"]} days, {fmt(s["prs"])} pull requests, {fmt(s["stars"])} stars '
        f'across {s["repos"]} public repositories.</desc>',
        f'<defs><linearGradient id="bar" x1="0" y1="1" x2="0" y2="0">'
        f'<stop offset="0" stop-color="{c["mint"]}"/><stop offset="1" stop-color="{c["sky"]}"/></linearGradient>'
        f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["sky"]}"/>'
        f'<stop offset="0.55" stop-color="{c["mint"]}"/><stop offset="1" stop-color="{c["indigo"]}"/></linearGradient></defs>',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="2"/>',
        f'<text x="40" y="56" font-family="{MONO}" font-size="18" fill="{c["muted"]}">'
        f'<tspan fill="{c["mint"]}">$</tspan> git log --author=Kingvic300 --since="1 year ago"</text>',
        f'<text x="{W-40}" y="56" text-anchor="end" font-family="{MONO}" font-size="14" fill="{c["muted"]}">'
        f'updated {s["updated"]}</text>',
    ]

    # contributions chart
    cx, cy, cw, ch = 40, 110, 700, 200
    weekly = s["weekly"]
    peak = max(weekly) or 1
    gap = 3
    bw = (cw - gap * (len(weekly) - 1)) / max(len(weekly), 1)
    out.append(f'<text x="{cx}" y="{cy-14}" font-family="{SANS}" font-size="15" font-weight="600" fill="{c["text"]}">'
               f'Contributions per week</text>')
    out.append(f'<line x1="{cx}" y1="{cy+ch}" x2="{cx+cw}" y2="{cy+ch}" stroke="{c["faint"]}" stroke-width="1.5"/>')
    for i, v in enumerate(weekly):
        h = max(2.0, ch * v / peak) if v else 2.0
        fill = "url(#bar)" if v else c["faint"]
        out.append(f'<rect x="{cx + i*(bw+gap):.1f}" y="{cy+ch-h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="1.5" fill="{fill}"/>')
    first = dt.date.fromisoformat(s["first"]).strftime("%b %Y")
    out.append(f'<text x="{cx}" y="{cy+ch+24}" font-family="{MONO}" font-size="13" fill="{c["muted"]}">{first}</text>')
    out.append(f'<text x="{cx+cw}" y="{cy+ch+24}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{c["muted"]}">now</text>')
    out.append(f'<text x="{cx+cw}" y="{cy-14}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{c["muted"]}">peak {fmt(peak)}/wk</text>')

    # stat tiles (2 x 3)
    tiles = [
        (fmt(s["total"]), "contributions", c["sky"]),
        (f'{s["longest"]}d', "longest streak", c["mint"]),
        (f'{s["current"]}d', "current streak", c["mint"]),
        (fmt(s["prs"]), "pull requests", c["indigo"]),
        (fmt(s["stars"]), "stars earned", c["sky"]),
        (fmt(s["repos"]), "public repos", c["indigo"]),
    ]
    tx, ty, tw, th, tg = 790, 90, 175, 72, 16
    for i, (val, label, col) in enumerate(tiles):
        x = tx + (i % 2) * (tw + tg)
        y = ty + (i // 2) * (th + tg)
        out.append(f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="10" fill="none" stroke="{c["border"]}" stroke-width="1.5"/>')
        out.append(f'<rect x="{x}" y="{y+16}" width="3" height="{th-32}" rx="1.5" fill="{col}"/>')
        out.append(f'<text x="{x+18}" y="{y+36}" font-family="{SANS}" font-size="26" font-weight="700" fill="{c["text"]}">{escape(val)}</text>')
        out.append(f'<text x="{x+18}" y="{y+58}" font-family="{MONO}" font-size="13" fill="{c["muted"]}">{label}</text>')

    # languages bar
    ly = 392
    out.append(f'<text x="40" y="{ly-8}" font-family="{SANS}" font-size="15" font-weight="600" fill="{c["text"]}">Languages I ship with</text>')
    out.append(f'<text x="{W-40}" y="{ly-8}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{c["muted"]}">share of code in public repos</text>')
    palette = [c["sky"], c["mint"], c["indigo"], c["amber"], c["slate"]]
    x, bar_w = 40.0, W - 80
    out.append(f'<clipPath id="lc"><rect x="40" y="{ly+4}" width="{bar_w}" height="10" rx="5"/></clipPath><g clip-path="url(#lc)">')
    rest = 1 - sum(p for _, p in s["langs"])
    for (name, p), col in zip(s["langs"], palette):
        out.append(f'<rect x="{x:.1f}" y="{ly+4}" width="{bar_w*p:.1f}" height="10" fill="{col}"/>')
        x += bar_w * p
    if rest > 0:
        out.append(f'<rect x="{x:.1f}" y="{ly+4}" width="{bar_w*rest:.1f}" height="10" fill="{c["faint"]}"/>')
    out.append("</g>")
    lx = 40
    for (name, p), col in zip(s["langs"], palette):
        label = f"{name} {p*100:.0f}%"
        out.append(f'<circle cx="{lx+5}" cy="{ly+34}" r="5" fill="{col}"/>')
        out.append(f'<text x="{lx+16}" y="{ly+39}" font-family="{MONO}" font-size="14" fill="{c["muted"]}">{escape(label)}</text>')
        lx += 30 + len(label) * 8.6

    out.append(f'<rect x="1" y="{H-6}" width="{W-2}" height="5" rx="2.5" fill="url(#accent)"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set; leaving existing cards untouched.")
    try:
        stats = summarize(fetch(token))
    except Exception as exc:  # keep the last good card on any API problem
        sys.exit(f"GitHub API unavailable ({exc}); leaving existing cards untouched.")
    for name, colors in THEMES.items():
        with open(os.path.join(OUT_DIR, f"stats-{name}.svg"), "w", encoding="utf-8") as f:
            f.write(render(stats, colors))
    print(json.dumps({k: v for k, v in stats.items() if k != "weekly"}))


if __name__ == "__main__":
    main()
