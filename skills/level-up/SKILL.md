---
name: level-up
description: Use weekly to find and ship one new automation. Walks the 3Ms interview — Mindset (find the candidate) → Method (scope one) → Machine (build it). Trigger on "let's level up", "what should I automate next", "find me leverage this week", or as a Friday ritual. One run = one shipped artifact.
---

> *Adapted from The Three Ms of AI™. © 2026 Nate Herk. All rights reserved.*
> *The Three Ms of AI™ is a trademark of Nate Herk.*

## What this skill does

Walks Gera through the 3Ms each week to surface and ship one new automation. **One interview = one artifact.** It also installs the 3Ms framework into Gera's head over time — after 4-6 runs, he starts spotting opportunities mid-week without prompting because the questions have become internal defaults.

This is the brain-rewire mechanism. Servy doesn't need cron jobs to anchor this behavior; it needs `/level-up` running every Friday.

## What `/level-up` is NOT

- Not `/audit`. `/audit` is structural ("is the AIOS built right?"). `/level-up` is functional ("what business leverage am I missing?"). Run `/audit` first if structure is messy.
- Not a multi-candidate planner. One run = one shipped artifact.
- Not a coach. Gera does the thinking. The skill conducts the interview.

## When `/level-up` runs

- **Cadence: weekly, Friday afternoon.** Review the week, surface one automation, ship Monday.
- **On-demand any time.** Mid-week if a manual task itches.

## Inputs the skill reads

