#!/usr/bin/env python3
"""Check a redesigned README and its SVG assets against what GitHub will render.

usage: lint_readme.py <repo-dir> [--readme README.md]

Errors (exit 1): things GitHub strips or that break the page: inline <svg>/<style>/
<script>/style="", missing image files, SVGs that load external resources or run
scripts, invalid XML, missing alt text.
Warnings: missing dark or narrow variants, missing reduced-motion rule, large files,
hard <br> inside paragraphs, badge walls.
"""
import argparse
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

KB = 1024


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--readme", default="README.md")
    args = ap.parse_args()
    repo = pathlib.Path(args.repo)
    readme = repo / args.readme
    errors, warns = [], []
    if not readme.exists():
        print(f"ERROR: {readme} not found")
        return 1
    md = readme.read_text(encoding="utf-8")
    # Ignore fenced code: examples there aren't rendered as HTML.
    live = re.sub(r"```.*?```", "", md, flags=re.S)

    for pat, why in [(r"<svg\b", "inline <svg> is stripped by GitHub; use an image file"),
                     (r"<style\b", "<style> is stripped by GitHub"),
                     (r"<script\b", "<script> is stripped by GitHub"),
                     (r"\sstyle\s*=", 'style="" attributes are stripped by GitHub'),
                     (r"<video\b[^>]*src=\"(?!https://github.com/user-attachments)", "<video> only plays user-attachments URLs")]:
        for m in re.finditer(pat, live, re.I):
            errors.append(f"README line {live[:m.start()].count(chr(10)) + 1}: {why}")

    # Images and their alt text.
    for m in re.finditer(r"<img\b[^>]*>", live, re.I):
        tag = m.group(0)
        alt = re.search(r'alt="([^"]*)"', tag)
        if not alt or len(alt.group(1).strip()) < 8:
            errors.append(f"README: image without useful alt text: {tag[:90]}")
    for m in re.finditer(r"!\[([^\]]*)\]\(([^)\s]+)", live):
        if len(m.group(1).strip()) < 8:
            warns.append(f"README: markdown image with thin alt text: {m.group(0)[:80]}")

    refs = set(re.findall(r'(?:src|srcset)="([^"]+)"', live)) | set(re.findall(r"!\[[^\]]*\]\(([^)\s]+)", live))
    local = sorted(r for r in refs if not re.match(r"[a-z]+:", r) and not r.startswith("#"))
    for r in local:
        if not (repo / r.split("#")[0]).exists():
            errors.append(f"README references missing file: {r}")

    # Picture blocks: theme and width coverage.
    for block in re.findall(r"<picture>.*?</picture>", live, re.S | re.I):
        img = re.search(r'<img[^>]*src="([^"]+)"', block)
        name = img.group(1) if img else "?"
        if "prefers-color-scheme: dark" not in block:
            warns.append(f"{name}: no dark-mode source")
        if "max-width" not in block:
            warns.append(f"{name}: no narrow (phone) source")
        srcs = re.findall(r'srcset="([^"]+)"', block)
        if img and img.group(1) in srcs:
            warns.append(f"{name}: a <source> repeats the fallback image (no-op variant)")

    for m in re.finditer(r"<p\b[^>]*>(.*?)</p>", live, re.S | re.I):
        inner = m.group(1)
        if re.search(r"\w[^<>]*<br\s*/?>\s*\n?\s*\w", inner) and "<img" not in inner and "<a " not in inner:
            warns.append("README: hard <br> inside a paragraph wraps badly on phones")
    badges = len(re.findall(r"shields\.io|badge", live, re.I))
    if badges > 5:
        warns.append(f"README: {badges} badges; keep it to 3-5 at most")

    # SVG assets referenced by the README.
    for r in local:
        p = repo / r.split("#")[0]
        if p.suffix.lower() != ".svg" or not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        size = p.stat().st_size
        if re.search(r"<!DOCTYPE|<!ENTITY", text, re.I):
            # Not needed in a README SVG, and refusing them keeps the parser below safe from entity tricks.
            errors.append(f"{r}: has a DOCTYPE/ENTITY declaration; remove it")
            continue
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            errors.append(f"{r}: invalid XML ({e})")
            continue
        if re.search(r"<script\b|\bon[a-z]+\s*=", text, re.I):
            errors.append(f"{r}: contains script or event handlers (won't run, may be blocked)")
        for m in re.finditer(r'(?:xlink:)?href\s*=\s*"([^"]+)"', text):
            if not m.group(1).startswith("#") and not m.group(1).startswith("data:"):
                errors.append(f"{r}: external reference {m.group(1)[:60]} (blocked in image SVGs)")
        if re.search(r"@import|url\(\s*['\"]?(?:https?:|//)", text):
            errors.append(f"{r}: loads an external stylesheet or font (blocked in image SVGs)")
        if not any(el.tag.endswith("title") for el in root.iter()):
            warns.append(f"{r}: no <title>")
        if re.search(r"@keyframes|<animate", text) and "prefers-reduced-motion" not in text:
            warns.append(f"{r}: animates but has no prefers-reduced-motion rule")
        if size > 1024 * KB:
            errors.append(f"{r}: {size / KB:.0f} KB is too large")
        elif size > 100 * KB:
            warns.append(f"{r}: {size / KB:.0f} KB; aim for under 100 KB")
        if "viewBox" not in text:
            warns.append(f"{r}: no viewBox, so it won't scale cleanly")

    for e in errors:
        print("ERROR:", e)
    for w in warns:
        print("warn: ", w)
    svgs = [r for r in local if r.endswith(".svg")]
    print(f"\n{len(errors)} errors, {len(warns)} warnings · {len(svgs)} SVGs referenced")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
