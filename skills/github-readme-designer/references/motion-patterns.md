# Motion patterns for README SVGs

All of these are CSS keyframes inside the SVG's `<style>`, with helpers in `scripts/svgkit.py`. Percentages are positions in one loop cycle.

## Principles (learned the hard way)

1. **The finished frame is the default.** Write the element's attributes in its final state (lit, full length, visible). Animations describe the journey from an earlier state, with `animation-fill-mode: both`. Then reduced-motion viewers, static screenshots and any viewer that doesn't animate all see a complete picture.
2. **Loop everything a reader might scroll to.** A one-shot animation on page load is over before anyone scrolls to it. Data visuals loop: animate in over ~15-25% of the cycle, **hold** for most of it (people need time to read), fade out over ~8%, reset invisibly, repeat.
3. **Hold longer than you animate.** A 9-14 s cycle with 60-70% hold reads as calm. Short, busy loops read as noise.
4. **One timeline per scene.** When one thing causes another (a beam passing a row lights the row; a marker reaching a station fills it), compute both from the same cycle and percentages and use `linear` timing on the driver. Easing the driver but not the followers makes them drift apart.
5. **One signature, quiet everywhere else.** The hero carries the boldest motion. Other visuals use reveal, draw-in and count-up. Don't animate decoration (backgrounds, textures).
6. **Stagger, don't synchronise.** Lists and rows come in 3-6% of the cycle apart.
7. **Fade with opacity, move with transform.** Both are cheap. Avoid animating layout attributes.

## Recipes

**Loop reveal**: visible from `on%` to `off%`:
```css
.x { animation: x 12s linear infinite both; }
@keyframes x { 0%,20% { opacity: 0 } 21.5%,95% { opacity: 1 } 100% { opacity: 0 } }
```
`svgkit.reveal(cls, cycle, on, off)`.

**Draw a line** (bars, strike-throughs, connectors): `stroke-dasharray: L; stroke-dashoffset` from `L` to `0`. `svgkit.draw(cls, cycle, length, start, end)`.

**Slide a dot / grow a bar**: `transform: translateX(-d)` → `0`, or `scaleX(0)` → `1` with `transform-box: fill-box; transform-origin: left center`. `svgkit.slide()` / `svgkit.grow()`.

**Count up**: stack one `<text>` per intermediate value (5-7 steps, not every integer). Each is visible for its slice of the travel; only the final value is visible by default. Put the texts in the same group as the moving dot so the number rides along. `svgkit.count_up()`.

**Sweep** (beam, scanner, radar): rotate a wedge around a pivot with `transform-box: view-box; transform-origin: Xpx Ypx`. Compute the angles to the first and last target with `atan2` (plus a few degrees of margin) rather than guessing. Light each target at `start + (end-start) * (i + 0.5) / n`.

**Ticker** (a long list scrolling past): duplicate the list, clip it with a `clipPath`, translate by exactly one list height, `linear infinite`; add a gradient fade at the bottom edge.

**Typed lines** (prompts, terminals, files): reveal one line at a time across ~50% of the cycle, then highlight key lines (a tinted rect + accent bar + a short `← note`) a little later, hold, reset.

**Ring / gauge**: `stroke-dasharray: C` and offset `C * (1 - value)`, rotated -90° around the centre.

**Travelling marker** (flows): translate along the axis over ~80% of the cycle with gentle easing; each station fills at `5 + 80 * i / (n-1)` %.

## Reduced motion

`svgkit.svg_doc()` appends `@media (prefers-reduced-motion: reduce) { * { animation: none !important } }`. Because base attributes are the final state, this shows the finished picture. Support for this media query inside image SVGs isn't verified everywhere, which is one more reason the final state must be the default.

## Checking motion

- Open the SVG directly in a browser and watch two full cycles.
- To inspect a moment, pause every animation at the same time:
  `document.getAnimations().forEach(a => { a.pause(); a.currentTime = 0.6 * cycleMs })`.
- Screenshot tools often capture the first frame or lag behind; don't conclude something is broken from one screenshot. Check computed styles or pause at a time instead.
