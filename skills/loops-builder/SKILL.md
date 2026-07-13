---
name: loops-builder
description: Designs, builds, optimizes, or audits an AGENT LOOP — the depth primitive that runs reason→act→observe until an objective done-check passes, always with a mandatory hard cap. Type `/loops-builder` when something should iterate until a verifiable criterion is met (tests green, gate passed) rather than run once. It builds the loop but NEVER fires it — build is cheap, fire is expensive.
argument-hint: [loop goal, or existing loop/skill name to optimize/audit]
disable-model-invocation: true
---

# /loops-builder

Builds **agent loops**: the depth primitive that runs reason→act→observe until a *verifiable* done-check passes, bounded by a mandatory hard cap. Sibling of `/workflow-builder` (width fan-out), `/routines-builder` (cadence), `/agents-team-builder` (peer crew), `/skill-builder`, `/agent-builder` — that family picks the mechanism; this one is the DEPTH-loop specialist, operationalizing `references/agent-loops.md` the way `/workflow-builder` operationalizes `references/claude-code-workflows.md`. Flow: decision gate (is this even loop-shaped? → route if not) → 6-round Discovery Interview (goal+done-check, verification, shape, mechanism, hard cap, confirm) → 18 validation gates → emit the right loop skeleton for the chosen mechanism. The loop-engineering doctrine lives in `references/agent-loops.md` — read it before building. The copy-pasteable **template library** (14 templates), the full gate detail, and the per-mechanism mechanics live in [reference.md](reference.md) — read it before emitting any skeleton.

**The one load-bearing fact (from the doctrine):** a loop has **no model-side terminator** — it runs until an operator, schedule, or cap stops it. So *the human must supply the brake*. Every loop this skill emits ships with BOTH an **objective done-check** AND a **numeric hard cap**. No exceptions.

**Official taxonomy (Claude Code team, 2026-07-06).** Four loop types map 1:1 onto this skill's routes: **turn-based** = a plain prompt (our "just ask / skill" route — sharpen it by encoding verification as a skill); **goal-based** = `/goal` (an evaluator model checks your criterion at each stop attempt — deterministic criteria like tests-passed or a score threshold converge best); **time-based** = `/loop` (local watched session) and `/schedule` (Cloud Routine) — match the interval to how often the watched thing changes; **proactive** = `/schedule` + `/goal` + dynamic workflows + auto mode composed, no human in real time. Wiki page: `references/claude-code-loops.md`.

## Phase 0 — Source check (silent)

Confirm `references/agent-loops.md` and this skill's [reference.md](reference.md) exist. If either is missing, stop and tell Gera which to restore. Don't build a loop from memory — the mechanics (`/goal`, `/loop`, Stop hooks, the workflow API) drift.

## Phase 1 — Decision gate (mandatory)

Don't ask "what loop?" yet. **First confirm the task is loop-shaped**, then which tier. Most tasks do NOT need a loop (doctrine: "the majority of tasks don't need loops"). One AskUserQuestion summarizing the task; route away on any of these:

