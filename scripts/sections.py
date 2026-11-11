"""Generate the experience timeline, hackathon cards and tech stack card.

Usage:  python3 scripts/sections.py
Writes: assets/experience-{dark,light}.svg, assets/stack-{dark,light}.svg,
        assets/cards/hack-*.svg

Standard library only. Edit EXPERIENCE, HACKATHONS or STACK and re-run.
"""

import os
from html import escape

from brand_paths import PATHS
from cards import item_card, item_height, text_block, wrap
from theme import MONO, SANS, THEMES, kicker, shell

ROOT = os.path.join(os.path.dirname(__file__), "..")
ASSETS = os.path.join(ROOT, "assets")

# newest first; role=None shows only the company
EXPERIENCE = [
    dict(company="TechB", role=None, period="Now",
         text="TechB (tec-bank.com), a trusted real-time payment platform for managing and growing wealth."),
    dict(company="TXIO Labs", role="Founder, CTO & Developer", period="Now",
         text="Multi-chain developer tooling: web app, CLI, desktop app and API. Part of the GrantFox open source program."),
    dict(company="Naelix Tech Group", role="Full Stack Engineer", period="Mar 2026 – now",
         text="Node.js, NestJS, PostgreSQL and Redis services for a startup building digital products for businesses and individuals."),
    dict(company="Maseev Invisible Digitals", role="Backend Engineer", period="Feb 2026 – now",
         text="Backend for a Lagos IT agency that designs and builds websites, apps and software for businesses."),
    dict(company="Steerify", role="Co-Founder", period="Nov 2025 – now",
         text="Product direction and architecture for a software studio serving African entrepreneurs, including SteerSolo and SureTruqs."),
    dict(company="CVtoCareer", role="Full-Stack Engineer", period="Oct 2025 – now",
         text="Dashboards, onboarding flows and admin tools, plus REST APIs, authentication services and background jobs."),
    dict(company="Raoatech", role="Software Development Instructor", period="Aug – Oct 2025",
         text="Taught Python, JavaScript and backend fundamentals through project-based learning."),
    dict(company="Sabiedu", role="Agentic AI Engineer", period="Jul – Aug 2025",
         text="Agentic AI systems for document analysis and automated task execution, wired into dashboards."),
    dict(company="Semicolon Africa", role="Trainee Developer", period="Jul 2024 – Jul 2025",
         text="Backend services with TDD in Spring Boot, Flask and .NET: REST APIs, JWT authentication and query tuning."),
]

HACKATHONS = {
    "hack-digitaldrive": dict(title="Digitaley Drive", kicker="digitaley drive hackathon", status="1st place",
        text="First place at the Digitaley Drive hackathon, won as a team.",
        tags=["Team build"]),
    "hack-ecx": dict(title="ECX 5.0", kicker="engineering career expo · 2025", status="winner",
        text="Won at ECX 5.0, the Engineering Career Expo's 2025 tech programme and grand finale in Lagos.",
        tags=["Lagos", "2025"]),
}

# (label, simple-icons slug or None, brand color or None for the text color)
STACK = [
    ("Languages", [("TypeScript", "typescript", "#3178C6"), ("Java", "openjdk", None), ("Python", "python", "#3776AB"),
                   ("Rust", "rust", None), ("Solidity", "solidity", None)]),
    ("Backend", [("Node.js", "nodedotjs", "#5FA04E"), ("NestJS", "nestjs", "#E0234E"), ("Spring", "spring", "#6DB33F"),
                 ("Django", "django", None), ("Axum", "rust", None), ("Swagger", "swagger", "#85EA2D")]),
    ("Data", [("PostgreSQL", "postgresql", "#4169E1"), ("MongoDB", "mongodb", "#47A248"), ("Redis", "redis", "#FF4438"),
              ("MySQL", "mysql", "#4479A1"), ("SQLite", "sqlite", "#0F80CC")]),
    ("AI", [("LLMs & agents", None, None), ("scikit-learn", "scikitlearn", "#F7931E"), ("pandas", "pandas", None),
            ("TF-IDF", None, None)]),
    ("Web3", [("Sui · Move", "sui", "#4DA2FF"), ("Ethereum", "ethereum", None), ("Solana", "solana", "#9945FF"),
              ("Stellar · Soroban", "stellar", None), ("Aptos", None, None)]),
    ("Frontend & desktop", [("React", "react", "#61DAFB"), ("Next.js", "nextdotjs", None), ("Tailwind", "tailwindcss", "#06B6D4"),
                            ("Tauri", "tauri", "#FFC131"), ("Electron", "electron", "#47848F")]),
    ("DevOps & tools", [("Docker", "docker", "#2496ED"), ("GitHub Actions", "githubactions", "#2088FF"), ("Git", "git", "#F05032"),
                        ("Postman", "postman", "#FF6C37"), ("Linux", "linux", None)]),
]

