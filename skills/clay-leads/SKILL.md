---
name: clay-leads
description: Use when Gera wants outbound leads — "find me leads", "build a lead list", "get me 50 leads for <avatar>", "cold outreach list", "enrich these companies", "who should I email for <offer>", or "/clay-leads". Sources + waterfall-enriches B2B leads via the official Clay plugin (verified emails/phones) and drafts personalized outreach from the business context pack, delivering a campaign-ready CSV. Costs Clay credits — never auto-invoke on a hunch; drafts only, nothing ever sends.
argument-hint: '[N] [ICP / avatar, e.g. "50 HVAC owners in Texas metros"]'
disable-model-invocation: true
---

## What this skill does

Runs the outbound half of the funnel (inbound = Penny → `/lead-pipeline`; marketplace = `/workana`): Claude Code orchestrates, Clay supplies the data. One run = a scoped ICP → sourced + enriched leads (verified emails, pain-point signals) → personalized subject/body drafts in the business's voice → one CSV Gera imports into Clay to campaign from. Method + verified platform limits: `references/clay-leadgen.md`. Connection + install: `connections.md` #28.

**Hard law: this skill produces lists and drafts. It never sends anything, never buys anything, and never spends credits without stating the estimate and getting Gera's OK first.**

## Step 1 — Prereq gate (all three, in order)

1. **Plugin + auth:** run `clay whoami` (exit 0 = signed in; exit 3 = not). If the `clay` CLI is missing or unauthenticated, STOP and hand Gera the install block from `connections.md` #28 (marketplace installs + `clay login` are his hands; remind him the post-login Claude Code restart is mandatory). Do not improvise another data source.
2. **Credit balance:** `clay credits` — if the balance can't cover the estimate in Step 3, say so before anything else (Free plan = 100 Data Credits/mo; a Nate-scale 50-lead enriched run ≈ 172).
3. **Context pack:** confirm which identity is prospecting and load its context — Penguin Alley agency: `context/about-business.md` + `projects/REGISTRY.md`; Cleia: its REGISTRY entry + pilot facts; services/workshops: the priced menu. Cold copy without a real offer + proof reads as slop — if the pack is thin for this ICP, tell Gera what's missing instead of padding with generalities.

## Step 2 — Scope the run (with Gera)

Pin down, from `$ARGUMENTS` plus at most one round of questions: **N** (default 25 on a trial account, not 50), **ICP/avatar** (industry, size, geography, decision-maker titles), **the CTA** (e.g. "yes to a 90-second Loom"), and **the offer** the copy sells. Echo the scope back in one line before spending anything.

## Step 3 — Cost gate (blocking)

Look up real prices before running: `clay routines get <routine-id>` → `estimatedCreditCost` for each enrichment in the plan, multiply by N, add the search cost. State: *"~X credits ≈ $Y at plan rates; balance is Z. Proceed?"* **Default cap: 200 credits/run** — exceeding it needs Gera's explicit raise. On a trial/free workspace also state how much of the monthly allotment this run consumes.

## Step 4 — Source + enrich (CLI-first)

- Work through the `clay` CLI / plugin skills (search → routines), not raw MCP calls, per CLI > API > MCP.
- For N ≥ ~25, fan out subagents or a dynamic workflow by segment (Nate's pattern: one agent per city/vertical, then aggregate + dedupe + yield-check). Verify, don't trust: every lead needs a **verified** email status; a blank cell beats an invented one — never fabricate enrichment data.
- Remember platform limits (`references/clay-leadgen.md`): searches = people/companies only; tables are read-only to agents; Workflows are Alpha. The CSV is built locally, not in a Clay table.

## Step 5 — Copy pass

For each lead: personalization hook (from pain points / review signals / recent events, with the hook's source kept in its own column), subject, body. Voice rules are binding: curious-learner register, no hype, no fake familiarity, honest about where the business actually is (Nate's demo copy literally said "I'm still getting this off the ground" — that honesty is the model). If a proven cold-email strategy doc exists in `knowledge/`, use it as the style guide; don't freestyle structure.

## Step 6 — Verify + deliver

Verification pass before delivery: dedupe, no blank required columns (email, subject, body), email_status = verified (or the lead moves to a `needs-review` sheet), copy actually references the lead's own data. Deliver to `money/leads/<date>-<slug>/leads.csv` + `run-summary.md` (scope, credits estimated vs actually spent, yield rate, anything skipped). Report the spend honestly even when it overshot.

## Step 7 — Handoff checklist (Gera's hands, in Clay's UI)

Give Gera this list, done for him up to the send boundary: import CSV → new table → Campaign → add lead list → message from variables (`email subject` / `email body` rows) → preview → sender accounts (the in-UI "buy pre-warmed accounts" flow from the video is undocumented on clay.com — verify in-app; ~30 sends/day/account while warming) → 3-day follow-up slots (Servy can draft these). **Launching the campaign is Gera's click, always** — and agency outreach additionally respects the pa-outreach case-study gate.

## Step 8 — Bookkeeping

Append the run to `references/log.md` (`## [date] run | clay-leads — <slug>`): N, credits, yield, what to fix next run. First real run: capture what worked/broke and update this skill same-session.

## Never

- Never send, schedule, or buy anything (emails, domains, accounts, credit top-ups).
- Never spend credits without the Step-3 estimate + OK; never blow the 200-credit cap silently.
- Never use for SoftServe prospecting or route SoftServe data through Clay (policy §7) — Penguin Alley / personal only.
- Never fabricate or pad enrichment fields; never ship copy Gera hasn't seen for an external send.
- Never connect the hosted `clay-for-reps` MCP connector alongside the plugin (Clay's own guidance).
