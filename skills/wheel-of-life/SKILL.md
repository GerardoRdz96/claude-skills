---
name: wheel-of-life
description: Use when Gera wants a life review or life check-in — "wheel of life", "life review", "rate my life", "how's my life balance", "life check-in", "how am I really doing", or a quarterly personal review. Interview-based 9-spoke life assessment (Health body/mind/soul · Work growth/money/mission · Relationships family/romance/friends) scored 1-10 on satisfaction with the energy invested, grounded in behavioral evidence, ending in a breakdown + action plan. SAFETY - if Gera didn't explicitly ask for a life review, OFFER first ("want me to run the wheel of life on you?") and wait for yes; never launch a long personal interview on a passing comment.
argument-hint: [optional: focus area, e.g. "health" or "compare with last run"]
---

## What this skill does

A structured life review: interview Gera one question at a time across the 9 spokes of the wheel of life, score each 1-10, then deliver the honest breakdown — where the wheel wobbles, why, and the 3 highest-leverage actions. The wheel metaphor is the point: you can be firing on all cylinders at work, but if health is a 3 the whole wheel thumps on every rotation.

Source: Jack Roberts' Wheel of Life review (video `1DOLq8xy0qI`, 2026-07-04, `knowledge/jack-fable5-five-things-1DOLq8xy0qI.md` [02:15-04:15]); the full prompt is gated in his Skool group — this skill implements the structure *visible on screen* (frame pass + his live demo, not the full gated text): **five phases — Picture (interview) → Scores → Diagnosis → Strategy → Operating System** — with the rules "listen and probe, no advice until we've got the full picture," find **the single constraint throttling everything else** (his phrasing, verbatim from the demo), and end with a **90-day plan + weekly operating cadence**. Interview mechanics borrow from `/grill-me` (one question at a time, checkpoint every answer).

## The 9 spokes

| Area | Spokes |
|---|---|
| **Health** | Body (physical health, sleep, food, movement) · Mind (focus, stress, learning) · Soul (peace, purpose, joy) |
| **Work** | Growth (skills, career trajectory) · Money (income, savings, debt) · Mission (does the work matter to you) |
| **Relationships** | Family · Romance · Friends |

The score is NOT "how good is this area" — it's **satisfaction with the current investment and its visible results** (1 = neglected, 10 = fully invested and it shows). If Gera is investing hard but unhappy with results, that's a mid score plus a note on *why* — the gap between effort and result is diagnostic gold.

## Setup — before the first question

1. `date +%F` for today's date.
2. Create the capture file `knowledge/grills/{YYYY-MM-DD}-wheel-of-life.md` (knowledge/ is gitignored — this stays private). Seed it with: date, the 9-spoke table (scores empty), empty Q&A log, empty Findings.
3. **Check for a previous run:** `ls knowledge/grills/*wheel-of-life*`. If one exists, read its scores first — this run becomes a trend comparison, and say so up front.
4. Pull what Servy already knows so questions start smart, not cold: `context/about-me.md`, `context/priorities.md`, `money/MISSION-1M.md` for Mission/Money, and (if the Money spoke comes up) `python3 scripts/finances.py` for period state. **Any of these missing, stale, or erroring → proceed without it and note the gap in the capture file** — never block the interview on a file, and never invent its contents. Never make Gera re-state what the repo already knows — confirm it instead.

## Interview method — behavioral evidence, then the score

This is Jack's key move (and what makes the review honest): **don't ask "rate your body 1-10" cold.** First ask for concrete recent behavior, THEN propose a score he can correct.

- Per spoke: 1-2 behavioral questions max. The pattern for Body (from the video): *"Walk me through yesterday physically — what time you woke up, how you felt waking, what you ate and drank, when you actually fell asleep."* Adapt the same shape per spoke (Mind: "what did you last learn on purpose?"; Friends: "when did you last see one, not counting work?").
- One question at a time. After each answer, **checkpoint to the capture file before asking the next** (the `/grill-me` rule — the file is the source of truth, not your context).
- After the evidence, propose: *"That sounds like a 6 — fair?"* Gera confirms or corrects. His number wins.
- Spanish or English, whichever he's speaking. Keep it warm — this is a check-in with a friend, not an audit.
- If `$ARGUMENTS` names a focus area, do only that area's spokes (still with evidence-first).
- Pace: ~15-20 questions total for a full wheel. Offer a break at each area boundary ("Health done — keep rolling into Work?").

**No advice during the interview.** Jack's rule, and it's right: listen and probe only until the full picture exists. Advice leaks bias into later answers.

## Output — diagnosis, strategy, operating system

When all spokes are scored, walk the remaining phases, writing each into the capture file and delivering in chat:

1. **The wheel (Scores):** all 9 scores, visually (a simple markdown table + a one-line shape read: "strong work side, wobbly health side"). Plus trend deltas if a previous run exists.
2. **Diagnosis:** the 2-3 lowest spokes, the *pattern* connecting them (they're rarely independent), and **the single constraint** — the one spoke that, fixed, lifts the others (Jack's framing; ToC thinking, same engine as `/bottleneck`). **Escape hatch:** if no single spoke defensibly controls the others, say so and name the strongest *pattern* instead — never force a constraint that isn't there.
3. **Strategy:** a **90-day plan** built around that constraint — exactly 3 actions, each small enough to start this week. Not 10 actions — 3.
4. **Operating system:** the weekly cadence that keeps it alive — what gets checked, when, and where it lives (route Money moves to `/finances`, Growth to `/rnd`, deferred items to pending.md tagged `[gera]`).

Offer (don't force) an HTML wheel artifact: `artifacts/wheel-of-life/{date}-wheel.html` with an SVG radar chart of the 9 scores (+ previous run's outline as ghost overlay if it exists). If built, it goes through `frontend-design` + `scripts/frontend-review.sh` like any visual artifact (Front-End Review Law), and gets the standard ~30-60s video abstract unless Gera says no video.

## Cadence

At the end, note in the capture file when the next run is due (**quarterly** default) and offer to append a `[gera]` reminder to `pending.md`.

## Notes / guardrails

- **Private by design:** captures live in gitignored `knowledge/grills/`. Never copy scores or personal details into committed files (wiki pages may reference that a review happened + themes, never the raw answers). This includes `pending.md` and `decisions/log.md`: reminders written there are **sanitized** ("quarterly wheel re-run due October", "start the Body action from the July wheel") — no scores, no health/relationship specifics.
- **Not therapy, not coaching-guru:** plain warm honesty. If something heavy surfaces (health scare, relationship crisis), drop the process and just be a good listener; the wheel can wait.
- **No SoftServe content:** the Work spokes are about Gera's satisfaction and trajectory, not SoftServe internal specifics. If the conversation drifts into Internal+ material, nudge to Claude Desktop per the data boundary.
- **Don't score for him.** Propose from evidence, but the number is his call.
- Effort: Jack's own doc says run the interview at **low** and escalate only for the diagnosis/strategy phases — the questions don't need big brain, the synthesis does. Follow that.
