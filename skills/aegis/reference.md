# `/aegis` reference — rubric, adjudication, crosswalk, output templates

This file is loaded by the skill when it needs detail. SKILL.md holds the workflow; this holds the scoring rules, the crosswalk, and the two output templates.

## 1. The rubric

26 controls live in `rubric.json`, organized by NIST AI RMF function (after the 2026-06-02 Codex review):

- **GOVERN** (7) — accountability owner, AI use policy, **regulatory applicability register**, risk tolerance, roles/training, supply-chain inventory, governance review cadence.
- **MAP** (6) — system/model card, intended use & limits, data lineage/consent, stakeholder & impact (FRIA), foreseeable misuse, human oversight.
- **MEASURE** (9) — eval/test coverage, safety/red-team, bias/fairness, logging/observability, agent tool-permission scoping, **security & resilience testing**, **privacy-risk assessment**, recourse/feedback, production monitoring.
- **MANAGE** (4) — **risk treatment & go/no-go**, rollback/kill-switch, change management, incident-response plan.

Each control has: `id` (AEGIS-prefixed — **NOT** a NIST subcategory number), `function`, `nist_rmf` (the real NIST AI RMF subcategory it maps to), `title`, `what_it_checks`, `category` (code | hybrid | policy), `evidence_signals` (files + content), `interview_question`, `remediation`, `crosswalk` {iso42001, eu_ai_act}, `applicability` (EU obligations are conditional on classification), `severity` (1–3).

**Classification first.** Run `AEGIS-GOV-03` (regulatory applicability register) early — the system's EU AI Act classification (prohibited / high-risk / limited / minimal; GPAI; provider vs deployer) determines which EU obligations apply and therefore which controls are scored vs marked `NA`. Do not apply EU tags as if universally binding.

## 2. How the scanner reports (it does NOT decide)

`scripts/proof-gap-scan.py` returns, per control, an `evidence` strength — never a verdict:

- **strong** — a *control-specific* file matched (e.g. `INCIDENT_RESPONSE.md`, `MODEL_CARD.md`, `GOVERNANCE.md`). Likely real, but still inspect it.
- **candidate** — only a *generic* file matched (e.g. `package.json`, `tests/`, `VERSION`). Proves little on its own — inspect before trusting.
- **weak** — only a `content` keyword matched (the term appears in prose or code). May be a mere mention, not an implemented control.
- **none** — nothing matched.

The scanner is read-only, deterministic (sorted walk), and excludes its own files by default so it never scores aegis's rubric/reference as evidence. Adjudication is the skill's job.

## 3. Adjudication rules (the skill decides the status)

Five statuses: **VERIFIED_FILE** · **ATTESTED** · **PARTIAL** · **GAP** · **NA**. For each control, combine scanner evidence + a look at the matched path(s) + interview answers + the system's classification:

| Scanner evidence | What the skill does | Typical status |
|---|---|---|
| **strong** | Open/inspect the matched file. Does it substantively implement/document the control, or just mention it? | VERIFIED_FILE if substantive; PARTIAL if thin/aspirational; GAP if only a passing mention. |
| **candidate** | A generic file matched. Inspect: does it actually evidence *this* control? | PARTIAL if it partly does; GAP otherwise (or interview a `policy`/`hybrid` control). |
| **weak** | Keyword only. For `code` controls, inspect the file — is it implemented? For `policy`/`hybrid`, ask the `interview_question`. | PARTIAL / ATTESTED / GAP per what you find. |
| **none** | For `policy`/`hybrid` controls, ask the `interview_question` (code-absence ≠ truly absent). For `code` controls, GAP. | ATTESTED only if the user gives a concrete specific answer; GAP if vague/declined/skipped. |

**Hard rules:**
- Absence of evidence is a GAP, never a free pass.
- **ATTESTED ≠ VERIFIED_FILE.** An attested control rests only on the user's word, scores less (see §4), and must be labeled "(attested)" in the report. Never give attestation the same weight as an inspected artifact.
- A skipped or vague interview answer is a GAP, never ATTESTED. Defensibility over flattery — self-report is the exact weakness of the survey that named this problem.
- Mark a control **NA** only when the applicability register (`AEGIS-GOV-03`) shows it's out of scope for this system's classification — and say why in the report.
- Never invent evidence or assume a control exists because it "probably does."

## 4. Scoring

- Per control credit: **VERIFIED_FILE = 1.0 · ATTESTED = 0.75 · PARTIAL = 0.5 · GAP = 0 · NA = excluded**.
- Per function: `readiness% = round(100 * earned / possible)` where each in-scope control contributes its `severity` weight × its credit; NA controls drop out of the denominator.
- Overall: severity-weighted across all in-scope controls.
- **Readiness bands:** 0–49% Not audit-ready · 50–74% Partial · 75–89% Substantially ready · 90–100% Audit-ready.
- Gap priority = `severity × effort_inverse` — list critical (sev 3) low-effort fixes first.

