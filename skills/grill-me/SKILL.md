---
name: grill-me
description: Use PROACTIVELY whenever Gera is working something OUT OF HIS HEAD rather than asking a quick question — he's mulling or scoping a plan/design/decision, describing a process or how he does something, floating a half-formed idea, or wants to capture/document/scope knowledge before building. Natural signals (he will rarely say "grill me"): "I've been thinking about…", "I have an idea for…", "I want to build/plan/figure out…", "I'm not sure how to approach…", "let me think this through", "help me scope/organize this", "here's how I do X", "I keep doing X by hand", or any long mulling-out-loud message. Also the explicit "grill me", "interrogate me", "stress-test this", "extract this into the wiki", "/grill-me". The relentless one-question-at-a-time extraction engine that captures his thinking to a durable doc and graduates it into the wiki. SAFETY: unless he explicitly asked to be grilled, OFFER first ("want me to grill you on this and capture it?") and wait for yes — never silently launch a long interview on a quick question. Distinct from brainstorming (explores NEW design space) and the builders' discovery interviews (tied to building ONE artifact); grill-me extracts EXISTING knowledge/decisions Gera already holds.
argument-hint: [topic to grill on]
---

## What this skill does

Relentlessly interview Gera about every aspect of a topic until you reach shared understanding. Walk down each branch of the decision tree, resolving dependencies one by one. The real goal is to **extract what's in Gera's head into a durable, organized markdown file** so nothing is lost as context fills up — and then **graduate** that capture into Servy's wiki so the knowledge compounds.

This is the general-purpose extraction engine Servy was missing. The builders (`/skill-builder`, `/agent-builder`, …) each run a Discovery Interview tied to building one artifact. This skill grills Gera about *anything* — a business process, a Jumpstart engagement detail, a plan, a design, a codebase decision — for its own sake, and files the result.

Source + doctrine: `references/grill-me-skill.md`. Original by Matt Pocock; Nate Herk's checkpointing fork in `knowledge/grill-me-source/grill-me-SKILL.md`. Servy adaptation: captures live in `knowledge/grills/`, **not** a parallel `brainstorms/` folder, and they graduate into `context/` or `references/` per `references/wiki-protocol.md`.

## When to fire — and offer vs. just go

This skill should catch Gera even when he never says "grill me." Watch for the **situation**, not the phrase: he's mulling a plan/design/decision out loud, describing a process or "how I do X," floating a half-formed idea, or scoping something before a build. That's a grill opportunity.

But the cost of getting it wrong is asymmetric — silently launching a 30-question interview when he wanted a quick answer is worse than a missed trigger. So:

