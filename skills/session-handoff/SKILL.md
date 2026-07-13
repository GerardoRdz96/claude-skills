---
name: session-handoff
description: Use when Gera wants to wrap up, clear context, switch machines or tools, or continue work in a fresh session — "hand off", "wrap up this session", "save where we are", "I need to clear context", "write a handoff", "we're at the token ceiling", "/session-handoff". Prints AND saves a structured handoff note (started / decisions locked / shipped / key files / running state / verification / deferred / next steps / gotchas) so the next session — in Claude Code, a Cowork tab, Codex, Gemini, or any tool — picks up exactly where this one left off without re-deriving anything. The cheapest insurance an AIOS has against context loss.
argument-hint: [optional: topic or destination of the handoff]
disable-model-invocation: true
---

## What this skill does

Generates a **tool-agnostic handoff note** for the current session: one markdown block a fresh session can read to continue the work cold. Servy is multi-LLM (Claude Code + Cowork + Codex + Gemini + local brains), so the note must orient *any* of them — name files by full path, never "the file we edited".

Doctrine: `references/claude-code-context-management.md` (#22 — the **~120k-token ceiling**: cross ~12% of the 1M window → ask for a full summary → `/clear` → paste it back; #23 session chaining: discovery → planning → execution as separate warm-started sessions). *Pattern credit: Nate Herk — "if you keep retyping the same prompt, that's a skill."*

## When to fire

- Gera says he's done for now, switching tools (Claude Code ↔ Cowork ↔ Codex/Gemini ↔ another machine), or context is filling.
- **Proactively offer one line** (don't insist) when a long session is clearly winding down, or when `/context` / the statusline shows the thread past the fire band: **~120k tokens** (conservative Servy default) — **250-300K on 1M-window models** (Nate's ~25%-of-window rule, 2026-07-11 Nate 6h course [2:00:48]).
- **New-build vs same-build key** (Nate [5:19:16]): starting a *different* project/build while context is high → hand off for a fresh window; still editing and improving the *same* build → stay in the session, the warm context is the asset.
- A **3rd–4th `/compact`** is about to be needed — quality degrades past 3–4 compacts in a row [5:38:39], hand off instead.
- Gera is **stepping away for more than ~1 hour** (the subscription cache TTL): the next message will reprocess everything cold anyway, so bank the state now [5:52:54].

## Sibling boundary — pick the right tool

- **`/session-handoff` (this skill)** — general, tool-agnostic, any session. Use for "wrap up / switch tools / clear context / save where we are". Output is a portable note + a saved file.
- **`/gsd-pause-work`** — mid-GSD-phase pause that writes GSD's own state files; use only inside an active GSD phase. `/gsd-resume-work` restores it.
- They compose: inside a GSD phase that's also ending the day, run `/gsd-pause-work` for the phase state, then `/session-handoff` for the human-readable cross-tool note.

## The handoff template

Produce this filled in from the ACTUAL session — concrete paths and command-ready next steps, never vague summaries. Drop any section that's genuinely empty rather than padding it.

```
# Session handoff — {YYYY-MM-DD} — {topic}

## Where we started
- {the goal/request that opened the session}

## Decisions locked (don't relitigate)
- {decision} — why: {one line}  ({link to decisions/log.md if logged})

## Shipped this session
- {completed item, with file paths + commit SHA if committed/pushed}

## Key files (the map for a cold start)
- {path} — {what it is / why it matters now}

## Running state (live as of handoff)
- Branch: {branch} · pushed: {yes/no} · build/tests: {green/red/last result}
- Background work: {any routines armed, agents/workflows mid-run, deploys in flight}

## Verification deferred
- {anything shipped but NOT verified end-to-end — what's untested and the command/check that would verify it}

## In progress / next steps
1. {next concrete action, specific enough to start cold — include the command if there is one}

## Waiting on Gera (gates)
- {decision or manual step only he can do}

## Gotchas for the next session
- {anything surprising: a failing test, a quirk found, a constraint, an env caveat}
```

## Where it goes

1. **Print it in chat** (always — Gera may just copy it into the next session). The resume path is `/copy` → `/clear` → paste into the fresh session: takes **under a minute**, vs a slow `/compact` — and autocompact fires too late to save quality anyway (Nate 6h course, 2026-07-11 [5:53:25]).
2. **Save it** to `knowledge/handoffs/{YYYY-MM-DD}-{slug}.md` (create the folder if needed). `knowledge/` is the immutable drop zone — a handoff is a session artifact, it lives here, not in the wiki.
3. **Reconcile the trackers** (don't duplicate — point):
   - Any follow-up that would otherwise be lost → append to `pending.md` and say you did.
   - If a decision was made this session and isn't logged → offer to add it to `decisions/log.md`.
   - Don't write to `references/log.md` unless the session actually ingested/shipped wiki work (that's the wiki timeline, not a session journal).

## Guardrails

- **Report honestly.** If something is half-done, broken, or unverified, the handoff says so plainly. A flattering handoff is a useless handoff — the next session inherits the lie.
- **Tool-agnostic.** No "the function we just wrote" / "that file" — absolute paths and real names, because the reader may be Codex or a cold Claude with zero history.
- **Under a page.** Orientation, not a transcript. If it's growing past a screen, you're journaling, not handing off.
- **Don't act on the work** — this skill writes the note and reconciles trackers; it does not keep building. Wrapping up means wrapping up.
