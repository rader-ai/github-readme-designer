# Running in Claude Code, Codex and ChatGPT

The skill is plain Agent Skills format (`SKILL.md` with only `name` and `description` in its frontmatter, plus `scripts/`, `references/`, `examples/`), so the same folder works everywhere. What changes is how you get the repo in and the result out.

## Claude Code / Codex CLI (shell available)

- **Read:** `gh repo clone owner/name -- --depth 1`, or the current checkout. Private repos work when `gh auth status` shows access (`repo` scope).
- **Run:** Python 3.9+ for `svgkit.py`, `lint_readme.py` and `preview.py`; no third-party packages. Run the project itself on its sample data if that's safe and fast.
- **Preview:** `preview.py` uses `gh api markdown` to render through GitHub's real Markdown API, then writes a local HTML file. Open it with a local server or browser pane; emulate dark mode and a ~375px width to check every variant.
- **Deliver:** commit to a new branch, push only after the user says so, and give the branch URL. A PR only on request. Never push to the default branch.
- **Install locations:** Claude Code reads `~/.claude/skills/github-readme-designer/` or `.claude/skills/`; Codex reads `~/.agents/skills/` or `.agents/skills/`.

## ChatGPT

- **Read:** the GitHub connector can read repos the user authorised, private ones included, but can't write. If it's unavailable, ask for a zip upload or the README plus key files.
- **Run:** the sandbox runs Python, so `svgkit.py`, the per-repo build script and `lint_readme.py` work. It generally has no `gh` and no outbound network, so `preview.py` falls back to a basic local Markdown renderer (it says so in the page). The before/after comparison still works.
- **Deliver:** a zip with `README.md`, `.github/assets/*.svg`, the build script and `before-after.html`, plus a short note on where each file goes. The user commits it.
- **Install:** ChatGPT skills import the Agent Skills format (upload the folder as a zip). Availability depends on plan and admin settings.

## Claude apps (claude.ai)

Zip the `github-readme-designer` folder and upload it as a custom skill. Same as ChatGPT: read via an uploaded zip or a connector, deliver a zip.
