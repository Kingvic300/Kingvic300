"""Shared colors and fonts for every generated SVG in this repo."""

THEMES = {
    "dark": dict(bg="#0B1220", border="#1E293B", text="#E2E8F0", muted="#94A3B8",
                 pill="#111A2E", faint="#1E293B", sky="#36BCF7", indigo="#818CF8",
                 mint="#34D399", amber="#FBBF24", slate="#64748B"),
    "light": dict(bg="#F8FAFC", border="#E2E8F0", text="#0F172A", muted="#475569",
                  pill="#EEF2F7", faint="#E2E8F0", sky="#0284C7", indigo="#4F46E5",
                  mint="#059669", amber="#B45309", slate="#94A3B8"),
}

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def accent_gradient(c, gid="accent"):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{c["sky"]}"/>'
            f'<stop offset="0.55" stop-color="{c["indigo"]}"/>'
            f'<stop offset="1" stop-color="{c["mint"]}"/></linearGradient>')


def window_chrome(c, w, label, right=""):
    """Terminal-style title bar: three dots, a path label, a divider."""
    out = [f'<circle cx="{34 + 22 * i}" cy="32" r="6" fill="{c["faint"]}"/>' for i in range(3)]
    out.append(f'<text x="104" y="37" font-family="{MONO}" font-size="15" fill="{c["muted"]}">{label}</text>')
    if right:
        out.append(f'<text x="{w - 32}" y="37" text-anchor="end" font-family="{MONO}" font-size="13" '
                   f'fill="{c["muted"]}">{right}</text>')
    out.append(f'<line x1="2" y1="56" x2="{w - 2}" y2="56" stroke="{c["border"]}" stroke-width="1.5"/>')
    return "".join(out)
