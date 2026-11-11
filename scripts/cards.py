"""Generate the README banner and SVG cards (light and dark) from CONTENT below.

Usage:  python3 scripts/cards.py
Writes: assets/banner-{dark,light}.svg and assets/cards/*.svg

Standard library only. Edit the text in CONTENT and re-run; the README links
to the files by name, so it does not need to change.
"""

import base64
import os
from html import escape

from theme import MONO, SANS, THEMES, accent_gradient, window_chrome

ROOT = os.path.join(os.path.dirname(__file__), "..")
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ASSETS, "cards")
AVATAR = os.path.join(ASSETS, "media", "avatar.webp")


# ---------------------------------------------------------------- helpers

def wrap(text, size, width, bold=False):
    """Greedy word wrap using an average glyph width; deliberately conservative."""
    per = size * (0.56 if bold else 0.52)
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


def frame(w, h, c, title, body, accent):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="1.5"/>'
        f'{body}'
        f'<rect x="1" y="1" width="{w-2}" height="4" rx="2" fill="{c[accent]}" opacity="0.9"/>'
        f'</svg>\n'
    )


def pills(x, y, tags, c, max_x):
    out, cx, cy = [], x, y
    for t in tags:
        w = len(t) * 7.2 + 18
        if cx + w > max_x:
            cx, cy = x, cy + 30
        out.append(f'<rect x="{cx}" y="{cy}" width="{w:.0f}" height="22" rx="11" fill="{c["pill"]}" stroke="{c["border"]}"/>'
                   f'<text x="{cx + w/2:.0f}" y="{cy+15}" text-anchor="middle" font-family="{MONO}" '
                   f'font-size="12" fill="{c["muted"]}">{escape(t)}</text>')
        cx += w + 8
    return "".join(out)


def mark(kind, x, y, col):
    """Small geometric marks for the 'What I do' cards."""
    if kind == "square":
        return f'<rect x="{x}" y="{y}" width="14" height="14" rx="3" fill="none" stroke="{col}" stroke-width="2"/>'
    if kind == "hex":
        pts = " ".join(f"{x+7+8*dx:.1f},{y+7+8*dy:.1f}" for dx, dy in
                       [(0, -1), (0.87, -0.5), (0.87, 0.5), (0, 1), (-0.87, 0.5), (-0.87, -0.5)])
        return f'<polygon points="{pts}" fill="none" stroke="{col}" stroke-width="2"/>'
    if kind == "tri":
        return f'<polygon points="{x+7},{y} {x+15},{y+14} {x-1},{y+14}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round"/>'
    return (f'<circle cx="{x+4}" cy="{y+7}" r="4" fill="none" stroke="{col}" stroke-width="2"/>'
            f'<circle cx="{x+13}" cy="{y+7}" r="4" fill="none" stroke="{col}" stroke-width="2"/>')


# ---------------------------------------------------------------- banner

def banner(c):
    W, H = 1200, 300
    with open(AVATAR, "rb") as f:
        avatar = base64.b64encode(f.read()).decode()
    ax, ay, ar = 1000, 172, 86
    tags = [("{ api }", 812, 96, "sky"), ("move", 1118, 82, "indigo"),
            ("agents", 1112, 262, "mint"), ("rust", 846, 250, "amber")]
    tag_svg = "".join(
        f'<rect x="{x - (len(t)*8.4+24)/2:.0f}" y="{y-15}" width="{len(t)*8.4+24:.0f}" height="28" rx="14" '
        f'fill="{c["bg"]}" stroke="{c[col]}" stroke-width="1.5"/>'
        f'<text x="{x}" y="{y+4}" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{c[col]}">{escape(t)}</text>'
        for t, x, y, col in tags)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Victor Oladimeji</title>