## 5. Crosswalk note

The ISO/IEC 42001 and EU AI Act tags in `rubric.json` are **indicative mappings** to help a team find the matching clause — not legal advice or a certified equivalence. They were adversarially reviewed by Codex on 2026-06-02, but this is **not a certified or "passed" crosswalk**: known imprecisions remain (exact NIST subcategory numbers and ISO clause numbers). Validate NIST subcategories against the NIST AI RMF Core and ISO wording against a licensed ISO/IEC 42001:2023 copy before relying on them. **EU AI Act obligations are conditional on the system's legal classification** (see `AEGIS-GOV-03`) — most apply only to high-risk systems, Art. 27 only to specified deployers, Arts. 53/55 only to GPAI providers. Always state applicability; never present a conditional obligation as universal. The report footer must say all of this.

## 6. Output template — Audit-Readiness Report

Write markdown to `artifacts/proof-gap/<date>-<target>-audit.md` and an HTML twin (per `references/html-as-llm-output.md`).

```markdown
# AI Governance Audit-Readiness Report — <target>
**Date:** <date> · **Framework:** NIST AI RMF 1.0 (+ ISO 42001 / EU AI Act crosswalk) · **Tool:** /aegis v1

## Verdict
**Overall readiness: NN% — <band>**
> One-paragraph plain-language verdict: could this pass a 90-day governance audit, and what's the single biggest risk?

## Readiness by NIST function
| Function | Readiness | Gaps |
|---|---|---|
| GOVERN | NN% | n |
| MAP | NN% | n |
| MEASURE | NN% | n |
| MANAGE | NN% | n |

## Control detail
| Control | Status | Evidence / Attestation | NIST AI RMF | ISO 42001 | EU AI Act (applicability) |
|---|---|---|---|---|---|
| AEGIS-GOV-01 Named accountability owner | GAP | none | GOVERN 2.1 | 5.3 | Art. 17(1)(m) (high-risk providers) |
| AEGIS-GOV-03 Regulatory applicability register | ATTESTED | attested: classified limited-risk, deployer | GOVERN 1.1 | 4.1 / 6.1.2 | Arts. 2/6/51 |
| ... | | | | | |

## Top fixes (prioritized for a 90-day window)
1. **[CRITICAL] <control> —** <remediation>. (Why it matters / audit exposure.)
2. ...

## Methodology & caveats
- Hybrid evidence: code scan + targeted attestation. Items marked "(attested)" rest on your answers, not file evidence.
- Crosswalk tags are indicative, not legal advice.
- <note degradation to interview-only if no scannable target>
```

## 7. Output template — Agent Incident-Response Playbook

Write markdown to `artifacts/proof-gap/<date>-<target>-ir-playbook.md` and an HTML twin. Tailor every section to the detected system (what the agent can touch, which tools it has, where it runs).

```markdown
# Agent Incident-Response Playbook — <target>
**Date:** <date> · **Owner:** <accountability owner or "UNASSIGNED — fix first">

## 1. System snapshot
- What the agent does, what tools/data/systems it can reach, where it runs, blast radius if it misbehaves.

## 2. Detection signals
- Concrete signs of an incident (error spikes, anomalous tool calls, cost spikes, user reports, drift alerts).

## 3. Kill switch
- The exact, fastest way to stop the agent now. <command / flag / console step or "MISSING — must build">.

## 4. Rollback
- How to revert to the last known-good model/prompt/config version.

## 5. Blast-radius containment
- Revoke credentials/scopes, isolate affected data, freeze downstream automations.

## 6. Escalation & roles
- Who is paged, in what order; the accountability owner; external notification duties (e.g., EU AI Act Art. 73 serious-incident reporting if applicable).

## 7. Communication
- Internal + affected-user messaging; who approves external statements.

## 8. Tabletop test (run this)
- One concrete scenario (e.g., "the agent starts emailing customers unprompted") walked step-by-step through sections 3–7 to prove the plan works. Closes the "20% have a *tested* plan" gap.

## 9. Review cadence
- When this playbook is re-tested and updated.
```

## 8. Anti-patterns (do NOT)

- Do not score a control VERIFIED off a weak keyword match without inspecting the path.
- Do not present indicative crosswalk tags as compliance/legal certainty.
- Do not skip the tabletop section of the IR playbook — a plan that isn't tested is the exact gap the research names.
- Do not auto-publish or share the report externally; it may contain sensitive system detail. Local artifact only unless the user explicitly asks.
