# What GitHub renders in a README

Checked October 2026 against GitHub's Markdown API and live github.com. Where something is unverified it says so.

## Stripped from README HTML

- Inline `<svg>`, `<style>`, `<script>`, and the `style=""` attribute: all removed. So no CSS in the README itself, and every visual must be an image file.
- `<video src="repo-file.mp4">` is removed. Video only plays from a `https://github.com/user-attachments/assets/…` URL, which you get by uploading through the GitHub web editor (no public API). GIF is the fallback.
- `class` and `id` are removed or prefixed; you can't target anything with CSS.

## Kept

`p`, `div` with `align`; `picture`, `source` (`media`, `srcset`), `img` (`src`, `alt`, `width`, `height`, `align`); `details`, `summary`; `table` and its parts; `sub`, `sup`, `kbd`, `br`, `b`, `i`, `em`, `strong`, `code`, `pre`, `a`, `hr`. Markdown callouts `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`. Mermaid code blocks render, but they're static and only on github.com.

## SVG loaded as an image

The browser runs it in "secure animated mode":

- **Works:** CSS `@keyframes` and transitions inside a `<style>` element in the SVG; SMIL (`<animate>`, `<animateTransform>`); gradients, clip paths, masks, filters; `transform-box` / `transform-origin`; `foreignObject` with inline HTML/CSS.
- **Doesn't:** JavaScript, any external reference (web fonts, `@import`, external images, `<use href="other.svg">`), hover/click interaction.
- **Fonts:** a `font-family` stack uses fonts already installed on the viewer's machine. To guarantee a face, embed a subset as base64 `@font-face` (adds 15-60 KB per weight) or convert the text to paths. Default: system stacks. Pick stacks that degrade gracefully, e.g. `'Iowan Old Style','Charter','Palatino Linotype',Georgia,serif` and `ui-monospace,'SF Mono',Menlo,Consolas,monospace`, and leave ~10% slack in text widths because metrics differ between platforms.
- The SVG is XML: escape `&` as `&amp;` and `<` as `&lt;` in text and CSS.
- Give it `role="img"` plus `<title>` and `<desc>`; the README `alt` is what screen readers on GitHub actually use, so write that well too.

## Light/dark and narrow/wide

Use `<picture>`. The first `<source>` whose `media` matches wins, so order from most to least specific:

```html
<picture>
  <source media="(max-width: 1011px) and (prefers-color-scheme: dark)" srcset=".github/assets/x-narrow-dark.svg">
  <source media="(max-width: 1011px)" srcset=".github/assets/x-narrow-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/x-dark.svg">
  <img src=".github/assets/x-light.svg" alt="…" width="100%">
</picture>
```

- `max-width` is the **viewport**, not the README column. Under 1012px GitHub's README column is narrow (the sidebar takes room until ~768px), so 1011px is the useful breakpoint for switching to 640px-wide designs.
- `prefers-color-scheme` follows the viewer's GitHub theme on github.com. A media query *inside* the SVG is less reliable (Safari didn't follow it for image SVGs in 2025-26), so ship separate files rather than one SVG that themes itself.
- The `#gh-dark-mode-only` / `#gh-light-mode-only` URL fragments are legacy; non-GitHub renderers (npm, IDEs) show both images. Use `<picture>`.
- Browsers pick the source at load; resizing a window doesn't always swap it. Reload when testing.
- **Unverified:** whether the GitHub mobile apps report dark mode to images, and whether `prefers-reduced-motion` is honoured inside image SVGs (include it anyway).

## Sizes and hosting

- Commit assets to the repo (convention: `.github/assets/`) and reference them by relative path. They work in private repos for anyone with access, have no uptime or rate-limit risk, and aren't cached by Camo.
- External images go through GitHub's Camo proxy (5 MB cap, cached, no auth). Avoid live badge or stats services for anything important.
- Uploaded images/GIFs cap at 10 MB. Keep SVGs small: a well-built one is 5-20 KB; worry above ~100 KB.
- `width="100%"` on `img` scales the image to the column; GitHub also caps images at `max-width: 100%`.
