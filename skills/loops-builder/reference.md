# Loops-builder reference — mechanisms, the 14-template library, 18 gates

The deep companion to `SKILL.md`. Doctrine: `references/agent-loops.md`. Workflow JS API (for workflow-mechanism loops): `.claude/skills/workflow-builder/reference.md` — do not duplicate it; co-build with it. Provenance: the `loops-builder-research` workflow (7 researchers + synthesis, 2026-06-22) cross-read against Servy's live loop inventory; skeletons hand-verified against the doctrine + the workflow API.

## The one rule everything serves

A loop has **no model-side terminator** — it runs until an operator, schedule, or cap stops it. So every loop ships with **two brakes**:
1. **Objective done-check** — a machine-testable proposition: *named artifact/state + measurable threshold/keyword + machine-observable signal*. Not "improve it", not "until satisfied".
2. **Numeric hard cap** — an explicit integer (turns / iterations / budget / wall-clock). The done-check might never pass; the cap is what guarantees the loop ends.

The objective-goal template (read this back to Gera in Round 1 if his answer is fuzzy):
> "Iterate until **`<artifact>`** satisfies **`<threshold/keyword>`**, provable by **`<exact command → expected signal>`**; stop after **`<N>`** iterations and report."

## Mechanism cheat-sheet (the session-level primitives)

| Mechanism | When | Default cap behavior | The cap YOU must supply |
|---|---|---|---|
| **`/goal`** | depth, iterate-to-done, watched | **no default cap** — runs until done-check holds | `--max-turns N` (headless) + a counter-aware `Stop` hook; operator Esc (interactive) |
| **`/loop <interval>`** | poll an external resource during a watched session | session-bound; dies with the terminal (~3-7d max) | Esc cancels the pending wakeup; or a `Stop` hook |
| **`/loop` self-paced** | model schedules its own next wakeup (dynamic mode) | same session bounds | model stops scheduling; Esc. **GAP — no living Servy impl** |
| **bash `while`/`until` (Ralph)** | exceeds one context window; model self-terminates early | runs until the shell condition flips | the `until <check>` condition **and** `MAX_ITER` |
| **dynamic workflow** (`.claude/workflows/*.js`) | width fan-out that iterates (until-dry/-count/-budget) | 1000-agent lifetime cap (a backstop, not a brake) | `round < MAX_ROUNDS` + `budget.total && budget.remaining() > 50_000` at the TOP of the body |
| **Cloud Routine** (`/schedule` → `routines/*.md`) | unattended cadence, survives a closed laptop | daily plan caps (Pro 5 / Max 15 / Enterprise 25) | single-pass prompt with an explicit success criterion (NOT iterate-until-done semantics) |

Remote/cloud Claude Code sessions: **`/loop` is disabled** — use a Cloud Routine or `claude -p` + launchd.

Official names (`references/claude-code-loops.md`): plain prompting = **turn-based**, `/goal` = **goal-based**, `/loop`/`/schedule` = **time-based** (local vs cloud), schedule+goal+dynamic-workflows+auto-mode composed = **proactive**.

## Verification wiring (pick the type, then wire it)

Decision rule, in order — take the first that fits:
1. Can a bash command / test return a boolean with zero opinion? → **functional** (always try first). Wire: the exact command + expected exit/output in the done-check.
2. Must the output be *seen* — rendered, in a browser, as an image/PDF — to confirm? → **visual**. Wire: Playwright screenshot → the agent reads the *image*. Reading source HTML to infer visual truth does NOT count.
3. Needs taste / domain judgment a machine assertion can't capture? → **judgment**. Wire: an enumerable rubric (JSON, per-dimension, evidence-forcing, with a "return Unknown" escape) scored by a **different model lineage** (Codex for Claude-actor output — No-Self-Review Law). The grader defaults to *fail* unless every dimension cites evidence.
4. Is the next action irreversible (send / delete / publish / pay / deploy / merge-to-main)? → **human-gate**. Wire: the loop PAUSES with APPROVE / REJECT / DEFER before the action. In unattended loops, "pause" = push to a `claude/<name>/<date>` branch + Telegram digest with a revert command (never a blocking stdin read).

