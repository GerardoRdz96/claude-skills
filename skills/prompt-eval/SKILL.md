---
name: prompt-eval
description: Use to put an objective score on a prompt, system prompt, tool description, or skill by running it across a test dataset and grading the outputs (code graders + a Codex model-grader), then iterate one technique at a time and measure the gain. Triggers - "eval this prompt", "score this prompt", "is this prompt better", "A/B these prompts", "build an eval set for X", "tune this system prompt", "regression-test Cleia's system prompt", "/prompt-eval". Operationalizes the "Building with the Claude API" course (Part 2 evals + Part 3 improvement loop). NOT /eval (that scores a code diff); this scores model OUTPUT over a dataset.
---

# /prompt-eval

Turn "this prompt feels better" into a number. This is the eval loop the Claude API
course teaches, wired for Servy: **define a dataset, run the prompt across every
case, grade each output, average to one score, then change one technique and
re-score.** It is the tool for Gera's literal duty of tuning prompts / embeddings /
LLM configs, and a regression net for Cleia's system prompts.

Engine: `scripts/prompt_eval.py` (stdlib + the Anthropic Messages API for clean runs;
the model-grader routes to **Codex**, never Claude — No-Self-Review Law, since Claude
must not grade Claude's own output). Deterministic core is covered by
`tests/prompt-eval/test_prompt_eval.py` (25 tests). Deep reference: `reference.md`.

Distinct from [[eval]] (which judges a code *diff* against a rubric). This judges
model *output* across a *dataset*.

## The loop

1. **Frame it.** Get from Gera: the prompt-under-test (a file, a wiki page, or a
   Cleia/PA system prompt) and a one-line **task** description ("what is this prompt
   supposed to do"). Pick the mode (below).
2. **Get a dataset.** Either Gera has golden cases, or generate one:
   `python3 scripts/prompt_eval.py gen --task "<task>" --n 6 --out cases.json`
   (cheap Haiku, the course's dataset-gen step). Always eyeball the generated cases
   and add any real edge cases Gera names.
3. **Baseline.** Score the current prompt:
   `python3 scripts/prompt_eval.py eval --prompt prompt.txt --cases cases.json --task "<task>" --target <your production model> --graders "nonempty,no_fence,regex:^(billing|technical|other)$" --out baseline.json`
   (`--target` = the model the prompt SHIPS on; eval on what you ship, not a cheaper model.)
   Add `--no-model-grade` to skip the Codex grader (free, code-graders only) while
   iterating fast; drop it for the real quality number.
4. **Read the score + the weaknesses.** One overall %, per-case scores, and the
   Codex grader's one-line weakness per case. The weaknesses tell you which lever to pull.
5. **Iterate ONE technique at a time** (never several at once, you cannot attribute
   the gain otherwise). Apply one of the course's techniques to the prompt, save a new
   file, re-run `eval --out after.json`, then:
   `python3 scripts/prompt_eval.py compare --before baseline.json --after after.json`
   Narrate which lever earned the delta. Keep the winner, repeat until it plateaus.
6. **Ship the winner.** Hand Gera the highest-scoring prompt + the before/after table.

## What you can evaluate

The harness has two run **modes** (the `--mode` flag), plus two **patterns** that reuse the
same dataset -> run -> grade machinery (they are NOT separate `--mode` values, they are how
you set up the cases and graders):

**`--mode` values:**
- **system** (default) — the prompt-under-test is a **system prompt**; each case `input` is
  the user message. For tuning a Cleia/PA system prompt or any assistant persona.
- **template** — the prompt-under-test is a **template containing `{input}`**; the harness
  substitutes each case in. For a one-shot transformation/classification prompt.

**Patterns (run in `system` or `template` mode, with the right cases + graders):**
- **tool-description** — to test whether a tool/MCP schema gets *selected and filled*
  correctly, put trigger and near-miss non-trigger inputs in the dataset and grade with
  `contains:`/`regex:` on the expected tool name/args. (Course Part 4 tool-description rules.)
- **skill** — to test whether a skill reliably *triggers*, run ~3 scenario cases and compare
  the score across `--target haiku`, `sonnet`, `opus`; a skill that only fires on Opus is
  fragile. (The measure half `/skill-builder` authors but never runs.)

## Code graders (`--graders`, comma-separated)

`nonempty` · `json_valid` · `no_fence` (output not wrapped in ```) · `expected` (exact
match vs each case's `expected` field) · `contains:<substr>` · `regex:<pattern>` ·
`max_len:<n>`. Combine them; the code score is their average (0-1), blended 40/60 with
the Codex model score. See `reference.md` for the technique catalog and grader design.

## Guardrails

- **Eval on the model you SHIP (Anthropic rule).** Pass `--target <your production model>`, or pin it once via `SERVY_PROD_MODEL` (env/.env). A prompt's score is MODEL-SPECIFIC, so a number from a cheaper or different model than production measures the wrong thing. The harness defaults `--target` to your pinned prod model (else `opus`) and **warns** when you gate a decision on a cheap tier. `haiku` is for `gen` (making test cases) only — never the eval target. ([[anthropic-best-practices]].)
- **The model-grader is Codex, by law.** Never swap it to Claude. Grading a
  prompt-UNDER-TEST is fine; this skill must never become Servy grading its own freshly
  authored output (that is still a Codex job under the No-Self-Review Law).
- **It costs tokens.** Runs hit the Anthropic API (`ANTHROPIC_API_KEY`) per case and Codex
  per case when model-grading. Keep datasets small (5-8 cases) while iterating.
- **SoftServe boundary.** Never paste SoftServe Internal+ or customer prompts/data through
  this for a non-approved channel; personal/public-data prompts (Cleia, PA, Gera's own) only.
