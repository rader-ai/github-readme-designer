"""Build the README visuals for github-readme-designer, with the skill's own svgkit.

    python3 .github/readme/build.py

Writes hero, proof and flow (light/dark × wide/narrow) to .github/assets/.
Numbers in the proof come from evals/results/iteration-1 (one run per repo).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/github-readme-designer/scripts"))
import svgkit as sk  # noqa: E402

# A designer's cutting mat, with CMYK printer's marks.
THEMES = {
    "light": dict(bg="#E6EFEA", grid="#D3E2DA", ink="#13302A", muted="#55706A", faint="#A9BDB5", card="#F8FBF9",
                  line="#CBDBD3", band="#13302A", bandtext="#F3F8F5", bandmuted="#9DB8AF", plain="#B7C8C1",
                  magenta="#C8336E", cyan="#11899B", yellow="#D99A12", grey="#9AACA5"),
    "dark": dict(bg="#0D1C18", grid="#152C26", ink="#E6F0EC", muted="#8FA9A1", faint="#35524A", card="#11251F",
                 line="#21413A", band="#1C3B33", bandtext="#EAF3EF", bandmuted="#8FB0A6", plain="#2E4A43",
                 magenta="#F0609A", cyan="#3CC4D6", yellow="#F2C14E", grey="#4D6A62"),
}


def mat(w, h, t):
    """Cutting-mat grid: fine lines every 32px, stronger every 160px."""
    lines = []
    for x in range(32, w, 32):
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{t["grid"]}" stroke-width="{1.4 if x % 160 == 0 else .7}"/>')
    for y in range(32, h, 32):
        lines.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{t["grid"]}" stroke-width="{1.4 if y % 160 == 0 else .7}"/>')
    return f'<rect width="{w}" height="{h}" rx="18" fill="{t["bg"]}"/>\n<g>{"".join(lines)}</g>\n'


def crop_marks(x, y, w, h, color, gap=7, ln=14):
    m = []
    for cx, dx in ((x, -1), (x + w, 1)):
        for cy, dy in ((y, -1), (y + h, 1)):
            m.append(f'<line x1="{cx + dx * gap}" y1="{cy}" x2="{cx + dx * (gap + ln)}" y2="{cy}" stroke="{color}" stroke-width="1.5"/>')
            m.append(f'<line x1="{cx}" y1="{cy + dy * gap}" x2="{cx}" y2="{cy + dy * (gap + ln)}" stroke="{color}" stroke-width="1.5"/>')
    return "".join(m)


def cmyk(cx, cy, r, t, op=.85):
    return (f'<g opacity="{op}"><circle cx="{cx - r * .55}" cy="{cy}" r="{r}" fill="{t["cyan"]}" opacity=".85"/>'
            f'<circle cx="{cx + r * .55}" cy="{cy}" r="{r}" fill="{t["magenta"]}" opacity=".75"/>'
            f'<circle cx="{cx}" cy="{cy - r * .8}" r="{r}" fill="{t["yellow"]}" opacity=".7"/></g>')


# ---------- hero: a plain README is redesigned in front of you ----------

def readme_card(x, y, w, h, t, cycle=12):
    """The signature: a grey README; a registration line scans across and the designed page wipes in, then rewinds."""
    css, out = [], []
    pad = 26
    out.append(f'<rect x="{x}" y="{y - 30}" width="118" height="34" rx="7" fill="{t["card"]}" stroke="{t["line"]}"/>'
               f'<text class="mono" x="{x + 59}" y="{y - 9}" font-size="12.5" text-anchor="middle" fill="{t["muted"]}">README.md</text>'
               f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{t["card"]}" stroke="{t["line"]}"/>'
               + crop_marks(x, y, w, h, t["magenta"]))

    # Before: what most READMEs look like.
    yy = y + pad + 16
    out.append(f'<text class="mono" x="{x + pad}" y="{yy}" font-size="16" font-weight="700" fill="{t["muted"]}"># my-project</text>')
    yy += 22
    for frac in (0.88, 0.94, 0.62):
        out.append(f'<rect x="{x + pad}" y="{yy}" width="{(w - 2 * pad) * frac:.0f}" height="8" rx="4" fill="{t["plain"]}"/>')
        yy += 18
    blocks = [("## Install", None), (None, 36), ("## Usage", None), (None, (0.9, 0.76, 0.84, 0.5)), ("## License", None), (None, (0.7,))]
    for head, body in blocks:
        if yy > y + h - 30:
            break
        if head:
            yy += 14
            out.append(f'<text class="mono" x="{x + pad}" y="{yy}" font-size="13" fill="{t["muted"]}">{head}</text>')
            yy += 14
        elif isinstance(body, int):
            out.append(f'<rect x="{x + pad}" y="{yy}" width="{w - 2 * pad}" height="{body}" rx="5" fill="{t["line"]}"/>')
            yy += body + 6
        else:
            for frac in body:
                if yy > y + h - 24:
                    break
                out.append(f'<rect x="{x + pad}" y="{yy}" width="{(w - 2 * pad) * frac:.0f}" height="8" rx="4" fill="{t["plain"]}"/>')
                yy += 18

    # After: the same page, designed. Revealed by a clip that grows left to right.
    css.append(sk.grow("wipe", cycle, 8, 40, off=90, timing="linear"))
    after = [f'<rect x="{x + 1}" y="{y + 1}" width="{w - 2}" height="{h - 2}" rx="9" fill="{t["card"]}"/>']
    bx, by, bw, bh = x + 16, y + 16, w - 32, min(118, h * .3)
    after.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{t["band"]}"/>'
                 f'<text class="serif" x="{bx + 20}" y="{by + 42}" font-size="27" fill="{t["bandtext"]}">my-project</text>'
                 f'<text class="mono" x="{bx + 21}" y="{by + 64}" font-size="11.5" fill="{t["bandmuted"]}">{sk.esc(sk.fit("Does one thing, and shows you it works.", 11.5, bw - 130))}</text>'
                 + "".join(f'<rect x="{bx + 20 + i * 72}" y="{by + bh - 34}" width="62" height="20" rx="10" fill="none" stroke="{t["bandmuted"]}"/>' for i in range(3))
                 + cmyk(bx + bw - 46, by + bh / 2 + 4, 17, t, .95))
    # Mini results chart.
    cy0 = by + bh + 34
    after.append(f'<text class="mono" x="{bx}" y="{cy0}" font-size="10.5" letter-spacing="1.5" fill="{t["muted"]}">RESULTS</text>')
    rows = [(0.30, 0.86), (0.42, 0.95), (0.25, 0.78)]
    cw = bw - 70
    for i, (a, b) in enumerate(rows):
        ry = cy0 + 22 + i * 24
        xa, xb = bx + 40 + cw * a, bx + 40 + cw * b
        css.append(sk.draw(f"bar{i}", cycle, xb - xa, 42 + i * 3, 52 + i * 3, off=90))
        after.append(f'<rect x="{bx}" y="{ry - 4}" width="28" height="8" rx="4" fill="{t["plain"]}"/>'
                     f'<line class="bar{i}" x1="{xa:.0f}" y1="{ry}" x2="{xb:.0f}" y2="{ry}" stroke="{t["magenta"]}" stroke-width="4" stroke-linecap="round"/>'
                     f'<circle cx="{xa:.0f}" cy="{ry}" r="5" fill="{t["card"]}" stroke="{t["grey"]}" stroke-width="2.5"/>'
                     f'<circle cx="{xb:.0f}" cy="{ry}" r="6" fill="{t["magenta"]}"/>')
    # Mini flow with a travelling marker.
    fy = cy0 + 22 + len(rows) * 24 + 26
    if fy < y + h - 20:
        n, fx0, fx1 = 4, bx + 14, bx + bw - 14
        xs = [fx0 + (fx1 - fx0) * i / (n - 1) for i in range(n)]
        after.append(f'<line x1="{fx0}" y1="{fy}" x2="{fx1}" y2="{fy}" stroke="{t["faint"]}" stroke-width="2" stroke-dasharray="5 6"/>'
                     + "".join(f'<circle cx="{sx:.0f}" cy="{fy}" r="8" fill="{t["card"]}" stroke="{t["cyan"]}" stroke-width="2.5"/>' for sx in xs))
        css.append(f"""