## The counter-aware `Stop` hook (the `/goal` brake)

A `Stop`-event hook in `settings.json` is how a `/goal` loop knows to keep going or stop. A done-check alone can loop forever, so the canonical hook carries BOTH brakes. (Official goal-based behavior: `/goal` also runs an evaluator-model stop-check against your stated criterion at each stop attempt — which is why deterministic criteria converge best; the counter-aware hook below is the house brake layered on top, and the **≤ 8 counter cap stays binding**.) Delegate the actual settings write to `/hooks-builder`; this is the logic it implements:

```bash
#!/usr/bin/env bash
# .claude/hooks/goal-stop.sh — keep iterating until DONE or CAP, then allow stop.
S=.loop-state/iter; mkdir -p .loop-state; n=$(cat "$S" 2>/dev/null || echo 0)
# DONE (objective done-check) → allow stop:
if npm test >/dev/null 2>&1 && git diff --quiet; then rm -f "$S"; exit 0; fi
# HARD CAP hit without passing → allow stop (the /goal report surfaces the escalation).
# KEEP THIS <= 8: Claude Code force-ends the turn after 8 consecutive Stop-hook blocks
# (override with CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=N). A counter above 8 never fires.
if [ "$n" -ge 8 ]; then rm -f "$S"; exit 0; fi
# else → block the stop (keep working) and count:
echo $((n+1)) > "$S"
echo '{"decision":"block","reason":"done-check failed (tests red or tree dirty) — keep iterating"}'
```
Returning `{"decision":"block","reason":...}` blocks the stop and feeds the reason back as the next instruction; exit-0 with no output allows the stop. Swap the `npm test && git diff --quiet` line for the task's real done-check. **The hard cap interacts with a harness limit:** Claude Code ends a turn with a warning after **8 consecutive `Stop`-hook blocks** (`references/claude-code-changelog.md`), overridable via `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=N`. So a counter cap above 8 silently never fires — keep the hook counter ≤ 8, or set the env var to match, and keep the two in sync. (This limit is on the `Stop`-hook brake only; `--max-turns N` for headless `/goal` is a separate, larger turn cap and is unaffected.)

## Template library (14)

Each: shape × mechanism × verification, the stop condition (both brakes), the Servy exemplar or GAP, and a skeleton. Climb the shapes only when needed — **start solo**.

### Solo loops

**T1 · solo-goal-loop** — solo / `/goal` / functional. *Open-ended coding or research where done is machine-checkable but step count is unpredictable. The primary recommendation.* Stop: Stop hook returns done when the check passes (`npm test` exits 0, `git status` clean, file-with-keyword exists); cap = `--max-turns N` / counter hook. Servy: `.claude/skills/build/SKILL.md` (GSD TDD loop) + `scripts/test-gate.py` (false-green guards). 
```
/goal "Make `npm test` pass and leave `git status --porcelain` empty. Stop after 15 iterations and report."
# headless:  claude -p --max-turns 15 "<same objective done-check>"
# + wire .claude/hooks/goal-stop.sh (above) via /hooks-builder
```

**T2 · loop-interval-polling** — solo / `/loop <interval>` / functional. *Check an external resource (deploy, CI, API) at a fixed interval during a watched session. NOT overnight.* Stop: Esc / Stop hook; cap = session lifetime. Match the interval to how often the resource actually changes (official rule); react to an event instead of polling when one exists. Servy: GAP (used ad-hoc, no file).
```
/loop 90s "curl -fsS https://app.example.com/health && echo UP"
# dies with the terminal; for unattended → a Cloud Routine instead.
```

**T3 · loop-self-paced** — solo / `/loop` self-paced / functional. *Model paces its own wakeups (short when active, long when idle).* Stop: model stops scheduling / Esc; cap = session. Servy: **GAP** — mechanism documented in `references/claude-code-feature-tiers.md`, no living impl.
```
/loop        # omit the interval → dynamic mode; the model schedules its next wake
# sub-300s keeps the prompt cache warm; 1200-1800s for idle ticks; never exactly 300s.
```