**NOT loop-shaped → route elsewhere and STOP:**
- Fixed, predictable, known-step-count path → **script** (`scripts/`) or a plain **skill** (`/skill-builder`).
- Single-shot, no iteration → **just ask Claude** (official *turn-based* loop — improve its verification with a skill, don't add a loop).
- Splits into many independent pieces that run at the same time (WIDTH, not depth) → **`/workflow-builder`**.
- Recurring cadence, single-pass per fire (no iterate-until-criteria) → **`/routines-builder`** / **`/servy-routine`** (official *time-based* `/schedule`).
- "Done" cannot be stated as a machine-checkable proposition → **do NOT loop**; fix the goal first, or do it by hand (a loop with no checkable done-criterion drifts forever).
- Task touches SoftServe Internal+ / customer data → **BLOCK** any multi-brain or cloud-routine loop skeleton; that data class isn't an approved channel (`references/softserve-ai-usage-policy.md`).

**Loop-shaped → which control-flow owner?** (Anthropic's dividing line)
- Code can enumerate the steps up front → that's a *workflow* (evaluator-optimizer, plan-execute, fan-out). The loop still belongs here if it iterates to a bar, but the artifact is a `.claude/workflows/*.js` — co-built with the `/workflow-builder` reference.
- The LLM must decide the next step at runtime (step count unpredictable) → autonomous agent loop. **Proceed.**

**Which tier? Climb only when needed (doctrine: START SOLO).**
solo → maker-checker (quality matters, maker can't grade itself) → manager-helpers (fans into N parallel pieces). Default to solo. Pin the tier in Discovery, not here.

## Phase 2 — Preflight (state once)

- **Cost reality.** Loops burn tokens fast — one unbounded loop "begs for your session limit"; an unguarded workflow burned half a $200/mo sub in ~30 min. Start small + bounded, then scale.
- **Placement.** If the loop must survive a closed laptop or run for days, it is NOT a `/loop` or bash while-loop (those die with the session/terminal) — it's a Cloud Routine. Apply `references/routine-placement-framework.md`.
- **Verification is the point.** Anthropic's Agent SDK calls "verify your work" the most underrated step. A loop is only as good as its done-check. Functional verification is the default — reach for it first.

## Phase 3 — Discovery Interview

AskUserQuestion, one round at a time; skip rounds already answered. Stop when 95% confident. Full rationale per question in [reference.md](reference.md).

**Round 1 — Goal + done-check (BLOCK until answered).** (1) The task in one sentence (outcome, not process). (2) The single most concrete DONE signal — file+content check, test exit code, count reached, API status; never "looks good"/"until satisfied". (3) Can a bash one-liner / test answer yes/no with zero human opinion? If yes → functional. If no → why? (4) Is the done-criterion **reachable** (can it converge), or is it a moving target?

**Round 2 — Verification type + grader.** (1) Must the output be SEEN (rendered/image/PDF) to confirm? → visual (Playwright screenshot; reading source HTML does NOT count). (2) Does correctness need taste/domain judgment? → judgment: who scores it? **WARN if the scorer is the same model that produced it** (No-Self-Review). (3) Is any action irreversible (delete/send/publish/pay/deploy/merge-to-main)? List each → each gets a mandatory human-gate. (4) Name BOTH failure paths: verification fails before the cap, AND cap hit without passing.

**Round 3 — Loop shape + escalation.** (1) Many independent pieces at once? → width → `/workflow-builder`. (2) Need a separate checker grading the maker? → maker-checker; same model as maker? **WARN** → recommend Codex (cross-lineage). (3) Continues across context windows / overnight? → Ralph/loop-engineering template (state on disk). (4) Re-attempts the same goal across separate episodes and should learn from prior failures? → Reflexion template (reflections to a loop-state file).

**Round 4 — Mechanism + placement.** (1) Run when laptop closed / days unattended? → Cloud Routine (`/routines-builder`) or Managed Agent — a `/loop`/bash loop won't survive. (2) In a remote/cloud Claude Code session? → `/loop` is disabled there; use a Cloud Routine or `claude -p` + launchd. (3) One-time watched "run until done" → `/goal` or bash while-loop; recurring cadence → Cloud Routine. (4) Headless `/goal` (CI/script)? → `--max-turns N` is REQUIRED; no default exists.

**Round 5 — Hard cap + cost.** (1) Max iterations/turns before stop+escalate — name an explicit integer (default 10 interactive `/goal`, 20 bash `MAX_ITER` if undecided). (2) Token/cost budget — for workflows the `budget.total && budget.remaining() > 50_000` guard is mandatory; for `/goal` what's the acceptable spend before escalating? (3) Fan-out worker count — **WARN above ~40 workers**; workers on Haiku, synthesis on the session model. (4) Where does output land + who reviews before "shipped"? (cloud → `claude/<name>/<date>` branch + Telegram digest with revert).

**Round 6 — Confirmation + pre-arm checklist.** Echo a fenced summary: name, done-check (exact command/condition), verification type + grader, shape, mechanism, hard cap (turns + budget), both failure paths, output landing. Then confirm: (a) for any persistent artifact (files/wiki/tools/PRs) a **cross-lineage Codex review** step is wired before "shipped"; (b) for cloud routines, a supervised "Run now" test will be watched before arming; (c) whether to open a `/hooks-builder` session for the Stop hook (required for `/goal`, recommended for any functional-verification loop). Get explicit yes before writing anything.

## Phase 4 — Validation gates

Block on any RED. Full detail in [reference.md](reference.md) (§Validation gates).

| Gate | Check | If RED |
|---|---|---|
| **GOAL-IS-OBJECTIVE** | Done-criterion = named artifact/state + measurable threshold/keyword + machine-observable signal | Block — return the `artifact + threshold + signal` template; reject "improve"/"until satisfied" |
| **HARD-CAP-BOTH-BRAKES** | Skeleton has BOTH an objective done-check AND a numeric cap | Block — inject safe defaults with a WARNING comment (`--max-turns 15` / `MAX_ITER=20`) |
| **VERIFIER-IS-INDEPENDENT** | The verifier is structurally isolated from the actor (a process the actor can't rewrite) | Flag reward-hacking risk (agent can overwrite tests / weaken asserts / fake-green exit) |
| **NO-SELF-REVIEW-JUDGMENT** | Any judgment/maker-checker grader is a DIFFERENT lineage (Codex for Claude-actor output) | Block — insert a labeled `codex` review step |
| **DEDUPE-ALL-SEEN** | Loop-until-dry dedupes vs ALL seen (Set declared OUTSIDE the while), never vs confirmed | Block — hoist the Set; else judge-rejected findings reappear forever |
| **BUDGET-GUARD-BEFORE-SPAWN** | Workflow loops check `budget.total && budget.remaining() > 50_000` at the TOP of the body | Block — the half-a-subscription gate |
| **PLACEMENT-CLOSED-LAPTOP** | Closed-laptop / multi-day → Cloud Routine or Managed Agent, not `/loop`/bash | Block the `/loop`/bash skeleton → `/routines-builder` |
| **REMOTE-SESSION-NO-LOOP** | Remote/cloud session → `/loop` is disabled | Redirect to Cloud Routine or `claude -p` + launchd |
| **HUMAN-GATE-IRREVERSIBLE** | Every irreversible action has a pause-for-approval block before it | Block — insert human-gate; in unattended loops replace stdin-block with branch+digest |
| **WORKERS-ON-HAIKU** | Fan-out workers on Haiku; synthesis on session model | Warn — add the model comment to worker calls |
| **ADVERSARIAL-JUDGES-DIVERSE** | Adversarial verify = ≥3 STRUCTURALLY different stances (reproduce / refute / severity) | Replace duplicate judges with the exhaustive-review.js triad |
| **CLOUD-ROUTINE-SUPERVISED-TEST** | Cloud-routine skeleton includes a watched "Run now" before arming | Block schedule-arming until a supervised run passes |
| **CONTEXT-ABOVE-TEN-TURNS** | Cap > 10 turns → a summarize-and-handoff / fresh-context step | Insert summarization at N/2 + hard handoff at N |
| **STOP-HOOK-WIRED** | `/goal` loops include a `Stop`-event hook wired to the done-check | Refer to `/hooks-builder`; label the gap in the skeleton |
| **RIGHT-PRIMITIVE-AND-MODEL** | Smallest primitive that fits + cheapest model that suffices (official token rule) | Warn — step down loop→`/goal`→skill→script; workers to Haiku |
| **PILOT-BEFORE-LARGE-RUN** | Any fan-out that can spawn many agents gets a small-slice pilot first (official) | Block the full run — emit the narrowed pilot invocation first |
| **INTERVAL-MATCHES-CHANGE-RATE** | `/loop`/`/schedule` interval matches how often the watched thing changes | Warn — lengthen the interval or react to an event instead |
| **SCRIPTS-FOR-DETERMINISTIC-STEPS** | Deterministic steps inside the loop run as scripts, not re-reasoned each turn | Warn — extract to `scripts/` and call from the loop |

## Phase 5 — Generate the artifact

Pick the template from [reference.md](reference.md) §Template library by (shape × mechanism × verification) and emit per the **output contract** for that mechanism:

- **`/goal`** (solo/maker-checker, watched) — emit the `/goal "<objective done-check>"` invocation + the `Stop`-hook spec (delegate the hook to `/hooks-builder`). No file unless a hook is wired. Headless → add `--max-turns N`.
- **`/loop` interval / self-paced** (solo polling, watched, session-bound) — emit the invocation string with the interval (or "self-paced"), the session-bound + machine-on caveat, and the Esc/Stop-hook brake. *Self-paced `/loop` has no living Servy implementation (GAP) — say so.*
- **bash while-loop / Ralph** (solo, exceeds one context window) — WRITE two files: `TASK_PROMPT.md` (goal + verifiable done-criterion + mistake-corrections) and the runner (`until <done-check>; do (( ++i > MAX_ITER )) && exit 1; …; done`, with `bash scripts/sacred-zones.sh --check-staged` as a pre-commit). The brake is the `until` done-check + the `MAX_ITER` guard INSIDE the body (don't fold the cap into the `until` condition — it can exit as if success), NOT a settings.json hook.
- **dynamic workflow** (loop-until-dry / -count / -budget, manager-helpers, adversarial-verify) — co-build the `.claude/workflows/<name>.js` with the `/workflow-builder` reference (house meta/phase/agent skeleton, bounds, dedupe, `.filter(Boolean)`). Don't duplicate that skill's API doc. **Cost multiplier (measured 2026-06-22):** loop-until-dry + per-finding 3-judge verify is `fresh-findings × judges × rounds` — one real run hit **~187 agents / 6.6M tokens**; cap `MAX_ROUNDS` at 2-3 for audits and bound findings-per-round. Invoke a brand-new saved workflow by **`scriptPath`** until the name-registry refreshes (it won't resolve by name on first run).
- **evaluator-optimizer / maker-checker (high-stakes)** — emit the JS with distinct maker/checker labels + a `codex exec --skip-git-repo-check "<rubric + artifact>"` cross-lineage check; the rubric is an enumerable JSON constant, never prose.
- **scheduled Cloud Routine** (single-pass producer / threshold-accumulator) — WRITE `routines/<name>.md` via the `/routines-builder` prompt template (Step 0 reconcile, branch push, supervised "Run now"). Threshold-accumulator calls `scripts/backlog-util.py probe/promote`. *This is single-pass, NOT iterate-until-done — say so.*

Self-check any JS with `node --check`. Self-check any shell with `bash -n`. **Never fire the loop.**

## Phase 6 — Output to chat

```
## Loop ready: <name> (<mechanism>)

Done-check: <exact command/condition>   ·   Hard cap: <turns> + <budget>
Verification: <type> (grader: <who>)    ·   Shape: <solo|maker-checker|manager-helpers>
Files written: <paths or "none — invocation only">

### Brake (both, always)
Objective: <the testable done-check>  ·  Cap: <the numeric limit>

### First run
Run SUPERVISED on a small/narrowed scope; watch ONE full iteration and confirm the done-check
actually flips before trusting it unattended. <If persistent artifacts: route the output to Codex.>

### Watch usage (official introspection)
`/usage` per-skill/subagent/MCP breakdown · `/goal` (no args) turns + tokens so far · `/workflows` per-agent tokens + stop any agent
```

## Phase 7 — Log + register

- Append `references/log.md`: `## [<date>] create | Loop — <name> (<mechanism>)` + one detail line.
- If the loop produces a reusable workflow/routine, register it where its family does (workflow → CLAUDE.md "Saved workflows" bullet; routine → `routines/` + CLAUDE.md). A one-off `/goal`/`/loop` needs no registration.
- New mechanics learned while building → update [reference.md](reference.md) here, not scattered notes.

## Mode 2 — Optimize / Mode 3 — Audit

**Optimize** (a loop misbehaves): read the artifact first — never optimize unread code. Symptom → fix: runs forever → no hard cap, or done-check not machine-checkable, or dedupe vs wrong set; confidently-wrong "done" → verifier not independent (reward-hacking) or same-lineage grader; cost spike → no budget guard / workers too big / unbounded fan-out; cloud loop dies → it was a `/loop`/bash loop that needed a Cloud Routine; `/goal` won't stop → Stop hook not wired to the done-check.

**Audit checklist** (per loop/skeleton): [ ] objective done-check (artifact+threshold+signal) [ ] numeric hard cap present [ ] verifier independent of actor [ ] judgment grader is cross-lineage [ ] irreversible actions human-gated [ ] dedupe vs ALL-seen if looping [ ] budget guard at top (workflows) [ ] placement matches survive-closed-laptop [ ] supervised first-run noted [ ] Stop hook wired (`/goal`) [ ] smallest primitive + cheapest model [ ] piloted on a small slice [ ] interval matches change rate [ ] deterministic steps scripted [ ] still matches its `agent-loops.md` doctrine entry.

## Notes / discipline

- **Never fire the loop for him.** Build = cheap (text/files); fire = expensive (tokens/$). Gera (or another skill) invokes it. Same rule as `/workflow-builder` and `/agents-team-builder`.
- **The prompt IS the loop.** The done-check and cap carry all the safety — write them tight.
- **Two brakes, always.** Objective done-check AND numeric cap. A loop with only one is a runaway bill.
- **Start solo.** Don't reach for maker-checker or fleets until a single agent genuinely can't keep up. Multi-agent loops are for hardcore-coder inner loops, not knowledge work.
- **Review of any persistent artifact routes to Codex** (No-Self-Review Law; official agrees — a second agent with fresh context is less biased). Same-lineage `warden`-style lint is the *weaker* gate — distinguish it.
- **Encode verification as skills.** (official) Manual check steps become a SKILL.md with tools to see/measure the result; the more quantitative the checks, the better the loop self-verifies.
- **Fix the system, not the instance.** (official) When a result misses the bar, encode the correction into the skill/rubric/TASK_PROMPT.md so every future iteration inherits it — never just patch the one output.
- Skill stays under 500 lines; template skeletons + gate detail live in [reference.md](reference.md).

## Related

- `references/agent-loops.md` — the loop-engineering doctrine (trigger·action·stop + verification, 4 verification types, 3 shapes, when-NOT-to-loop). This skill's source page.
- `references/claude-code-loops.md` — the OFFICIAL Claude Code loop taxonomy (turn-based / goal-based / time-based / proactive) + token-usage & code-quality rules; raw capture: `knowledge/claude-code-loops/2026-07-06-getting-started-with-loops.md`.
- [reference.md](reference.md) — the 14-template library (skeletons + Servy exemplars/gaps), full gate detail, mechanism cheat-sheet, contradiction resolutions.
- `references/claude-code-workflows.md` + `/workflow-builder` — the WIDTH sibling (fan-out); co-built for workflow-mechanism loops.
- `references/routine-placement-framework.md` + `/routines-builder` — the placement gate + cadence sibling.
- `/hooks-builder` — designs the `Stop`-event hook the `/goal` brake delegates to.
- `references/agentic-engineering-patterns.md` — patterns 1 (self-improving loops) + 7 (agent loops); the Servy implementation map.
- Sibling builders: `/skill-builder`, `/agent-builder`, `/agents-team-builder`, `/plugin-builder`, `/framework-builder`, `/servy-routine`.
