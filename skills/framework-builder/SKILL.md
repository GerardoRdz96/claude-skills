---
name: framework-builder
description: Turns Gera's thinking or a topic into a reusable DECISION FRAMEWORK — a named decision rule / rubric / scorecard / gate that terminates in an ACTION (pick / build / skip / score), in the 3Ms / Four Cs / routine-placement shape. Type `/framework-builder` to structure a decision into an executable tool, often downstream of /grill-me. Not for software/code frameworks, prose SOPs, or wiki pages with no decision rule.
disable-model-invocation: true
argument-hint: [topic | knowledge/grills/<capture>.md | "from <wiki pages>"]
---

## What this skill does

Turns Gera's thinking or a topic into a **reusable, structured framework** — and graduates it into the wiki, wiring it into Servy when it's a decision rule Servy runs. It is the synthesis step that produces the kind of page Servy already keeps (3Ms, Four Cs, the routine-placement framework, ai-applicability): a named, ordered, *executable* decision tool.

**The one non-negotiable:** a framework's output is an **ACTION** (pick / build / skip / score / which-home), **not understanding**. If what you'd produce is descriptive (the reader finishes with thoughts but no verdict), it is a wiki page, not a framework — stop and route it to normal `references/` ingest. This test gates the whole skill.

Full template, the 11-point quality gate, antipatterns, the two type patterns, graduation, and the wiring rule live in **`reference.md`** (read it before building).

## Where it sits (don't collide)
- **`/grill-me`** EXTRACTS raw thinking to a capture. `/framework-builder` is **downstream**: it STRUCTURES a capture (or a short focused extraction it runs itself) into a decision tool. If the thinking isn't captured yet and is deep, offer to run `/grill-me` first, then chain here.
- **brainstorming** explores NEW design space; **`/skill-builder`** builds skills. This builds a framework (a reusable decision rule), which may then *back* a skill.
- **NOT for:** software/code frameworks, prose playbooks or SOPs, or ordinary wiki pages that have no decision rule (those are normal `references/` ingest).

## Process

**0. Scope (decide before gathering).**
   - **Type:** personal **thinking/decision** framework (client = Servy/Gera) or generic **client/Jumpstart delivery** framework (client = a customer's team)? They share the skeleton but differ in grounding + wiring — see `reference.md` "Two types".
   - **Source:** a fresh **topic** (run a SHORT focused extraction — a handful of targeted questions, not a full grill) or **existing material** (a named `knowledge/grills/` capture, named wiki pages, a decision log) to synthesize. Optional: research-ground it (`/deep-research` or web) when the claims need external authority (as routine-placement did).
   - **SoftServe boundary (any client/Jumpstart work) + data-classification gate.** Generic methodology ONLY — anonymized archetypes. HARD STOP (does NOT enter Servy): customer IP/data/names, **SoftServe Internal+ methodology, engagement artifacts, proprietary runbooks, or "sanitized" customer-derived material** unless explicitly approved. And before any step routes to an external tool (`/deep-research`, web, Codex, the multi-brain in step 1/4): classify the inputs — **never send SoftServe/customer/Internal+ material to external tools**; those are personal/public-data only (`references/softserve-ai-usage-policy.md`).

**1. Gather.** Read the capture / named pages, or ask the short targeted question set. Pull the raw decisions, ratios, stop-conditions, and real examples. Don't re-implement grill-me; lean on it.

**2. Find the axis + draft the decision rule.** Name the ONE optimization axis / load-bearing fact (the bolded scoping line). Draft the decision rule in the fitting form — **ordered-rules / flowchart / gated-table** (`reference.md`). Make every step emit a **named branch/verdict**; state order as a rule.

**3. Complete the instrument.** Add the **verdict/scoring rubric** (gated `if ANY / only when ALL` + tie-breakers + "guide not arithmetic"), the **stop-rules/tells** (so it can say no to itself), and **≥2 dogfooded applications where possible — one ACTION case AND one STOP/boundary case** (a framework only ever used to say "yes" is unvalidated). If only one real case exists, file it as **provisional**, or keep it as normal wiki ingest until a second case validates it.

**4. Quality gate (MANDATORY, before graduating).** Append an **explicit pass/fail checklist** to the draft — each of the 11 gate items in `reference.md` marked ✓/✗, naming the terminal verdicts, the stop-rules, and the dogfood result(s). If ANY item is ✗ — especially the non-negotiable (all prose / no executable decision rule) — STOP: fix it or route to normal wiki ingest. Do not file a fake framework. **Codex review is MANDATORY** (not just "substantial") for any framework that will be **wired into Servy** or used for **client/Jumpstart delivery** (No-Self-Review Law): `git diff | codex exec --skip-git-repo-check "Is this a real, executable decision framework or descriptive prose? Find any step that doesn't branch, any verdict decided by vibes, any missing stop-rule, any ungated 'it depends'."`

**5. Graduate (wiki-protocol).** Write `references/<kebab>-framework.md` to the skeleton; update `references/index.md` (summary == the page's one-liner); register a `knowledge/` raw source in `knowledge/README.md` if distilled from one (mark "(digest)"); append `## [<date>] create | <Name>` to `references/log.md`; lay `**Related:**` cross-links (no orphans); run the build-triage reflex; optionally fire `warden`. Full checklist in `reference.md`.

**6. Wire into Servy (decision frameworks only — PROPOSE-THEN-CONFIRM).** If it's a rule Servy runs repeatedly, propose the exact wiring (skill gate / one-line CLAUDE.md pointer / standing hook), **show Gera the diff, and wait for an explicit yes** — never auto-edit CLAUDE.md or a SKILL.md, never touch identity-core, respect the 200-line cap. Wiring must be **bidirectional** (page names the skill AND the skill/CLAUDE.md names the page). The page's own `## Wiring` section can ship without confirmation (it's wiki prose). Client/Jumpstart frameworks get NO CLAUDE.md standing behavior and NO automatic behavioral gate. Cross-linking a delivery skill (`/jumpstart`, `/forge`) so it consumes the page **is itself wiring** — so it's also propose-then-confirm + bidirectional, not a free edit.

**7. Optional HTML artifact.** Offer a polished HTML artifact (`artifacts/frameworks/<date>-<slug>.html`) per `references/html-as-llm-output.md` — a framework with a flowchart/table is a strong candidate to forward.

## Output
- **Canonical:** `references/<kebab>-framework.md` (markdown, no frontmatter) + `references/index.md` entry + `references/log.md` line.
- **Optional:** an HTML artifact; a **proposed** CLAUDE.md/skill wiring diff (applied only on Gera's yes).

## Guardrails
- **The decision-rule gate is non-negotiable** — no executable rule, no framework (route to normal ingest).
- **SoftServe boundary** — client frameworks are generic-only; customer IP never enters Servy.
- **Don't duplicate `/grill-me`** — chain off it for deep extraction; this skill does only a short focused extraction itself.
- **Wiring is propose-then-confirm + bidirectional** — never auto-edit CLAUDE.md/identity-core; respect the budget cap.
- **No orphans, honest provenance** — index entry, ≥1 `Related` link, a `Sources` line, dated footer (see `reference.md`).
- This skill is conversational/synthesis — stays in the live session; it may fan out to `/deep-research` or Codex, but doesn't fork itself to an isolated agent.