**T5 · loop-until-count** — solo / dynamic workflow / functional. *Accumulate a target count where each round adds 0..N.* Stop: `items.length >= TARGET`; cap = `round < MAX_ROUNDS`. Servy: GAP (closest = per-tier caps in `routines/evolution-ingestion.md`).
```js
const items = []; const seen = new Set(); let round = 0
while (items.length < TARGET_COUNT && round < MAX_ROUNDS) {
  round++
  const r = await agent("Find more <X>; return only new ones.", { schema: HITS })
  for (const h of r.hits) if (!seen.has(key(h))) { seen.add(key(h)); items.push(h) }
  log(`${items.length}/${TARGET_COUNT} after round ${round}`)
}
```

**T6 · loop-until-budget** — solo / dynamic workflow / functional. *Scale depth to an available token budget.* Stop: budget guard BEFORE spawning; cap = `round < MAX_ROUNDS`. Servy: GAP (guard pattern in `references/claude-code-workflows.md`).
```js
let round = 0
while (budget.total && budget.remaining() > 50_000 && round < MAX_ROUNDS) {
  round++                                  // guard at TOP — without budget.total, remaining() is Infinity
  const r = await agent("Go one level deeper on <X>.", { schema: FINDINGS })
  // accumulate r.findings
}
```

**T10 · ralph-loop-engineering** — solo / bash `until` / functional. *Exceeds one context window, or the model self-terminates before the bar is met. State lives on disk across resets.* Stop: the `until` done-check; cap = `MAX_ITER`. Servy: **GAP** (pattern in `references/agentic-engineering-patterns.md` pattern 1).
```bash
#!/usr/bin/env bash
set -euo pipefail
MAX_ITER=${MAX_ITER:-20}; i=0
# done-check: tests green AND the TODO file emptied
until npm test >/dev/null 2>&1 && [ ! -s TODO.md ]; do
  (( ++i > MAX_ITER )) && { echo "HARD CAP $MAX_ITER — escalate to a human"; exit 1; }
  echo "── iteration $i ──"
  claude -p --permission-mode acceptEdits "$(cat TASK_PROMPT.md)" || true   # acceptEdits auto-writes ordinary edits — pair with a NARROW prompt + repo-local cwd + the sacred-zones guard below; never for secrets/irreversible actions
  bash scripts/sacred-zones.sh --check-staged || { echo "sacred-zone touched — abort"; exit 1; }
done
echo "DONE in $i iterations"
```
`TASK_PROMPT.md` = goal + verifiable done-criterion + accumulated mistake-corrections (the CLAUDE.md of the loop). The brake is the `until` condition + `MAX_ITER`, **not** a settings.json hook.

**T11 · reflexion-multi-trial** — solo / `/goal` or workflow / functional. *The agent keeps failing the same class of error; learn across SEPARATE attempts without weight updates (distinct from in-context Self-Refine).* Stop: deterministic done-check; cap = `MAX_TRIALS=3`, memory window `N_MEMORY=5`. Servy: closest = `scripts/backlog-util.py probe/promote` (Dreaming).
```js
const reflections = []                                   // loop STATE → a loop-state file, NEVER knowledge/
for (let t = 0; t < MAX_TRIALS; t++) {
  const attempt = await agent(`Goal: <X>.\nPrior reflections:\n${reflections.slice(-5).join("\n")}`, { schema: RESULT })
  if (await doneCheck(attempt)) return attempt           // deterministic
  const r = await agent("You failed. In 2 sentences: what to do differently next attempt?", { schema: REFL })
  reflections.push(r.text)
}
```

### Maker-checker loops (quality matters; the maker can't grade itself)

