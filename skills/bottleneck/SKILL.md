---
name: bottleneck
description: Use when Gera wants to find what's actually limiting his business or money progress — "find the bottleneck", "what's the constraint", "theory of constraints review", "why isn't revenue moving", "what should I fix first in the business", "business review". Theory-of-Constraints review over the REAL pipeline numbers (attention → leads → conversion → delivery → retention → cash → hours) that names THE single constraint and builds an action strategy around it. Personal / Penguin Alley / freelance business ONLY — refuses SoftServe-internal business analysis (data boundary).
argument-hint: [optional: scope, e.g. "penguin alley", "freelance", "the alley"]
---

## What this skill does

Finds the ONE constraint that governs everything else, using the Theory of Constraints (Goldratt), and turns it into an action strategy. The premise: a business is a pipeline, and total throughput equals the narrowest stage — Jack's Lamborghini example: 100 bonnets/week, 500 paint jobs/week, **1 engine/week** → you ship 1 car/week, and getting better at paint changes nothing. Working on anything except the constraint is motion, not progress. (The pipe is a *diagnostic model*, not a literal equality — real stages have conversion rates, lag, and demand-quality effects; the point is finding where flow narrows most, not computing exact throughput.)

Source: Jack Roberts' Theory of Constraints business review (video `1DOLq8xy0qI`, 2026-07-04, `knowledge/jack-fable5-five-things-1DOLq8xy0qI.md` [12:49-14:04]); his exact prompt is gated in his Skool group, so this implements the method from the video. Servy twist: we don't interview for numbers we already have — **read the ledgers first.**

## Gate 0 — scope check (hard)

Personal and Penguin Alley / freelance business only. If the ask is about SoftServe strategy, team throughput, Jumpstart pipeline, or anything Internal+ → refuse and point to Claude Desktop (Enterprise) / Cowork. Same rail as every money session.

## Step 1 — ground in the real numbers (before any question)

Read, in order:
1. `money/MISSION-1M.md` — the $1M ledger; only verified dollars count (standing rule for money sessions).
2. `money/GERA-NOW.md` + latest `money/audit-*.json` if present.
3. `projects/REGISTRY.md` — what's shipped, what state it's in.
4. Latest PA CEO brief: `ls pa/ceo-briefs/*.md 2>/dev/null | sort | tail -1` — if none exist, mark PA-brief evidence UNKNOWN and move on (never fabricate the org's read).
5. `context/priorities.md` — this quarter's stated focus.
6. `pending.md` — open loops (hours leak into these).

Build the pipeline table from evidence, marking each stage KNOWN (with the number + source) or UNKNOWN:

| Stage | What it measures | Evidence found |
|---|---|---|
| Attention | people who see us (posts, views, followers) | |
| Leads | people who raise a hand (DMs, signups, Workana invites) | |
| Conversion | leads → paying (proposals sent/won, pricing) | |
| Delivery | can we ship what's sold (capacity, quality) | |
| Retention | do they stay/return (churn, repeat) | |
| Cash | does money actually arrive (invoiced vs collected, costs) | |
| Hours | Gera's real available hours after SoftServe | |

## Step 2 — fill only the gaps (short interview)

Ask ONLY about UNKNOWN stages — one question at a time, max ~5 questions, each with your best-guess answer attached so Gera can confirm or correct. Do not re-ask what the ledgers already say.

**When UNKNOWN cells dominate the table**, open with Nate's 5x diagnostic (6h course [2:13:30]): *"If tomorrow you got 5x the customers going through your pipe, what would break first?"* — it forces a mental walk of the day-to-day and surfaces where flow stops faster than stage-by-stage questions. Flag: this is the **client-facing wording** — the phrasing to reuse when scoping constraints with a client (Jumpstart conversations included; the wording travels even though this skill's data never does).

## Step 3 — name THE constraint

Pick **one** stage. Not a top-3, not "several areas need work" — the whole ToC review turns on naming a single constraint. State it with the evidence chain: *"Throughput is capped at X because [stage] only does Y, while every stage before it can do 10Y."* If two stages genuinely tie, pick the one earlier in the pipeline and say why.

**UNKNOWN-heavy guard:** if the stages critical to the call are still UNKNOWN after the interview, do NOT manufacture certainty — name a **provisional constraint** (labeled as such, with confidence low/med) and make this week's first move *instrumentation* (start measuring the unknown stage), not optimization. "Evidence over vibes" outranks "pick one."

Sanity check the classic trap: **Hours is usually the hidden constraint for a solo operator with a day job** — verify whether the named constraint would still bind if Gera had 20 more hours/week. If not, Hours is the real constraint.

## Step 4 — the five focusing steps → action strategy

Apply Goldratt's sequence to the named constraint:

1. **Identify** — done (step 3).
2. **Exploit** — squeeze the constraint as-is: what gets 20% more out of it with zero new resources this week?
3. **Subordinate** — everything else serves the constraint: what should Gera STOP doing because it feeds a non-constraint? (Be specific — name current activities from pending.md/priorities that don't feed the constraint.)
4. **Elevate** — only if exploit+subordinate aren't enough: what investment (automation, delegation to the PA agents, a tool, money) widens the constraint?
5. **Repeat warning** — name the likely NEXT constraint once this one breaks, so the fix doesn't overshoot.

Default Shift applies at every step: for each action, ask "to what extent could AI/the PA agent org do this instead of Gera's hours?"

## Output

Write `money/bottleneck/{YYYY-MM-DD}-review.md` (create the dir if needed) with: the pipeline table + evidence, the named constraint + reasoning, the 5-step strategy, and **this week's 3 moves** (concrete, constraint-serving, small enough to start now). Summarize in chat leading with the constraint, not the process.

Then:
- Offer to log the strategy decision to `decisions/log.md` (Gera decides — suggest, don't auto-log).
- Append deferred moves to `pending.md` tagged `[gera]`/`[servy]`.
- If the constraint implicates a PA agent's lane (e.g. Leads → pa-outreach gate, Conversion → pa-proposal-writer), say which agent owns the follow-through.

## Notes / guardrails

- **Evidence over vibes:** every number in the pipeline table needs a source (file or Gera's explicit answer). No invented percentages — UNKNOWN is a valid and useful cell.
- **One constraint.** Resisting the urge to fix everything IS the method. If Gera pushes for a broader list, deliver the one constraint first, then park the rest in pending.md.
- **Not /roast, not /audit:** `/roast` attacks an idea before building; `/audit` scores the AIOS itself (Four Cs); `/bottleneck` analyzes the operating business's flow. If Gera brings a new idea to bottleneck, route to `/roast`.
- **Money data stays where it lives:** amounts and client names in `money/` (committed, private repo) are fine; never copy them into public-facing artifacts or posts. Minimize client identifiers even internally (first name or initials once context is clear), respect NDAs/platform ToS (Workana names stay in `money/`), and sanitize anything that leaves `money/bottleneck/` — a pending.md reminder says "follow up on the July constraint plan", not the client or the number.
- Cadence: worth re-running monthly, or after any constraint-breaking event (first paid client, a product shipping, schedule change).
- Effort: ledger-reading and gap questions run cheap (low/default); the constraint call and strategy are the "first 20% that sets all the quality" — escalate to high there (Jack's rent-Einstein rule).
