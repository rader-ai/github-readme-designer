"""Generate the lighthouse-fix README assets: hero, proof and flow, light + dark.

Every SVG is self-contained (no external refs, no JS), animates with CSS
keyframes, and falls back to its finished state under prefers-reduced-motion.
"""
import math
import pathlib
import sys

# svgkit lives in the skill's scripts/ folder.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import svgkit as sk  # noqa: E402
from svgkit import MONO, SERIF  # noqa: E402,F401

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out/.github/assets")

THEMES = {
    "light": dict(  # nautical chart paper
        bg="#EEF2F1", contour="#D3DFDD", ink="#13293D", muted="#5B6F7C",
        faint="#A9B8BF", row="#E2E9E8", lit="#FFF0D2", beam="#E39A2D",
        beamfill="#F2B54C", grey="#9DAAB2", tower="#13293D", rock="#3B5265",
    ),
    "dark": dict(  # night sea
        bg="#0F1D29", contour="#18293A", ink="#E8EEF0", muted="#8DA2B0",
        faint="#3E5568", row="#152636", lit="#3A2D14", beam="#F5B84A",
        beamfill="#F5B84A", grey="#4F6575", tower="#C9D5DC", rock="#24394C",
    ),
}


def contours(w, h, c, n=7, seed=0.0):
    """Depth contours, like a sea chart."""
    paths = []
    for i in range(n):
        y0 = h * (i + 0.6) / n
        amp = 10 + 6 * math.sin(i * 1.7 + seed)
        pts = []
        for x in range(0, w + 41, 40):
            y = y0 + amp * math.sin(x / 140 + i * 0.9 + seed) + 5 * math.sin(x / 47 + i)
            pts.append(f"{x},{y:.1f}")
        paths.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{c["contour"]}" stroke-width="1.2"/>')
    return "\n  ".join(paths)


def svg(w, h, title, desc, style, body, c):
    """Every visual sits on the chart-paper background with depth contours."""
    texture = f'<rect width="{w}" height="{h}" rx="18" fill="{c["bg"]}"/>\n<g>\n  {contours(w, h, c)}\n</g>\n'
    return sk.svg_doc(w, h, title, desc, style, texture + body)


# ---------- hero ----------

ROWS = [  # label, rank tag or None (lab only)
    ("Render-blocking requests", "#2 · developer"),
    ("Legacy JavaScript", None),
    ("LCP request discovery", "#1 · developer"),
    ("DOM size", None),
    ("Third-party tags", "#3 · marketing ops"),
    ("Font display", None),
    ("Layout shift culprits", "#4 · CMS owner"),
    ("Cache lifetimes", None),
]




# Each asset comes in a wide (desktop) and a narrow (phone) layout.
HERO = {
    "wide": dict(W=1280, H=440, lantern=(1192, 176), beam_len=640,
                 rows=(648, 84, 28, 37, 404), text=(64, 98), title=46, gap=56,
                 body_y=284, chips_y=350),
    "narrow": dict(W=640, H=770, lantern=(570, 470), beam_len=560,
                   rows=(40, 344, 30, 40, 440), text=(40, 64), title=40, gap=48,
                   body_y=214, chips_y=262),
}


