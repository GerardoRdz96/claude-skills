# /prompt-eval — reference

Deep reference for the prompt-evaluation skill. Operationalizes "Building with the
Claude API" Part 2 (evaluation), Part 3 (prompt engineering), and Part 4 (tool
descriptions). The canonical course ingest is [[claude-api-fundamentals]].

## Why an eval at all

The course's core claim: you cannot improve a prompt you cannot measure. Eyeballing one
or two outputs hides regressions and rewards prompts that happen to work on the example
you stared at. An eval gives a single number across a *dataset*, so a change is provably
better, not just different. This is exactly Gera's duty ("tune prompts / embeddings / LLM
configs") and the safety net Cleia's system prompts lack today.

## The 5-step eval workflow (course Part 2)

1. **Define the task** in one line. The grader needs it to judge "good".
2. **Build a test dataset.** Real golden cases beat generated ones, but generated cases
   (`gen`, cheap Haiku, temperature 1.0 for variety) get you moving. Always include edge
   cases: empty input, adversarial input, the format that broke last time.
3. **Run the prompt** across every case (clean Messages API call, not the agent harness).
4. **Grade** each output two ways:
   - **Code graders** (deterministic, free, fast): format/JSON-parse/regex/length/exact.
     Use these for anything objectively checkable. They never drift.
   - **Model grader** (a judgment call): routed to **Codex** with reasoning-before-score
     scaffolding. Used for quality dimensions code cannot check (helpfulness, tone,
     correctness of reasoning).
5. **Aggregate to one number.** Code-avg (0-1) blended 40/60 with the model score
   (1-10 -> 0-1). One number per case, averaged across cases.

## Why the model grader reasons before it scores

Asking for a bare 1-10 makes a judge cluster everything at 6-7 (it hedges). Forcing
`strengths -> weaknesses -> reasoning -> score` makes the number fall out of the analysis,
so scores spread and become discriminating. This is the LLM-as-judge scaffolding the
course teaches, and `build_model_grade_prompt` hard-codes that order.

**No-Self-Review Law:** the judge is Codex (a different lineage). Claude grading Claude's
own output is the exact blind-spot failure Servy bans. The harness enforces this in
`run_model_grade` (it shells to `codex exec`, never to Claude).

## Prompt-engineering technique catalog (course Part 3) — change ONE per round

Apply one, re-score, keep if it helped. In rough order of leverage:

1. **Be clear and direct.** Say exactly what you want and the output format. Remove
   ambiguity before anything fancy. Often the single biggest jump.
2. **Be specific about the format.** "Reply with only the lowercase label" beats "classify
   this". Name the exact shape; pair with a `regex`/`no_fence` grader.
3. **Structure with XML tags.** Wrap distinct parts (`<instructions>`, `<context>`,
   `<example>`, `<input>`) so the model does not confuse data for instructions.
4. **Few-shot examples.** Add 1-3 worked examples. Mine the best one from your current
   top-scoring case (its input + the ideal output). Examples teach format and edge handling
   faster than prose.
5. **Assign a role** (system prompt). "You are a senior support classifier" focuses behavior.
6. **Let it think** (chain-of-thought) for reasoning tasks: ask for steps before the answer,
   then have it put the final answer in a tagged block you extract.
7. **Prefill / speak-for-Claude.** Start the assistant turn (e.g. with `{` or `<answer>`)
   and pair a stop sequence to force clean structured output with no preamble. (See the
   `claude-api-fundamentals` "Structured data: prefilling + stop sequences" section.)

The discipline: one lever per round, always re-measured. The `compare` command prints the
delta and you state which lever earned it.

## Run modes vs evaluation patterns

The `--mode` flag has exactly two values, **system** and **template**. "tool-description" and
"skill" are not flags; they are evaluation *patterns* you run in one of those two modes by
choosing the right cases and graders.

- **`--mode system`** — prompt-under-test is the system prompt, case `input` is the user turn.
  The default; use for any assistant persona / Cleia or PA system prompt.
- **`--mode template`** — prompt-under-test is a template with `{input}`; the harness
  substitutes each case and sends it as the user turn (no system). Use for a single
  transformation, classification, or extraction prompt.

Patterns built on those two modes:

- **tool-description pattern** — the unit under test is a tool/MCP `description` + arg
  descriptions. Generate trigger cases (should select the tool) and near-miss non-trigger
  cases (should NOT), and grade with `contains:`/`regex:` for the right tool name and argument
  values. The course's lesson: descriptions should be 3-4 sentences (what it does / when to
  use it / what it returns) with a description per argument; abstract beats hyper-specialized.
- **skill pattern** — the unit is a Skill's `description` + body. Score whether the skill
  triggers on the scenarios it should and stays quiet otherwise, across
  `--target haiku/sonnet/opus`. A skill that only fires on Opus is a description problem, not a
  model problem. (This is the measure half that `/skill-builder` authors but never runs.)

## Worked example (system-prompt mode)

```bash
# 1. dataset
python3 scripts/prompt_eval.py gen \
  --task "Classify a support message as billing | technical | other; reply with only the label." \
  --n 6 --out cases.json

# 2. baseline
python3 scripts/prompt_eval.py eval --prompt v1.txt --cases cases.json \
  --task "Classify ... reply with only the label." \
  --graders "nonempty,no_fence,regex:^(billing|technical|other)$" --out v1.json

# 3. apply ONE technique (added an explicit format line + a role) -> v2.txt, re-score
python3 scripts/prompt_eval.py eval --prompt v2.txt --cases cases.json \
  --task "Classify ... reply with only the label." \
  --graders "nonempty,no_fence,regex:^(billing|technical|other)$" --out v2.json

# 4. delta
python3 scripts/prompt_eval.py compare --before v1.json --after v2.json
```

## CLI surface

- `gen --task --n [--model haiku] [--out]` — generate a test dataset.
- `eval --prompt --cases --task [--mode system|template] [--graders ...] [--target sonnet] [--temperature 0.0] [--no-model-grade] [--out] [--json]` — run + grade + aggregate.
- `compare --before --after` — before/after delta table.

Graders: `nonempty`, `json_valid`, `no_fence`, `expected` (vs case `expected` field),
`contains:<s>`, `regex:<pat>`, `max_len:<n>`. Note: `--graders` is comma-separated, so a
`contains:`/`regex:` argument cannot itself contain a comma; run a second eval for that case.

## Maintenance

After each real run, note what worked / what to fix and refine this skill (the Four-Cs
"update the skill" ritual). Candidate v2 features: an embeddings/retrieval grader
(cosine vs a reference answer), a cost/latency column per run, and a Cleia-system-prompt
regression preset.
