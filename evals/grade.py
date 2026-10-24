"""Grade the scriptable assertions for each run; leaves judgment ones for a reviewer.

usage: python3 grade.py <iteration-dir>
Writes <run>/grading.json with expectations [{text, passed, evidence}]; judgment
assertions are written with passed=None and must be filled in afterwards.
"""
import json
import pathlib
import re
import subprocess
import sys

IT = pathlib.Path(sys.argv[1])
REPOS = {"inp-fix-from-scratch": "inp-fix", "lasso-voice-skill": "lasso", "glyphmotion-redesign": "Glyphmotion"}
BASE = {l.split(":")[0]: l.strip() for l in (IT / "remote-baseline.txt").read_text().splitlines()}


def remote_state(repo):
    b = subprocess.run(["gh", "api", f"repos/rader-ai/{repo}/branches", "--jq", 'map(.name+"@"+.commit.sha[:7])|join(",")'],
                       capture_output=True, text=True).stdout.strip()
    s = subprocess.run(["gh", "api", f"repos/rader-ai/{repo}", "--jq", ".size"], capture_output=True, text=True).stdout.strip()
    p = subprocess.run(["gh", "pr", "list", "-R", f"rader-ai/{repo}", "--state", "all", "--json", "number", "--jq", "length"],
                       capture_output=True, text=True).stdout.strip()
    return f"{repo}: {b} size={s} prs={p}"


def find_readme(out):
    cands = [p for p in out.rglob("README.md") if ".git/" not in str(p) and "node_modules" not in str(p)]
    cands.sort(key=lambda p: (len(p.relative_to(out).parts), -p.stat().st_mtime))
    return cands[0] if cands else None


