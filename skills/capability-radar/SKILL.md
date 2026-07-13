---
name: capability-radar
description: Use when Gera asks "what should we build", "any capabilities to build", "what's on the capability radar", "scan for build opportunities", "should this be a skill/agent/routine", or when you want to log/act on a detected build opportunity. The inward-facing sibling of the Opportunity Engine — it watches Servy's own work + Codex review output for capabilities worth building (skills, agents, teams, plugins, routines, hooks, workflows, scripts), auto-builds the safe ones (Tier-S at HIGH confidence + Codex BUILD verdict) and surfaces the rest as suggestions. Triggers — "capability radar", "what should we build", "build opportunities", "/capability-radar".
argument-hint: ["" (show candidates) | "build <pattern>" | "log" | "digest"]
---

## What this skill does

Capability Radar is the **detector** that closes the loop on Servy's self-evolution: it spots when there is *enough signal* to build one of the 8 capability types, then routes the decision through the **existing creation matrix** (`references/autonomous-entity-charter.md` §2) — it does NOT invent a new build pipeline. It is the inward sibling of the Opportunity Engine (`routines/opportunity-engine.md`): that one scouts the market for products to build *for users*; this one watches *our own work* for capabilities to build *for Servy*.

The deterministic half lives in `scripts/capability-radar.py` (signal capture, dedup, scoring). The **judgment half is this skill**: classify the artifact type + risk tier, run the Codex gate, and either auto-build or suggest.

Read the design spec once if unsure: `docs/superpowers/specs/2026-06-16-capability-radar-design.md`.

## The two-gate Codex coordination (the No-Self-Review Law, applied)

Codex appears at **two** points — never skip either:
1. **Pre-build validation** — before auto-building OR before promoting a HIGH suggestion, ask Codex whether it is worth building and whether the artifact type + tier are right. Codex's verdict (BUILD / SUGGEST / SKIP) gates the auto-build.
2. **Post-build review** — after any builder produces the artifact, Codex reviews it before it registers. (This is the standing No-Self-Review Law — Servy never reviews its own output.)

## Modes

### Mode A — show candidates (default: `/capability-radar` with no args)
1. Run `python3 scripts/capability-radar.py score --json`.
2. **Re-cluster near-duplicate pattern keys with judgment** (the engine only does exact-normalized matching — merging "build a foo skill" with "foo skill needed" is a judgment task the engine deliberately leaves to you).
3. Render a ranked table in chat: band · artifact guess · tier · signal count · sources · title. Lead with HIGH, then MEDIUM, then a one-line count of LOW watchlist items.
4. Offer the next action per HIGH candidate: build now (if Tier-S) or queue a suggestion (if Tier-X).

### Mode B — build a candidate (`/capability-radar build <pattern>`)
1. **Classify** with Servy's front-door triage — "Skill vs Agent vs Routine — decide first" (CLAUDE.md):
   - Needs to run unattended on a schedule/event? → **routine** (Tier-X) or **hook** (Tier-X).
   - Gera starts it, needs isolated context / restricted tools? → **agent** (Tier-S).
   - Interactive workflow we run together? → **skill** (Tier-S).
   - Many independent pieces fanned out at once? → **workflow** (Tier-S file / Tier-X when fired).
   - A small crew that talks peer-to-peer? → **agent-team** (Tier-S template / Tier-X when fired).
   - Deterministic, no judgment? → **script** (Tier-P/S).
   - Shippable bundle for distribution? → **plugin** (Tier-S source / Tier-X installed).
2. **Assign the tier** (P/S/X) per charter §2.
3. **Codex pre-build gate** — run the validation (see snippet below). Proceed to build only on BUILD.
4. **Route to the matching builder skill** — `/skill-builder`, `/agent-builder`, `/agents-team-builder`, `/plugin-builder`, `/routines-builder` (or `/servy-routine`), `/workflow-builder`, `/hooks-builder`. Let that builder run its own Discovery Interview + decision gate (do not bypass them).
5. **Codex post-build review** — route the new files to Codex; fix findings; re-review if HIGH findings.
6. **Register + provenance** — update the relevant CLAUDE.md roster line + `references/index.md` if it's a wiki page, and file a provenance record at `references/provenance/<date>-<name>.md` (charter §6: what/why/spec/builder/Codex verdict/validator verdict/test evidence; for Tier-X add armed-by + date once Gera arms it).
7. **Tier-X stops at "built, not armed."** Hand Gera the arming step (the relevant builder's supervised first-fire) — never self-arm a hook/routine/team/plugin (charter §5 gate 1).

### Mode C — log a signal manually (`/capability-radar log`)
When you notice in-conversation that we just did something 3+ times by hand, or hand-built something that should be reusable, log it:
```
python3 scripts/capability-radar.py log --source manual \
  --title "<stable short pattern title>" --artifact <type> --tier <P|S|X> \
  --evidence "<one-line what happened>"
```
Use a **stable** `--title` (or `--pattern-key`) so repeats collapse onto one candidate.

### Mode D — render the digest (`/capability-radar digest`)
`python3 scripts/capability-radar.py digest` → the Telegram body. (The daily routine does this automatically; this mode is for manual preview.)

## The auto-build bar (charter §2 + Gera's 2026-06-16 decision)

Auto-build **only** when ALL hold:
- Tier is **S** (skill / agent / team-template / workflow-file / plugin-source) — Tier-X is always suggest-only.
- Engine band is **HIGH** (≥3 distinct signals AND ≥2 distinct source types).
- Codex pre-build verdict is **BUILD**.

No fixed daily quota — the HIGH bar self-throttles. If several cross at once, build the top-confidence ones and **explicitly list any deferred** (no silent skips — `feedback-pa-post-no-silent-skips` discipline applies here too).

## Codex pre-build gate snippet
```bash
codex exec --skip-git-repo-check "Detected build opportunity for Servy:
PATTERN: <title>
PROPOSED: <artifact type> at risk tier <P|S|X>
EVIDENCE: <signal evidence samples>
Is this worth building now? Is the artifact type and tier right?
Reply with exactly one of BUILD / SUGGEST / SKIP on the first line, then one line why."
```

## Hard floors (never waive)
- SoftServe boundary: no customer IP enters a signal, a suggestion, or a built artifact — ever.
- Sacred zones (`scripts/sacred-zones.sh`), identity-core frozen sections, voice-anchor discipline.
- External voice stays draft-first; the only outbound is the Telegram digest to Gera's own channel.
- Spend / keys / arming Tier-X = Gera-only (charter §5).

## After every run (Four-Cs Capabilities discipline)
Capture what worked / what to fix and update this skill in the same session. A skill that never gets feedback rots.

## Related
- `scripts/capability-radar.py` — the engine (log/score/digest/prune).
- `routines/capability-radar.md` — the daily cloud routine (Tier-X, Gera arms).
- `references/autonomous-entity-charter.md` §2/§5/§6 — creation matrix, HITL gates, provenance.
- `evolution-backlog.md` — threshold-crossers graduate here as `[cap-radar][capability]` items.
- Builder family: `/skill-builder` `/agent-builder` `/agents-team-builder` `/plugin-builder` `/routines-builder` `/servy-routine` `/workflow-builder` `/hooks-builder`.
