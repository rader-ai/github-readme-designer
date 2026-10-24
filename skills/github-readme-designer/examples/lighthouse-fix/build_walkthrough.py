"""Generate the three walkthrough visuals for the lighthouse-fix README.

1. report  - what a Lighthouse / PageSpeed report gives you (lab vs real visitors, flagged audits)
2. read    - how the skill reads it: metric triage, then ranked cards with owners
3. prompt  - an excerpt of the fix prompt it writes for a coding agent

All content comes from running the skill on evals/reports/betabound.txt.
Same rules as build_lighthouse.py: self-contained SVG, CSS keyframes only,
finished state under prefers-reduced-motion, wide + narrow, light + dark.
"""
import pathlib
import sys

from build_visuals import MONO, SERIF, THEMES, sk, svg

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out/.github/assets")

STATUS = {
    "light": dict(good="#2F8F5B", warn="#C98316", bad="#C4473A", card="#F7FAF9", line="#D5E0DF"),
    "dark": dict(good="#5CC28A", warn="#F0B048", bad="#F07A6A", card="#132433", line="#22384A"),
}

BASE_STYLE = f"""
.mono {{ font-family: {MONO}; }}
.serif {{ font-family: {SERIF}; }}
"""


reveal = sk.reveal


def panel(x, y, w, h, c, s, label):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{s["card"]}" stroke="{s["line"]}"/>'
            f'<text class="mono" x="{x + 20}" y="{y + 30}" font-size="12" letter-spacing="1.5" font-weight="700" fill="{c["muted"]}">{label}</text>')


# ---------- 1. what comes back ----------

FIELD = [  # metric, p75, verdict, good / needs improvement / poor shares (None where the report doesn't split it)
    ("LCP", "1.7 s", "good", (84, None, None)),
    ("INP", "287 ms", "bad", (28, 70, 2)),
    ("CLS", "0.08", "good", (91, None, None)),
]
LAB = [("LCP", "9.4 s", "bad"), ("FCP", "5.3 s", "bad"), ("TBT", "70 ms", "good"), ("CLS", "0", "good")]
AUDITS = [
    ("cache-insight", "1,020 KiB"), ("render-blocking-insight", "390 ms"), ("image-delivery-insight", "96 KiB"),
    ("forced-reflow-insight", ""), ("network-dependency-tree", ""), ("font-display-insight", "10 ms"),
    ("viewport-insight", ""), ("legacy-javascript-insight", "13 KiB"), ("dom-size-insight", ""),
    ("lcp-breakdown-insight", ""), ("third-parties-insight", ""), ("unused-javascript", "133 KiB"),
    ("unminified-css", "4 KiB"), ("unminified-javascript", "3 KiB"), ("image-alt", ""), ("link-name", ""),
    ("object-alt", ""), ("heading-order", ""), ("errors-in-console", ""), ("valid-source-maps", ""),
    ("link-text", ""), ("crawlable-anchors", ""), ("agent-accessibility-tree", ""), ("viewport", ""),
]


