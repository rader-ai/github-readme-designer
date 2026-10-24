#!/usr/bin/env python3
"""Find text that spills outside its SVG, across the animation loop, using headless Chrome.

usage: check_bounds.py <svg-file-or-folder> [...] [--pad 2] [--all]

Each SVG is inlined into a page; its animations are paused at eight points in
the loop and then switched off (the finished frame, which reduced-motion viewers
see). At each point every visible <text> element's box is compared with the
image's edges, or with its clip region if it sits in a clip-path (where only
words cut mid-way count). --all checks every shape, not just text (expect hits
from deliberate full-bleed textures). Exit 1 if anything spills.

Needs Google Chrome or Chromium. Set CHROME=/path/to/chrome if it isn't found.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
]

PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>body{{margin:0}}</style></head>
<body>{svg}<pre id="out"></pre>
<script>
const svg = document.querySelector('svg'), pad = {pad}, all = {all};
const box = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
const sx = box.width / (vb && vb.width ? vb.width : box.width), sy = box.height / (vb && vb.height ? vb.height : box.height);
const sel = all ? 'text,rect,circle,ellipse,line,polyline,polygon,path,image' : 'text';
const hits = new Map();
function scan(when) {{
  for (const el of svg.querySelectorAll(sel)) {{
    if (el.closest('defs,clipPath,mask,symbol')) continue;
    let op = 1, n = el;
    while (n && n !== svg) {{ const cs = getComputedStyle(n); op *= parseFloat(cs.opacity); if (cs.display === 'none' || cs.visibility === 'hidden') op = 0; n = n.parentElement; }}
    if (op < 0.3) continue;
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    // Clipped content (tickers, drifting strips) is judged against its clip region instead of the image edge.
    let edge = box; const clipped = el.closest('[clip-path]');
    if (clipped) {{ const cr = clipped.getBoundingClientRect(); edge = {{ left: Math.max(box.left, cr.left), right: Math.min(box.right, cr.right), top: Math.max(box.top, cr.top), bottom: Math.min(box.bottom, cr.bottom) }}; }}
    const over = {{ left: (edge.left - r.left) / sx, right: (r.right - edge.right) / sx, top: (edge.top - r.top) / sy, bottom: (r.bottom - edge.bottom) / sy }};
    let sides = Object.entries(over).filter(([, v]) => v > pad);
    if (clipped) {{
      // Fully hidden content (a ticker's off-screen rows) is fine; so is a vertical cut (rows scrolling past).
      // A line that is visible but cut on its left or right side is worth a look.
      const visible = r.right > edge.left && r.left < edge.right && r.bottom > edge.top && r.top < edge.bottom;
      sides = visible ? sides.filter(([k]) => k === 'left' || k === 'right') : [];
    }}
    if (!sides.length) continue;
    const key = el.tagName + '|' + (el.textContent || '').trim().slice(0, 40);
    const prev = hits.get(key) || {{ tag: el.tagName, text: (el.textContent || '').trim().slice(0, 40), over: '', when: [], clipped: !!clipped }};
    if (!prev.when.includes(when)) prev.when.push(when);
    const worst = sides.map(([k, v]) => k + ' ' + v.toFixed(0) + 'px').join(', ');
    if (worst.length > prev.over.length) prev.over = worst;
    hits.set(key, prev);
  }}
}}
const anims = document.getAnimations();
const dur = Math.max(0, ...anims.map(a => a.effect.getComputedTiming().duration || 0));
if (dur) for (let i = 0; i < 8; i++) {{ const f = 0.05 + i * 0.125; anims.forEach(a => {{ a.pause(); a.currentTime = dur * f; }}); scan(Math.round(f * 100) + '%'); }}
const st = document.createElement('style'); st.textContent = '*{{animation:none!important}}'; document.head.appendChild(st);
scan('finished');
document.getElementById('out').textContent = 'BOUNDS' + JSON.stringify([...hits.values()]) + 'END';
</script></body></html>"""


def find_chrome():
    env = os.environ.get("CHROME")
    if env:
        return env
    for c in CANDIDATES:
        p = c if os.path.isabs(c) else shutil.which(c)
        if p and os.path.exists(p):
            return p
    return None


def check(chrome, svg_path, pad, all_shapes):
    text = svg_path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"<\?xml[^>]*\?>", "", text)
    if re.search(r"<!DOCTYPE|<!ENTITY", text, re.I):
        return None, "has a DOCTYPE/ENTITY declaration; remove it"
    with tempfile.TemporaryDirectory() as tmp:
        page = pathlib.Path(tmp) / "page.html"
        page.write_text(PAGE.format(svg=text, pad=pad, all="true" if all_shapes else "false"), encoding="utf-8")
        r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                            f"--user-data-dir={tmp}/profile", "--virtual-time-budget=3000", "--dump-dom", page.as_uri()],
                           capture_output=True, text=True, timeout=90)
    m = re.search(r"BOUNDS(.*?)END", r.stdout, re.S)
    if not m:
        return None, "Chrome produced no result: " + (r.stderr.strip().splitlines() or ["unknown error"])[-1][:120]
    return json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--pad", type=float, default=2, help="pixels of overflow to tolerate")
    ap.add_argument("--all", action="store_true", help="check every shape, not just text")
    a = ap.parse_args()
    chrome = find_chrome()
    if not chrome:
        print("Chrome/Chromium not found (set CHROME=...). Check narrow variants by eye instead.")
        return 2
    files = []
    for p in map(pathlib.Path, a.paths):
        files += sorted(p.rglob("*.svg")) if p.is_dir() else [p]
    bad = warned = 0
    for f in files:
        hits, err = check(chrome, f, a.pad, a.all)
        if err:
            print(f"?  {f.name}: {err}")
            continue
        errs = [h for h in hits if not h["clipped"]]
        if hits:
            if errs:
                bad += 1
            else:
                warned += 1
            print(f"{'✗' if errs else '!'}  {f.name}" + ("" if errs else "  (clipped lines cut at the side: intended?)"))
            for h in hits[:8]:
                where = "finished frame" if h["when"] == ["finished"] else "at " + ", ".join(h["when"][:5]) + " of the loop"
                print(f"     <{h['tag']}> {h['text']!r} spills {h['over']} {'past its clip ' if h['clipped'] else ''}({where})")
            if len(hits) > 8:
                print(f"     …and {len(hits) - 8} more")
        else:
            print(f"✓  {f.name}")
    print(f"\n{bad} of {len(files)} SVGs have text past the edge; {warned} more have clipped lines cut at the side to check by eye")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