def hero(c, size="wide"):
    L = HERO[size]
    W, H = L["W"], L["H"]
    LX, LY = L["lantern"]
    CYCLE = 12
    SWEEP_END = 50  # % of cycle when the beam reaches the bottom row
    rx0, ry0, rh, step, rw = L["rows"]
    cx = rx0 + rw / 2
    top = math.degrees(math.atan2(LY - (ry0 + rh / 2), LX - cx)) + 3
    bottom = math.degrees(math.atan2(LY - (ry0 + 7 * step + rh / 2), LX - cx)) - 3

    style = [f"""
.mono {{ font-family: {MONO}; }}
.serif {{ font-family: {SERIF}; }}
.beam {{ transform-box: view-box; transform-origin: {LX}px {LY}px; transform: rotate({(top + bottom) / 2:.1f}deg);
  animation: sweep {CYCLE}s linear infinite both; }}
@keyframes sweep {{
  0% {{ transform: rotate({top:.1f}deg); opacity: 0; }}
  6% {{ opacity: .95; }}
  {SWEEP_END}% {{ transform: rotate({bottom:.1f}deg); opacity: .95; }}
  {SWEEP_END + 10}% {{ transform: rotate({bottom:.1f}deg); opacity: 0; }}
  100% {{ transform: rotate({top:.1f}deg); opacity: 0; }}
}}
.glow {{ animation: glow 2.4s ease-in-out infinite alternate both; }}
@keyframes glow {{ from {{ opacity: .55; }} to {{ opacity: 1; }} }}
"""]
    ty = rh / 2 + 5
    rows = []
    for i, (label, tag) in enumerate(ROWS):
        y = ry0 + i * step
        hit = 6 + (SWEEP_END - 6) * (i + 0.5) / len(ROWS)
        a, b = hit - 1.5, hit + 2.5
        if tag:
            style.append(f"""
.r{i} .bg {{ animation: r{i}bg {CYCLE}s linear infinite both; }}
.r{i} .tag, .r{i} .tick {{ animation: r{i}on {CYCLE}s linear infinite both; }}
@keyframes r{i}bg {{ 0%,{a:.1f}% {{ fill: {c['row']}; }} {b:.1f}%,95% {{ fill: {c['lit']}; }} 100% {{ fill: {c['row']}; }} }}
@keyframes r{i}on {{ 0%,{a:.1f}% {{ opacity: 0; }} {b:.1f}%,95% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}""")
            rows.append(f"""<g class="r{i}">
  <rect class="bg" x="{rx0}" y="{y}" width="{rw}" height="{rh}" rx="6" fill="{c['lit']}"/>
  <rect class="tick" x="{rx0}" y="{y}" width="4" height="{rh}" rx="2" fill="{c['beam']}"/>
  <text class="mono" x="{rx0 + 16}" y="{y + ty}" font-size="14" fill="{c['ink']}">{label}</text>
  <text class="mono tag" x="{rx0 + rw - 12}" y="{y + ty}" font-size="12.5" font-weight="700" text-anchor="end" fill="{c['beam']}">{tag}</text>
</g>""")
        else:
            style.append(f"""
.r{i} .bg {{ animation: r{i}bg {CYCLE}s linear infinite both; }}
.r{i} .lbl {{ animation: r{i}lbl {CYCLE}s linear infinite both; }}
.r{i} .tag {{ animation: r{i}tag {CYCLE}s linear infinite both; }}
@keyframes r{i}bg {{ 0%,{a:.1f}% {{ fill: {c['row']}; }} {hit + .5:.1f}% {{ fill: {c['lit']}; }} {b + 4:.1f}%,100% {{ fill: {c['row']}; }} }}
@keyframes r{i}lbl {{ 0%,{a:.1f}% {{ opacity: .75; }} {b + 4:.1f}%,95% {{ opacity: .38; }} 100% {{ opacity: .75; }} }}
@keyframes r{i}tag {{ 0%,{b:.1f}% {{ opacity: 0; }} {b + 4:.1f}%,95% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}""")
            rows.append(f"""<g class="r{i}">
  <rect class="bg" x="{rx0}" y="{y}" width="{rw}" height="{rh}" rx="6" fill="{c['row']}"/>
  <text class="mono lbl" x="{rx0 + 16}" y="{y + ty}" font-size="14" fill="{c['muted']}" opacity=".38">{label}</text>
  <text class="mono tag" x="{rx0 + rw - 12}" y="{y + ty}" font-size="12.5" text-anchor="end" fill="{c['muted']}">lab only</text>
</g>""")

    # Tower drawn around a lantern at (1192, 176), then moved to this layout's lantern.
    tower = f"""
<g transform="translate({LX - 1192} {LY - 176})">
  <path d="M1110 404 Q1150 372 1192 376 Q1240 372 1272 404 Z" fill="{c['rock']}"/>
  <path d="M1176 382 L1182 206 L1202 206 L1208 382 Z" fill="{c['tower']}"/>
  <rect x="1180" y="236" width="24" height="9" fill="{c['bg']}" opacity=".9"/>
  <rect x="1179" y="300" width="26" height="9" fill="{c['bg']}" opacity=".9"/>
  <rect x="1176" y="200" width="32" height="7" rx="1" fill="{c['tower']}"/>
  <rect x="1182" y="168" width="20" height="32" rx="2" fill="{c['tower']}"/>
  <rect class="glow" x="1185" y="172" width="14" height="22" rx="2" fill="{c['beamfill']}"/>
  <path d="M1178 168 L1192 154 L1206 168 Z" fill="{c['tower']}"/>
</g>"""
    bl = L["beam_len"]
    beam = f"""
<defs>
  <linearGradient id="bg" x1="1" y1="0" x2="0" y2="0">
    <stop offset="0" stop-color="{c['beamfill']}" stop-opacity=".55"/>
    <stop offset=".75" stop-color="{c['beamfill']}" stop-opacity=".12"/>
    <stop offset="1" stop-color="{c['beamfill']}" stop-opacity="0"/>
  </linearGradient>
</defs>
<polygon class="beam" points="{LX},{LY - 4} {LX - bl},{LY - 46} {LX - bl},{LY + 46} {LX},{LY + 4}" fill="url(#bg)"/>"""

    tx, ey = L["text"]
    t1 = ey + L["title"] + 24
    t2 = t1 + L["gap"]
    by, cy = L["body_y"], L["chips_y"]
    text = f"""
<text class="mono" x="{tx}" y="{ey}" font-size="13" letter-spacing="2" fill="{c['muted']}">LIGHTHOUSE / PAGESPEED REPORT → RANKED FIXES</text>
<text class="serif" x="{tx - 2}" y="{t1}" font-size="{L['title']}" fill="{c['ink']}">Forty audits in.</text>
<text class="serif" x="{tx - 2}" y="{t2}" font-size="{L['title']}" font-style="italic" fill="{c['ink']}">The few that matter, fixed.</text>
<text class="mono" x="{tx}" y="{by}" font-size="15" fill="{c['muted']}">Triaged on real-visitor data. Ranked by savings.</text>
<text class="mono" x="{tx}" y="{by + 24}" font-size="15" fill="{c['muted']}">Handed off as prompts a coding agent can run.</text>
<g class="mono" font-size="13" fill="{c['ink']}">
  <rect x="{tx}" y="{cy}" width="132" height="30" rx="15" fill="none" stroke="{c['faint']}"/>
  <text x="{tx + 66}" y="{cy + 20}" text-anchor="middle">Claude Code</text>
  <rect x="{tx + 142}" y="{cy}" width="84" height="30" rx="15" fill="none" stroke="{c['faint']}"/>
  <text x="{tx + 184}" y="{cy + 20}" text-anchor="middle">Codex</text>
  <rect x="{tx + 236}" y="{cy}" width="104" height="30" rx="15" fill="none" stroke="{c['faint']}"/>
  <text x="{tx + 288}" y="{cy + 20}" text-anchor="middle">ChatGPT</text>
</g>"""
    body = beam + "\n" + "\n".join(rows) + tower + text
    return svg(W, H, "lighthouse-fix",
               "A lighthouse beam sweeps a list of Lighthouse audits. Four that hurt real visitors light up "
               "and get a rank and an owner; the rest are marked lab only.",
               "".join(style), body, c)


