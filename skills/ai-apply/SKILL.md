---
name: ai-apply
description: Use when Gera wants to decide whether AI genuinely belongs in a task or workflow, and at what depth - "should I use AI for this", "does AI fit here", "is this worth automating", "where does AI help in X", "assess this for AI", "AI applicability check", "/ai-apply". Walks the 6-question AI Applicability Framework one question at a time (grill-me style, each question carrying a recommended answer inferred from context), then files a completed assessment with an adopt / augment / skip verdict. Personal and public-data work only - never routes SoftServe customer data or Internal+ IP through the multi-brain. Distinct from /grill-me (extracts existing knowledge) and the builders (build one artifact); this one DECIDES whether to build at all.
argument-hint: [task or workflow to assess]
---

# /ai-apply

The front-door decision skill: given a task or workflow, walk Gera through the AI Applicability Framework one question at a time and land an honest **adopt / augment / skip** verdict. It answers "to what extent can AI be leveraged here?" before any build starts.

This is the *judgment* half of deciding what to build. It sits one step upstream of `/build`, `/skill-builder`, `/level-up`, and the rest of the builder family — those build the thing; this decides whether the thing is worth building, and in what shape.

The question sequence, the "what a good answer looks like" notes, and the scoring rubric are the **AI Applicability Framework** — read `references/ai-applicability-framework.md` (the generic version + scoring section) before running. That page is the source of truth; this skill is the interview that walks it and files the result.

## When to use

- Gera invokes `/ai-apply` or says "should I use AI for this", "does AI fit here", "is this worth automating", "where does AI help in X", "assess this for AI", "AI applicability check".
- He's about to build/automate something and you (or he) aren't sure AI is the right call, or aren't sure how deep to go.
- Distinct from neighbors: `/grill-me` extracts knowledge Gera already holds; the builders' Discovery Interviews are tied to building ONE artifact; this skill DECIDES whether to build at all. If he's already decided to build and just wants it built, skip straight to `/build`.

If he didn't ask and there's no live decision on the table, don't manufacture work.

## The boundary (read this before the data question)

This skill is for **personal and public-data** tasks only. The moment a task touches SoftServe Internal+ material or customer IP/code, the assessment itself must not route any of that content through the multi-brain (Codex / Gemini / local brains) or through Servy. Question 5 is the explicit gate; if it blocks, the verdict is SKIP-or-RE-ROUTE and you say so plainly. See `references/softserve-ai-usage-policy.md`.

## Setup — do this BEFORE the first question

