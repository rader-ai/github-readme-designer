"""svgkit: small helpers for building animated, GitHub-safe README SVGs.

Import it from a per-repo build script:

    import sys; sys.path.insert(0, "<skill>/scripts")
    import svgkit as sk

    THEMES = {"light": {...tokens...}, "dark": {...tokens...}}

    def hero(t, size):            # t = theme tokens, size = "wide" | "narrow"
        W, H = (1280, 440) if size == "wide" else (640, 760)
        css, body = [], []
        ...
        return sk.svg_doc(W, H, "Title", "What it shows", "".join(css), "".join(body), bg=t["bg"])

    sk.write_all(".github/assets", {"hero": hero}, THEMES)
    print(sk.picture("hero", "Alt text that says what the image shows"))

Every document gets <title>/<desc>, role="img", and a prefers-reduced-motion
rule. Write elements in their FINISHED state and let animations describe how
they get there, so reduced motion and non-animating viewers see a complete
picture. No dependencies beyond the standard library.
"""
from __future__ import annotations

import pathlib
import re
from xml.sax.saxutils import escape

MONO = "ui-monospace,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
SERIF = "'Iowan Old Style','Charter','Palatino Linotype',Georgia,serif"
SANS = "system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"

# Average advance width per font-size unit, with slack for platform differences.
_ADVANCE = {"mono": 0.62, "serif": 0.52, "sans": 0.55}

SIZES = {"wide": "", "narrow": "-narrow"}  # file suffix per layout


def esc(text) -> str:
    """Escape text for SVG/XML content and attributes."""
    return escape(str(text), {'"': "&quot;"})


def text_width(text: str, size: float, family: str = "mono", letter_spacing: float = 0) -> float:
    """Approximate rendered width in px. Good enough to catch overflow; leave ~10% slack."""
    return len(text) * (size * _ADVANCE[family] + letter_spacing)


def fit(text: str, size: float, max_width: float, family: str = "mono") -> str:
    """Return text, truncated at a word boundary with an ellipsis, so it fits max_width."""
    if text_width(text, size, family) <= max_width:
        return text
    while text and text_width(text + "…", size, family) > max_width:
        cut = text.rsplit(" ", 1)[0]
        text = cut if cut != text else text[:-1]
    return text.rstrip(" ,.;:") + "…"


def wrap(text: str, size: float, max_width: float, family: str = "mono") -> list[str]:
    """Greedy word wrap into lines that fit max_width."""
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and text_width(trial, size, family) > max_width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + ([line] if line else [])


def svg_doc(w: int, h: int, title: str, desc: str, style: str, body: str,
            bg: str | None = None, rx: int = 18) -> str:
    """Wrap a body in a complete, self-contained SVG document."""
    back = f'<rect width="{w}" height="{h}" rx="{rx}" fill="{bg}"/>\n' if bg else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
<title id="t">{esc(title)}</title>
<desc id="d">{esc(desc)}</desc>
<style>
.mono {{ font-family: {MONO}; }}
.serif {{ font-family: {SERIF}; }}
.sans {{ font-family: {SANS}; }}
{style}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
{back}{body}
</svg>
"""


# ---------- animation helpers: each returns CSS for one class ----------

def _end(off: float, reset: str) -> str:
    """The closing frame: hold to off% then reset by 100%, or just hold if off is 100."""
    return "" if off >= 100 else f" 100% {{ {reset} }}"


def _anim(cls: str, cycle: float, frames: str, timing: str = "linear") -> str:
    return (f"\n.{cls} {{ animation: {cls} {cycle}s {timing} infinite both; }}"
            f"\n@keyframes {cls} {{ {frames} }}")


def reveal(cls: str, cycle: float, on: float, off: float = 95, fade: float = 1.5) -> str:
    """Fade in at on%, stay until off%, fade out by 100%. Visible by default."""
    return _anim(cls, cycle, f"0%,{on:.1f}% {{ opacity: 0; }} {on + fade:.1f}%,{min(off, 100)}% {{ opacity: 1; }}" + _end(off, "opacity: 0;"))


def draw(cls: str, cycle: float, length: float, start: float, end: float, off: float = 95,
         timing: str = "cubic-bezier(.2,.7,.2,1)") -> str:
    """Draw a stroke from nothing to full between start% and end%. Set stroke-dasharray via this CSS."""
    return (f"\n.{cls} {{ stroke-dasharray: {length:.1f}; }}"
            + _anim(cls, cycle, f"0%,{start:.1f}% {{ stroke-dashoffset: {length:.1f}; }} "
                                f"{end:.1f}%,{min(off, 100)}% {{ stroke-dashoffset: 0; }}" + _end(off, f"stroke-dashoffset: {length:.1f};"), timing))


def slide(cls: str, cycle: float, dist: float, start: float, end: float, axis: str = "X",
          timing: str = "cubic-bezier(.2,.7,.2,1)") -> str:
    """Move from -dist to the element's own position between start% and end%."""
    return _anim(cls, cycle, f"0%,{start:.1f}% {{ transform: translate{axis}({-dist:.1f}px); }} "
                             f"{end:.1f}%,100% {{ transform: translate{axis}(0); }}", timing)