def report(c, size="wide"):
    s = STATUS[[k for k, v in THEMES.items() if v is c][0]]
    CYCLE = 12
    if size == "wide":
        W, H = 1280, 470
        boxes = [(64, 84, 360, 340), (448, 84, 388, 340), (860, 84, 356, 340)]
    else:
        W, H = 640, 1150
        boxes = [(40, 84, 560, 300), (40, 404, 560, 340), (40, 764, 560, 340)]
    style = [BASE_STYLE]
    body = [f'<text class="mono" x="{boxes[0][0]}" y="56" font-size="13" letter-spacing="2" fill="{c["muted"]}">WHAT COMES BACK · BETABOUND.COM, MOBILE, OCT 21 2026</text>']

    # Lab panel: score ring + lab metrics.
    x, y, w, h = boxes[0]
    body.append(panel(x, y, w, h, c, s, "LAB TEST · ONE SIMULATED PHONE"))
    rx, ry, r = x + 90, y + 130, 56
    circ = 2 * 3.14159 * r
    style.append(f"""
.ring {{ stroke-dasharray: {circ:.1f}; stroke-dashoffset: {circ * 0.4:.1f}; animation: ring {CYCLE}s cubic-bezier(.2,.7,.2,1) infinite both; }}
@keyframes ring {{ 0%,3% {{ stroke-dashoffset: {circ:.1f}; }} 18%,100% {{ stroke-dashoffset: {circ * 0.4:.1f}; }} }}""")
    body.append(f"""
<circle cx="{rx}" cy="{ry}" r="{r}" fill="none" stroke="{s['line']}" stroke-width="10"/>
<circle class="ring" cx="{rx}" cy="{ry}" r="{r}" fill="none" stroke="{s['warn']}" stroke-width="10" stroke-linecap="round" transform="rotate(-90 {rx} {ry})"/>
<text class="serif" x="{rx}" y="{ry + 14}" font-size="42" text-anchor="middle" fill="{c['ink']}">60</text>
<text class="mono" x="{rx}" y="{ry + r + 30}" font-size="12" text-anchor="middle" fill="{c['muted']}">performance</text>""")
    mx = x + 200
    for i, (m, v, st) in enumerate(LAB):
        my = y + 92 + i * 34
        style.append(reveal(f"lab{i}", CYCLE, 8 + i * 3))
        body.append(f'<g class="lab{i}"><text class="mono" x="{mx}" y="{my}" font-size="14" fill="{c["muted"]}">{m}</text>'
                    f'<text class="mono" x="{x + w - 24}" y="{my}" font-size="15" font-weight="700" text-anchor="end" fill="{s[st]}">{v}</text></g>')
    body.append(f'<text class="mono" x="{x + 20}" y="{y + h - 22}" font-size="12" fill="{c["muted"]}">Accessibility 85 · Best practices 96 · SEO 77</text>')

    # Field panel: distribution bars for real visitors.
    x, y, w, h = boxes[1]
    body.append(panel(x, y, w, h, c, s, "REAL VISITORS · CHROME UX REPORT, 28 DAYS"))
    bw = w - 40
    for i, (m, v, st, (g, n, p)) in enumerate(FIELD):
        by = y + 78 + i * 74
        on = 22 + i * 6
        body.append(f'<text class="mono" x="{x + 20}" y="{by}" font-size="14" fill="{c["ink"]}">{m}</text>'
                    f'<text class="mono" x="{x + w - 20}" y="{by}" font-size="15" font-weight="700" text-anchor="end" fill="{s[st]}">{v}</text>')
        segs, sx = [], x + 20
        split = ((g, s["good"]), (n, s["warn"]), (p, s["bad"])) if n is not None else ((g, s["good"]), (100 - g, s["line"]))
        for j, (share, col) in enumerate(split):
            sw = bw * share / 100
            segs.append(f'<rect x="{sx:.1f}" y="{by + 12}" width="{max(sw - 2, 0):.1f}" height="12" rx="3" fill="{col}"/>')
            sx += sw
        style.append(f"""
.bar{i} {{ transform-box: fill-box; transform-origin: left center; animation: bar{i} {CYCLE}s cubic-bezier(.2,.7,.2,1) infinite both; }}
@keyframes bar{i} {{ 0%,{on}% {{ transform: scaleX(0); }} {on + 10}%,95% {{ transform: scaleX(1); }} 100% {{ transform: scaleX(0); }} }}""")
        body.append(f'<g class="bar{i}">{"".join(segs)}</g>'
                    f'<text class="mono" x="{x + 20}" y="{by + 44}" font-size="12" fill="{c["muted"]}">{f"{g}% good · {n}% needs work · {p}% poor" if n is not None else f"{g}% of visits good"}</text>')
    style.append(reveal("verdict", CYCLE, 44))
    body.append(f'<g class="verdict"><text class="mono" x="{x + 20}" y="{y + h - 22}" font-size="14" font-weight="700" fill="{s["bad"]}">Core Web Vitals: Failed</text></g>')

    # Audit panel: the flagged list scrolls past, as it does in a real report.
    x, y, w, h = boxes[2]
    body.append(panel(x, y, w, h, c, s, "24 AUDITS FLAGGED"))
    lh, top = 30, y + 50
    view = h - 64
    rows = []
    for j, (name, save) in enumerate(AUDITS + AUDITS):
        ry2 = top + 20 + j * lh
        rows.append(f'<text class="mono" x="{x + 20}" y="{ry2}" font-size="13.5" fill="{c["ink"]}">{name}</text>'
                    + (f'<text class="mono" x="{x + w - 20}" y="{ry2}" font-size="12.5" text-anchor="end" fill="{c["muted"]}">{save}</text>' if save else ""))
    style.append(f"""
.scroll {{ animation: scroll 24s linear infinite; }}
@keyframes scroll {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-{len(AUDITS) * lh}px); }} }}""")
    body.append(f"""
<defs><clipPath id="auditclip"><rect x="{x}" y="{top}" width="{w}" height="{view}"/></clipPath>
<linearGradient id="fadeb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{s['card']}" stop-opacity="0"/><stop offset="1" stop-color="{s['card']}"/></linearGradient></defs>
<g clip-path="url(#auditclip)"><g class="scroll">{"".join(rows)}</g></g>
<rect x="{x + 1}" y="{top + view - 50}" width="{w - 2}" height="50" fill="url(#fadeb)"/>""")
    return svg(W, H, "What a Lighthouse report gives you",
               "Betabound on mobile. Lab test: performance 60, LCP 9.4 seconds. Real visitors: LCP 1.7 seconds is good, "
               "INP 287 milliseconds needs work, so Core Web Vitals fail. 24 audits are flagged.",
               "".join(style), "\n".join(body), c)


