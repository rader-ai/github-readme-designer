---
name: github-readme-designer
description: Redesign a GitHub repository's README into a designed, animated page that explains what the project does and why someone should use it, with themed light/dark motion visuals (animated SVG hero, proof charts, flow diagrams, step-by-step walkthroughs) that play right on github.com, plus phone-width versions. Use this whenever someone wants to redesign, improve, polish, "make nicer", add visuals or animation to, or write from scratch a README for a repo, public or private, even if they don't say "animated" or "motion"; also when they share a GitHub repo URL and ask how to make it more appealing, or say their README is boring, missing or needs a hero/banner/demo.
---

# github-readme-designer

Turn a repository's README into a page that sells the project in its first screen and then proves it. The visuals are animated SVG files that GitHub shows inline, in light and dark, at desktop and phone widths.

The bar: someone landing on the repo knows **what it is, why they want it, and that it works** before they scroll, and every visual shows something true about *this* project, taken from its own code, data or outputs, never a generic illustration.

## How this works on GitHub (read before designing anything)

GitHub strips inline `<svg>`, `<style>`, `style=""` and all JavaScript from READMEs. Motion is only possible through **image files**: an SVG loaded as an image may animate with CSS `@keyframes` (or SMIL) but cannot run scripts or load anything external (fonts, images, CSS). So every visual here is a self-contained `.svg` committed to the repo and shown with `<picture>`, which picks the dark/light and wide/narrow version. Details and the full allowlist: `references/github-constraints.md`.

## Workflow

### 1. Get the repo

- **Shell with git/gh available (Claude Code, Codex CLI):** clone it (`gh repo clone owner/name -- --depth 1`), or work in the checkout you're in. Private repos work if `gh` is logged in with access.
- **ChatGPT or no shell:** read files through the GitHub connector, or ask the user to upload the repo as a zip / paste the README and key files. You'll deliver files plus instructions instead of pushing. See `references/platforms.md`.

### 2. Understand the project before designing

Read the existing README, the main entry points, the package manifest, any `examples/`, `evals/`, `docs/`, sample data and test fixtures. Write down, in plain words:

- **What it is**, in one sentence a newcomer would get.
- **Who it's for** and the moment they'd reach for it.
- **The claim** that makes it worth downloading (faster, safer, fewer steps, better results…).
- **The proof** that exists in the repo: benchmarks, eval results, before/after numbers, screenshots, real outputs. Never invent numbers. If there is no proof, say so to the user and design around a real demo instead.
- **The real inputs and outputs.** What does a user hand it, and what comes back? If the repo ships sample data and it can be run safely and quickly (no secrets, no network side effects, under a few minutes), **run it** and use the actual output in the walkthrough visuals. Real output is more convincing than any mockup, and it keeps you honest. If you can't run it, quote real fixtures or test expectations, and label excerpts as excerpts.

**If the code isn't there** (an empty repo, a private repo you can't read, only a description), tell the user before doing anything else. You can still draft a starter README from what is known, but don't present guesses as facts: no install commands, file paths, option names, results or features you haven't seen. Where the README needs them, put a visible placeholder in the README itself (`> [!NOTE] Install steps go here once the code is pushed.`), not just a note in your summary, because the README is what readers will see. A schematic hero is fine if it's labelled as one.

Keep the author's voice. If the existing copy is good, reorder and trim it rather than rewrite it.

**Save the "before" now.** Copy the current README (and note if there is none) to `README.before.md` outside the files you'll commit, e.g. in a scratch folder. The before/after comparison in step 7 is the main thing the user will look at, and it's only possible if the original is kept untouched.

### 3. Pick a visual identity from the project's own world

Every project gets its own look, never a house style. Find the subject's world (a lighthouse for a Lighthouse tool, a scoreboard for a sports tool, a terminal for a CLI, a recipe card for a cooking app) and derive from it:

- **Palette:** 6-8 named tokens for light and the same for dark (`bg`, `ink`, `muted`, `faint`, `row`/`card`, `accent`, plus status colours if the data has good/bad). Check contrast in both.
- **Type:** system font stacks only (a serif or sans for display, a monospace for data). Embedding fonts makes files big; see constraints.
- **Signature:** the one memorable motion idea, in the hero, that *shows what the tool does*. For lighthouse-fix: a beam sweeps a list of audits, and only the ones that hurt real visitors light up with a rank and owner. Ask: "what is the tool's core move, as a picture?"

Avoid the three looks every AI design defaults to (cream + terracotta serif, near-black + one neon accent, newspaper hairlines) unless the subject truly calls for one. Spend boldness on the signature; keep everything else quiet.

### 4. Plan the page