.ship {{ animation: ship {cycle}s cubic-bezier(.6,0,.4,1) infinite both; }}
@keyframes ship {{ 0%,55% {{ transform: translateX(0); opacity: 0; }} 57% {{ opacity: 1; }} 85%,100% {{ transform: translateX({fx1 - fx0:.0f}px); opacity: 1; }} }}""")
        after.append(f'<circle class="ship" cx="{fx0}" cy="{fy}" r="4.5" fill="{t["ink"]}" opacity="0"/>')
    out.append(f'<defs><clipPath id="reveal"><rect class="wipe" x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs>'
               f'<g clip-path="url(#reveal)">{"".join(after)}</g>')

    # The registration line rides the edge of the wipe, on the same timeline.
    css.append(f"""
.scan {{ animation: scan {cycle}s linear infinite both; }}
@keyframes scan {{ 0%,7% {{ transform: translateX(0); opacity: 0; }} 8% {{ transform: translateX(0); opacity: 1; }}
  40% {{ transform: translateX({w}px); opacity: 1; }} 42%,89% {{ transform: translateX({w}px); opacity: 0; }}
  90% {{ transform: translateX({w}px); opacity: 1; }} 99.5% {{ transform: translateX(0); opacity: 1; }} 100% {{ transform: translateX(0); opacity: 0; }} }}""")
    out.append(f'<g class="scan" opacity="0"><rect x="{x - 5}" y="{y - 10}" width="10" height="{h + 20}" fill="{t["magenta"]}" opacity=".18"/>'
               f'<line x1="{x}" y1="{y - 10}" x2="{x}" y2="{y + h + 10}" stroke="{t["magenta"]}" stroke-width="2.5"/>'
               f'<circle cx="{x}" cy="{y - 16}" r="6" fill="none" stroke="{t["magenta"]}" stroke-width="1.5"/>'
               f'<line x1="{x - 9}" y1="{y - 16}" x2="{x + 9}" y2="{y - 16}" stroke="{t["magenta"]}" stroke-width="1.2"/></g>')

    # Before / after label above the card's top-right corner.
    css.append(f"""
