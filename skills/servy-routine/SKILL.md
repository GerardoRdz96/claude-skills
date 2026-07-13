---
name: servy-routine
description: Use to schedule a new cloud Claude routine for Servy. Triggers - "schedule a routine", "create a cloud routine for X", "build a new Claude routine", "automate this on a schedule", "make this run twice daily / nightly / weekly", "set this up to run in the cloud", or when a /routines-builder decision lands on "cloud routine". Bakes in Servy's standing defaults (Servy env, scoped tools, MCP keyring stripped, `claude/<name>/<date>` branch push, in-prompt setup) so Gera doesn't have to think about claude.ai every time. The only claude.ai handoff is when a routine needs a real secret env var.
---

## What this skill does

Servy operates on a few sharp defaults for cloud routines (the "[Four Cs](../../../references/four-cs.md) Capabilities + Connections" layer). This skill encodes them so I drive the entire setup — Gera answers 3-4 questions and the routine is armed and tested. The only time Gera touches `claude.ai` is when a new routine genuinely needs a **secret env var** (those must live in the cloud Environment, not in prompts or the repo — secrets in git history persist even after deletion).

This skill is the **builder** for cloud routines specifically. The generic [`/routines-builder`](../routines-builder/SKILL.md) skill is the **decision gate** (routine vs hook vs `/loop` vs ritual skill). When the answer is "cloud routine," this skill takes over.

## Standing defaults — what I bake in automatically

Read `routines/_servy.json` first; it's the source of truth. Current defaults:

| Field | Value | Why |
|---|---|---|
| `environment_id` | The Servy env at claude.ai | Shared by every Servy routine — no per-routine env sprawl |
| `environment_network` | **Full** | Set once at claude.ai when the env was created; all routines inherit |
| Model | `claude-sonnet-4-6` | Cheap + fast for mechanical SOPs (most routines). Bump to Opus only when prose quality drives the value. |
| Repo | `https://github.com/GerardoRdz96/Servy` | Most Servy routines operate on the Servy repo. Override per routine. |
| `allowed_tools` | `["Bash", "Read", "Write", "Edit", "Glob", "Grep"]` | Minimum useful set. Add only what the routine actually needs. |
| `mcp_connections` | **Stripped** (`clear_mcp_connections: true`) | The Four Cs lesson: "instructions ≠ capabilities — don't put a key on the keyring you don't want exercised." The API auto-attaches every connector by default; we always strip. |
| Branch policy | Push only to `claude/<name>/<YYYY-MM-DD>`. Never `main`. | Built-in review gate — Gera merges what he wants |
| Setup deps | Bake `pip install` into the routine prompt, not the env's Setup script | Avoids a claude.ai trip per new dep. ~1s overhead per run is acceptable. |
| Spec file | `routines/<name>.md` is the authoritative prompt source | Routine prompt is a *pointer* to the spec; we edit the spec, not the routine, to evolve behavior |
| Timezone | `America/Monterrey` (Gera's local) — convert to UTC for cron | UTC-6 year-round (no DST since 2022 reform) |

## What I CAN and CAN'T manage from here

| Thing | Managed via API by me | Notes |
|---|---|---|
| Routine config (env_id, prompt, schedule, model, allowed_tools, mcp_connections) | ✅ Yes — `RemoteTrigger` create/update/run | Full control |
| Which routines exist + their state | ✅ Yes — list/get | |
| **Env Network mode** (Trusted/Full/None) | ❌ Set once at claude.ai per env | Servy env is already Full — every routine using it inherits |
| **Env Setup script** | ❌ claude.ai only — but we don't use it; we bake into prompts instead | |
| **Env variables / secrets** | ❌ claude.ai only — security boundary | If a routine needs e.g. an API key, surface that to Gera as the one handoff |
| Deleting routines | ❌ API doesn't support; direct Gera to https://claude.ai/code/routines | |

## Workflow — Discovery, then build

**Step 0 — Triage.** If it's unclear this should be a cloud routine, invoke `/routines-builder` first (decision gate: routine vs hook vs `/loop` vs ritual skill). If Gera has already said "schedule a routine" or "make a cloud routine," continue.

**Step 1 — Load defaults.** Read `routines/_servy.json`. If `environment_id` is the TODO placeholder, ask Gera **once** for the Servy env_ID (from `claude.ai/code` → Environments → Servy → ID), write it into the JSON, commit. After that, every future routine picks it up — no more asks.

**Step 2 — Discovery (compact; auto-mode may collapse this to one batched AskUserQuestion):**

1. **Routine name** — kebab-case, used for the spec file (`routines/<name>.md`), branch prefix (`claude/<name>/<date>`), and the routine name field. Example: `nate-watch`, `weekly-audit`, `monthly-digest`.
2. **Schedule** — Gera's local time (Monterrey). Convert to UTC cron and **confirm the conversion** before creating. Min interval is 1 hour. For one-off, use `run_once_at` UTC.
3. **What it should do** — the user-facing task. Capture verbatim; the spec file is where it becomes precise.
4. **Repo** — default is `GerardoRdz96/Servy`. Override only if it should operate elsewhere.
5. **Deps?** — any Python packages the prompt will need. We bake `pip install --quiet <pkgs>` into the prompt's first step.
6. **Secrets?** — does it need an API key, OAuth token, anything sensitive? If yes: **this is the one claude.ai handoff** — Gera adds the env var to the Servy env at claude.ai before we Run-now. If no: nothing else needed.
7. **Model** — default Sonnet 4.6; bump to Opus only if prose quality matters (e.g. drafting wiki pages, external content) AND run frequency is low enough that the extra tokens are worth it.

**Step 3 — Write the spec at `routines/<name>.md`.** Structure mirrors `routines/nate-watch.md`:
- Top: claude.ai setup notes (this is read-only-by-Gera reference; we don't go to claude.ai if the defaults cover us).
- `## Routine prompt` section: the full instructions the routine executes. Be specific, name files/dirs, state success criteria, set boundaries (which paths it can touch), define push policy (`claude/<name>/<date>` only), define failure handling (log + continue), bake any `pip install` lines at the top.
- Boundaries must include: `Never push to main. Never modify CLAUDE.md, scripts/*.py, .claude/, connections.md unless this routine is specifically about one of those.`
- If the routine uses secrets, the spec must say it plainly: `<KEY> is available as an environment variable. Use it directly from the environment. Do NOT look for a .env file — the cloud clone has none.` Without this line, cloud runs default to hunting for `.env` (CLAUDE.md documents that's where keys live locally) and error out.
- If the routine needs memory across stateless runs (last-seen IDs, cursors, dedupe): keep it in `scripts/<name>-state.json` — the standing memory-trail convention (`nate-watch-state.json`, `tech-radar-state.json` are live examples). The spec reads it at start and updates it at the end so runs continuously get better. Cloud caveat: state written by a run lands on its `claude/` branch and only feeds future runs once merged.

**Step 4 — Build the routine prompt.** The actual prompt sent to the routine is a *short pointer* to the spec file:

```
You are a scheduled Claude Code routine running in Anthropic's cloud.

1. Read CLAUDE.md for project conventions.
2. Open routines/<name>.md, find the section titled '## Routine prompt', and execute it exactly. That section is the authoritative spec.

Reminders that override any conflicting impulse:
- If there is nothing to do, exit cleanly without committing or pushing.
- Only modify files the spec explicitly allows.
- Push only to claude/<name>/<YYYY-MM-DD> branches. NEVER push to main.
- [include only when the routine uses secrets] <KEY> is available as an environment variable. Use it directly from the environment. Do NOT look for a .env file — this clone has none.
- If this run fails, end loudly: send Gera a Telegram message naming the routine and the error (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env vars; skip if absent), then log the failure to references/log.md and commit it so the trail survives. Never fail silently.

Begin.
```

This makes the routine self-updating: edit the spec, the next run uses the new behavior. No re-creating the routine.

**Step 5 — Create + scope the routine.** Two `RemoteTrigger` calls:

1. `action: "create"` with body:
   ```json
   {
     "name": "<name>",
     "cron_expression": "<cron-UTC>",
     "enabled": true,
     "job_config": {
       "ccr": {
         "environment_id": "<from _servy.json>",
         "session_context": {
           "model": "<model>",
           "sources": [{"git_repository": {"url": "<repo>"}}],
           "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]
         },
         "events": [{"data": {
           "uuid": "<fresh v4 uuid>",
           "session_id": "",
           "type": "user",
           "parent_tool_use_id": null,
           "message": {"content": "<short pointer prompt>", "role": "user"}
         }}]
       }
     }
   }
   ```
2. `action: "update"` with body `{"clear_mcp_connections": true}` — strip the auto-attached keyring (the Four Cs lesson).

Generate the UUID with `python3 -c "import uuid; print(uuid.uuid4())"`.

**Step 6 — Run-now.** `action: "run"` with the new trigger_id. Surface the live session URL: `https://claude.ai/code/routines/<trigger_id>`. Tell Gera to watch it (the `/routines-builder` supervised-test rule). Don't claim "done" until the first run succeeds — verification before completion.

**Step 7 — Verify outcome.** After the Run-now finishes (or Gera reports what he saw):
- ✅ Success → routine is armed. Register it in `references/capabilities.md` only if this routine is meant to surface as a user-facing capability (most routines are background; nate-watch is a skill, the routine just powers part of it). Per the CLAUDE.md budget protocol, capabilities never get per-entry lines in CLAUDE.md.
- ⚠️ Network error on Sheets/YouTube/etc → Servy env's network isn't Full, or env_id is wrong. Either fix the env at claude.ai or `update` the routine to point at a Full-network env.
- ⚠️ Missing secret → surface to Gera which env var to add to Servy env at claude.ai. Re-run.
- ⚠️ Push rejected → permissions on `claude/` branch prefix. Direct Gera to claude.ai routine settings.

**Step 8 — Update bookkeeping.** If this routine adds a new domain to Servy:
- Update `connections.md` (new domain row + a status note).
- Update `references/capabilities.md` if it's a user-facing capability worth flagging.
- Don't commit `routines/_servy.json` updates as part of routine setup — those are infrastructure changes that get their own commit when env_id changes.

## When to bypass this skill

- One-shot run (`run_once_at`) for a non-recurring chore — fine to use `/schedule` directly.
- A routine in a different repo (not Servy) where Servy's defaults don't apply.
- Debugging an existing routine — use `/schedule` directly to list/get/update.

## Examples (compressed)

**"Schedule a weekly project-audit routine that runs every Sunday 8pm."**
→ name `weekly-audit`, cron `0 2 * * 1` (8pm Sunday Monterrey = 02:00 Monday UTC), spec at `routines/weekly-audit.md` that says: pull repo, run `/audit`, commit the scoreboard to `references/audits/<date>.md`, push `claude/weekly-audit/<date>`. No deps, no secrets, Sonnet, no claude.ai trip.

**"Set up a routine that posts the daily digest to Slack at 9am."**
→ Decision-gate stop: needs Slack → check claude.ai Connectors. If Slack isn't connected at claude.ai/customize/connectors, direct Gera there first. If yes: name `daily-slack-digest`, attach Slack connector via `mcp_connections` (don't strip it this time — we WANT this key), Opus model (prose), bake any deps in-prompt, supervised Run-now.

## Notes

- **The skill's own source of truth** is `routines/_servy.json` (defaults) + this SKILL.md (process). Keep them in sync.
- **First time only:** Gera pastes the Servy env_ID once. After that, this skill is fully self-driving except for the secret-env-var case.
- **No Discovery Interview ceremony** by default — auto-mode collapses Step 2 to a single batched `AskUserQuestion`. If Gera explicitly asks for a thorough Discovery (per the `feedback-skill-building` memory), invoke `/skill-builder` patterns alongside.
- **Pre-flight checklist** from `references/claude-code-routines.md` still applies: Run-now + watch, confirm network mode, test failure path, don't autoretry blindly.