**T7 · maker-checker** — maker-checker / `/goal` or workflow / judgment. *Generate, then a structurally separate fresh agent grades before accepting.* Stop: checker `score >= PASS_MARK` (default 8/10) with per-dimension evidence; cap = MAX_ITER. Servy: `routines/evolution-ingestion.md` Step 4 (`warden` — **same-lineage, weaker**) + `.claude/teams/the-builder-room.md` reviewer (**Codex, cross-lineage, the gold standard**).
```js
const draft = await agent("Produce <artifact> meeting <spec>.", { schema: ARTIFACT })
const verdict = await agent(
  `Grade against this rubric; default pass=false unless EVERY dimension cites evidence.\nRubric: ${JSON.stringify(RUBRIC)}\n\n${JSON.stringify(draft)}`,
  { schema: VERDICT })                                   // high-stakes Claude-actor output → checker is Codex, see below
```
Cross-lineage (high-stakes, persistent artifact): `codex exec --skip-git-repo-check "Grade against <rubric>: <artifact>"`. **Same-lineage Claude-checks-Claude (warden) is the weaker gate** — fine for low-stakes lint, not for shipping.

**T8 · evaluator-optimizer** — maker-checker loop / workflow / functional-first. *Enumerable criteria + iterative refinement measurably improves (translation, code-vs-tests, copy-vs-checklist).* Stop: evaluator PASS (structured, not "looks good") or a deterministic checker passes; cap = MAX_ITER. Servy: `.claude/skills/eval/SKILL.md` (Codex-judge-diff).
```js
let artifact = await agent("Draft <X>.", { schema: ART })
for (let i = 0; i < MAX_ITER; i++) {
  const ev = await agent(`Evaluate vs ${JSON.stringify(CRITERIA)}; return {pass, perDimFeedback}.`, { schema: EVAL })
  if (ev.pass) break
  artifact = await agent(`Revise to fix: ${JSON.stringify(ev.perDimFeedback)}\n\n${JSON.stringify(artifact)}`, { schema: ART })
}
```
If the evaluator must be the same model as the optimizer, prefer a **deterministic** checker (tests/lint/type) over an LLM judge, or route the judge to Codex.

**T14 · adversarial-verify-phase** — maker-checker / workflow / judgment. *Embed inside loop-until-dry or fan-out as the verify phase; each candidate is judged by N structurally different stances before counting.* Not a loop itself. Servy: `.claude/workflows/exhaustive-review.js` (the 3-judge triad).
```js
const LENSES = ['reproduce-it', 'refute-it', 'severity-check']     // structurally DIFFERENT stances, not 3 clones
const votes = (await parallel(LENSES.map(lens => () =>
  agent(`Judge "${f.desc}" via the ${lens} lens. Default real=false unless you can cite evidence.`, { schema: VERDICT }))))
  .filter(Boolean)
const real = votes.filter(v => v.real).length >= Math.floor(LENSES.length / 2) + 1   // true majority (≥2 of 3); raise to unanimous for high-stakes
```

### Manager-helpers loops (the job fans into independent parallel pieces)

**T4 · loop-until-dry** — manager-helpers / dynamic workflow / judgment. *Exhaustive coverage where one pass misses things; fire parallel finders until K dry rounds.* Stop: `K=2` consecutive dry rounds (after dedupe vs ALL-SEEN); cap = `MAX_ROUNDS` (2-3 for audits, 6 max). Servy: `.claude/workflows/exhaustive-review.js` (canonical) + `wiki-audit.js` + `loop-safety-audit.js` (built+run by `/loops-builder` 2026-06-22). **Measured cost (the loops-burn-tokens lesson, live):** a 4-finder × 4-round run with per-finding 3-judge verify spawned **~187 agents / 6.6M tokens / ~23 min** — verify cost = `fresh-findings × judges × rounds`, and it hit the cap *without converging* (kept finding fresh gaps). For audits: cap `MAX_ROUNDS` at 2-3, bound findings-per-round, or batch-verify (1 refute-default judge first, escalate to 3 only on survivors).
```js
const seen = new Set(); let dry = 0, round = 0           // Set OUTSIDE the loop — dedupe vs ALL seen, never vs confirmed
while (dry < 2 && round < 6) {
  round++
  const fresh = (await parallel(FINDERS.map(f => () => agent(f.prompt, { schema: FINDINGS }))))
    .filter(Boolean).flatMap(r => r.findings)
    .filter(b => { const k = key(b); if (seen.has(k)) return false; seen.add(k); return true })  // add-on-first-see: also dedupes duplicates WITHIN the round
  if (!fresh.length) { dry++; continue }
  dry = 0
  // …verify fresh via T14, accumulate confirmed
}
```

