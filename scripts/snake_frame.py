"""Wrap the Platane/snk contribution snake in a card that matches the README.

Usage:  python3 scripts/snake_frame.py dist
Reads:  dist/github-snake.svg, dist/github-snake-dark.svg (raw snk output)
Writes: the same files, framed.

Standard library only. Missing or already framed files are skipped.
The snake colors themselves are set in .github/workflows/snake.yml.
"""

import os
import re
import sys

from theme import MONO, THEMES, kicker, shell

FILES = {"github-snake.svg": "light", "github-snake-dark.svg": "dark"}
PAD_X, TOP, BOTTOM = 32, 64, 18


def frame(raw, c):
    raw = re.sub(r"<\?xml[^>]*\?>", "", raw).strip()
    if 'data-framed="1"' in raw:
        return None
    m = re.match(r"<svg\b([^>]*)>", raw)
    vb = re.search(r'viewBox="([-\d.\s]+)"', m.group(1))
    _, _, vw, vh = (float(v) for v in vb.group(1).split())
    W = int(vw + 2 * PAD_X)
    H = int(TOP + vh + BOTTOM)
    attrs = re.sub(r'\s(?:width|height)="[^"]*"', "", m.group(1))
    inner = f'<svg x="{PAD_X}" y="{TOP}" width="{vw:g}" height="{vh:g}"{attrs}>' + raw[m.end():]

    # legend: the five dot colors snk used, read back from its CSS variables
    levels = dict(re.findall(r"--c([0-4]):(#[0-9a-fA-F]{3,8})", raw))
    legend, lx = [], W - PAD_X - 34
    for i in range(4, -1, -1):
        if str(i) in levels:
            legend.append(f'<rect x="{lx - 12}" y="31" width="11" height="11" rx="3" fill="{levels[str(i)]}" '
                          f'stroke="{c["border"]}" stroke-width="0.8"/>')
            lx -= 15
    legend.append(f'<text x="{lx - 4}" y="41" text-anchor="end" font-family="{MONO}" font-size="12" fill="{c["muted"]}">less</text>')
    legend.append(f'<text x="{W-PAD_X}" y="41" text-anchor="end" font-family="{MONO}" font-size="12" fill="{c["muted"]}">more</text>')

    body = (kicker(PAD_X, 41, "Contribution snake · last 12 months", c, color=c["accent"])
            + "".join(legend) + inner)
    out = shell(W, H, c, "Contribution snake eating the last year of GitHub contributions", body, rx=18)
    return out.replace("<svg ", '<svg data-framed="1" ', 1)


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "dist"
    for name, theme in FILES.items():
        path = os.path.join(folder, name)
        if not os.path.exists(path):
            print(f"skip {path}: not found")
            continue
        with open(path, encoding="utf-8") as f:
            out = frame(f.read(), THEMES[theme])
        if out is None:
            print(f"skip {path}: already framed")
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"framed {path}")


if __name__ == "__main__":
    main()
