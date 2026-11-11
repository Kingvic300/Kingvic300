"""Render the "Behind the commits" activity card from real GitHub data.

Usage:  GITHUB_TOKEN=... python3 scripts/stats.py
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

from theme import MONO, SANS, THEMES, kicker, shell

LOGIN = "Kingvic300"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

QUERY = """
query($login: String!) {
  user(login: $login) {
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
    today = dt.date.today().isoformat()
    weeks = [[d for d in w["contributionDays"] if d["date"] <= today] for w in cal["weeks"]]
    weeks = [w for w in weeks if w]
    days = [d for w in weeks for d in w]

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
    best = max(days, key=lambda d: d["contributionCount"]) if days else {"contributionCount": 0, "date": today}

    langs = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            langs[name] = langs.get(name, 0) + edge["size"]
    for skip in ("HTML", "CSS", "Jupyter Notebook", "Dockerfile", "Shell", "Makefile"):
        langs.pop(skip, None)
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]

    return dict(
        total=cal["totalContributions"],
        weekly=[sum(d["contributionCount"] for d in w) for w in weeks],
        week_starts=[w[0]["date"] for w in weeks],
        current=current,
        longest=longest,
        best=best["contributionCount"],
        best_date=best["date"],
        prs=user["pullRequests"]["totalCount"],
        repos=user["repositories"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in user["repositories"]["nodes"]),
        langs=[(n, s / total) for n, s in top],
        updated=today,
    )


def fmt(n):
    return f"{n:,}"


def render(s, c):
    W, H = 1200, 480
    out = [
        kicker(40, 50, "Activity · last 12 months", c, color=c["accent"]),
        kicker(W - 40, 50, f'updated {s["updated"]}', c, anchor="end"),
        f'<text x="40" y="94" font-family="{SANS}" fill="{c["text"]}">'
        f'<tspan font-size="34" font-weight="700">{fmt(s["total"])}</tspan>'
        f'<tspan font-size="16" fill="{c["muted"]}" dx="10">contributions in the last year</tspan></text>',
    ]

    # weekly contributions chart with gridlines and month labels
    cx, cy, cw, ch = 96, 132, 644, 196
    weekly = s["weekly"]
    peak = max(weekly) or 1
    for frac in (1, 0.5):
        y = cy + ch - ch * frac
        out.append(f'<line x1="{cx}" y1="{y:.1f}" x2="{cx+cw}" y2="{y:.1f}" stroke="{c["border"]}" stroke-dasharray="3 5"/>')
        out.append(f'<text x="{cx-10}" y="{y+4:.1f}" text-anchor="end" font-family="{MONO}" font-size="11" '
                   f'fill="{c["muted"]}">{fmt(round(peak*frac))}/wk</text>')
    out.append(f'<line x1="{cx}" y1="{cy+ch}" x2="{cx+cw}" y2="{cy+ch}" stroke="{c["border"]}" stroke-width="1.5"/>')
    gap = 3
    bw = (cw - gap * (len(weekly) - 1)) / max(len(weekly), 1)
    last_month = None
    for i, v in enumerate(weekly):
        x = cx + i * (bw + gap)
        if v:
            h = max(3.0, ch * v / peak)
            op = 0.35 + 0.65 * v / peak
            out.append(f'<rect x="{x:.1f}" y="{cy+ch-h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" '
                       f'fill="{c["accent"]}" fill-opacity="{op:.2f}"/>')
        else:
            out.append(f'<rect x="{x:.1f}" y="{cy+ch-3:.1f}" width="{bw:.1f}" height="3" rx="1.5" fill="{c["faint"]}"/>')
        month = s["week_starts"][i][:7]
        if month != last_month:
            if last_month is not None and int(month[5:]) % 2 == 1:
                label = dt.date.fromisoformat(month + "-01").strftime("%b")
                out.append(f'<text x="{x:.1f}" y="{cy+ch+22}" font-family="{MONO}" font-size="12" fill="{c["muted"]}">{label}</text>')
            last_month = month

    # stat tiles (2 x 3)
    best_day = dt.date.fromisoformat(s["best_date"]).strftime("%d %b")
    tiles = [
        (f'{s["current"]}d', "current streak"),
        (f'{s["longest"]}d', "longest streak"),
        (fmt(s["prs"]), "pull requests"),
        (fmt(s["best"]), f"best day · {best_day}"),
        (fmt(s["repos"]), "public repos"),
        (fmt(s["stars"]), "stars earned"),
    ]
    tx, ty, tw, th, tg = 784, 74, 180, 78, 16
    for i, (val, label) in enumerate(tiles):
        x = tx + (i % 2) * (tw + tg)
        y = ty + (i // 2) * (th + tg)
        out.append(f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="12" fill="{c["bg"]}" stroke="{c["border"]}"/>')
        out.append(f'<text x="{x+18}" y="{y+38}" font-family="{SANS}" font-size="26" font-weight="700" '
                   f'fill="{c["accent"] if i == 0 else c["text"]}">{escape(val)}</text>')
        out.append(f'<text x="{x+18}" y="{y+60}" font-family="{MONO}" font-size="12.5" fill="{c["muted"]}">{escape(label)}</text>')

    # languages: segmented bar plus legend
    ly = 400
    out.append(kicker(40, ly - 12, "Languages I ship with", c))
    out.append(kicker(W - 40, ly - 12, "share of code in public repos", c, anchor="end"))
    bar_w, seg_gap = W - 80, 4
    x = 40.0
    parts = list(s["langs"])
    rest = 1 - sum(p for _, p in parts)
    if rest > 0.005:
        parts.append(("Other", rest))
    usable = bar_w - seg_gap * (len(parts) - 1)
    colors = c["scale"] + [c["faint"]]
    for i, (name, p) in enumerate(parts):
        col = colors[i] if name != "Other" else c["faint"]
        out.append(f'<rect x="{x:.1f}" y="{ly}" width="{max(usable*p, 2):.1f}" height="12" rx="4" fill="{col}"/>')
        x += usable * p + seg_gap
    lx = 40
    for i, (name, p) in enumerate(s["langs"]):
        label = f"{name} {p*100:.0f}%"
        out.append(f'<rect x="{lx}" y="{ly+28}" width="10" height="10" rx="3" fill="{colors[i]}"/>')
        out.append(f'<text x="{lx+16}" y="{ly+37}" font-family="{MONO}" font-size="13" fill="{c["muted"]}">{escape(label)}</text>')
        lx += 36 + len(label) * 8

    desc = (f'GitHub activity for {LOGIN}: {fmt(s["total"])} contributions in the last year, longest streak '
            f'{s["longest"]} days, {fmt(s["prs"])} pull requests, {fmt(s["stars"])} stars across {s["repos"]} public repositories.')
    return shell(W, H, c, desc, "".join(out), rx=18)


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
    print(json.dumps({k: v for k, v in stats.items() if k not in ("weekly", "week_starts")}))


if __name__ == "__main__":
    main()
