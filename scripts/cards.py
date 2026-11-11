"""Generate the README banner, cards and social icons (light and dark).

Usage:  python3 scripts/cards.py
Writes: assets/banner-{dark,light}.svg, assets/cards/*.svg, assets/icons/*.svg

Standard library only. Edit the text in CONTENT and re-run; the README links
to the files by name, so it does not need to change. Cards in the same group
share one height so each row lines up.
"""

import base64
import os
from html import escape

from brand_paths import PATHS
from theme import MONO, SANS, THEMES, kicker, shell

ROOT = os.path.join(os.path.dirname(__file__), "..")
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ASSETS, "cards")
ICONS = os.path.join(ASSETS, "icons")
AVATAR = os.path.join(ASSETS, "media", "avatar.webp")


# ---------------------------------------------------------------- helpers

def wrap(text, size, width, bold=False):
    """Greedy word wrap using an average glyph width; deliberately conservative."""
    per = size * (0.54 if bold else 0.485)
    limit = max(1, int(width / per))
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if len(test) <= limit:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def text_block(x, y, lines, size, fill, leading, family=SANS, weight="400"):
    spans = "".join(
        f'<tspan x="{x}" dy="{0 if i == 0 else leading}">{escape(l)}</tspan>' for i, l in enumerate(lines)
    )
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{spans}</text>')


def pill_rows(tags, x, max_x):
    rows, cx = 1, x
    for t in tags:
        w = len(t) * 7.2 + 18
        if cx + w > max_x and cx != x:
            cx, rows = x, rows + 1
        cx += w + 8
    return rows


def pills(x, y, tags, c, max_x):
    out, cx, cy = [], x, y
    for t in tags:
        w = len(t) * 7.2 + 18
        if cx + w > max_x and cx != x:
            cx, cy = x, cy + 30
        out.append(f'<rect x="{cx:.0f}" y="{cy}" width="{w:.0f}" height="22" rx="6" fill="{c["bg"]}" stroke="{c["border"]}"/>'
                   f'<text x="{cx + w/2:.0f}" y="{cy+15}" text-anchor="middle" font-family="{MONO}" '
                   f'font-size="12" fill="{c["muted"]}">{escape(t)}</text>')
        cx += w + 8
    return "".join(out)


def tile(x, y, c, inner, size=40):
    return (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="10" fill="{c["accent_soft"]}"/>'
            f'<g transform="translate({x + (size-24)/2} {y + (size-24)/2})" fill="none" stroke="{c["accent"]}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{inner}</g>')


# 24x24 line icons for the focus cards
GLYPHS = {
    "server": '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/>'
              '<circle cx="7" cy="7.5" r="0.6"/><circle cx="7" cy="16.5" r="0.6"/><path d="M11 7.5h6M11 16.5h6"/>',
    "spark": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M18.5 16.5l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7z"/>',
    "cube": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>',
    "window": '<rect x="3" y="4" width="18" height="14" rx="2"/><path d="M3 8h18M8 21h8M12 18v3"/>',
}


def status(x_right, y, label, c, color):
    w = len(label) * 8.1
    return (f'<circle cx="{x_right - w - 9:.1f}" cy="{y - 4}" r="3.5" fill="{color}"/>'
            + kicker(x_right, y, label, c, anchor="end"))


# ---------------------------------------------------------------- banner