- **He explicitly asked** ("grill me", "interrogate me on this", "/grill-me", "stress-test this") → **just go.** Start the interview.
- **You inferred the opportunity** (he didn't say it) → **OFFER first, one line, then wait:** *"Sounds like there's a lot in your head here — want me to grill you on it and capture it into the wiki? (it's a relentless one-question-at-a-time session)"* Only start if he says yes. If he says no or just wants the quick answer, drop it and answer normally.
- **It's a genuine quick question** (a fact, a small fix, a yes/no) → **do not fire.** No offer.

Don't collide with neighbors: if he's exploring brand-new design space, that's `brainstorming`; if he's building one specific artifact, that's the relevant builder's own discovery interview. Grill-me is for extracting knowledge and decisions he **already holds**.

## The capture file is the whole point

Long interviews fill up context. If you hold answers only in your head, you will eventually misremember, conflate, or drop something. So you **checkpoint to disk after every single answer**. The file, not your context, is the source of truth. Never make Gera ask you to save progress.

## Setup — do this BEFORE the first question

1. **Pick the topic + slug.** From `$ARGUMENTS` if given, else ask Gera one line: "What are we grilling on?" Make a kebab slug.
2. **Get today's date:** `date +%F`.
3. **Create the capture file** at `knowledge/grills/{YYYY-MM-DD}-{topic-slug}.md` (create the `knowledge/grills/` folder if it doesn't exist). Every grill capture lives here — one predictable home, regardless of topic. Do NOT scatter captures into project folders or invent a `brainstorms/` folder.
4. **Seed it immediately** with the template below: title, date, the goal of the session, empty Summary, empty Q&A log, empty Open flags.
5. **Tell Gera where you're saving**, in one line. Then ask Q1.

## The checkpoint rule (non-negotiable)

After EVERY answer Gera gives, BEFORE you ask the next question:
- **Append** a structured entry to the capture file (use Edit): the question topic, the key facts and decisions from his answer (in his words where the wording matters), and any flags (things he couldn't answer + who can).
- **Update or correct earlier entries** if a later answer changes them. Keep the running Summary current.
- **Only then** ask the next question.

Never batch multiple answers into one write. Checkpoint one answer at a time. The point is that if context is lost at any moment, the file already holds everything said so far.

## Interview method

- Ask **one question at a time.** For each, provide **your recommended answer** (your best inference from his context — CLAUDE.md, the wiki, the repo) so Gera can simply confirm, correct, or redirect.
- **Resolve dependencies in order:** settle the upstream decision before the ones that depend on it.
- **Explore instead of asking.** If a question can be answered by reading a file, the codebase, or the wiki, do that instead of asking. If Gera hands you a doc, read it and only surface what's net-new.
- **Flag and move on.** When Gera can't answer something (only a stakeholder knows — e.g. the manager, a client, a coworker), capture it as a flag with the right owner and move on. Don't stall.
- **Keep going** until Gera says you're done or you've covered every branch. Near the end, offer a completeness backstop: "Anything we haven't touched?"
- Match the voice rules in `references/voice.md` — warm, plain, low jargon. This is a conversation, not an interrogation transcript.

## Capture file template

```
# {Topic}: Grill / Discovery Notes
Date: {date} · Goal: {one line}

## Summary / key decisions
(running synthesis, updated as you go)

## Q&A log
### Q1 — {topic}
- Asked: {question}
- Captured: {facts, decisions, in Gera's words where it matters}
- Flags: {open item -> owner}
...

## Open flags (pending input)
- {item} -> {who can answer}
```

## At the end — reconcile, then graduate (the Servy step)

1. **Final reconciliation pass:** read the whole capture file for contradictions or gaps and fix them. Make the Summary stand on its own.
2. **Recap to Gera** in chat: what's captured, what's still flagged (with owners), and the suggested next step.
3. **Offer to graduate** the polished knowledge into Servy's wiki, and **propose the destination** per `references/wiki-protocol.md`:
   - Business / domain / "about Gera or the work" facts → a `context/` file.
   - Reusable knowledge, a framework, an entity/concept page → a `references/` wiki page (new or folded into an existing one); then update `references/index.md` and append a `## [date] ingest` line to `references/log.md`.
   - A plan/spec/design that will drive a build → the relevant `docs/` or `projects/` spot.
   Name the target you recommend and why; let Gera confirm, redirect, or defer. Don't auto-write into the wiki without his yes (Bike Method — keep him in the loop).
4. **Propagation scan (related artifacts).** A grill usually surfaces nuance that existing artifacts are missing. After reconciliation, scan `.claude/skills/*/SKILL.md` names + descriptions and `references/index.md` for anything related to the grill topic — a skill, a wiki page, a guide. If you find matches, offer Nate-style: *"You have a packaging skill and a packaging page, and we covered nuance that's in neither — want me to fold it in?"* On his yes, fold only the specific new nuance into each artifact (smallest faithful edit, never a rewrite). Same consent rule — propose, don't auto-write. (Nate's end-of-grill move, 2026-07-11 course [4:27:46].)
5. **Glossary harvest (English-term capture).** Grills are full of English technical terms Gera stumbled on — those belong in the working glossary so they don't evaporate. After reconciliation, run `python3 scripts/glossary-harvest.py --capture knowledge/grills/{file}.md`. It proposes new terms only (bolded terms, acronyms, "what is X" asks, multiword domain phrases), already deduped against `references/tech-comm-glossary.md`. Show Gera the proposed block, fill the `<plain definition>` and `<say-it-in-a-meeting sentence>` for the ones he keeps, and **on his yes** append them under the right `## Category` heading in the glossary. Same consent rule as the rest of graduation — propose, don't auto-write. Generic knowledge only; never put customer specifics on that page.
6. If Gera defers graduation, the capture stays in `knowledge/grills/` and you log a one-line follow-up in `pending.md`.

## Re-running

Grills are re-runnable. To deepen or update an existing capture, open the same `knowledge/grills/` file and say "grill me again on this" — append new Q&A, reconcile against earlier entries, re-offer graduation.

## Notes / guardrails

- **One question at a time. Always.** Batching defeats the purpose and overwhelms Gera.
- **Never skip a checkpoint.** The file is the source of truth, not your context window.
- **Don't invent answers.** If only a stakeholder knows, flag it with an owner — don't fill the gap with a plausible guess.
- **No parallel knowledge store.** Captures go in `knowledge/grills/`; polished knowledge graduates into the existing `context/` / `references/` structure. Never create a `brainstorms/` folder.
- **Don't graduate without consent.** The wiki is Servy's source of truth; a grill capture is raw working material until Gera approves the promotion.
- This skill is interactive and conversational — it must stay in the live session (do not fork to an isolated agent).
