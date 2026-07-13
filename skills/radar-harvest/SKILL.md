---
name: radar-harvest
description: Use to mine the day's FULL radar fetch (not just the top 3) into the wiki so knowledge compounds, and to turn tool/model-release signals into adoption decisions + capabilities. Triggers - "harvest the radar", "grow the wiki from today's news", "what should we adopt", "any tools to adopt", "ingest today's radar", "/radar-harvest". The sibling of /tech-radar (which fetches + digests the top items) and the Opportunity Engine (outward painpoints) - this one keeps the discarded 99% as compounding knowledge AND spots adoptable tools (e.g. "GLM-5.2 tops open coding") to wire into Servy. Personal/public-data only - never SoftServe customer IP.
argument-hint: [date YYYY-MM-DD | "adopt" to only run the adoption pass]
---

## What this skill does

`/tech-radar` fetches ~500 items every morning and the digest keeps ~3. That discarded 99% is exactly the knowledge that should compound, and a line like *"GLM-5.2 takes the open coding crown"* is a **signal to act**, not just to report. This skill mines the same raw fetch into two flows:

1. **Knowledge growth** — the wiki-worthy discards become `references/` pages so Servy's knowledge grows every day.
2. **Adoption** — named tool/model releases Servy could *use* flow through an adopt / watch / skip decision; STRONG adopts become `[capability]` backlog items (→ the `backlog-util.py` bridge → `the-builder-room`).

It **composes existing machinery, it is not a parallel system**: input is `tech-radar-fetch.py`'s raw JSON; output lands in the `references/` wiki and the `evolution-backlog.md` bridge. Engine: `scripts/radar-harvest.py`. Cloud sibling: `routines/radar-harvest.md`.

## Governance (read before running)

- Ingesting wiki pages + filing backlog items = **Tier-S** (auto). The Ingestion loop already auto-writes the wiki; this is the same risk class.
- Actually **WIRING** an adopted tool — installing a CLI, editing the `multi-brain` model roster, adding an MCP — is **Tier-X**. This skill **SUGGESTS** it (digest + a `[capability]` item + a `pending.md` line); **Gera arms** the install/edit. Never auto-install or auto-edit the roster. (A doc-only note in `references/ai-dev-tools-landscape.md` is the one Tier-S exception.)
- **SoftServe boundary** (`references/softserve-ai-usage-policy.md`): public/personal data only. Never ingest customer IP, never route it through the multi-brain.

## Process

0. **Ensure today's fetch exists.** If `knowledge/radar/<date>-raw.json` is missing, run `python3 scripts/tech-radar-fetch.py` (don't re-fetch if it's already there — same-day dedup).
1. **Plan.** `python3 scripts/radar-harvest.py plan --date <date>` → JSON `{ingest:[...], adopt:[...]}`. This is the scored shortlist, not the whole 500.
2. **Ingest (knowledge growth).** For each `ingest` item (respect the cap), follow `references/wiki-protocol.md`:
   - Read the source/summary; if it's thin, fetch the URL for substance (`WebFetch` / `ctx_fetch_and_index`).
   - Write a NEW concept/tool/entity page **or** fold into the closest existing page (the engine already dampened things the wiki covers — prefer appending a dated note to a stub-worth item). Quality over count: a few solid pages beat 8 stubs.
   - Update `references/index.md` and append a `## [<date>] ingest | radar-harvest` line to `references/log.md`.
3. **Adopt (signal → capability).** For each `adopt` candidate:
   - Log the signal for cross-day accumulation: `python3 scripts/radar-harvest.py signal --tool "<name>" --title "<t>" --url "<u>" --source "<s>"`.
   - `python3 scripts/radar-harvest.py score` to see which tools are **STRONG** (≥3 mentions, or ≥2 mentions from ≥2 sources over 7d).
   - For a STRONG candidate, run a quick **adopt / watch / skip** decision — invoke `/ai-apply` on "should Servy adopt <tool>?" or spin `the-lab` for a dossier. On **adopt**: file `python3 scripts/backlog-util.py add --tier T2 --source radar-harvest --desc "[capability] adopt <tool>: <one-line why> — wire via <skill/script/roster note>"` (→ bridge → builder). On **watch**: keep the signal, no backlog item. On **skip**: nothing.
   - If adoption implies a Tier-X wiring (CLI install / roster edit / MCP), add a `pending.md` line for Gera to arm — do NOT wire it yourself.
4. **Digest.** `python3 scripts/radar-harvest.py digest --plan <plan.json>` and send to Telegram (`TG_BOT_TOKEN`/`TG_CHAT_ID` from `.env`): pages added, adopt candidates + verdicts, what was queued vs what needs Gera to arm.
5. **Report** in chat: pages ingested (with links), adopt verdicts, capabilities filed, Tier-X items parked for Gera.

## Caps & discipline
- Ingest ≤ 8 pages/day, adopt ≤ 5 candidates/day (engine defaults; tune with `--ingest-cap`/`--adopt-cap`). Don't flood the wiki — the `warden` agent lints it.
- Re-runnable and idempotent-ish: re-running the same day appends, the dedup dampener stops re-paging covered topics, and the signal store dedups by tool key over the window.
- `"adopt"` argument → skip step 2, run only the adoption pass (steps 3-4).
