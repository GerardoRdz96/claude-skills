---
name: build
description: Use when Gera asks to build, implement, or ship a non-trivial feature/system/component, says "build this", "implement X", "let's build", "run this through the pipeline", or types /build. Routes the work through the doctrine pipeline — triage → plan (Superpowers) → execute by dominant risk (Superpowers TDD vs GSD) → adversarial review (Codex). Redirects width-shaped tasks to a dynamic workflow instead.
argument-hint: [what to build]
---

## What this skill does

Operationalizes Servy's build doctrine: **plan with Superpowers → execute by which risk dominates → always close with adversarial review.** It is a *router*, not a builder — its job is to pick the right primitive and sequence, then hand off to Superpowers / GSD / Codex / a workflow. Doctrine source: `references/claude-code-power-skills.md` (the pairing + risk-routing + the 2026-06-01 benchmark) and `references/claude-code-workflows.md` (depth-vs-width).

Read both doctrine pages' relevant sections if the routing call is non-obvious. Otherwise follow the stages below.

---

## Stage 0 — Triage (decide whether the pipeline even applies)

Four gates, in order. **Announce the verdict of each.**

**Gate A — Width check (pipeline vs workflow).** Ask: *"Does this break into many independent pieces that run at the same time?"* (e.g. migrate 50 call-sites, review 30 files, audit every skill, research many sources).
- **Yes → this is a workflow, not the pipeline.** Stop here. Tell Gera, and redirect: propose a dynamic workflow (`references/claude-code-workflows.md`), or `/deep-research` if it's a research question. If each independent piece *also* needs to be built well, the shape is "a workflow whose stages run this pipeline" — say so.
- **No → continue to Gate B.**

**Gate B — Triviality check (skip the heavy process).** Is this a small, well-specified, single-file-ish change?
- **Yes → skip the pipeline.** Just build it inline, or use `/gsd-fast` for a trivial atomic task. The benchmark showed zero quality gain from the heavy process on tiny well-specified work, and Superpowers adds ~8% overhead on simple tasks. Say "this is trivial, building it directly" and do it. Still offer the Codex review at the end if anything was subtle.
- **No → run the full pipeline (Stages 1–3).**

**Gate C — Idea gate (`/roast`, money pipeline).** If this is a *new product / feature / business bet* (a thing Gera could sell, launch, or spend real build-time on) rather than a scoped implementation task, run **`/roast` FIRST** — the 5-persona council returns GO/RESHAPE/KILL + the cheapest 48h test before any code. A KILL or RESHAPE here saves the entire build. Skip for clearly-scoped implementation work (a bug fix, a refactor, an internal tool). Source: `references/nate-money-upgrades.md`.

**Gate D — Definition of done (KPI gate).** Anything headed into the full pipeline names its *done* BEFORE Stage 1 plans a thing. For a product / feature / business build: **one metric + direction + target** ("5 leads/week today → 15/week"), sealed with the alignment test — *"if we hit this number, does everyone call this build a success?"* If the honest answer is no, rescope until it is. For internal tooling with no business number, name the observable definition of done instead (what behavior, verified how). The target is also the STOP condition: hitting it formally ends the build phase — no perpetual nice-to-haves; a shipped user-facing product flips to `maintenance` in `projects/REGISTRY.md`. *"A clear definition of done is what keeps you from scope-creeping on yourself."* (Nate 6h course, 2026-07-11 [0:19:49] + [2:14:31]; closes the 2026-06-15 definition-of-done gap. `/level-up` Phase 2 Step 5 carries the same gate.)

If invoked automatically on a build request, this stage is also where you **confirm before spawning anything** — state the route you're taking and proceed unless Gera redirects.

---

## Stage 1 — Plan with Superpowers

Invoke the Superpowers planning chain on the task:
- `superpowers:brainstorming` if the requirements/design aren't settled yet (this is the default front door for anything ambiguous).
- Then `superpowers:writing-plans` to produce ONE plan artifact with bite-sized, testable steps and exact file paths.

The plan is the shared contract for whatever executes it. **Do not skip planning** — correctness is won here. Keep the plan in the project (not a global scratch dir).

**YAGNI gate (before the plan is final):** run the plan through `/ponytail` — cut every step, dependency, and abstraction that doesn't earn its place (deleting an idea is free at plan time, expensive after execution). Never cut validation/security/data-loss/accessibility — lazy ≠ negligent. The leanest correct plan goes to Stage 2. (Ladder + rules live in the skill.)

---

## Stage 2 — Execute, routed by the dominant risk

State which risk dominates and which route you're taking, then execute. Default routing:

| Dominant risk | Route | How |
|---|---|---|
| **Bug-cost** — tricky logic, money/financial math, algorithms, heavy edge cases, security/auth, data integrity | **Superpowers TDD** | `superpowers:test-driven-development` (+ `subagent-driven-development` if there are independent tasks). Test-first red→green per task, then self-review twice (spec match + code quality). Pay the ~2.5× time/token premium because a bug here is expensive. |
| **Context-rot** — long, multi-file, many tasks, "hand it off and walk away" | **GSD** | `/gsd-autonomous` (or `/gsd-plan-phase` → `/gsd-execute-phase`). Import the Stage-1 plan via `/gsd-import` so GSD executes the same contract. Fresh subagent per task keeps context clean across the long haul; scope-drop + verification gates apply. |
| **Both** | **Hybrid** | GSD for the breadth/bulk, Superpowers TDD on the 1–2 critical modules (the financial/algorithmic/security core). |
| **Iterative-correctness** — the task must run *until a verifiable bar is met* (tests green, rubric pass, coverage/threshold reached), not just built once | **`/loops-builder`** | Scaffold an agent loop with both brakes (objective done-check + numeric hard cap) and the right mechanism (`/goal` + Stop hook, bash/Ralph, or evaluator-optimizer). The loop drives the build *to* the bar; Codex still reviews the result at Stage 3. Doctrine: `references/agent-loops.md`. |

If the dominant risk is genuinely ambiguous, ask Gera one question to disambiguate (bug-cost vs context-rot). Otherwise infer, state your read, and proceed.

**Self-verify before review (standing rule).** Every execution prompt (whichever route) ends with: *"Once built, verify your own work the way a human would — run it, click through it (Playwright/browser for UIs), and walk it as 3 personas (beginner / engineer / business owner): can each one understand and use it? Fix what the walkthrough surfaces before reporting done."* Self-verify-by-doing lifts first-pass quality ~70%→92% (Nate Herk's field number, Fable second-brain video). It runs *upstream of* — never instead of — Stage 3's adversarial review: Codex should only ever see code that already survived its own walkthrough. Doctrine: `references/claude-code-power-skills.md`. **For any UI / user-facing / form / landing surface, the formalized version of this rule is `/verify-loop`** — the definition-of-done loop + adversarial stress-test (malformed inputs); use it instead of an ad-hoc walkthrough. Source: `references/nate-money-upgrades.md`.

---

## Stage 3 — Adversarial review (always-on closer for non-trivial builds)

**This stage is not optional.** The benchmark's strongest finding: both build processes shipped latent bugs their own gates missed and still passed the tests — only the adversarial pass caught them.

1. **Codex review (always).** Per the **No-Self-Review Law**, route the produced code to Codex — never self-review. Run via Bash:
   ```
   git diff | codex exec --skip-git-repo-check "Adversarially review this diff against the spec/plan. Hunt for REAL bugs: edge cases, off-by-one, rounding/float, validation holes, state leaks, security. List each with a line ref. End with 'BUGS: <n>' and 'QUALITY: <1-10>'."
   ```
   (Or point Codex at the changed files if there's no diff yet.) Surface Codex's findings to Gera and fix the real ones — applying `superpowers:receiving-code-review` discipline (verify before implementing, don't blindly agree).
2. **`/ultra-review` (propose, never auto-run).** If the change is high-stakes — auth, payments, data migrations, a big refactor — *propose* `/ultra-review` before merging. It bills money (3 free, then ~$5–20) and takes 10–20 min, so **ask Gera first** (CLAUDE.md hard rule). Never launch it yourself.
3. **Front-End Review Law (any UI / landing / visual surface — mandatory).** Codex reviews *code*, not how it *looks*. If the build has a front-end, it is not done until it passes the visual gate: it must have been built *through* `frontend-design` + `taste-skill` (Stage 2, never hand-rolled defaults), and you must run `scripts/frontend-review.sh <url>` — it screenshots desktop+mobile and routes them to a vision model (different lineage = no self-review for design) for a `BLOCK/PASS` anti-slop verdict. **Ship only on PASS**; fix the TOP_ISSUES and re-run on BLOCK. A public-repo product also needs a README with images. Doctrine: `references/front-end-review-framework.md`.

---

## Output & close

- A built, reviewed feature with Codex findings addressed.
- If the work is on a branch and complete, offer `superpowers:finishing-a-development-branch` to decide merge/PR/cleanup. Follow git-safety rules — confirm before anything touching the remote.
- **If what shipped is a launchable product or offer** (not an internal tool), offer the **`gtm-kit`** workflow — idea → full go-to-market kit (positioning, market research, launch plan, outreach, content calendar) via 6 parallel agents. The money-pipeline close: roast (validate) → build → verify-loop → **gtm-kit (go to market)**. Source: `references/nate-money-upgrades.md`.
- Summarize: what was built, which route was taken and why, what Codex found, what's left.

## Notes & guardrails

- **You are the router, not the implementer.** Delegate execution to Superpowers/GSD; delegate review to Codex. Keep the main session clean.
- **Never auto-launch `/ultra-review`** — always ask (it costs money). Codex review *is* auto for non-trivial builds.
- **Never self-review** the code you just produced — Codex only (No-Self-Review Law).
- **Don't force the pipeline onto trivial or width-shaped work** — that's what Stage 0 is for. Misrouting wastes tokens.
- **N=1 honesty:** the risk-routing defaults come from a single benchmark run. If a routing call feels wrong for the task in front of you, trust the task over the table and say why.
- **Anthropic best-practices are binding.** Any LLM / agent / prompt / eval / tool / skill / MCP work inside the build follows `references/anthropic-best-practices.md` (eval on the production model · dataset matches production · pin the model id · one technique per eval iteration · precise tool descriptions · workflow-before-agent). Doctrine, not optional — it's how Anthropic says to use Claude.
- Match `references/voice.md` when talking to Gera through the stages.
