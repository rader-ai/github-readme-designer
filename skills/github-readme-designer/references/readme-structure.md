# README structure, patterns and the visual catalogue

From reading the source of ~37 well-known READMEs (charmbracelet/vhs and gum, astral-sh/uv and ruff, lazygit, browser-use, zellij, textual/rich, excalidraw, atuin, supabase, next.js, tailwind…), plus building the lighthouse-fix reference.

## What the best ones do

- **The first screen sells.** Logo or hero, a tagline under 15 words, at most 3-5 badges (or none), then **proof** within the first 10-25 lines of source: a demo, a benchmark chart, a before/after. Install comes in the first two sections.
- **One visual per idea, directly under its heading**, with 1-3 sentences of copy. lazygit puts a short video under every feature heading; gum a GIF per command.
- **Proof is data, not adjectives.** uv opens with a themed benchmark chart and a one-line caption. Captions say what was measured and how.
- **Two good lengths:** a pitch page that hands off to docs (50-150 lines), or a full manual with a strong hook (400-900 lines). Either works if the first screen works. Push long reference material into `<details>`.
- **Honesty builds trust.** "Limits", "one run per setup", "built by the same person who wrote the skill": small print like this makes the claims more believable, not less. Keep it.

## Anti-patterns

- Badge walls; sponsor or language-switcher blocks above the product.
- Ten install methods before the user knows what the thing does. One command, then `<details>`.
- `<picture>` whose dark and light sources are the same file.
- Huge unlabelled GIFs, no width, no caption. Black logos that vanish in dark mode.
- A hero that's a link to a video (adds a click before any value).
- Visuals that are decoration: abstract gradients, stock-like illustrations, anything that doesn't show the project.
- Invented numbers, invented sample output, or a chart split the data doesn't support.
- Hard `<br>` inside paragraphs (wraps mid-sentence on phones).

## Reference models

- **browser-use/browser-use:** theming and layout; `<picture>` with combined width + theme media queries.
- **astral-sh/uv:** proof-first hero with a themed benchmark chart.
- **jesseduffield/lazygit:** a visual per feature, tagged with `<!-- demo: x -->` so they can be regenerated.
- **charmbracelet/vhs:** the demo is made from code (`.tape`) and links to its source.
- **rader-ai/lighthouse-fix:** the reference implementation for this skill (see `examples/lighthouse-fix/`).

## Visual catalogue: which visual for which content

| Content | Visual | Motion idea |
|---|---|---|
| The core idea (always) | **Hero**: name, tagline, chips + the signature animation | The tool's core move as a picture, looping slowly (10-14 s) |
| Results, benchmarks, evals | **Proof chart**: dumbbell (before→after), bars, or a small multiple | Loop: draw in, count up, hold, fade |
| A pipeline or process | **Flow**: numbered stations on a line (vertical when narrow) | A marker travels the line; stations light as it passes |
| What the user gives it | **Input panel**: a file, form, report or command as it really looks | Values reveal, lists scroll past (ticker) |
| How it decides | **Triage/ranking**: table with verdicts, ranked cards with owners | Rows evaluate in turn; strike-through; cards slide in |
| What comes out | **Output window**: editor/terminal/document with the real output | Lines type in, then key lines highlight with a note |
| CLI tools | **Terminal**: real command and real output | Typed command, output streams in |
| Before vs after (code, UI, text) | **Split panel** or a wipe between two states | Wipe or cross-fade on a loop, holding each side |
| Architecture | **Diagram** of real components (or a Mermaid block if it must be editable) | Packets move along edges |

Pick 3-6 visuals. A hero and a proof are almost always worth it; the walkthrough (input → decision → output, built from a real run) is what makes people understand the project.

## Copy

- Write from the user's side: what they give it, what they get, what it saves them. Plain verbs, sentence case, no hype words.
- Each visual's caption or lead-in sentence says what to notice ("the top five all move INP, the one metric real visitors fail").
- Keep the author's existing phrasing where it's good; the redesign is mostly structure and visuals.