.lb {{ animation: lb {cycle}s linear infinite both; }}
@keyframes lb {{ 0%,7% {{ opacity: 1; }} 9%,92% {{ opacity: 0; }} 95%,100% {{ opacity: 1; }} }}
.la {{ animation: la {cycle}s linear infinite both; }}
@keyframes la {{ 0%,38% {{ opacity: 0; }} 41%,89% {{ opacity: 1; }} 91%,100% {{ opacity: 0; }} }}""")
    out.append(f'<text class="mono lb" x="{x + w - 14}" y="{y - 10}" font-size="12" font-weight="700" letter-spacing="2" text-anchor="end" fill="{t["muted"]}" opacity="0">BEFORE</text>'
               f'<text class="mono la" x="{x + w - 14}" y="{y - 10}" font-size="12" font-weight="700" letter-spacing="2" text-anchor="end" fill="{t["magenta"]}">AFTER</text>')
    return "".join(css), "\n".join(out)


def hero(t, size):
    wide = size == "wide"
    W, H = (1280, 470) if wide else (640, 760)
    tx = 64 if wide else 40
    title = 50 if wide else 44
    ey = 104 if wide else 64
    css, card = readme_card(*((690, 112, 526, 306) if wide else (40, 390, 560, 330)), t)
    t1, t2 = ey + title + 22, ey + title * 2 + 30
    by = t2 + 52
    chips = ["animated SVG", "light + dark", "phone widths"]
    cx, chip_svg = tx, []
    for c in chips:
        cw = sk.text_width(c, 13) + 26
        chip_svg.append(f'<rect x="{cx}" y="{by + 54}" width="{cw:.0f}" height="30" rx="15" fill="none" stroke="{t["faint"]}"/>'
                        f'<text class="mono" x="{cx + cw / 2:.0f}" y="{by + 74}" font-size="13" text-anchor="middle" fill="{t["ink"]}">{c}</text>')
        cx += cw + 10
    body = f"""{mat(W, H, t)}