**T9 · plan-then-execute** — manager-helpers / dynamic workflow / functional. *Complex multi-step goal whose shape is knowable up front; steps may run in parallel.* Stop: every plan step DONE with output matching its typed `success_criterion`; cap = step count + per-step turn cap. Servy: `.claude/teams/the-builder-room.md` (multi-session). 
```js
const plan = await agent("Break <goal> into independent steps; each with a machine-checkable success_criterion.", { schema: PLAN })
const done = await pipeline(plan.steps,
  s => agent(`Execute: ${s.desc}`, { schema: STEP_RESULT }),
  (res, s) => agent(`Verify "${s.desc}" meets: ${s.success_criterion}. Return {met, evidence}.`, { schema: CHECK }))
```

### Scheduled producers (cadence, not iterate-to-done — route to /routines-builder)

**T12 · scheduled-single-pass-producer** — solo / cloud routine / human-gate. *Recurring autonomous task, ONE output per run, then stop. NOT an iterate-until-criteria loop.* Stop: output pushed to `claude/<name>/<date>` + log line + Telegram digest; cap = daily plan cap. Servy: `routines/opportunity-engine.md`, `capability-radar.md`, `evolution-discovery.md`. → build via `/routines-builder`.

**T13 · threshold-accumulator** — solo / `/loop` self-paced or routine / judgment. *A signal must be confirmed N times across SEPARATE runs before graduating to a buildable action; probe-count-bounded, not time-bounded.* Stop: `probes >= THRESHOLD` (2) → auto-promote, loop stops visiting; dead verdicts evict. Servy: `scripts/backlog-util.py cmd_probe()` + `routines/evolution-dreaming.md` — **the only living stateful multi-cycle loop**.
```
# per run:   python3 scripts/backlog-util.py probe   --id <x> --verdict promising|dead
# at thresh: python3 scripts/backlog-util.py promote --id <x>   # → [capability]; loop stops visiting it
# state persists across runs in evolution-backlog.md
```

## Validation gates — the why (condensed)

