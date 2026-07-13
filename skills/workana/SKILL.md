---
name: workana
description: Use to find freelance opportunities on Workana and draft tailored bids in Gera's voice. Triggers - `/workana`, "find freelance work", "find clients", "any freelance projects", "scan workana", "workana opportunities", "find me a gig", "what's on workana", "draft a bid for <project>". Runs the read-only scanner `scripts/workana-scan.py` (content-negotiated JSON from Workana's public job board), ranks projects against Gera's profile (agentic AI, AI integrations, chatbots/RAG, workflow automation, API work, full-stack AI apps, bilingual EN/ES), surfaces a fit-ranked digest, then on request fetches a chosen project's full detail and drafts a personalized proposal for Gera to paste. READ-ONLY — never logs in, never bids, never submits. Personal Penguin-Alley agency use, 100% separate from SoftServe.
---

# /workana

Servy's front door to Gera's freelance deal-flow on **Workana** (a LATAM-first freelance marketplace — Spanish/Portuguese heavy, which is Gera's native-language edge). This skill finds fit-ranked opportunities and helps Gera win them, while keeping a hard read-only boundary: Servy surfaces and drafts, **Gera submits**.

This is the agency-arm intake for the Penguin Alley empire (`references/penguin-alley-org-chart.md` Arm 4). A Workana lead that converts to a real engagement graduates into `/forge` for the full build.

## When to use

- Gera invokes `/workana` or any natural trigger ("find freelance work", "any gigs", "scan workana", "draft a bid for X").
- The daily `routines/workana-scan.md` Telegram digest surfaced something and Gera wants to act on it.
- Gera wants a targeted search ("find me RAG chatbot projects", "anything in Spanish about automation").

If Gera didn't ask and the routine didn't fire, don't manufacture work.

## The connection (how it works)

Workana has **no public API**. The scanner uses the site's own data path: requesting a public `/jobs` browse URL with the header `X-Requested-With: XMLHttpRequest` content-negotiates to **JSON** instead of the HTML shell — exactly what a logged-out browser does when you scroll the public board. We read public listings, nothing more. Full mechanism + safety posture: `references/workana.md`.

Key tuning fact: the `query=` free-text search returns **fresh, newest-first** results; the `skills=` taxonomy filter returns stale ones. The scanner drives off `query=`. Config (queries, scoring weights, budget floor, language) lives in `scripts/workana-scan.config.json`.

## Process

### Step 1 — Scan
Run the scanner and surface the ranked digest.

- Default (new since last run): `python3 scripts/workana-scan.py --new-only --limit 12`
- Everything matching (peek, no state change): `python3 scripts/workana-scan.py --all --limit 15`
- Targeted: `python3 scripts/workana-scan.py --query "rag chatbot" --query "n8n" --all`
- Higher floor: `python3 scripts/workana-scan.py --min-budget 500`

Each line shows `[score] title · budget · bids · payment✓ · country · recency (fit reasons)` and a direct `/job/<slug>` link. Read the **score signals** for Gera:
- **Few bids = better odds.** A $1–3k project with 2 bids beats one with 90 bids.
- **payment✓** = verified payment method = a real, more-serious client.
- **Recency** — "fresh"/"yesterday" projects are still open; "months ago" usually filled.
- **Budget** — fixed `Over USD 3,000` and mid `USD 1,000–3,000` are the sweet spot.

Recommend the 2–4 best by *odds × fit × budget*, not just raw score.

### Step 2 — Deep-read a chosen project
When Gera picks one, fetch its full detail (the digest only carries a short description):

Run this exact command — the UA below is the scanner's own (`UA` in `scripts/workana-scan.py`); use it verbatim, do not improvise or truncate it:

```bash
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" \
  -H "X-Requested-With: XMLHttpRequest" -H "Accept: application/json" \
  "https://www.workana.com/job/<slug>"
```
or `WebFetch` the public `https://www.workana.com/job/<slug>` URL. Pull: the real requirements, scope, deliverables, client country/history, budget, and what would make a bid stand out.

### Step 3 — Draft a tailored bid (Gera submits)
Write a short, personalized proposal **in the project's language** (Spanish or English — match it). Voice rails (`references/voice.md` + the LinkedIn-voice memory):
- Curious-learner register, warm and specific. **No hype, no guru framing, no "I'm an expert in everything."**
- Open by showing you understood *their* problem, not by listing your résumé.
- Anchor credibility in **real Penguin Alley work** where relevant: Cleia (full-stack AI app — Next.js + Supabase + Stripe + an AI assistant with per-workspace memory), agentic systems, RAG, automation pipelines, Claude/OpenAI integrations, WhatsApp/Telegram bots.
- Ask **1–2 sharp scoping questions** that prove you've thought about the build.
- Keep it tight (a Workana proposal is a pitch, not an SOW). End with a clear next step.
- No Penguin Alley penguin imagery — this is a text proposal. PA branding is for PA-page social content only.

Output the draft for Gera to **review and paste into Workana himself**. Never auto-submit.

### Step 4 — Track it (optional)
If Gera bids, append a line to `agency/workana-pipeline.md` (create if absent): date · project · budget · bid sent · status. This is the agency deal-flow ledger.

### Step 5 — Convert
If a client replies and it becomes a real engagement, **graduate to `/forge`** (Phase 1 `forge-discovery` → spec → build → Codex review → deploy). For a formal SOW once scoped, hand the capture to `pa-proposal-writer`.

## Boundary (non-negotiable)

- **READ-ONLY on Workana.** The scanner never logs in, never bids, never touches an account. Submitting a proposal is an outward action Gera approves and performs each time.
- **Polite.** The scanner uses realistic request volume + delays + a hard request cap. Don't hammer it; don't add a tight loop.
- **SoftServe-separate.** This is Penguin Alley / personal freelance income — 100% independent of Gera's SoftServe employment (`references/penguin-alley-org-chart.md`: the agency arm is clear, not in conflict). Never route SoftServe customer data or IP near a freelance bid.

## Files

- Engine: `scripts/workana-scan.py` · Config: `scripts/workana-scan.config.json` · State: `scripts/workana-seen.json` (gitignored)
- Routine: `routines/workana-scan.md` + `scripts/workana-scan-job.sh` + `launchd/com.servy.workana-scan.plist`
- Wiki: `references/workana.md` · Agency context: `references/penguin-alley-org-chart.md`