<text class="mono" x="{tx}" y="{ey}" font-size="13" letter-spacing="2" fill="{t['muted']}">A SKILL FOR CLAUDE CODE, CODEX AND CHATGPT</text>
<text class="serif" x="{tx - 2}" y="{t1}" font-size="{title}" fill="{t['ink']}">Your README,</text>
<text class="serif" x="{tx - 2}" y="{t2}" font-size="{title}" font-style="italic" fill="{t['ink']}">before and after.</text>
<text class="mono" x="{tx}" y="{by}" font-size="15" fill="{t['muted']}">Reads the repo, finds the proof, and builds</text>
<text class="mono" x="{tx}" y="{by + 24}" font-size="15" fill="{t['muted']}">animated visuals that play right on GitHub.</text>
{"".join(chip_svg)}
{card}"""
    return sk.svg_doc(W, H, "github-readme-designer",
                      "A plain grey README card is scanned by a registration line; behind it the designed version wipes in, "
                      "with a hero band, a results chart that draws itself and a flow with a moving marker, then it rewinds.",
                      css, body)


# ---------- proof: the first test round ----------

CHECKS = [("Glyphmotion", 9, 10, 10), ("lasso", 10, 11, 11), ("inp-fix", 7, 10, 11)]  # name, without, with, out of
GAPS = [("Visuals with a phone version", (0, 7), (11, 11)),
        ("Visuals with a dark version", (5, 7), (11, 11)),
        ("Runs that showed a before/after", (2, 3), (3, 3))]


def proof(t, size):
    wide = size == "wide"
    CYCLE = 10
    W, H = (1280, 480) if wide else (640, 860)
    mx = 64 if wide else 40
    A = (64, 168) if wide else (40, 168)       # panel origins
    B = (680, 168) if wide else (40, 476)
    pw = 536 if wide else 560
    css = [sk.loop_fade("bars", CYCLE, in_end=2, hold=88, out=96)]
    body = [mat(W, H, t),
            f'<text class="mono" x="{mx}" y="68" font-size="13" letter-spacing="2" fill="{t["muted"]}">{"FIRST TEST ROUND · 3 OF MY REPOS · SAME PROMPT, WITH AND WITHOUT THE SKILL" if wide else "FIRST TEST ROUND · WITH VS WITHOUT"}</text>',
            f'<text class="serif" x="{mx - 2}" y="{114}" font-size="{32 if wide else 30}" fill="{t["ink"]}">The same model does more of it right.</text>']

    # Panel A: share of checks passed, per repo.
    ax, ay = A
    body.append(f'<text class="mono" x="{ax}" y="{ay}" font-size="13" font-weight="700" letter-spacing="1.5" fill="{t["ink"]}">CHECKS PASSED</text>'
                f'<text class="mono" x="{ax + 140}" y="{ay}" font-size="13" fill="{t["muted"]}">· 10-11 per repo</text>')
    x0, x1 = ax + 120, ax + pw - 70
    sx = lambda v: x0 + (v - .5) / .5 * (x1 - x0)
    for v in (.5, .75, 1):
        body.append(f'<line x1="{sx(v):.0f}" y1="{ay + 22}" x2="{sx(v):.0f}" y2="{ay + 196}" stroke="{t["faint"]}" stroke-dasharray="2 5"/>'
                    f'<text class="mono" x="{sx(v):.0f}" y="{ay + 216}" font-size="12" text-anchor="middle" fill="{t["muted"]}">{int(v * 100)}%</text>')
    for i, (name, a, b, n) in enumerate(CHECKS):
        y = ay + 56 + i * 56
        xa, xb = sx(a / n), sx(b / n)
        s, e = 4 + i * 6, 20 + i * 6
        css.append(sk.draw(f"l{i}", CYCLE, xb - xa, s, e, off=100))
        css.append(sk.slide(f"d{i}", CYCLE, xb - xa, s, e))
        body.append(f'<text class="mono" x="{ax}" y="{y + 5}" font-size="14" fill="{t["ink"]}">{name}</text>'
                    f'<circle cx="{xa:.1f}" cy="{y}" r="8" fill="{t["bg"]}" stroke="{t["grey"]}" stroke-width="3"/>'
                    f'<text class="mono" x="{xa - 14:.1f}" y="{y + 5}" font-size="13" text-anchor="end" fill="{t["muted"]}">{a}/{n}</text>'
                    f'<g class="bars"><line class="l{i}" x1="{xa:.1f}" y1="{y}" x2="{xb:.1f}" y2="{y}" stroke="{t["magenta"]}" stroke-width="4" stroke-linecap="round"/>'
                    f'<g class="d{i}"><circle cx="{xb:.1f}" cy="{y}" r="9" fill="{t["magenta"]}"/>'
                    f'<text class="mono" x="{xb + 16:.1f}" y="{y + 5}" font-size="14" font-weight="700" fill="{t["ink"]}">{b}/{n}</text></g></g>')

    # Panel B: what the skill added that the plain model skipped.
    bx, by = B
    body.append(f'<text class="mono" x="{bx}" y="{by}" font-size="13" font-weight="700" letter-spacing="1.5" fill="{t["ink"]}">WHAT CHANGED</text>')
    bw = pw - 110
    for i, (label, (a, an), (b, bn)) in enumerate(GAPS):
        y = by + 40 + i * 66
        s, e = 30 + i * 6, 44 + i * 6
        css.append(sk.grow(f"g{i}", CYCLE, s, e, off=100))
        css.append(sk.grow(f"h{i}", CYCLE, s - 4, e - 4, off=100))
        body.append(f'<text class="mono" x="{bx}" y="{y}" font-size="14" fill="{t["ink"]}">{label}</text>'
                    f'<rect x="{bx}" y="{y + 12}" width="{bw}" height="10" rx="5" fill="{t["line"]}"/>'
                    f'<rect x="{bx}" y="{y + 28}" width="{bw}" height="10" rx="5" fill="{t["line"]}"/>'
                    f'<g class="bars">'
                    + (f'<rect class="h{i}" x="{bx}" y="{y + 12}" width="{bw * a / an:.1f}" height="10" rx="5" fill="{t["grey"]}"/>' if a else "")
                    + f'<rect class="g{i}" x="{bx}" y="{y + 28}" width="{bw * b / bn:.1f}" height="10" rx="5" fill="{t["magenta"]}"/></g>'
                    f'<text class="mono" x="{bx + bw + 12}" y="{y + 21}" font-size="12.5" fill="{t["muted"]}">{a} of {an}</text>'
                    f'<text class="mono" x="{bx + bw + 12}" y="{y + 37}" font-size="12.5" font-weight="700" fill="{t["ink"]}">{b} of {bn}</text>')
    ly = H - 34
    body.append(f'<g class="mono" font-size="13" fill="{t["muted"]}">'
                f'<circle cx="{mx + 8}" cy="{ly - 4}" r="7" fill="{t["bg"]}" stroke="{t["grey"]}" stroke-width="3"/><text x="{mx + 24}" y="{ly + 1}">without the skill</text>'
                f'<circle cx="{mx + 188}" cy="{ly - 4}" r="8" fill="{t["magenta"]}"/><text x="{mx + 204}" y="{ly + 1}">with the skill</text>'
                + (f'<text x="{W - 64}" y="{ly + 1}" text-anchor="end">One run per repo. The skill used about 1.6× the tokens.</text>' if wide else
                   f'<text x="{mx}" y="{ly - 30}">One run per repo. The skill used about 1.6× the tokens.</text>')
                + '</g>')
    return sk.svg_doc(W, H, "Test results with and without github-readme-designer",
                      "Checks passed: Glyphmotion 9 of 10 without the skill, 10 of 10 with it; lasso 10 of 11 to 11 of 11; inp-fix 7 of 11 to 10 of 11. "
                      "Visuals with a phone version: 0 of 7 without, 11 of 11 with. Dark version: 5 of 7 to 11 of 11. Before/after shown: 2 of 3 runs to 3 of 3.",
                      "".join(css), "".join(body))


# ---------- flow ----------

STATIONS = [
    ("Read the repo", "code, docs, sample data", "and the old README"),
    ("Find the proof", "real results, real output;", "runs it when it's safe"),
    ("Pick a look", "a palette and one signature", "from the project's world"),
    ("Build visuals", "animated SVG, light + dark,", "desktop + phone"),
    ("Before / after", "checked, then side by side,", "before anything is pushed"),
]


def flow(t, size):
    wide = size == "wide"
    CYCLE, n = 8, len(STATIONS)
    if wide:
        W, H, mx = 1280, 320, 64
        pts = [(128 + i * 256, 132) for i in range(n)]
    else:
        W, H, mx = 640, 700, 40
        pts = [(70, 126 + i * 128) for i in range(n)]
    axis = "X" if wide else "Y"
    (fx, fy), (lx, ly) = pts[0], pts[-1]
    dist = (lx - fx) if wide else (ly - fy)
    css = [f"""
