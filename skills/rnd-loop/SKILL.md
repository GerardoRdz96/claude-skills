---
name: rnd-loop
description: Use when Gera wants to run the FULL R&D loop on a topic — research it, then actually test it, and come out with a decision — not just one half. Triggers — "run the r&d loop on X", "research and prototype X", "rnd-loop X", "take X from question to decision", "should we adopt X (and prove it)", "full loop on X", "/rnd-loop". The powerful workflow that chains the two halves of an R&D Engineer's job: /storm-research (what is true about X) → pick the hypothesis worth testing → /spark (build a throwaway spike, measure it, decide GO/NO-GO/PIVOT). Emits one R&D dossier linking the verified research briefing and the feasibility verdict. The single front door for "I have a question and I want to end with a defensible decision."
argument-hint: "[the topic/technique to research then test]"
---

# /rnd-loop — research → prototype → decide

## Why this exists

An R&D Engineer's job is a loop, not two errands: **Scan → frame a hypothesis → spike → evaluate → decide → capture.** `/storm-research` owns the front (Scan). `/spark` owns the back (spike → decide). `/rnd-loop` is the thin conductor that runs the whole arc on one topic and hands Gera a single **R&D dossier**: the verified briefing *and* the evidence-backed verdict, linked. Use it when the goal is not "tell me about X" or "test X" but **"I have a question and I want to end with a decision I can defend."**

It is glue, not a new engine — it sequences the two proven engines with a human gate where it matters (a real R&D Engineer chooses *what* to test). Wiki: `references/rnd-instrument.md`.

## Gate 0 — SoftServe refusal

Inherits BOTH halves' boundary, at the stricter end (the loop ends in *running code*). Refuse if the topic or any spike would touch SoftServe customer IP/code/strategy or Jumpstart specifics — run it in the `ss` instance / a SoftServe-approved tool. Public / personal / Penguin-Alley topics proceed.

## The loop

**1 — Research (Scan).** Run `/storm-research` on the topic in full (5 lenses → contradiction map → synthesis → citation-verify → Codex verdict → HTML briefing). Save the briefing JSON; you will feed it to the spike framer. Show Gera the 60-second summary.

**2 — Frame + pick (HITL).** Run the spark engine's `frame` stage on the briefing:
```
Workflow({ scriptPath: ".claude/skills/spark/spark.workflow.js",
           args: { stage: "frame", idea: topic, briefing, reader, goal } })
```
Present the ranked experiments. **Gera picks the one hypothesis worth a spike** (or `--auto` → #1, state the assumption). This is the hinge of the loop — research becomes a testable bet. Stop and let him choose unless told to run unattended.

**3 — Spike → decide.** Hand off to `/spark` from its Phase 2: build the throwaway spike → assess (route by artifact_type to `/verify-loop` / `/eval` / `/prompt-eval` / a direct benchmark) → run the engine's `verdict` stage → Codex final verdict → render the HTML feasibility verdict (Front-End-Review-Law'd).

**4 — Dossier + capture.** Emit a short index that links the two artifacts as one **R&D dossier**:
- the STORM briefing → `artifacts/research/<date>-<slug>.html`
- the SPARK verdict → `artifacts/research/<date>-<slug>-verdict.html`

Both render steps also emit the source JSON into the combined dossier at `artifacts/research/<slug>.dossier.json` (via `scripts/arc-dossier.py`, upserting one half at a time), which is what **The Arc** dashboard (`rnd-arc/`) reads to auto-populate over time.

Then capture (Phase 5 of `/spark`): file durable learnings to the wiki, log `/rnd` XP for a completed loop, and name the next move (a GO points at a `/build`; a PIVOT points at the next experiment; a NO-GO is a documented week saved).

## Notes

- **The human gate is non-negotiable by default.** The loop pauses between research and spike so Gera picks the bet. `--auto` exists for unattended runs but should state every assumption it made.
- **One loop, one hypothesis, one decision.** If the research surfaces several bets worth testing, run the loop once per bet (or queue them) — do not braid three spikes into one muddy verdict.
- **Cost shape:** STORM (~10–14 agents) + spark frame (~4) + spark verdict (~4) + the spike build + 2 Codex passes. Far cheaper than it looks, and you can say so. For a quick gut-check use the halves directly; reach for `/rnd-loop` when the topic deserves the full arc.
- **Distinct from its parts:** `/storm-research` alone = knowledge, no test. `/spark` alone = test an idea you already hold, no research front. `/rnd-loop` = the whole instrument, research-grounded and evidence-closed.
- Match `references/voice.md` through the phases.