- `context/priorities.md` — what Gera said matters
- `context/about-me.md` — top_pain, role
- `connections.md` — what's reachable, by what mechanism
- `references/3ms-framework.md` — the framework (used to quote principles back)
- `references/ai-consultant-path-framework.md` — the constraint-first lens (rank candidates by the business constraint they gate, not by frequency; doctor-not-pharmacist)
- `decisions/log.md` — recent decisions (what's already shipped or considered)
- `.claude/skills/*/SKILL.md` frontmatter — what capabilities exist
- Recent `audits/audit-{date}.md` if present

## Execution — three phases

### Phase 1 — Mindset interview (find the candidate)

Surface 1-3 candidates ranked by leverage. Ask these in order, conversationally:

1. *"Walk me through your week. What did you do 3+ times?"* (frequency)
2. *"Anything that felt manual, boring, or copy-paste?"* (drudgery)
3. *"Anything where you thought 'a smart intern could handle this'?"* (delegation)
4. *"If 500 new clients showed up tomorrow, what would break first?"* (constraint)
5. *"What would give you 500 more clients tomorrow?"* (growth lever)
6. *"What are your triggers? Every time X happens — a lead lands, a specific type of email arrives, a ticket comes in — what do you HAVE to do next?"* (event → obligation)
7. *"What do you do every Monday? Every Friday?"* (cadence)

Q6–Q7 are the trigger audit (Nate 6h course, 2026-07-11 — three chapters converge on it). Candidates they surface are usually **routine-shaped**: they fire on something predictable, and an automation Gera must fire by hand keeps him as the trigger — *"if you're not around to trigger it, nothing happens."* Expect these to route to a **routine** (self-firing), not a manual-fire skill, when they reach Phase 3's Skill-vs-Agent-vs-Routine call.

Quote relevant Mindset principles when they fit:
- *"Sounds like the Default Shift applies — to what extent could AI be leveraged here?"*
- *"This is the Function Breakdown — you're not automating the whole job, just this one piece."*
- *"AI is better than you think and improving faster than you think. If it couldn't do this last quarter, it might be ready now."*

**Output of Phase 1:** numbered list of 1-3 candidate opportunities, one-line "why this is leverage" per candidate. **Rank by the constraint lens, not by frequency** — the top candidate is the one *gating a real business constraint* (slows the team, gates revenue, causes downstream pain), not merely the most repetitive: *"if you automate something that isn't actually constraining the business, you just saved 20 minutes nobody was waiting on."* Be the doctor, not the pharmacist — name the real problem before scoping the build (`references/ai-consultant-path-framework.md`). Ask: *"Pick one to scope."*

### Phase 2 — Method interview (scope one)

Gera picks one candidate. Walk the 5-step Method pipeline:

**Step 1 — Find the constraint.** Which bottleneck does this solve, or which growth lever does it open? Tie back to Phase 1 answers.

**Step 2 — EAD: Eliminate / Automate / Delegate.**
- **Eliminate first:** *"What happens if we just stop doing this?"* If the answer is "nothing breaks" → skill exits cheerfully. *"Don't automate waste."* This is a win, log to `decisions/log.md` and stop.
- **Automate second:** apply 60/30/10 framing. ~60% deterministic, ~30% AI-assisted, ~10% manual.
- **Delegate third:** if too complex/variable/judgment-heavy → suggest a person. Skill exits with a delegation suggestion, log it.

**Step 3 — Map the process.** Five elements:
- Trigger (what kicks it off)
- Data sources (where info comes from)
- Data transformations (how data changes shape)
- Decision points (where it branches)
- Destination (where output goes)

If Gera can't articulate any of the five: *"If you can't explain it to a person, you can't explain it to an AI. Sketch it on paper first, then come back."* Skill stops.

**Step 4 — Pick the autonomy level.**

| Level | Name | What happens |
|---|---|---|
| L0 | Manual | No AI |
| L1 | Suggested | AI suggests, human decides every step |
| L2 | Drafted | AI drafts, human reviews and edits |
| L3 | Supervised | AI runs, human validates periodically |
| L4 | Autonomous | AI handles end-to-end |

**Default = lowest level that solves the problem.** Push back on L4 unless Gera has explicitly run lower levels first. *"Workflows beat agents. If a decision doesn't HAVE to be made by AI, don't let AI make it."*

**Step 5 — Tie to a KPI.** Which of the Three Buckets does this move?
- More customers
- More value per customer
- Less cost

Plus a specific metric (response time, error rate, conversion rate, time-to-completion). **If Gera can't name a bucket and a metric, skill stops.** *"If your automation doesn't move a number, why are you building it?"*

The metric needs **direction + target**, not just a name — "5 leads/week today → 15/week", agreed BEFORE building starts. Seal it with the alignment test: *"if we hit this number, does everyone call this a success?"* If not, rescope. The target is also the STOP condition: hitting it formally ends the build phase and the automation moves to **maintenance mode** — improvements can come later, the heavy lifting is done; a shipped user-facing product flips to `maintenance` in `projects/REGISTRY.md`. *"A clear definition of done is what keeps you from scope-creeping on yourself."* (Nate 6h course, 2026-07-11 [0:19:49] + [2:14:31].)

**Output of Phase 2:** scoped automation spec written to `decisions/log.md` as a dated entry with all five answers + autonomy level + KPI. Durable record of what was decided and why.

### Phase 3 — Machine handoff (build it)

Ask: *"How do you want to ship this?"* Options ordered by Boring-is-Beautiful default:

1. **Prompt-only** — saved prompt template Gera runs by hand. Zero infrastructure. Highest manual involvement.
2. **Deterministic skill** — SKILL.md that runs a script (no AI step). Best for transformations with clear rules.
3. **AI-assisted skill** — SKILL.md with one AI call inside. Drafts, classifies, summarizes.
4. **Sub-agent** — multi-step agent. Last resort. Only if the work genuinely needs reasoning + tool use.

**Default selected = highest non-AI option that solves the problem.** Gera has to explicitly choose more autonomy.

Once chosen, route to the appropriate scaffolder:
- `skill-creator` if available globally (Anthropic-shipped)
- `skill-builder` (Servy has it locally)
- Otherwise write a SKILL.md / agent file inline with frontmatter, location, and contents

**Every scaffolded artifact ships with these two headers at top:**

```markdown
---
bike-method-phase: 1  # Phase 1 — Training wheels. Run manually first.
three-ms-attribution: |
  Adapted from The Three Ms of AI™ © 2026 Nate Herk.
---
```

This locks every new build into Phase 1 of the Bike Method — no silently skipping manual validation. Phase advances only by explicit edit.

Surface the Machine principles when scaffolding:
- **Lego Principle** — smallest steps, zero-AI first if possible
- **Validation Chain** — test each step before chaining
- **Iteration Mindset** — ship the POC, expand from real usage

## Output contract

Every `/level-up` run produces:

1. **One `decisions/log.md` entry** — dated, with the Method spec
2. **One scaffolded artifact** — prompt, skill, or agent file
3. **A one-screen close** — what was scoped, what was built, and the Bike Method Phase 1 reminder

## Critical implementation rules

1. **One interview = one artifact.** No multi-candidate parallel scoping.
2. **Mindset phase always runs first.** Even if user comes in with a pre-formed idea.
3. **EAD enforces "eliminate first."** If the answer is Eliminate, exit cheerfully — that's a win, not a failure.
4. **Default to the lowest autonomy level that works.** Push back on L4.
5. **Boring-is-Beautiful default in Machine handoff.** Default = highest non-AI option.
6. **Tie-to-KPI is mandatory.** If Gera can't name bucket + metric (with direction + target), skill stops.
7. **Bike Method ships into every artifact.** `bike-method-phase: 1` in frontmatter.
8. **Read-only on Gera's files except `decisions/log.md` and the new artifact.** Don't modify other existing files.
9. **Trademark + attribution on output.** Every report and every scaffolded artifact references the framework.

---

> *The Three Ms of AI™ is a trademark of Nate Herk. © 2026 Nate Herk. All rights reserved.*