# ---------- 2. how we read it ----------

TRIAGE = [  # metric, lab, field, verdict text, verdict status
    ("LCP", ("9.4 s", "bad"), ("1.7 s", "good"), "lab only · rank lower", "muted"),
    ("INP", ("n/a", "muted"), ("287 ms", "bad"), "real visitors fail · fix first", "bad"),
    ("CLS", ("0", "good"), ("0.08", "good"), "fine", "good"),
]
CARDS = [  # rank, plain meaning, owner, note, lab-only?
    (1, "Outside services (tags, chat, analytics) slow the page.", "marketing ops", "moves INP", False),
    (2, "Scripts force the browser to recalculate layout over and over.", "developer", "moves INP", False),
    (3, "The page has a very large number of elements.", "developer", "moves INP", False),
    (5, "Old-browser code ships to modern browsers who don't need it.", "developer", "moves INP", False),
    (7, "Images are bigger files than they need to be.", "content", "lab only: real visitors pass LCP", True),
]


def read(c, size="wide"):
    s = STATUS[[k for k, v in THEMES.items() if v is c][0]]
    s = dict(s, muted=c["muted"])
    CYCLE = 12
    wide = size == "wide"
    if wide:
        W, H = 1280, 500
        tx, ty, tw = 64, 84, 540
        kx, ky, kw = 640, 84, 576
    else:
        W, H = 640, 910
        tx, ty, tw = 40, 84, 560
        kx, ky, kw = 40, 470, 560
    style = [BASE_STYLE]
    body = [f'<text class="mono" x="{tx}" y="56" font-size="13" letter-spacing="2" fill="{c["muted"]}">HOW THE SKILL READS IT</text>']

    # Triage table: lab vs real visitors per metric.
    cols = (tx, tx + 70, tx + 170) if wide else (tx, tx + 64, tx + 160)
    body.append(panel(tx, ty, tw, 280, c, s, "STEP 1 · CHECK EACH METRIC AGAINST REAL VISITORS"))
    hy = ty + 66
    for cx, lbl in zip(cols, ("", "LAB", "REAL")):
        body.append(f'<text class="mono" x="{cx + 20}" y="{hy}" font-size="11.5" letter-spacing="1.5" fill="{c["muted"]}">{lbl}</text>')
    for i, (m, (lv, ls), (fv, fs), verdict, vs) in enumerate(TRIAGE):
        ry = hy + 44 + i * 58
        on = 4 + i * 9
        style.append(reveal(f"tr{i}", CYCLE, on))
        style.append(reveal(f"tv{i}", CYCLE, on + 4))
        strike = ""
        if i == 0:
            style.append(f"""
.strike {{ stroke-dasharray: 60; animation: strike {CYCLE}s linear infinite both; }}
@keyframes strike {{ 0%,{on + 4}% {{ stroke-dashoffset: 60; }} {on + 7}%,95% {{ stroke-dashoffset: 0; }} 100% {{ stroke-dashoffset: 60; }} }}""")
            strike = f'<line class="strike" x1="{cols[1] + 16}" y1="{ry - 5}" x2="{cols[1] + 76}" y2="{ry - 5}" stroke="{c["ink"]}" stroke-width="2"/>'
        body.append(f'<g class="tr{i}"><text class="mono" x="{cols[0] + 20}" y="{ry}" font-size="15" font-weight="700" fill="{c["ink"]}">{m}</text>'
                    f'<text class="mono" x="{cols[1] + 20}" y="{ry}" font-size="15" fill="{s[ls]}">{lv}</text>'
                    f'<text class="mono" x="{cols[2] + 20}" y="{ry}" font-size="15" font-weight="700" fill="{s[fs]}">{fv}</text>{strike}</g>'
                    f'<g class="tv{i}"><text class="mono" x="{tx + tw - 20}" y="{ry}" font-size="13" text-anchor="end" fill="{s[vs]}">{verdict}</text></g>')
    style.append(reveal("verdict", CYCLE, 36))
    vy = ty + 330
    body.append(f'<g class="verdict"><text class="serif" x="{tx}" y="{vy}" font-size="25" fill="{c["ink"]}">“Fails for real visitors on responsiveness.”</text>'
                f'<text class="mono" x="{tx}" y="{vy + 32}" font-size="13.5" fill="{c["muted"]}">So every fix that moves INP ranks first.</text></g>')

    # Ranked cards.
    body.append(f'<text class="mono" x="{kx}" y="{ky + 12}" font-size="12" letter-spacing="1.5" font-weight="700" fill="{c["muted"]}">STEP 2 · RANK, AND NAME AN OWNER</text>')
    ch, gap = 62, 10
    for i, (rank, plain, owner, note, labonly) in enumerate(CARDS):
        cy = ky + 30 + i * (ch + gap)
        on = 42 + i * 5
        style.append(f"""
.k{i} {{ animation: k{i} {CYCLE}s cubic-bezier(.2,.7,.2,1) infinite both; }}
@keyframes k{i} {{ 0%,{on}% {{ opacity: 0; transform: translateX(24px); }} {on + 5}%,95% {{ opacity: {.5 if labonly else 1}; transform: translateX(0); }} 100% {{ opacity: 0; }} }}""")
        accent = c["faint"] if labonly else c["beam"]
        text = plain if wide or len(plain) <= 52 else plain[:50].rsplit(" ", 1)[0] + "…"
        body.append(f"""<g class="k{i}" opacity="{.5 if labonly else 1}">
  <rect x="{kx}" y="{cy}" width="{kw}" height="{ch}" rx="10" fill="{s['card']}" stroke="{s['line']}"/>
  <rect x="{kx}" y="{cy}" width="4" height="{ch}" rx="2" fill="{accent}"/>
  <text class="serif" x="{kx + 22}" y="{cy + 39}" font-size="24" fill="{c['ink']}">{rank}</text>
  <text class="mono" x="{kx + 58}" y="{cy + 26}" font-size="14" fill="{c['ink']}">{text}</text>
  <text class="mono" x="{kx + 58}" y="{cy + 48}" font-size="12.5" fill="{c['muted']}"><tspan font-weight="700" fill="{accent if not labonly else c['muted']}">{owner}</tspan> · {note}</text>
</g>""")
    style.append(reveal("more", CYCLE, 70))
    my = ky + 30 + len(CARDS) * (ch + gap) + 14
    body.append(f'<g class="more"><text class="mono" x="{kx}" y="{my}" font-size="13" fill="{c["muted"]}">+ 15 more cards · 2 lower-value findings parked for later</text></g>')
    return svg(W, H, "How lighthouse-fix reads a report",
               "Step 1: LCP is slow in the lab but good for real visitors, so it ranks lower; INP fails for real visitors, so it is fixed first. "
               "Step 2: ranked cards with owners. The top cards all move INP; image size is marked lab only and drops to rank 7.",
               "".join(style), "\n".join(body), c)