Default section order (adapt, don't force it):

1. **Hero image**: name, a tagline under ~15 words, the signature animation, and where it runs (platform chips).
2. **One short paragraph** under the hero: what it is, for whom.
3. **Nav links** (`Install · Results · How it works · Use`), 3-6 of them.
4. **Proof**: a chart or before/after visual of the repo's real results, with a one-line caption and honest limits.
5. **Install**: one copy-paste command first, then alternatives in `<details>`.
6. **How it works**: an overview flow diagram, then a **walkthrough** of real input → what the tool does with it → real output, one visual per step.
7. **Use / reference**: options, outputs table. Long reference material goes in `<details>`.

Visuals sit directly under the heading they illustrate. One visual per idea; don't decorate. See `references/readme-structure.md` for patterns from the best READMEs, anti-patterns, and the visual catalogue (which visual fits which kind of content).

Tell the user the plan (identity, signature, section list, visuals) in a few lines before building, unless they've said to just go.

### 5. Build the visuals

Write one small Python build script per repo (e.g. `.github/readme/build.py`, or outside the repo if the user prefers) that imports `scripts/svgkit.py` from this skill and generates every asset. Each visual is a function `(theme, size)`, and `svgkit.write_all()` writes all four variants:

```
<name>-light.svg  <name>-dark.svg  <name>-narrow-light.svg  <name>-narrow-dark.svg
```

Rules that matter (the reasons are in `references/motion-patterns.md`):

- **Loop data visuals; don't play them once.** A chart that animates on page load has already finished when the reader scrolls to it. Loop: draw in → count up → hold most of the cycle → fade → repeat.
- **The finished frame is the default.** Base attributes hold the final state; animations only describe how to get there. Then `prefers-reduced-motion` (which svgkit adds to every file) leaves a complete, correct picture, and so does any viewer that doesn't animate.
- **Drive related elements from one timeline.** If a beam sweeps rows and rows light as it passes, both use the same cycle and linear timing, or they drift apart.
- **Narrow versions are designed, not shrunk.** Wide is 1280px; narrow is 640px and restacks the layout (columns become rows, horizontal flows become vertical). GitHub scales images down, so on a phone a 640px design shows at about 0.55×: keep body text ≥14px in narrow designs.
- **Text must fit, for the whole loop.** Use `svgkit.text_width()` to check line lengths; truncate with "…" or wrap rather than overflow. Keep the name and headline still and fully inside the frame while they're on screen: if part of the scene drifts or scrolls, don't put the words in the drifting part.
- **Show only true data.** If a source gives one number, don't draw a split it doesn't have.
- Keep each SVG under ~60 KB (they're typically 5-20 KB).

`examples/lighthouse-fix/` contains the complete build scripts from the reference implementation: hero with a sweeping beam, a looping dumbbell chart with counting numbers, a flow diagram, and a three-step walkthrough (report panel, triage + ranked cards, a typed-in prompt in an editor window). Read them before writing your own; reuse patterns, not the look.

### 6. Write the README

Use `svgkit.picture(name, alt)` to produce each `<picture>` block (it emits the narrow-dark, narrow-light, dark, and light sources in the order GitHub needs). Every image gets real alt text that states what the visual says, including its numbers.

Only GitHub-safe HTML: `p align`, `picture`/`source`/`img`, `details`/`summary`, `table`, `sub`/`sup`, `kbd`, `br`, `b`/`i`. Markdown callouts (`> [!NOTE]`) are fine, sparingly. No hard `<br>` inside paragraphs (they wrap badly on phones).

### 7. Check it

```bash
python3 <skill>/scripts/lint_readme.py <repo>            # SVG safety, sizes, variants, alt text, README HTML
python3 <skill>/scripts/check_bounds.py <repo>/.github/assets   # text that spills outside its image, at the finished frame
python3 <skill>/scripts/preview.py <repo> --before README.before.md --out before-after.html
```

`check_bounds.py` renders every SVG in headless Chrome, pauses it at eight points in the loop and at the finished frame, and lists text that runs past the edge (✗, fix it) or clipped lines cut at the side (!, look and decide). Character-width estimates miss things, especially lettering built from glyphs or pixel fonts, and narrow layouts are where it happens. If Chrome isn't available it says so; then check the narrow variants by eye.

`preview.py` renders both READMEs through GitHub's real Markdown API when `gh` is available (so you see exactly what GitHub's sanitizer keeps), styled like github.com, side by side: **before** on the left, **after** on the right, each scrolling on its own, with a toggle for a single full-width view. With no `--before` it previews only the new README. If there was no README before, the left pane says so; that's a strong before/after in itself.

Then look at it: open the preview at desktop width and at ~375px, in light and dark (emulate `prefers-color-scheme`), and watch each animation through a full cycle. Screenshots often capture the first frame, so to inspect the finished state pause the animations at a point in their cycle (`document.getAnimations().forEach(a => { a.pause(); a.currentTime = ms })`) on the SVG opened directly. Fix overlaps, clipped text, and timing drift before handing over.

### 8. Deliver

- **Lead with the before/after.** Show the user `before-after.html` first (open it in a browser pane or send the file), then summarise what changed and why in a few lines: identity and signature, sections added or reordered, what each visual proves, and what copy you kept.
- **Pushing is the user's call.** Ask before pushing. Default: commit to a new branch (e.g. `readme-redesign`), push, and give the branch URL so they can see it on github.com. Open a PR only when they ask, and never push to the default branch yourself.
- **No push access (ChatGPT, forks):** deliver a zip of `README.md` + `.github/assets/` + the build script, with one line on where each goes.
- Put the summary in your final message: what you made, the calls you made without asking, and any placeholders left in the README. A separate summary file is optional (some environments don't allow writing one).
- Tell them what was not checked (Safari and the GitHub mobile app often differ on theme switching), and anything you couldn't verify or chose to leave out.

## Reference files

- `references/github-constraints.md`: what GitHub renders, what it strips, size limits, theme switching. Read before step 5.
- `references/readme-structure.md`: section patterns, anti-patterns, reference READMEs, visual catalogue. Read at step 4.
- `references/motion-patterns.md`: keyframe recipes (loop reveal, draw-in, count-up, sweep, ticker, typed lines) with timing rules. Read at step 5.
- `references/platforms.md`: running in Claude Code, Codex and ChatGPT; private repo access; what to deliver where.
- `scripts/svgkit.py`: SVG document wrapper, themes, text measurement, animation helpers, `picture()`, `write_all()`.
- `scripts/lint_readme.py`, `scripts/check_bounds.py`, `scripts/preview.py`: checks and the before/after preview.
- `examples/lighthouse-fix/`: the full reference implementation.