# ---------- proof ----------

PANELS = [
    dict(title="PROBLEMS FIXED", sub="trap site, 19 planted problems", lo=11, hi=19, unit="",
         rows=[("Haiku", 15, 18), ("Sonnet", 16, 19), ("Opus", 17, 19)]),
    dict(title="ANALYSIS SCORE", sub="5 real reports, graded blind", lo=70, hi=100, unit="%",
         rows=[("Haiku", 74, 85), ("Sonnet", 85, 97), ("Opus", 83, 100)]),
]


def proof(c, size="wide"):
    if size == "wide":
        W, H, mx = 1280, 470, 64
        eyebrow = "TESTED OCT 21, 2026 · SAME MODELS, WITH AND WITHOUT THE SKILL"
        origins = [(64, 0), (680, 0)]  # panel x, panel y offset
        legend_y, note = 432, (1216, 432, "end")
    else:
        W, H, mx = 640, 760, 40
        eyebrow = "TESTED OCT 21, 2026 · WITH VS WITHOUT THE SKILL"
        origins = [(40, 0), (40, 262)]
        legend_y, note = 690, (40, 726, "start")
    CYCLE = 9  # draw in, count up, hold, fade, repeat
    style = [f"""
.mono {{ font-family: {MONO}; }}
.serif {{ font-family: {SERIF}; }}
.bars {{ animation: bars {CYCLE}s linear infinite both; }}
@keyframes bars {{ 0% {{ opacity: 0; }} 2% {{ opacity: 1; }} 88% {{ opacity: 1; }} 96%,100% {{ opacity: 0; }} }}
"""]
    body = [f"""
<text class="mono" x="{mx}" y="70" font-size="13" letter-spacing="2" fill="{c['muted']}">{eyebrow}</text>
<text class="serif" x="{mx - 2}" y="116" font-size="34" fill="{c['ink']}">Every model did better with it.</text>"""]
    k = 0
    for p, (px, oy) in zip(PANELS, origins):
        x0, x1 = px + 92, px + 520
        sx = lambda v: x0 + (v - p["lo"]) / (p["hi"] - p["lo"]) * (x1 - x0)
        body.append(f"""
<text class="mono" x="{px}" y="{176 + oy}" font-size="13" font-weight="700" letter-spacing="1.5" fill="{c['ink']}">{p['title']}</text>
<text class="mono" x="{px + 8 + len(p['title']) * 9.6:.0f}" y="{176 + oy}" font-size="13" fill="{c['muted']}">· {p['sub']}</text>""")
        for t in (p["lo"], (p["lo"] + p["hi"]) / 2, p["hi"]):
            tx = sx(t)
            body.append(f'<line x1="{tx:.1f}" y1="{200 + oy}" x2="{tx:.1f}" y2="{372 + oy}" stroke="{c["faint"]}" stroke-dasharray="2 5"/>'
                        f'<text class="mono" x="{tx:.1f}" y="{394 + oy}" font-size="12" text-anchor="middle" fill="{c["muted"]}">{t:g}{p["unit"]}</text>')
        for j, (name, a, b) in enumerate(p["rows"]):
            y = 230 + oy + j * 56
            xa, xb = sx(a), sx(b)
            s = 4 + k * 5  # % of cycle when this bar starts
            e = s + 16     # % when it lands
            k += 1
            ease = "cubic-bezier(.2,.7,.2,1)"
            style.append(f"""
.l{k} {{ stroke-dasharray: {xb - xa:.1f}; animation: l{k} {CYCLE}s {ease} infinite both; }}
@keyframes l{k} {{ 0%,{s}% {{ stroke-dashoffset: {xb - xa:.1f}; }} {e}%,100% {{ stroke-dashoffset: 0; }} }}
.d{k} {{ animation: d{k} {CYCLE}s {ease} infinite both; }}
@keyframes d{k} {{ 0%,{s}% {{ transform: translateX({xa - xb:.1f}px); }} {e}%,100% {{ transform: translateX(0); }} }}""")
            # The value counts up from a to b while the dot travels.
            m = min(b - a, 6)
            vals = sorted({round(a + (b - a) * i / m) for i in range(1, m + 1)})
            counts = []
            for i, v in enumerate(vals):
                last = i == len(vals) - 1
                on = s + (e - s) * i / len(vals)
                off = s + (e - s) * (i + 1) / len(vals)
                frames = (f"0%,{on:.1f}% {{ opacity: 0; }} {on + .1:.1f}%,100% {{ opacity: 1; }}" if last else
                          f"0%,{on:.1f}% {{ opacity: 0; }} {on + .1:.1f}%,{off:.1f}% {{ opacity: 1; }} {off + .1:.1f}%,100% {{ opacity: 0; }}")
                style.append(f"\n.c{k}_{i} {{ animation: c{k}_{i} {CYCLE}s linear infinite both; }}\n@keyframes c{k}_{i} {{ {frames} }}")
                counts.append(f'<text class="mono c{k}_{i}" x="{xb + 16:.1f}" y="{y + 5}" font-size="14" font-weight="700" fill="{c["ink"]}" opacity="{1 if last else 0}">{v}{p["unit"]}</text>')
            body.append(f"""
<text class="mono" x="{px}" y="{y + 5}" font-size="14" fill="{c['ink']}">{name}</text>
<circle cx="{xa:.1f}" cy="{y}" r="8" fill="{c['bg']}" stroke="{c['grey']}" stroke-width="3"/>
<text class="mono" x="{xa - 14:.1f}" y="{y + 5}" font-size="13" text-anchor="end" fill="{c['muted']}">{a}{p['unit']}</text>
<g class="bars">
  <line class="l{k}" x1="{xa:.1f}" y1="{y}" x2="{xb:.1f}" y2="{y}" stroke="{c['beam']}" stroke-width="4" stroke-linecap="round"/>
  <g class="d{k}">
    <circle cx="{xb:.1f}" cy="{y}" r="9" fill="{c['beam']}"/>
    {"".join(counts)}
  </g>
</g>""")
    nx, ny, anchor = note
    body.append(f"""
<g class="mono" font-size="13" fill="{c['muted']}">
  <circle cx="{mx + 8}" cy="{legend_y}" r="7" fill="{c['bg']}" stroke="{c['grey']}" stroke-width="3"/>
  <text x="{mx + 24}" y="{legend_y + 5}">without the skill</text>
  <circle cx="{mx + 188}" cy="{legend_y}" r="8" fill="{c['beam']}"/>
  <text x="{mx + 204}" y="{legend_y + 5}">with the skill</text>
  <text x="{nx}" y="{ny + 5}" text-anchor="{anchor}">One run per setup. Scores move 1–2 points between runs.</text>
</g>""")
    return svg(W, H, "Results with and without lighthouse-fix",
               "Problems fixed out of 19: Haiku 15 to 18, Sonnet 16 to 19, Opus 17 to 19. "
               "Blind-graded analysis score: Haiku 74 to 85 percent, Sonnet 85 to 97, Opus 83 to 100.",
               "".join(style), "".join(body), c)