<desc id="d">Terminal-style banner for Victor Oladimeji (Kingvic300): full-stack engineer working on backend, AI and Web3.</desc>
<defs>{accent_gradient(c)}
<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c["sky"]}"/><stop offset="1" stop-color="{c["indigo"]}"/></linearGradient>
<radialGradient id="glow" cx="0.83" cy="0.55" r="0.42"><stop offset="0" stop-color="{c["sky"]}" stop-opacity="0.14"/><stop offset="1" stop-color="{c["sky"]}" stop-opacity="0"/></radialGradient>
<clipPath id="av"><circle cx="{ax}" cy="{ay}" r="{ar}"/></clipPath>
</defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="2"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="url(#glow)"/>
{window_chrome(c, W, "~/kingvic300", "lagos, ng")}
<text x="64" y="114" font-family="{MONO}" font-size="22" fill="{c["muted"]}"><tspan fill="{c["mint"]}">$</tspan> whoami</text>
<text x="60" y="190" font-family="{SANS}" font-size="66" font-weight="700" letter-spacing="-1.5" fill="{c["text"]}">Victor Oladimeji</text>
<text x="64" y="244" font-family="{MONO}" font-size="20" fill="{c["muted"]}">full-stack <tspan fill="{c["sky"]}">·</tspan> backend <tspan fill="{c["indigo"]}">·</tspan> ai <tspan fill="{c["mint"]}">·</tspan> web3 <tspan fill="{c["sky"]}">▌<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.2s" repeatCount="indefinite"/></tspan></text>
<circle cx="{ax}" cy="{ay}" r="{ar+18}" fill="none" stroke="{c["border"]}" stroke-width="1.5" stroke-dasharray="4 8">
<animateTransform attributeName="transform" type="rotate" from="0 {ax} {ay}" to="360 {ax} {ay}" dur="40s" repeatCount="indefinite"/></circle>
<circle cx="{ax}" cy="{ay}" r="{ar+6}" fill="none" stroke="url(#ring)" stroke-width="3"/>
<image href="data:image/webp;base64,{avatar}" x="{ax-ar}" y="{ay-ar}" width="{2*ar}" height="{2*ar}" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>
{tag_svg}
<rect x="1" y="{H-6}" width="{W-2}" height="5" rx="2.5" fill="url(#accent)"/>
</svg>
"""


# ---------------------------------------------------------------- card types

def focus_card(d, c):
    w, h = 400, 132
    col = c[d["accent"]]
    body = (mark(d["mark"], 26, 28, col)
            + f'<text x="52" y="41" font-family="{SANS}" font-size="19" font-weight="700" fill="{c["text"]}">{escape(d["title"])}</text>'
            + text_block(26, 72, wrap(d["text"], 14.5, w - 52), 14.5, c["muted"], 21))
    return frame(w, h, c, f'{d["title"]}: {d["text"]}', body, d["accent"])


def project_card(d, c):
    w, h = 266, 316
    col = c[d["accent"]]
    desc = wrap(d["text"], 14, w - 44)
    body = (f'<text x="22" y="40" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{col}">{escape(d["kicker"].upper())}</text>'
            + f'<text x="22" y="74" font-family="{SANS}" font-size="24" font-weight="700" fill="{c["text"]}">{escape(d["title"])}</text>'
            + text_block(22, 104, desc, 14, c["muted"], 20)
            + pills(22, 104 + 20 * len(desc) + 6, d["tags"], c, w - 18)
            + f'<line x1="22" y1="{h-52}" x2="{w-22}" y2="{h-52}" stroke="{c["border"]}" stroke-width="1.5"/>'
            + f'<text x="22" y="{h-24}" font-family="{SANS}" font-size="15" font-weight="700" fill="{col}">{escape(d["cta"])} ↗</text>')
    return frame(w, h, c, f'{d["title"]}: {d["text"]}', body, d["accent"])


def oss_height(d):
    return 104 + 20 * len(wrap(d["text"], 14, 356)) + 6 + 22 + 74


def oss_card(d, c):
    """Open source card. Height is shared across the group so cards line up."""
    w, h = 400, d["height"]
    col = c[d["accent"]]
    desc = wrap(d["text"], 14, w - 44)
    tags_y = h - 74 - 22
    body = (f'<text x="22" y="40" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{col}">{escape(d["kicker"].upper())}</text>'
            + f'<text x="22" y="72" font-family="{SANS}" font-size="21" font-weight="700" fill="{c["text"]}">{escape(d["title"])}</text>'
            + text_block(22, 104, desc, 14, c["muted"], 20)
            + pills(22, tags_y, d["tags"], c, w - 18)
            + f'<line x1="22" y1="{h-52}" x2="{w-22}" y2="{h-52}" stroke="{c["border"]}" stroke-width="1.5"/>'
            + f'<text x="22" y="{h-24}" font-family="{SANS}" font-size="15" font-weight="700" fill="{col}">{escape(d["cta"])} ↗</text>'
            + f'<text x="{w-22}" y="{h-24}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{c["muted"]}">{escape(d["meta"])}</text>')
    return frame(w, h, c, f'{d["title"]}: {d["text"]}', body, d["accent"])


# ---------------------------------------------------------------- content

CONTENT = {
    "focus-backend": (focus_card, dict(title="Backend", mark="square", accent="sky",
        text="APIs and backend systems in Node, NestJS, Spring and Rust that hold up under real traffic.")),
    "focus-ai": (focus_card, dict(title="AI & agents", mark="rings", accent="indigo",
        text="AI-powered products: learning systems, fraud detection and agentic workflows that do real work.")),
    "focus-web3": (focus_card, dict(title="Web3 tooling", mark="hex", accent="mint",
        text="Developer tools for Sui, Ethereum, Solana, Aptos and Stellar at TXIO Labs, plus Move and Solidity.")),
    "focus-desktop": (focus_card, dict(title="Local-first apps", mark="tri", accent="amber",
        text="Private, offline-first desktop apps with Tauri. Your data stays on your machine.")),

    "project-txio": (project_card, dict(title="TXIO", kicker="txio labs · web app", accent="sky",
        cta="txio.xyz",
        text="An API client and visual transaction builder for Sui. Postman's familiar shape with Web3 wired in: Move calls, PTBs and name resolution.",
        tags=["TypeScript", "React", "Sui"])),
    "project-txio-cli": (project_card, dict(title="TXIO CLI", kicker="txio labs · cli", accent="indigo",
        cta="View repository",
        text="One terminal, every chain. A single Rust binary for Sui, Ethereum, Solana, Aptos and Soroban, with the same flags and readable output.",
        tags=["Rust", "Multi-chain", "CLI"])),
    "project-txio-desktop": (project_card, dict(title="TXIO Desktop", kicker="txio labs · desktop", accent="mint",
        cta="Download",
        text="The TXIO console in its own window. Build, simulate, sign and run transactions across chains in a small Tauri app that updates itself.",
        tags=["Rust", "Tauri", "TypeScript"])),

    "project-sovra": (project_card, dict(title="Sovra", kicker="personal finance · ai", accent="indigo",
        cta="Live project",
        text="A money app that remembers your goals. Budgets, limits and past decisions live in a memory vault on Walrus, so its advice gets more personal over time.",
        tags=["TypeScript", "NestJS", "Sui", "Walrus"])),
    "project-stakesync": (project_card, dict(title="StakeSync", kicker="accountability · solana", accent="amber",
        cta="Live project",
        text="Join a challenge, put something on the line, and prove you showed up. Progress is checked against GitHub, LeetCode, Solana activity and more.",
        tags=["Solana", "TypeScript", "React"])),

    "project-headway": (project_card, dict(title="Headway", kicker="dev tools · reporting", accent="mint",
        cta="headwayhq.xyz",
        text="Your commits already tell the story. Headway connects to GitHub and builds daily, weekly and sprint engineering reports automatically.",
        tags=["GitHub API", "TypeScript", "AI"])),

    "oss-huntly": (oss_card, dict(title="Huntly", kicker="open source · job hunting", accent="indigo",
        cta="View repository", meta="Apache-2.0",
        text="A private job-hunting assistant that runs entirely on your machine. It finds vacancies, ranks them against your profile, tailors CVs and cover letters, and drafts emails that you approve before anything is sent.",
        tags=["Python", "Tauri", "Groq", "Gmail"])),
    "oss-forma": (oss_card, dict(title="Forma", kicker="open source · office suite", accent="sky",
        cta="Download Forma", meta="MIT",
        text="A free, offline desktop office app: documents, CSV and Excel sheets, forms, PDF editing and signing, plus a task and habit tracker. Your files stay on your computer.",
        tags=["TypeScript", "React", "Tauri"])),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    oss = [d for fn, d in CONTENT.values() if fn is oss_card]
    shared = max(oss_height(d) for d in oss)
    for d in oss:
        d["height"] = shared
    for theme, colors in THEMES.items():
        with open(os.path.join(ASSETS, f"banner-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(banner(colors))
        for name, (fn, data) in CONTENT.items():
            with open(os.path.join(OUT, f"{name}-{theme}.svg"), "w", encoding="utf-8") as f:
                f.write(fn(data, colors))
    print(f"wrote banner + {len(CONTENT) * len(THEMES)} cards")


if __name__ == "__main__":
    main()
