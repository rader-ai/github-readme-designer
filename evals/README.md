# Evals

Three test cases, each a real repo of mine, run with and without the skill using the same prompt.

| Case | What it tests |
| --- | --- |
| [`glyphmotion-redesign`](glyphmotion-redesign/) | A full redesign: themed, animated, dark mode, phone widths, before/after |
| [`lasso-voice-skill`](lasso-voice-skill/) | A writing skill, where proof is before/after text, not numbers, and the author's copy must be kept |
| [`inp-fix-from-scratch`](inp-fix-from-scratch/) | The repo turned out to be empty: does the run notice, and avoid inventing anything? |

Each case folder holds `prompt.md`, `case.yaml` and one file per check in `graders/`, in the layout `claude plugin eval` reads.

## Results: iteration 1 (Oct 23, 2026)

[`results/iteration-1/`](results/iteration-1/) has the benchmark, every check with its evidence (`grading.json`) and timing for all six runs. Summary:

| | With the skill | Without |
| --- | --- | --- |
| Checks passed | 31 / 32 (97%) | 26 / 32 (81%) |
| Mean tokens per run | 246k | 159k |
| Mean time per run | 12.5 min | 7.2 min |

- One run per configuration, so treat the gap as a direction, not a precise size.
- Checks 1-9 are scripted ([`grade.py`](grade.py)); the case-specific ones were graded by reading the outputs.
- The run outputs (cloned repos with new READMEs) aren't committed; they were up to 57 MB each.
- These runs used the first draft of the skill (then called `readme-motion`). The problems they surfaced are listed in [`fixes-applied.md`](results/iteration-1/fixes-applied.md) and are fixed in the current version, which hasn't been re-run yet.
