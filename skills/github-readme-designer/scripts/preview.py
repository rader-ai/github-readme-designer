#!/usr/bin/env python3
"""Render a README (and optionally the old one) to a local, GitHub-styled HTML page.

usage: preview.py <repo-dir> [--readme README.md] [--before OLD.md] [--out before-after.html]
                  [--repo owner/name] [--no-api]

With `gh` logged in, Markdown is rendered by GitHub's own API (mode gfm), so the
preview shows exactly what GitHub's sanitizer keeps. Without it, a basic local
renderer is used and the page says so. Relative image paths are rewritten so
the page works from wherever it's saved.

With --before, the page shows before (left) and after (right) side by side,
with buttons for one at a time. Images follow the viewer's light/dark setting
and switch to narrow versions below 1012px window width (reload after resizing).
"""
import argparse
import html
import json
import os
import pathlib
import re
import subprocess
import sys

CSS = "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.8.1/github-markdown.min.css"


def repo_slug(repo: pathlib.Path):
    try:
        url = subprocess.run(["git", "-C", str(repo), "remote", "get-url", "origin"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return None
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
    return m.group(1) if m else None


def render_api(md: str, slug):
    payload = {"text": md, "mode": "gfm"}
    if slug:
        payload["context"] = slug
    try:
        r = subprocess.run(["gh", "api", "markdown", "--input", "-"], input=json.dumps(payload),
                           capture_output=True, text=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return r.stdout if r.returncode == 0 and r.stdout.strip() else None


def render_basic(md: str) -> str:
    """Minimal GFM-ish renderer for when GitHub's API isn't reachable. Raw HTML passes through."""
    out, para, lst, code = [], [], None, None

    def inline(s):
        s = re.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<em>\1</em>", s)
        s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1">', s)
        return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)

    def flush():
        nonlocal para, lst
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            lst = None

    for line in md.splitlines():
        if code is not None:
            if line.startswith("```"):
                out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                code = None
            else:
                code.append(line)
            continue
        if line.startswith("```"):
            flush()
            code = []
        elif re.match(r"#{1,6} ", line):
            flush()
            n = len(line) - len(line.lstrip("#"))
            out.append(f"<h{n}>{inline(line[n:].strip())}</h{n}>")
        elif re.match(r"\s*([-*]|\d+\.) ", line):
            if para:
                flush()
            tag = "ol" if re.match(r"\s*\d+\.", line) else "ul"
            if not lst or lst[0] != tag:
                flush()
                lst = (tag, [])
            lst[1].append(re.sub(r"^\s*([-*]|\d+\.) ", "", line))
        elif line.lstrip().startswith("<") or line.startswith(">") or line.startswith("|"):
            flush()
            out.append(line.lstrip("> ") if line.startswith(">") else line)
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out)


def rebase(fragment: str, prefix: str) -> str:
    """Point relative src/srcset/href at the repo folder, relative to the output page."""
    def fix(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"[a-z]+:|#|/", url):
            return m.group(0)
        return f'{attr}="{prefix}{url}"'
    return re.sub(r'(src|srcset|href)="([^"]+)"', fix, fragment)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--before")
    ap.add_argument("--out", default="before-after.html")
    ap.add_argument("--repo", dest="slug")
    ap.add_argument("--no-api", action="store_true")
    a = ap.parse_args()

    repo = pathlib.Path(a.repo).resolve()
    out = pathlib.Path(a.out).resolve()
    slug = a.slug or repo_slug(repo)
    prefix = os.path.relpath(repo, out.parent).replace(os.sep, "/") + "/"
    prefix = "" if prefix == "./" else prefix
    notes = []

    def render(md: str) -> str:
        body = None if a.no_api else render_api(md, slug)
        if body is None:
            if "basic renderer" not in " ".join(notes):
                notes.append("Rendered with a basic local renderer (GitHub's API wasn't reachable), so details may differ from github.com.")
            body = render_basic(md)
        return rebase(body, prefix)

    after = render((repo / a.readme).read_text(encoding="utf-8"))
    panes = [("after", "After", after)]
    if a.before:
        bp = pathlib.Path(a.before)
        if bp.exists() and bp.read_text(encoding="utf-8").strip():
            before = render(bp.read_text(encoding="utf-8"))
        else:
            before = '<p><em>This repository had no README.</em></p>'
        panes.insert(0, ("before", "Before", before))

    title = f"{slug or repo.name}: README {'before / after' if a.before else 'preview'}"
    cols = "".join(f'<section class="pane" data-pane="{k}"><div class="label">{lbl}</div>'
                   f'<div class="frame"><article class="markdown-body">{body}</article></div></section>'
                   for k, lbl, body in panes)
    buttons = ('<div class="modes"><button data-mode="both" aria-pressed="true">Side by side</button>'
               '<button data-mode="before">Before</button><button data-mode="after">After</button></div>') if a.before else ""
    note = "".join(f"<p class='note'>{html.escape(n)}</p>" for n in notes)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{CSS}">
<style>
:root {{ --bg:#f6f8fa; --panel:#ffffff; --line:#d1d9e0; --ink:#1f2328; --muted:#59636e; --accent:#0969da; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#010409; --panel:#0d1117; --line:#3d444d; --ink:#f0f6fc; --muted:#9198a1; --accent:#4493f8; }} }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }}
header {{ display:flex; flex-wrap:wrap; gap:12px; align-items:center; justify-content:space-between; padding:12px 16px; border-bottom:1px solid var(--line); }}
header h1 {{ font-size:15px; margin:0; }}
.note, .hint {{ margin:0; color:var(--muted); font-size:12px; }}
.modes button {{ font:inherit; padding:5px 12px; border:1px solid var(--line); background:var(--panel); color:var(--ink); border-radius:6px; cursor:pointer; }}
.modes button[aria-pressed="true"] {{ border-color:var(--accent); color:var(--accent); font-weight:600; }}
.modes button:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
main {{ display:grid; grid-template-columns:repeat({len(panes)}, minmax(0,1fr)); gap:16px; padding:16px; }}
main[data-mode="before"] [data-pane="after"], main[data-mode="after"] [data-pane="before"] {{ display:none; }}
main[data-mode="before"], main[data-mode="after"] {{ grid-template-columns:minmax(0,1fr); max-width:1012px; margin:0 auto; }}
.label {{ font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:12px; margin:0 0 8px; }}
.frame {{ background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:24px 16px; max-height:calc(100vh - 120px); overflow:auto; }}
.markdown-body {{ max-width:980px; margin:0 auto; background:transparent; }}
@media (max-width: 760px) {{ main {{ grid-template-columns:minmax(0,1fr); }} .frame {{ max-height:none; }} }}
</style></head>
<body>
<header><div><h1>{html.escape(title)}</h1><p class="hint">Images follow your light/dark setting and switch to phone versions below 1012px window width (reload after resizing).</p>{note}</div>{buttons}</header>
<main data-mode="both">{cols}</main>
<script>
document.querySelectorAll('.modes button').forEach(b => b.addEventListener('click', () => {{
  document.querySelector('main').dataset.mode = b.dataset.mode;
  document.querySelectorAll('.modes button').forEach(x => x.setAttribute('aria-pressed', x === b));
}}));
</script>
</body></html>
"""
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out}" + (f"  ({notes[0]})" if notes else "  (rendered by GitHub's Markdown API)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