# ---------- flow ----------

STATIONS = [
    ("Your report", ["JSON, text, screenshot", "or just a URL"]),
    ("Real visitors", ["Chrome UX field data", "decides what matters"]),
    ("Rank", ["by savings, and by how", "badly a metric fails"]),
    ("Fix prompts", ["one per area, or one", "all-in-one prompt"]),
    ("Right owner", ["developer, marketing ops", "or CMS owner"]),
]


def flow(c, size="wide"):
    CYCLE = 7
    n = len(STATIONS)
    if size == "wide":  # stations left to right, captions centred below
        W, H, mx = 1280, 310, 64
        pts = [(128 + i * 256, 128) for i in range(n)]
        axis = "X"
    else:  # stations top to bottom, captions to the right
        W, H, mx = 640, 690, 40
        pts = [(70, 124 + i * 128) for i in range(n)]
        axis = "Y"
    (fx, fy), (lx, ly) = pts[0], pts[-1]
    dist = (lx - fx) if axis == "X" else (ly - fy)
    style = [f"""
.mono {{ font-family: {MONO}; }}
.serif {{ font-family: {SERIF}; }}
.ship {{ animation: ship {CYCLE}s cubic-bezier(.6,0,.4,1) infinite both; }}
@keyframes ship {{ 0% {{ transform: translate{axis}(0); opacity: 0; }} 5% {{ opacity: 1; }} 85% {{ transform: translate{axis}({dist}px); opacity: 1; }} 100% {{ transform: translate{axis}({dist}px); opacity: 0; }} }}
"""]
    body = [f"""
<text class="mono" x="{mx}" y="56" font-size="13" letter-spacing="2" fill="{c['muted']}">HOW A REPORT BECOMES FIXES</text>
<line x1="{fx}" y1="{fy}" x2="{lx}" y2="{ly}" stroke="{c['faint']}" stroke-width="2" stroke-dasharray="6 7"/>"""]
    for i, ((x, y), (name, sub)) in enumerate(zip(pts, STATIONS)):
        pct = 5 + 80 * i / (n - 1)
        style.append(f"""
.s{i} {{ animation: s{i} {CYCLE}s linear infinite both; }}
@keyframes s{i} {{ 0%,{max(pct - 2, 0):.1f}% {{ fill: {c['bg']}; }} {pct + 1:.1f}%,96% {{ fill: {c['beam']}; }} 100% {{ fill: {c['bg']}; }} }}""")
        body.append(f"""
<circle class="s{i}" cx="{x}" cy="{y}" r="15" fill="{c['beam']}" stroke="{c['beam']}" stroke-width="3"/>
<text class="mono" x="{x}" y="{y + 5}" font-size="13" font-weight="700" text-anchor="middle" fill="{c['ink']}">{i + 1}</text>""")
        if size == "wide":
            body.append(f"""
<text class="serif" x="{x}" y="{y + 56}" font-size="23" text-anchor="middle" fill="{c['ink']}">{name}</text>
<text class="mono" x="{x}" y="{y + 88}" font-size="15" text-anchor="middle" fill="{c['muted']}">{sub[0]}</text>
<text class="mono" x="{x}" y="{y + 110}" font-size="15" text-anchor="middle" fill="{c['muted']}">{sub[1]}</text>""")
        else:
            body.append(f"""
<text class="serif" x="{x + 40}" y="{y + 8}" font-size="26" fill="{c['ink']}">{name}</text>
<text class="mono" x="{x + 40}" y="{y + 36}" font-size="16" fill="{c['muted']}">{sub[0]} {sub[1]}</text>""")
    body.append(f'<circle class="ship" cx="{fx}" cy="{fy}" r="6" fill="{c["ink"]}"/>')
    return svg(W, H, "How lighthouse-fix works",
               "Five steps: your report, real-visitor triage, ranking, fix prompts, and routing each fix to its owner.",
               "".join(style), "".join(body), c)


if __name__ == "__main__":
    sk.write_all(OUT, {"hero": hero, "proof": proof, "flow": flow}, THEMES)
