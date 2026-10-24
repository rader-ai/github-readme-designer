# Reference implementation: rader-ai/lighthouse-fix

Live: https://github.com/rader-ai/lighthouse-fix (PR #1 added the redesign).

| File | What it is |
|---|---|
| `README.before.md` | The original README: good copy, no visuals |
| `README.after.md` | The redesign |
| `build_visuals.py` | Hero, proof chart, flow diagram (+ theme tokens and the contour texture) |
| `build_walkthrough.py` | The three walkthrough visuals: report, read, prompt |

Run: `python3 build_visuals.py <out-dir>` and `python3 build_walkthrough.py <out-dir>` (24 SVGs: 6 visuals × light/dark × wide/narrow).

## The design brief, as decided

- **Subject's world:** Lighthouse reports, and lighthouses. The tool's core move is triage: of ~40 audits, light up the few that hurt real visitors.
- **Signature:** a lighthouse beam sweeps a list of real audit names; rows it passes either light up with a rank and an owner ("#1 · developer") or dim to "lab only". The whole product idea, in one loop.
- **Palette:** light = nautical chart paper (pale blue-grey, depth contours, navy ink); dark = night sea. One accent: sodium-amber lamp light. Status colours (good/warn/bad) only in the data visuals.
- **Type:** system serif for display (chart-label feel, italic second line), system mono for data.

## Visuals and why each exists

1. **Hero**: the signature, plus tagline and platform chips.
2. **Proof**: a dumbbell chart of the repo's real eval results (with vs without the skill), looping: draw in, count up, hold, fade. The caption keeps the author's honest limits.
3. **Flow**: five stations from report to owner; a marker travels the line.
4. **Walkthrough**, built from actually running the skill on `evals/reports/betabound.txt`:
   - *What comes back*: lab score ring, real-visitor distribution bars, a scrolling list of the 24 flagged audits.
   - *How it reads it*: lab vs real per metric (LCP struck through as lab-only, INP "fix first"), the verdict the tool wrote, ranked cards with owners; a lab-only card dimmed at #7.
   - *What the agent gets*: an editor window, tabs for each area prompt, the scripts prompt typing in, key lines highlighted with notes.

## Lessons that became skill rules

- The first chart animated once on load; the user scrolled down and saw a still chart. → Loop data visuals.
- The beam eased while rows lit on a linear timeline, so they drifted. → One timeline per scene.
- Wide SVGs were unreadable on phones. → Designed narrow variants + `(max-width: 1011px)` sources.
- A `<br>` in the intro split sentences on phones. → No hard breaks in paragraphs.
- The field-data panel first showed made-up good/needs/poor splits for LCP and CLS; the report only gave "% good". → Show only true data.
- The user asked to see the real inputs and outputs ("how reports come back, how we read them, how we provide prompts"). → The walkthrough is built from a real run, and the skill asks for one by default.
