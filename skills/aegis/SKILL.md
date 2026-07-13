---
name: aegis
description: Invoked explicitly via /aegis (model auto-invocation is disabled — natural asks won't fire it; deliberate, because a full governance audit is expensive). Audits an AI system/repo against the NIST AI RMF (ISO/IEC 42001 + EU AI Act crosswalk) and produces two artifacts — a scored Audit-Readiness Report and an Agent Incident-Response Playbook.
argument-hint: [target-path] (defaults to current directory)
disable-model-invocation: true
---

## What `/aegis` does

Closes the **AI governance proof-gap** (Grant Thornton 2026: 78% of execs can't pass a 90-day AI governance audit; only ~20% have a tested agent incident-response plan). You point it at an AI system/repo; it produces two evidence-backed artifacts scored against the **NIST AI RMF** with **ISO/IEC 42001 + EU AI Act crosswalk** tags:

1. **Audit-Readiness Report** — scored gap analysis + prioritized 90-day fix list.
2. **Agent Incident-Response Playbook** — kill switch, rollback, containment, escalation, and a runnable tabletop test.

It works by the **hybrid evidence model**: scan for what code can prove, then interview only for the org/policy controls code can't prove. Conservative by design — absence of evidence is a gap, not a free pass.

## Files this skill uses

- `rubric.json` — 26 controls with `nist_rmf` subcategory mapping, evidence signals, interview questions, ISO/EU crosswalk + applicability, severity. (Control IDs are AEGIS-prefixed — they are NOT NIST subcategory numbers; the real NIST mapping is the `nist_rmf` field.)
- `reference.md` — adjudication rules, scoring, crosswalk note, and the two output templates. **Read it before scoring.**
- `scripts/proof-gap-scan.py` — deterministic, read-only evidence scanner.

## Workflow

### Step 0 — Resolve the target
Target path = `$1` if given, else the current directory. Tell the user what you're about to audit.

### Step 1 — Scan for evidence
Run the scanner and read its JSON:
```
python3 scripts/proof-gap-scan.py "<target>"
```
- If it returns `{"error": ..., "mode": "interview-only"}` (target isn't a directory) → announce **interview-only mode** (graceful degradation) and skip to Step 3 using the full rubric.
- If `looks_like_ai_repo` is false → warn the user this may not be an AI system before continuing.
- The scanner reports `evidence`: **strong** (control-specific file) / **candidate** (generic file) / **weak** (keyword only) / **none**. This is candidate evidence, **not a verdict**.

### Step 1.5 — Establish classification (do this early)
Adjudicate `AEGIS-GOV-03` (regulatory applicability register) first, interviewing if needed: is the system prohibited / high-risk / limited / minimal? GPAI? Are you provider or deployer? This determines which EU-conditional controls are in scope vs marked **NA**. Do not apply EU obligations as if universal.

### Step 2 — Adjudicate controls against evidence
Read `reference.md` §3 (adjudication rules). For each control with **strong / candidate / weak** evidence:
- Open the matched path(s). Judge: does this artifact actually implement/document the control, or just mention it?
- Assign **VERIFIED_FILE / PARTIAL / GAP** per the rules. Never score VERIFIED_FILE off a bare keyword or a generic file without inspecting the path.

### Step 3 — Targeted interview (only for what code can't prove)
For `policy`/`hybrid` controls that ended Step 2 as `none`/`candidate`/`weak`-unresolved, ask their `interview_question`. Batch into one concise round (use AskUserQuestion where it helps). Rules:
- A concrete, specific answer → **ATTESTED** (label it as attested; it scores less than file evidence).
- A vague answer, "I think so," declined, or skipped → **GAP**. Never a free pass.
- Don't interview `code` controls that scored `none` — those are simply GAPs.

### Step 4 — Score
Per `reference.md` §4 (VERIFIED_FILE = 1.0, ATTESTED = 0.75, PARTIAL = 0.5, GAP = 0, NA excluded): compute per-function readiness %, overall severity-weighted readiness %, assign the band, and rank gaps by severity × effort.

### Step 5 — Write the Audit-Readiness Report
Use the template in `reference.md` §6. Write markdown to `artifacts/proof-gap/<YYYY-MM-DD>-<target-slug>-audit.md`, then render an HTML twin at the same path with `.html` (follow `references/html-as-llm-output.md` — scannable, scorecard-style). `<target-slug>` = basename of the target.

### Step 6 — Write the Agent Incident-Response Playbook
Use the template in `reference.md` §7. Tailor every section to the detected system (tools it can reach, blast radius, where it runs). Write markdown + HTML twin to `artifacts/proof-gap/<YYYY-MM-DD>-<target-slug>-ir-playbook.{md,html}`. The tabletop test (§8 of the template) is mandatory — it's what closes the "tested plan" gap.

### Step 7 — Summarize in chat
Report: overall readiness % + band, a one-line per-function breakdown, and the **top 3 prioritized fixes**. Give the two artifact paths. Offer to open the HTML.

## Guardrails

- **Conservative scoring.** Absence of evidence = GAP. Skipped/vague attestation = GAP. Defensibility over flattery — self-report is the exact weakness of the survey that named this problem.
- **Read-only.** Never modify the target. The scanner never writes to it.
- **Crosswalk = indicative + conditional.** ISO 42001 / EU AI Act tags help locate the matching clause; they are not legal advice or certified equivalence. EU obligations are conditional on the system's classification (`AEGIS-GOV-03`) — most apply only to high-risk systems. State applicability; never present a conditional obligation as universal. The report footer must say so.
- **Local artifact only.** The report can contain sensitive system detail. Write it to `artifacts/proof-gap/` and do not share/publish externally unless the user explicitly asks.
- **Don't invent evidence.** If you can't see it and the user can't attest to it specifically, it's a gap.
- **No self-certification of the rubric.** The rubric/crosswalk was adversarially reviewed by Codex (No-Self-Review Law) on 2026-06-02; re-review after material rubric changes.

## Notes

- `category` in the rubric: `code` (provable by scan), `policy` (needs attestation), `hybrid` (either).
- Severity: 1 good-practice · 2 important · 3 critical/blocking for an audit.
- To extend coverage, add controls to `rubric.json` — no code change needed; the scanner is config-driven.
