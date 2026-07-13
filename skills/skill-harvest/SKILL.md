---
name: skill-harvest
description: Use to mine Gera's recent Claude Code sessions for repeated manual work that should become a skill — the DATA-DRIVEN sibling of /level-up (which interviews him). Triggers — "what should I turn into a skill", "harvest skills from my sessions", "what do I keep doing by hand", "mine my history for skills", "skill audit", "/skill-harvest". Reads the real transcripts (scripts/skill-harvest.py), clusters what he actually repeats, classifies each candidate (already-covered / automated / SoftServe-bound / buildable), and proposes skills as a task → output → proposed-skill table. Ends by offering to build the top pick via /skill-builder.
---

## What this skill does

The video that birthed this (Chase AI, "Agentic OS Setup That Will 10x Claude Code", 2026-06-25) names three ways to find what to turn into a skill: do it manually, **have Claude read your last N sessions and propose skills**, or have Claude interview you. `/level-up` is the interview. **This is the read-your-sessions one.**

It runs a deterministic miner over the real session transcripts, then *I* (Claude) do the semantic clustering and judgment the script can't — so we go off what Gera actually does, not what he thinks he does. One run = a ranked candidate table + one skill teed up to build.

It pairs with [[level-up]] (the 3Ms interview) and feeds [[skill-builder]] (which actually builds the chosen skill). It is **discovery, not construction** — it never writes a skill itself; it hands the winner to `/skill-builder`.

## When to use vs /level-up

- **/skill-harvest** when you want evidence: "what does the data say I repeat?" Best run every few weeks, or when Gera suspects he's doing something by hand a lot.
- **/level-up** when you want the 3Ms interview + the Mindset install. Best as the Friday ritual.
- They compose: harvest surfaces candidates → level-up/skill-builder ships one.

## The process

### Step 1 — Mine the sessions
Run the miner and read its report:

```bash
python3 scripts/skill-harvest.py --sessions 40
```

Flags: `--sessions N` (default 30; `0` = all), `--days D` (only sessions touched in the last D days), `--min-repeat K` (group threshold, default 2), `--json OUT` (also dump the structured payload). For a broad sweep use `--sessions 80`; for "what have I done lately" use `--days 10`.

The report gives you: the existing-skills roster (so you exclude what's covered), **recurring intents grouped by repeat count** (the top candidates), slash-command usage (hot skills + any `⚠ not a known skill` commands), a distinct-prompt list (the raw material to cluster), slash-command args, and a bash-pattern histogram (recurring manual command workflows). The script already strips harness noise, routine/agent prompts, and Moltbook challenges — what's left is mostly real intent.

### Step 2 — Cluster semantically (this is the judgment the script can't do)
Read the distinct-prompt list and group prompts that are the *same underlying task* even when worded differently. Example clusters seen in practice: "draft a status message for my SoftServe team chat", "prep + QA a research deliverable doc", "make an explainer video for person/team X". A cluster of 2+ distinct prompts that map to one repeated workflow is a candidate.

### Step 3 — Classify every candidate (do NOT skip this)
Tag each cluster as exactly one of:

1. **Already covered** — an existing skill does this. Drop it (note which skill).
2. **Already automated** — a routine/agent already runs it unattended (the daily posts, pending-drain, moltbook, the messaging bridges). Drop it.
3. **🚧 SoftServe-bound** — the work is SoftServe customer/Internal+ work (R&D datasets, RaaS/Jumpstart deliverables, customer code, team-chat about SoftServe work). **This is the critical gate.** Per `references/cowork-bridge.md` + `references/softserve-ai-usage-policy.md`, personal Servy must NEVER build a skill that operates on SoftServe data. Recommend a **Cowork playbook** instead: Servy drafts the instructions-only playbook into `routines/cowork/` and Gera runs it in Claude Desktop (Enterprise). Surface it as "build this, but Enterprise-side, not here."
4. **⏰ Routine-shaped** — the cluster fires on a predictable trigger, not on Gera deciding to run it: an event ("every time a lead lands / a specific type of email arrives / a ticket comes in") or a cadence ("every Monday / every Friday"). Propose a **ROUTINE (self-firing)**, not a manual-fire skill — a skill Gera must trigger keeps *him* as the trigger: *"if you're not around to trigger it, nothing happens."* (Nate 6h course, 2026-07-11 [0:20:51] + [1:55:16]; the interview-side twin is `/level-up` Phase 1 Q6–Q7.)
5. **✅ Buildable here** — a genuinely repeated, personal/public-data workflow with no skill yet. These are the real wins.

Also flag any `⚠ not a known skill` slash command — that's Gera invoking a command that doesn't exist (a skill he wishes he had), which is a strong signal.

### Step 4 — Present the candidate table
Output a scannable table, candidates ranked by `(repeat count × leverage)`, buildable ones first:

| Repeated task | What he wants out | Class | Proposed skill |
|---|---|---|---|
| draft a SoftServe team-chat status update | a ready-to-paste message in his voice | 🚧 SoftServe → Cowork | `team-update` playbook in `routines/cowork/` (runs in Claude Desktop Enterprise) |
| fill/QA a personal document from Downloads | the doc completed + grammar-clean | ✅ Buildable | `/doc-assist` |

Keep it honest: if the only repeated work is already covered or SoftServe-bound, say "nothing net-new to build here, and here's why" — that's a valid, useful outcome (same discipline as the wiki build-gate).

### Step 5 — Offer to build the top pick
Recommend the single highest-leverage **✅ Buildable** candidate and offer to hand it to `/skill-builder` now. A **⏰ Routine-shaped** winner goes to `/routines-builder` / `/servy-routine` instead — the deliverable is a self-firing routine, not a skill. For 🚧 SoftServe candidates, offer to draft an instructions-only playbook into `routines/cowork/` (zero SoftServe data) for Gera to run in Claude Desktop (Enterprise). One run should end with either a skill being built or a clear "nothing to build, here's the evidence."

## Boundaries

- **Discovery only.** Never write a skill here — that's `/skill-builder`'s job.
- **SoftServe firewall is non-negotiable.** Never propose building a SoftServe-data skill in personal Servy. Route it to Claude Desktop (Enterprise) as a `routines/cowork/` playbook. When unsure whether a candidate is SoftServe-bound, treat it as SoftServe-bound.
- **Read-only on history.** The miner only reads transcripts; it writes nothing except the optional `--json` dump you point it at (use the job tmp dir, not the repo).
- **No raw transcript dumping into chat.** Read the miner's report, not the raw `.jsonl` files — they're huge and may carry SoftServe content.

## Why a script underneath (WAT)

The deterministic extraction — parse 30+ transcripts, filter noise, count repeats, diff against the skill roster — is code's job (`scripts/skill-harvest.py`). The semantic clustering + classification + judgment is mine. Code extracts, AI reasons. See [[wat-framework]].