def grow(cls: str, cycle: float, start: float, end: float, off: float = 95, origin: str = "left center",
         timing: str = "cubic-bezier(.2,.7,.2,1)") -> str:
    """Scale a bar from 0 to full width between start% and end%."""
    return (f"\n.{cls} {{ transform-box: fill-box; transform-origin: {origin}; }}"
            + _anim(cls, cycle, f"0%,{start:.1f}% {{ transform: scaleX(0); }} {end:.1f}%,{min(off, 100)}% {{ transform: scaleX(1); }}"
                                + _end(off, "transform: scaleX(0);"), timing))


def loop_fade(cls: str, cycle: float, in_end: float = 2, hold: float = 88, out: float = 96) -> str:
    """Fade a whole group in at the start of the cycle and out before it restarts."""
    return _anim(cls, cycle, f"0% {{ opacity: 0; }} {in_end}% {{ opacity: 1; }} {hold}% {{ opacity: 1; }} {out}%,100% {{ opacity: 0; }}")


def count_up(prefix: str, cycle: float, values: list, start: float, end: float,
             x: float, y: float, attrs: str = "", unit: str = "") -> tuple[str, str]:
    """Show values one after another between start% and end%, ending on the last.

    Returns (css, svg). Only the final value is visible by default. Pass 5-7
    values, not every integer. Put the svg in the same group as anything that
    moves with the number.
    """
    css, out, n = [], [], len(values)
    # Merge any class passed in attrs with the per-value class, so the element has one class attribute.
    m = re.search(r'class="([^"]*)"', attrs)
    extra, rest = (" " + m.group(1), attrs.replace(m.group(0), "").strip()) if m else ("", attrs)
    for i, v in enumerate(values):
        on = start + (end - start) * i / n
        cls = f"{prefix}{i}"
        if i == n - 1:
            frames = f"0%,{on:.1f}% {{ opacity: 0; }} {on + .1:.1f}%,100% {{ opacity: 1; }}"
        else:
            off = start + (end - start) * (i + 1) / n
            frames = f"0%,{on:.1f}% {{ opacity: 0; }} {on + .1:.1f}%,{off:.1f}% {{ opacity: 1; }} {off + .1:.1f}%,100% {{ opacity: 0; }}"
        css.append(_anim(cls, cycle, frames))
        out.append(f'<text class="{cls}{extra}" x="{x:.1f}" y="{y:.1f}" {rest} opacity="{1 if i == n - 1 else 0}">{esc(v)}{esc(unit)}</text>')
    return "".join(css), "".join(out)


def steps(a: float, b: float, n: int = 6) -> list:
    """Evenly spaced values from a to b (inclusive of b, exclusive of a), deduplicated, as ints when whole."""
    whole = float(a).is_integer() and float(b).is_integer()
    if whole:
        n = max(1, min(n, int(abs(b - a))))
    vals = []
    for i in range(1, n + 1):
        v = a + (b - a) * i / n
        v = int(round(v)) if whole else round(v, 2)
        if v not in vals:
            vals.append(v)
    return vals


# ---------- README output ----------

def picture(name: str, alt: str, assets: str = ".github/assets", width: str = "100%",
            narrow: bool = True, breakpoint: int = 1011) -> str:
    """A <picture> block choosing narrow/wide and dark/light variants, most specific first."""
    lines = ["<picture>"]
    if narrow:
        lines += [f'  <source media="(max-width: {breakpoint}px) and (prefers-color-scheme: dark)" srcset="{assets}/{name}-narrow-dark.svg">',
                  f'  <source media="(max-width: {breakpoint}px)" srcset="{assets}/{name}-narrow-light.svg">']
    lines += [f'  <source media="(prefers-color-scheme: dark)" srcset="{assets}/{name}-dark.svg">',
              f'  <img src="{assets}/{name}-light.svg" alt="{esc(alt)}" width="{width}">',
              "</picture>"]
    return "\n".join(lines)


def write_all(out_dir, visuals: dict, themes: dict, sizes=("wide", "narrow")) -> list[pathlib.Path]:
    """Call fn(theme_tokens, size) for every visual, theme and size; write <name><suffix>-<theme>.svg."""
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, fn in visuals.items():
        for theme, tokens in themes.items():
            for size in sizes:
                p = out / f"{name}{SIZES[size]}-{theme}.svg"
                p.write_text(fn(tokens, size), encoding="utf-8")
                written.append(p)
                print(f"{p}  {p.stat().st_size / 1024:.1f} KB")
    return written