# ---------- 3. the prompt ----------

# (text, kind) where kind is h1/h2/h3/text/mark; mark lines get a highlight and a note.
PROMPT_WIDE = [
    ("# Fix the Scripts (first- and third-party JS) findings from a Lighthouse report", "h1"),
    ("## Context", "h2"),
    ("Real visitors (Chrome UX Report, p75): LCP 1700 ms (good), INP 287 ms (needs-improvement).", "text"),
    ("Failing for real users: INP. Fix those first.", "mark:real visitors first"),
    ("Platform: WordPress. Fixes go in the theme, functions.php or plugin settings.", "text"),
    ("## Guardrails", "h2"),
    ("- A/B tests: every variant still renders and is still tracked.", "mark:keeps things working"),
    ("- Code owned by another team: change how it loads, not what it does.", "text"),
    ("## Cards", "h2"),
    ("### F1 · Outside services (tags, chat, analytics) slow the page.", "h3"),
    ("Moves: TBT, INP, LCP · Owner: marketing-ops · Rank 1 of 20", "text"),
    ("- googletagmanager.com/gtag/js | 176 KiB | 237 ms", "text"),
    ("Preferred fix: load after interaction or on consent; remove unused tags.", "text"),
    ("Avoid: Never silently remove tracking; list it for the owner to approve.", "mark:owner signs off"),
    ("Done when: Third-party main-thread time drops.", "mark:a check the agent runs"),
]
PROMPT_NARROW = [
    ("# Fix the Scripts findings", "h1"),
    ("## Context", "h2"),
    ("Real visitors (p75): LCP 1700 ms good,", "text"),
    ("INP 287 ms needs-improvement.", "text"),
    ("Failing for real users: INP. Fix those first.", "mark"),
    ("Platform: WordPress (theme, functions.php).", "text"),
    ("## Guardrails", "h2"),
    ("- Every A/B variant still renders and tracks.", "mark"),
    ("- Change how other teams' code loads,", "text"),
    ("  not what it does.", "text"),
    ("## Cards", "h2"),
    ("### F1 · Outside services slow the page.", "h3"),
    ("Moves: INP · Owner: marketing-ops · Rank 1", "text"),
    ("- googletagmanager.com/gtag/js | 237 ms", "text"),
    ("Preferred fix: load after interaction or", "text"),
    ("  on consent; remove unused tags.", "text"),
    ("Avoid: never silently remove tracking.", "mark"),
    ("Done when: third-party main-thread time drops.", "mark"),
]
TABS = ["all-in-one.md", "delivery.md", "media.md", "layout-css.md", "scripts.md", "access-seo.md"]