1. **GOAL-IS-OBJECTIVE** — a subjective goal ("improve") gives the loop nothing to test against, so it drifts. Force `artifact + threshold + observable signal`.
2. **HARD-CAP-BOTH-BRAKES** — a done-check that never passes = a runaway bill. Require BOTH an objective check AND a numeric cap; inject safe defaults (`--max-turns 15` / `MAX_ITER=20`) with a WARNING if absent.
3. **VERIFIER-IS-INDEPENDENT** — an agent that controls its own check can overwrite tests, weaken assertions, or exit early to fake green (reward hacking). The grader must be a process the actor can't rewrite.
4. **NO-SELF-REVIEW-JUDGMENT** — same lineage = same blind spots. Judgment/maker-checker graders are a different lineage (Codex for Claude-actor output).
5. **DEDUPE-ALL-SEEN** — in loop-until-dry, dedupe vs ALL seen (Set outside the while), never vs *confirmed* — else judge-rejected findings reappear every round and it never converges.
6. **BUDGET-GUARD-BEFORE-SPAWN** — check `budget.total && budget.remaining() > 50_000` at the TOP of the body, before a full round fires. The half-a-subscription gate.
7. **PLACEMENT-CLOSED-LAPTOP** — `/loop`/bash die with the session; closed-laptop/multi-day → Cloud Routine or Managed Agent.
8. **REMOTE-SESSION-NO-LOOP** — `/loop` is disabled in remote/cloud sessions; redirect to a routine or `claude -p` + launchd.
9. **HUMAN-GATE-IRREVERSIBLE** — pause before delete/send/publish/pay/deploy/merge; unattended = branch + digest, never a silent action.
10. **WORKERS-ON-HAIKU** — fan-out workers on Haiku, synthesis on the session model; an Opus/Fable session makes every worker expensive by default.
11. **ADVERSARIAL-JUDGES-DIVERSE** — ≥3 *structurally different* stances (reproduce / refute / severity), not 3 identical refuters; diversity catches failure modes redundancy can't.
12. **CLOUD-ROUTINE-SUPERVISED-TEST** — watch one "Run now" before arming a recurring schedule (routines run as Gera).
13. **CONTEXT-ABOVE-TEN-TURNS** — past ~10 turns, summarize-and-handoff so context doesn't bloat (compaction alone doesn't hand off cleanly).
14. **STOP-HOOK-WIRED** — a `/goal` loop without a `Stop` hook wired to the done-check can't self-terminate; delegate the hook to `/hooks-builder`.
15. **RIGHT-PRIMITIVE-AND-MODEL** — smallest primitive that fits, cheapest model that suffices (official token rule); most tasks need no loop at all.
16. **PILOT-BEFORE-LARGE-RUN** — dynamic workflows can spawn hundreds of agents; gauge usage on a small slice first (the ~187-agent run above is the local proof).
17. **INTERVAL-MATCHES-CHANGE-RATE** — don't run a time-based loop more often than the watched thing changes; react to events where possible.
18. **SCRIPTS-FOR-DETERMINISTIC-STEPS** — running a script is cheaper than re-reasoning the steps each iteration (official example: a PDF skill shipping a form-filling script the loop just runs).

## Resolved contradictions (the research flagged 7; here's the coherent model)

1. **Ralph "stop hook" ≠ Claude Code `Stop` hook.** Two distinct mechanisms. `/goal` & `/loop` brake = a `Stop`-event hook in `settings.json`. A bash while-loop's brake = its own `until <check>` + `MAX_ITER`. Never conflate; the templates keep them separate (T1 vs T10).
2. **Self-paced `/loop`** = the model scheduling its own next wakeup (dynamic mode). **No living Servy implementation — it's a GAP**, stated honestly in T3.
3. **`/deep-research` is NOT a loop** — it's a built-in *width* workflow (fan-out + vote → cited report). Use it for research; don't model it as a depth loop. Out of the library by design.
4. **Reflexion memory is loop STATE, not knowledge.** It lives in a loop-scoped state file (e.g. `.loop-state/reflections.md` or alongside the task), **never** `knowledge/` — `wiki-protocol.md` defines `knowledge/` as immutable raw sources; interpreted facts graduate to the wiki, loop state does neither.
5. **`warden` (same-lineage) vs Codex (cross-lineage).** T7 marks same-lineage lint as the *weaker* gate (ok for low-stakes) and requires Codex for persistent/shipped artifacts (No-Self-Review).
6. **Budget guard placement is type-specific, not contradictory.** loop-until-budget (T6) guards at the TOP on `budget`; loop-until-dry (T4) uses a `dry`-counter (no budget guard needed). Both correct for their type.
7. **Ingestion auto-merge-before-review** is a pre-existing Servy gap (tracked in `agent-loops.md`), not this skill's concern — but T7/T12 require the cross-lineage review BEFORE "shipped" for any new loop that emits persistent artifacts, so new loops don't repeat it.

## Related
- `references/agent-loops.md` — doctrine. `references/claude-code-loops.md` — official taxonomy + usage/quality rules. `.claude/skills/workflow-builder/reference.md` — workflow JS API (co-build for workflow loops).
- `references/routine-placement-framework.md` — placement gate. `references/agentic-engineering-patterns.md` — patterns 1 + 7 implementation map.
- `.claude/workflows/exhaustive-review.js` — living loop-until-dry + 3-judge verify. `scripts/backlog-util.py` — living threshold-accumulator. `scripts/test-gate.py` — functional-verification false-green guards.