1. **Pick the task + slug.** From `$ARGUMENTS` if given, else ask one line: "What task or workflow are we assessing?" Make a kebab slug.
2. **Get today's date:** `date +%F`.
3. **Read the framework:** `references/ai-applicability-framework.md` — the generic 6-question version and the adopt/augment/skip rubric. Also skim the `## Knowledge base` + `## Multi-LLM orchestration` sections of `CLAUDE.md` and `context/priorities.md` so your recommended answers reflect his real stack and current priorities.
4. **Create the assessment file** at `knowledge/ai-applicability/{YYYY-MM-DD}-{task-slug}.md` (create the `knowledge/ai-applicability/` folder if it doesn't exist). Seed it with the template below: title, date, the task in one line, empty per-question log, empty verdict.
5. **Tell Gera where you're saving**, in one line. Then ask Q1.

## The checkpoint rule (non-negotiable)

After EVERY answer, BEFORE the next question:
- **Append** the question's captured answer + the decision it drove to the assessment file (use Edit). Keep his wording where it matters.
- **Update** the running notes if a later answer changes an earlier one.
- **Only then** ask the next question.

Never batch. The file, not your context window, is the source of truth — if the session drops, the file already holds everything decided so far. (Same discipline as `/grill-me`.)

## Interview method — one question at a time, with a recommended answer

Walk the six questions **in order** (each upstream answer shapes the ones below it). For each question:

1. Ask it in plain words.
2. **Offer your recommended answer** — your best inference from his context (CLAUDE.md, the wiki, the repo, the task description) — so Gera can confirm, correct, or redirect instead of starting from blank. This is the grill-me move: never make him fill a void you could pre-fill.
3. Capture his actual answer + the decision it drives, checkpoint, then move on.

**Explore instead of asking** where you can — if a step is answerable from a file or the repo, read it rather than asking. **Flag and move on** if only a stakeholder knows (e.g. a manager, a client). Match `references/voice.md` — warm, plain, low jargon, first person, no em dashes. This is a conversation, not an interrogation.

### The six questions (full notes in the framework page)

1. **What is the task, and could it just stop existing?** — drives ELIMINATE vs CONTINUE. (If eliminate, you may be done — verdict SKIP.)
2. **Is this a real constraint, or just annoying?** — drives PRIORITIZE vs DEFER.
3. **Can you explain the steps clearly enough to hand to a person?** — capture the five elements (Trigger, Data Sources, Transformations, Decision Points, Destination); drives READY-TO-SCOPE vs MAP-FIRST.
4. **What share can AI realistically do, and where does a human stay?** — capture the 60/30/10-style split + the starting autonomy level (L0–L4); drives the AUGMENT-vs-AUTOMATE shape.
5. **Does it touch confidential/customer data — and is the channel allowed?** — the hard gate; drives PROCEED vs RE-ROUTE vs BLOCK.
6. **What number does this move, and how will you roll it out safely?** — capture one KPI + a phased rollout; drives GREEN-LIGHT vs PARK.

Early-exit allowed: if Q1 lands on eliminate, or Q5 hard-blocks with no re-route, you can short-circuit to the verdict — still checkpoint the answers you have and record why you stopped.

## Score the verdict

After the six answers, apply the rubric from the framework page (a guide, not arithmetic — one hard NO can sink a strong case):

- **SKIP** if any of: Q1 says eliminate, Q5 blocks with no legal re-route, or Q6 finds no number it moves. SKIP is a real, valuable outcome — name it without apology.
- **AUGMENT** (AI-assisted, human in the loop — the 30% lane) when the process is legible (Q3), Q4 keeps a meaningful human-review share, and you'd start LOW (L1–L2). The safe default for most worthwhile tasks.
- **ADOPT / AUTOMATE** (toward hands-off — the 60% lane) only when ALL hold: real constraint (Q2), fully legible process (Q3), large no-human-touch share (Q4), in-bounds channel (Q5), a concrete KPI (Q6), and a phased rollout. Don't jump straight to L4.

When it lands between AUGMENT and ADOPT, take AUGMENT and let real-usage data promote it later. Default to the lowest autonomy level that works; prefer boring/deterministic over clever.

## At the end — write the verdict, recap, hand off

1. **Finalize the assessment file:** fill the `## Verdict` block — the call (ADOPT / AUGMENT / SKIP), the starting autonomy level, the KPI, the data-channel ruling, and a two-line "why this call."
2. **Recap to Gera** in chat, terse: the verdict, the one reason that drove it, and the suggested next step.
3. **Hand off by verdict:**
   - **ADOPT / AUGMENT** → suggest the right builder via Servy's triage (script / multi-brain pre-checks, then Skill vs Agent vs Routine), and offer to kick off `/build` or the specific builder. Pass the captured process map along — it's the start of the Discovery Interview.
   - **SKIP** → done. Optionally note it so the same idea doesn't keep resurfacing.
4. If the task should graduate into the wiki as reusable knowledge (a process Gera will reuse), offer that per `references/wiki-protocol.md` — don't auto-write without his yes.

## Assessment file template

```
# AI Applicability: {Task}
Date: {date} · Task: {one line}

## Per-question log
### Q1 — Could it just stop existing?
- Recommended: {your inferred answer}
- Captured: {his answer}
- Decision: {ELIMINATE | CONTINUE}

### Q2 — Real constraint or just annoying?
- Recommended / Captured / Decision: {...}

### Q3 — Can you explain the steps to a person?
- Process map: Trigger / Data Sources / Transformations / Decision Points / Destination
- Decision: {READY-TO-SCOPE | MAP-FIRST}

### Q4 — What share can AI do, where does a human stay?
- Split: {fully-auto % / AI-assisted % / manual %}
- Starting autonomy level: {L0..L4}

### Q5 — Confidential/customer data, allowed channel?
- Data class: {public | personal | SoftServe Internal+ | customer IP}
- Decision: {PROCEED | RE-ROUTE | BLOCK}

### Q6 — What number does it move, rollout?
- KPI: {metric in a bucket}
- Rollout: {phased plan}

## Verdict
- Call: {ADOPT | AUGMENT | SKIP}
- Starting autonomy level: {L0..L4}
- KPI: {...}
- Data channel: {ruling}
- Why this call: {two lines}
- Next step: {builder / route / done}
```

## Notes / guardrails

- **One question at a time. Always.** Each carries a recommended answer so Gera can confirm or redirect.
- **Never skip a checkpoint.** Append to the file after every answer.
- **SKIP is a win, not a failure.** Don't talk Gera into a build the framework says to skip.
- **The data gate (Q5) is hard.** Personal/public-data only; never route SoftServe Internal+ or customer IP through Servy or the multi-brain. When in doubt, BLOCK and route to an approved tool.
- **Don't invent answers.** If only a stakeholder knows, flag it with an owner and move on.
- This skill is interactive — it stays in the live session (do not fork to an isolated agent).
- It's a decision skill, not a builder. When the verdict is ADOPT/AUGMENT, hand off to the right builder; don't start building inside this skill.
