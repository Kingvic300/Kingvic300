"""Shared colors, fonts and small drawing helpers for every generated SVG.

Palette: charcoal surfaces with one ember-orange accent. No gradients.
"""

from html import escape

THEMES = {
    "dark": dict(bg="#0E0F11", surface="#15171A", border="#2A2D33", text="#EDEEF0",
                 muted="#9BA1A9", faint="#22252A", accent="#FF7A1A", accent_soft="#33210F",
                 live="#3FB950",
                 scale=["#FF7A1A", "#FFA45C", "#FFCB9A", "#8A9099", "#4A4F57"],
                 snake="#FFA45C",
                 dots=["#1C1F24", "#4A2A14", "#8A4515", "#CC6417", "#FF7A1A"]),
    "light": dict(bg="#FFFFFF", surface="#FAFAF9", border="#E7E5E4", text="#1C1917",
                  muted="#57534E", faint="#F0EFED", accent="#E8590C", accent_soft="#FDEBDD",
                  live="#1A7F37",
                  scale=["#E8590C", "#F59F5B", "#F8C9A0", "#78716C", "#A8A29E"],
                  snake="#C2410C",
                  dots=["#EFEDEA", "#FDD8BC", "#FBB27A", "#F2853A", "#E8590C"]),
}

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def shell(w, h, c, label, body, rx=16):
    """Card shell: solid surface, hairline border, accessible title."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
        f'<rect x="0.75" y="0.75" width="{w-1.5}" height="{h-1.5}" rx="{rx}" fill="{c["surface"]}" '
        f'stroke="{c["border"]}" stroke-width="1.5"/>{body}</svg>\n'
    )


def kicker(x, y, text, c, anchor="start", color=None):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{MONO}" font-size="11.5" '
            f'letter-spacing="1.2" fill="{color or c["muted"]}">{escape(text.upper())}</text>')