DOT = ('<circle cx="12" cy="12" r="4" fill="none" stroke="{col}" stroke-width="2"/>'
       '<path d="M12 3v3M12 18v3M3 12h3M18 12h3" stroke="{col}" stroke-width="2" stroke-linecap="round"/>')


def experience(c):
    W, x_period, x_line, x_body = 880, 32, 194, 218
    body_w = W - x_body - 32
    y = 88
    rows = []
    for i, e in enumerate(EXPERIENCE):
        lines = wrap(e["text"], 14, body_w)
        current = "now" in e["period"].lower()
        head = f'<tspan font-weight="700" fill="{c["text"]}">{escape(e["company"])}</tspan>'
        if e["role"]:
            head += f'<tspan fill="{c["accent"]}" dx="8">· {escape(e["role"])}</tspan>'
        rows.append(
            f'<text x="{x_period}" y="{y+5}" font-family="{MONO}" font-size="12.5" fill="{c["muted"]}">{escape(e["period"])}</text>'
            + (f'<circle cx="{x_line}" cy="{y}" r="6" fill="{c["accent"]}"/>' if current else
               f'<circle cx="{x_line}" cy="{y}" r="5.5" fill="{c["surface"]}" stroke="{c["muted"]}" stroke-width="2"/>')
            + f'<text x="{x_body}" y="{y+6}" font-family="{SANS}" font-size="17">{head}</text>'
            + text_block(x_body, y + 30, lines, 14, c["muted"], 20))
        y += 30 + 20 * len(lines) + 26
    H = y - 6
    line = f'<line x1="{x_line}" y1="88" x2="{x_line}" y2="{H-56}" stroke="{c["border"]}" stroke-width="2"/>'
    top = (kicker(32, 46, "Where I've worked", c, color=c["accent"])
           + kicker(W - 32, 46, f"{len(EXPERIENCE)} roles · newest first", c, anchor="end"))
    return shell(W, H, c, "Experience: " + "; ".join(
        f'{e["company"]}{" (" + e["role"] + ")" if e["role"] else ""}, {e["period"]}' for e in EXPERIENCE),
        top + line + "".join(rows), rx=18)


def chip(x, y, name, slug, color, c):
    w = len(name) * 7.5 + 48
    col = color or c["text"]
    if slug:
        icon = (f'<g transform="translate({x+12} {y+9}) scale(0.6667)"><path fill="{col}" d="{PATHS[slug]}"/></g>')
    else:
        icon = f'<g transform="translate({x+12} {y+9}) scale(0.6667)">{DOT.format(col=c["accent"])}</g>'
    return w, (f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="34" rx="9" fill="{c["bg"]}" stroke="{c["border"]}"/>'
               + icon
               + f'<text x="{x+36:.0f}" y="{y+22}" font-family="{SANS}" font-size="14" fill="{c["text"]}">{escape(name)}</text>')


def stack(c):
    W, x0, gap = 880, 210, 8
    y = 76
    out = [kicker(32, 46, "Tools I reach for", c, color=c["accent"])]
    for label, items in STACK:
        out.append(kicker(32, y + 22, label, c))
        x = x0
        for name, slug, color in items:
            w, svg = chip(x, y, name, slug, color, c)
            if x + w > W - 32:
                x, y = x0, y + 44
                w, svg = chip(x, y, name, slug, color, c)
            out.append(svg)
            x += w + gap
        y += 50
    H = y + 14
    return shell(W, H, c, "Tech stack: " + "; ".join(
        f'{label}: ' + ", ".join(n for n, _, _ in items) for label, items in STACK), "".join(out), rx=18)


def main():
    h = max(item_height(d, 400) for d in HACKATHONS.values())
    for theme, c in THEMES.items():
        with open(os.path.join(ASSETS, f"experience-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(experience(c))
        with open(os.path.join(ASSETS, f"stack-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(stack(c))
        for name, d in HACKATHONS.items():
            with open(os.path.join(ASSETS, "cards", f"{name}-{theme}.svg"), "w", encoding="utf-8") as f:
                f.write(item_card(d, c, h, 400))
    print("wrote experience, stack and", len(HACKATHONS) * 2, "hackathon cards")


if __name__ == "__main__":
    main()