def prompt(c, size="wide"):
    s = STATUS[[k for k, v in THEMES.items() if v is c][0]]
    CYCLE = 14
    wide = size == "wide"
    lines = PROMPT_WIDE if wide else PROMPT_NARROW
    lh, fs = (25, 15) if wide else (27, 14.5)
    W = 1280 if wide else 640
    ex, ey, ew = (64, 76, 1152) if wide else (40, 76, 560)
    body_top = ey + 106
    eh = 106 + len(lines) * lh + 24
    H = ey + eh + 40
    style = [BASE_STYLE]
    body = [f'<text class="mono" x="{ex}" y="52" font-size="13" letter-spacing="2" fill="{c["muted"]}">WHAT YOUR CODING AGENT GETS · prompts/scripts.md (excerpt)</text>' if wide else
            f'<text class="mono" x="{ex}" y="52" font-size="13" letter-spacing="2" fill="{c["muted"]}">WHAT YOUR CODING AGENT GETS</text>',
            f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" rx="12" fill="{s["card"]}" stroke="{s["line"]}"/>']
    # Window chrome and one tab per area prompt.
    for i in range(3):
        body.append(f'<circle cx="{ex + 22 + i * 18}" cy="{ey + 22}" r="5" fill="{c["faint"]}"/>')
    tabs = TABS if wide else ["all-in-one.md", "scripts.md", "media.md", "…"]
    tx = ex + 20
    for t in tabs:
        tw = len(t) * 8.2 + 26
        active = t == "scripts.md"
        body.append(f'<rect x="{tx}" y="{ey + 40}" width="{tw:.0f}" height="30" rx="7" fill="{c["lit"] if active else "none"}" stroke="{c["beam"] if active else s["line"]}"/>'
                    f'<text class="mono" x="{tx + tw / 2:.0f}" y="{ey + 60}" font-size="13" text-anchor="middle" font-weight="{700 if active else 400}" fill="{c["ink"] if active else c["muted"]}">{t}</text>')
        tx += tw + 8
    # Lines appear one after another, then the key lines get highlighted.
    n = len(lines)
    for i, (text, kind) in enumerate(lines):
        y = body_top + i * lh
        on = 3 + 50 * i / n
        style.append(reveal(f"p{i}", CYCLE, on, fade=1))
        color, weight = c["ink"], 400
        if kind == "h1":
            color, weight = c["ink"], 700
        elif kind in ("h2", "h3"):
            color, weight = c["beam"], 700
        mark = ""
        if kind.startswith("mark"):
            mon = 60 + (i % 4) * 2
            style.append(f"""
.m{i} {{ animation: m{i} {CYCLE}s linear infinite both; }}
@keyframes m{i} {{ 0%,{mon}% {{ opacity: 0; }} {mon + 3}%,95% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}""")
            note = kind.split(":", 1)[1] if ":" in kind else ""
            mark = (f'<g class="m{i}"><rect x="{ex + 14}" y="{y - lh + 7}" width="{ew - 28}" height="{lh}" rx="5" fill="{c["lit"]}"/>'
                    f'<rect x="{ex + 14}" y="{y - lh + 7}" width="3" height="{lh}" fill="{c["beam"]}"/>'
                    + (f'<text class="mono" x="{ex + ew - 28}" y="{y}" font-size="12.5" font-weight="700" text-anchor="end" fill="{c["beam"]}">← {note}</text>' if note and wide else "")
                    + "</g>")
        body.append(f'{mark}<g class="p{i}"><text class="mono" x="{ex + 28}" y="{y}" font-size="{fs}" font-weight="{weight}" fill="{color}" xml:space="preserve">{text}</text></g>')
    return svg(W, H, "A fix prompt written by lighthouse-fix",
               "Excerpt of the scripts prompt for Betabound: context that names INP as the real-visitor failure, guardrails that keep "
               "A/B tests and tracking working, and card F1 with the flagged file, preferred fix, what to avoid and a done-when check.",
               "".join(style), "\n".join(body), c)


if __name__ == "__main__":
    sk.write_all(OUT, {"report": report, "read": read, "prompt": prompt}, THEMES)