.ship {{ animation: ship {CYCLE}s cubic-bezier(.6,0,.4,1) infinite both; }}
@keyframes ship {{ 0% {{ transform: translate{axis}(0); opacity: 0; }} 5% {{ opacity: 1; }} 85% {{ transform: translate{axis}({dist}px); opacity: 1; }} 100% {{ transform: translate{axis}({dist}px); opacity: 0; }} }}"""]
    body = [mat(W, H, t), f'<text class="mono" x="{mx}" y="58" font-size="13" letter-spacing="2" fill="{t["muted"]}">HOW A README GETS REDESIGNED</text>',
            f'<line x1="{fx}" y1="{fy}" x2="{lx}" y2="{ly}" stroke="{t["faint"]}" stroke-width="2" stroke-dasharray="6 7"/>']
    for i, ((x, y), (name, s1, s2)) in enumerate(zip(pts, STATIONS)):
        pct = 5 + 80 * i / (n - 1)
        css.append(f"""
.s{i} {{ animation: s{i} {CYCLE}s linear infinite both; }}
@keyframes s{i} {{ 0%,{max(pct - 2, 0):.1f}% {{ fill: {t['card']}; }} {pct + 1:.1f}%,96% {{ fill: {t['cyan']}; }} 100% {{ fill: {t['card']}; }} }}""")
        body.append(f'<circle class="s{i}" cx="{x}" cy="{y}" r="15" fill="{t["cyan"]}" stroke="{t["cyan"]}" stroke-width="3"/>'
                    f'<text class="mono" x="{x}" y="{y + 5}" font-size="13" font-weight="700" text-anchor="middle" fill="{t["ink"]}">{i + 1}</text>')
        if wide:
            body.append(f'<text class="serif" x="{x}" y="{y + 56}" font-size="23" text-anchor="middle" fill="{t["ink"]}">{name}</text>'
                        f'<text class="mono" x="{x}" y="{y + 88}" font-size="14" text-anchor="middle" fill="{t["muted"]}">{sk.esc(s1)}</text>'
                        f'<text class="mono" x="{x}" y="{y + 109}" font-size="14" text-anchor="middle" fill="{t["muted"]}">{sk.esc(s2)}</text>')
        else:
            body.append(f'<text class="serif" x="{x + 40}" y="{y + 6}" font-size="26" fill="{t["ink"]}">{name}</text>'
                        f'<text class="mono" x="{x + 40}" y="{y + 34}" font-size="15" fill="{t["muted"]}">{sk.esc(s1)}</text>'
                        f'<text class="mono" x="{x + 40}" y="{y + 56}" font-size="15" fill="{t["muted"]}">{sk.esc(s2)}</text>')
    body.append(f'<circle class="ship" cx="{fx}" cy="{fy}" r="6" fill="{t["ink"]}"/>')
    return sk.svg_doc(W, H, "How github-readme-designer works",
                      "Five steps: read the repo, find the proof, pick a look, build the visuals, then check and show a before/after before anything is pushed.",
                      "".join(css), "".join(body))


if __name__ == "__main__":
    sk.write_all(ROOT / ".github/assets", {"hero": hero, "proof": proof, "flow": flow}, THEMES)