def banner(c):
    W, H = 1200, 300
    with open(AVATAR, "rb") as f:
        avatar = base64.b64encode(f.read()).decode()
    ax, ay, ar = 1012, 138, 88
    chips, cx = [], 64
    for t in ["Backend", "AI & agents", "Web3 tooling", "Desktop apps"]:
        w = len(t) * 8.4 + 28
        chips.append(f'<rect x="{cx:.0f}" y="222" width="{w:.0f}" height="30" rx="8" fill="{c["bg"]}" stroke="{c["border"]}"/>'
                     f'<text x="{cx + w/2:.0f}" y="242" text-anchor="middle" font-family="{MONO}" font-size="14" '
                     f'fill="{c["text"]}">{escape(t)}</text>')
        cx += w + 10
    bw = 156
    by = ay + ar + 10
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Victor Oladimeji</title>
<desc id="d">Banner for Victor Oladimeji (Kingvic300): full-stack engineer building backend systems, AI products and Web3 developer tools.</desc>
<defs>
<pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{c["border"]}"/></pattern>
<clipPath id="av"><circle cx="{ax}" cy="{ay}" r="{ar}"/></clipPath>
<clipPath id="card"><rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="20"/></clipPath>
</defs>
<rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="20" fill="{c["surface"]}" stroke="{c["border"]}" stroke-width="1.5"/>
<rect x="800" y="0" width="400" height="{H}" fill="url(#grid)" clip-path="url(#card)"/>
{kicker(64, 84, "Full-stack engineer  ·  Lagos, Nigeria", c, color=c["accent"])}
<text x="60" y="156" font-family="{SANS}" font-size="66" font-weight="700" letter-spacing="-1.5" fill="{c["text"]}">Victor Oladimeji</text>
<text x="64" y="196" font-family="{SANS}" font-size="20" fill="{c["muted"]}">Backend systems, AI products and Web3 developer tools.</text>
{"".join(chips)}
<circle cx="{ax}" cy="{ay}" r="{ar+20}" fill="none" stroke="{c["muted"]}" stroke-opacity="0.5" stroke-width="1.5" stroke-dasharray="3 7">
<animateTransform attributeName="transform" type="rotate" from="0 {ax} {ay}" to="360 {ax} {ay}" dur="60s" repeatCount="indefinite"/></circle>
<circle cx="{ax}" cy="{ay}" r="{ar+6}" fill="{c["surface"]}" stroke="{c["accent"]}" stroke-width="3"/>
<image href="data:image/webp;base64,{avatar}" x="{ax-ar}" y="{ay-ar}" width="{2*ar}" height="{2*ar}" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>
<rect x="{ax - bw/2}" y="{by}" width="{bw}" height="30" rx="15" fill="{c["surface"]}" stroke="{c["border"]}" stroke-width="1.5"/>
<circle cx="{ax - bw/2 + 20}" cy="{by + 15}" r="4" fill="{c["live"]}"/>
<text x="{ax - bw/2 + 32}" y="{by + 20}" font-family="{MONO}" font-size="13" fill="{c["text"]}">open to collabs</text>
</svg>
"""


# ---------------------------------------------------------------- card types

def focus_height(d):
    return 96 + 21 * (len(wrap(d["text"], 14.5, 352)) - 1) + 26


def focus_card(d, c, h):
    w = 400
    body = (tile(24, 24, c, GLYPHS[d["glyph"]])
            + f'<text x="80" y="50" font-family="{SANS}" font-size="19" font-weight="700" fill="{c["text"]}">{escape(d["title"])}</text>'
            + kicker(w - 24, 49, d["num"], c)
            + text_block(24, 96, wrap(d["text"], 14.5, w - 48), 14.5, c["muted"], 21))
    return shell(w, h, c, f'{d["title"]}: {d["text"]}', body)


def item_height(d, w):
    lines = len(wrap(d["text"], 14, w - 44))
    rows = pill_rows(d["tags"], 22, w - 18)
    return 148 + 20 * (lines - 1) + 18 + 30 * rows + 62


def item_card(d, c, h, w):
    """Project / open-source card: monogram tile, status, kicker, title, text, tags, footer link."""
    desc = wrap(d["text"], 14, w - 44)
    tags_y = 148 + 20 * (len(desc) - 1) + 18
    body = (f'<rect x="22" y="22" width="40" height="40" rx="10" fill="{c["accent_soft"]}"/>'
            f'<text x="42" y="49" text-anchor="middle" font-family="{SANS}" font-size="19" font-weight="700" '
            f'fill="{c["accent"]}">{escape(d["title"][0])}</text>'
            + status(w - 22, 46, d["status"], c, c["live"] if d["status"] == "live" else c["accent"])
            + kicker(22, 92, d["kicker"], c)
            + f'<text x="22" y="121" font-family="{SANS}" font-size="22" font-weight="700" fill="{c["text"]}">{escape(d["title"])}</text>'
            + text_block(22, 148, desc, 14, c["muted"], 20)
            + pills(22, tags_y, d["tags"], c, w - 18)
            + f'<line x1="22" y1="{h-50}" x2="{w-22}" y2="{h-50}" stroke="{c["border"]}" stroke-width="1"/>'
            + f'<text x="22" y="{h-21}" font-family="{SANS}" font-size="14.5" font-weight="600" fill="{c["accent"]}">{escape(d["cta"])} →</text>'
            + (f'<text x="{w-22}" y="{h-21}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{c["muted"]}">{escape(d["meta"])}</text>'
               if d.get("meta") else ""))
    return shell(w, h, c, f'{d["title"]}: {d["text"]}', body)


def social_icon(kind, c):
    s = 48
    if kind == "portfolio":
        fill, stroke = c["accent"], "none"
        glyph = ('<g fill="none" stroke="#FFFFFF" stroke-width="1.8"><circle cx="12" cy="12" r="9"/>'
                 '<ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M4.5 7.5h15M4.5 16.5h15"/></g>')
    else:
        fill, stroke = {"linkedin": ("#0A66C2", "none"), "gmail": ("#EA4335", "none"),
                        "github": ("#24292F", "#3D444D")}[kind]
        glyph = f'<path fill="#FFFFFF" d="{PATHS[kind]}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}" role="img" '
            f'aria-label="{kind}"><rect x="0.5" y="0.5" width="{s-1}" height="{s-1}" rx="12" fill="{fill}" '
            f'stroke="{stroke}"/><g transform="translate(12 12)">{glyph}</g></svg>\n')


# ---------------------------------------------------------------- content

FOCUS = "focus", 400
BUILD = "build", 266
TXIO = "txio", 266
OSS = "oss", 400

CONTENT = {
    "focus-backend": (FOCUS, dict(title="Backend", glyph="server", num="01",
        text="APIs and backend systems in Node, NestJS, Spring and Rust that hold up under real traffic.")),
    "focus-ai": (FOCUS, dict(title="AI & agents", glyph="spark", num="02",
        text="AI-powered products: learning systems, fraud detection and agentic workflows that do real work.")),
    "focus-web3": (FOCUS, dict(title="Web3 tooling", glyph="cube", num="03",
        text="Developer tools for Sui, Ethereum, Solana, Aptos and Stellar at TXIO Labs, plus Move and Solidity.")),
    "focus-desktop": (FOCUS, dict(title="Local-first apps", glyph="window", num="04",
        text="Private, offline-first desktop apps with Tauri. Your data stays on your machine.")),

    "project-sovra": (BUILD, dict(title="Sovra", kicker="personal finance · ai", status="live", cta="Open Sovra",
        text="A money app that remembers your goals. Budgets, limits and past decisions live in a memory vault on Walrus, so its advice gets more personal over time.",
        tags=["TypeScript", "NestJS", "Sui", "Walrus"])),
    "project-stakesync": (BUILD, dict(title="StakeSync", kicker="accountability · solana", status="live", cta="Open StakeSync",
        text="Join a challenge, put something on the line, and prove you showed up. Progress is checked against GitHub, LeetCode, Solana activity and more.",
        tags=["Solana", "TypeScript", "React"])),
    "project-headway": (BUILD, dict(title="Headway", kicker="dev tools · reporting", status="live", cta="Open Headway",
        text="Your commits already tell the story. Headway connects to GitHub and builds daily, weekly and sprint engineering reports automatically.",
        tags=["GitHub API", "TypeScript", "AI"])),

    "project-txio": (TXIO, dict(title="TXIO", kicker="web app · sui", status="live", cta="txio.xyz",
        text="An API client and visual transaction builder for Sui. Postman's familiar shape with Web3 wired in: Move calls, PTBs and name resolution.",
        tags=["TypeScript", "React", "Sui"])),
    "project-txio-cli": (TXIO, dict(title="TXIO CLI", kicker="cli · multi-chain", status="oss", cta="View repository",
        text="One terminal, every chain. A single Rust binary for Sui, Ethereum, Solana, Aptos and Soroban, with the same flags and readable output.",
        tags=["Rust", "Multi-chain", "CLI"])),
    "project-txio-desktop": (TXIO, dict(title="TXIO Desktop", kicker="desktop · tauri", status="oss", cta="Download",
        text="The TXIO console in its own window. Build, simulate, sign and run transactions across chains in a small Tauri app that updates itself.",
        tags=["Rust", "Tauri", "TypeScript"])),

    "oss-huntly": (OSS, dict(title="Huntly", kicker="desktop · job hunting", status="oss", cta="View repository",
        meta="Apache-2.0",
        text="A private job-hunting assistant that runs entirely on your machine. It finds vacancies, ranks them against your profile, tailors CVs and cover letters, and drafts emails that you approve before anything is sent.",
        tags=["Python", "Tauri", "Groq", "Gmail"])),
    "oss-forma": (OSS, dict(title="Forma", kicker="desktop · office suite", status="oss", cta="Download Forma",
        meta="MIT",
        text="A free, offline desktop office app: documents, CSV and Excel sheets, forms, PDF editing and signing, plus a task and habit tracker. Your files stay on your computer.",
        tags=["TypeScript", "React", "Tauri"])),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(ICONS, exist_ok=True)
    heights = {}
    for (group, w), d in CONTENT.values():
        hgt = focus_height(d) if group == "focus" else item_height(d, w)
        heights[group] = max(heights.get(group, 0), hgt)
    for theme, colors in THEMES.items():
        with open(os.path.join(ASSETS, f"banner-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(banner(colors))
        for name, ((group, w), data) in CONTENT.items():
            if group == "focus":
                svg = focus_card(data, colors, heights[group])
            else:
                svg = item_card(data, colors, heights[group], w)
            with open(os.path.join(OUT, f"{name}-{theme}.svg"), "w", encoding="utf-8") as f:
                f.write(svg)
    for kind in ["portfolio", "linkedin", "gmail", "github"]:
        with open(os.path.join(ICONS, f"{kind}.svg"), "w", encoding="utf-8") as f:
            f.write(social_icon(kind, THEMES["dark"]))
    print(f"wrote banner, {len(CONTENT) * len(THEMES)} cards, 4 icons; heights {heights}")


if __name__ == "__main__":
    main()