def original_readme(repo):
    r = subprocess.run(["gh", "api", f"repos/rader-ai/{repo}/readme", "-H", "Accept: application/vnd.github.raw"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def grade(case, run):
    out = run / "outputs"
    repo = REPOS[case]
    rd = find_readme(out)
    exp = []

    def add(text, passed, evidence):
        exp.append({"text": text, "passed": passed, "evidence": evidence})

    meta = json.loads((IT / case / "eval_metadata.json").read_text())
    A = meta["assertions"]
    md = rd.read_text(encoding="utf-8", errors="replace") if rd else ""
    live = re.sub(r"```.*?```", "", md, flags=re.S)
    root = rd.parent if rd else out
    refs = set(re.findall(r'(?:src|srcset)="([^"]+)"', live)) | set(re.findall(r"!\[[^\]]*\]\(([^)\s]+)", live))
    local = sorted(r for r in refs if not re.match(r"[a-z]+:", r) and not r.startswith("#"))
    svgs = [root / r for r in local if r.lower().endswith(".svg") and (root / r).exists()]
    pics = re.findall(r"<picture>.*?</picture>", live, re.S | re.I)

    for a in A:
        key = a[:40]
        if a.startswith("The new README.md contains no inline"):
            bad = re.findall(r"<svg\b|<style\b|<script\b|\sstyle\s*=", live, re.I)
            add(a, bool(md) and not bad, f"README at {rd.relative_to(out) if rd else 'none'}; stripped constructs found: {bad[:5]}")
        elif a.startswith("Every image the new README.md references exists"):
            missing = [r for r in local if not (root / r.split('#')[0]).exists()]
            ext = [str(p.name) for p in svgs if re.search(r'<script|@import|url\(\s*[\'"]?(https?:|//)|href="(?!#|data:)[^"]+"', p.read_text(errors="replace"))]
            add(a, bool(local) and not missing and not ext, f"{len(local)} local refs; missing={missing[:4]}; external/script SVGs={ext[:4]}")
        elif a.startswith("Every <picture>/image visual"):
            # Judge the new SVG visuals; existing GIFs and badges don't need theme variants.
            svg_imgs = re.findall(r'<img\b[^>]*src="(?![a-z]+:)([^"]+\.svg)"', live)
            in_dark = [m for b in pics if "prefers-color-scheme: dark" in b or "prefers-color-scheme:dark" in b
                       for m in re.findall(r'<img\b[^>]*src="([^"]+\.svg)"', b)]
            bare = [x for x in svg_imgs if x not in in_dark]
            add(a, bool(svg_imgs) and not bare, f"{len(svg_imgs)} SVG images, {len(in_dark)} inside a dark-aware <picture>; without: {bare[:3]}")
        elif a.startswith("Every <picture> visual in the new README.md has a phone"):
            narrow = sum("max-width" in p for p in pics)
            add(a, len(pics) > 0 and narrow == len(pics), f"{narrow} of {len(pics)} <picture> blocks have a max-width source")
        elif a.startswith("At least one referenced SVG animates"):
            anim = [p.name for p in svgs if re.search(r"@keyframes|<animate", p.read_text(errors="replace"))]
            loops = [n for n in anim if re.search(r"infinite|repeatCount=\"indefinite\"", (root / next(r for r in local if r.endswith(n))).read_text(errors="replace"))]
            add(a, bool(loops), f"{len(anim)} animated SVGs, {len(loops)} loop")
        elif a.startswith("Every animated SVG the new README.md references includes"):
            anim = [p for p in svgs if re.search(r"@keyframes|<animate", p.read_text(errors="replace"))]
            miss = [p.name for p in anim if "prefers-reduced-motion" not in p.read_text(errors="replace")]
            add(a, bool(anim) and not miss, f"{len(anim)} animated SVGs; without reduced-motion: {miss[:4]}")
        elif a.startswith("Every image in the new README.md has alt text"):
            alts = re.findall(r'<img\b[^>]*?alt="([^"]*)"', live) + re.findall(r"!\[([^\]]*)\]", live)
            imgs = len(re.findall(r"<img\b|!\[", live))
            short = [x for x in alts if len(x.strip()) < 8]
            add(a, imgs > 0 and len(alts) == imgs and not short, f"{imgs} images, {len(alts)} with alt, {len(short)} too short")
        elif a.startswith("An HTML file in the outputs shows the original"):
            orig = original_readme(repo)
            probe_old = [s.strip() for s in re.split(r"[.\n]", orig) if len(s.strip()) > 40][:6]
            text_only = re.sub(r"<[^>]*>", " ", re.sub(r"```.*?```", " ", md, flags=re.S), flags=re.S)
            probe_new = [s.strip() for s in re.split(r"[.\n]", text_only) if len(s.strip()) > 40 and "](" not in s][:6]
            hits = []
            for h in out.rglob("*.html"):
                if ".git/" in str(h):
                    continue
                t = re.sub(r"<[^>]+>", " ", h.read_text(errors="replace"))
                t = re.sub(r"\s+", " ", t)
                old_ok = (not orig and re.search(r"no README|had no README|didn.t have a README|no existing README", t, re.I)) or \
                    sum(p[:30] in t for p in probe_old) >= 2
                new_ok = sum(re.sub(r"[*`_\[\]]", "", p)[:30] in t for p in probe_new) >= 2
                if old_ok and new_ok:
                    hits.append(str(h.relative_to(out)))
            add(a, bool(hits), f"before/after pages: {hits[:3] or 'none found'}")
        elif a.startswith("Nothing was pushed"):
            now = remote_state(repo)
            add(a, now == BASE[repo], f"before: {BASE[repo]} | now: {now}")
        elif a.startswith("At least half of the original README's longer sentences"):
            orig = original_readme(repo)
            sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", orig) if len(s.strip()) >= 40 and not s.strip().startswith(("|", "<", "#", "-", "`"))]
            flat = re.sub(r"\s+", " ", md)
            kept = [s for s in sents if s in flat]
            add(a, bool(sents) and len(kept) >= len(sents) / 2, f"{len(kept)} of {len(sents)} original sentences kept verbatim")
        else:
            add(a, None, "needs reviewer judgment")
    (run / "grading.json").write_text(json.dumps({"expectations": exp}, indent=2))
    done = [e for e in exp if e["passed"] is not None]
    print(f"{case}/{run.name}: {sum(e['passed'] for e in done)}/{len(done)} scripted pass, {len(exp) - len(done)} for review")


for case in REPOS:
    for run in sorted((IT / case).iterdir()):
        if run.is_dir() and (run / "outputs").exists():
            grade(case, run)
