---
name: meeting-hud
description: Use when Gera wants live meeting intelligence on his Mac — a near-real-time HUD of action items, decisions, open questions, and topics while a meeting runs (Teams, Zoom, Meet, or in-room). Triggers — "meeting hud", "listen to this meeting", "track this call", "take notes on this meeting live", "start the hud", "/meeting-hud", or Gera saying a meeting is about to start and he wants Servy on it. Captures system audio (audiotee, Core Audio taps) or mic, transcribes locally with whisper, and runs tiered local-first analysis. HARD GATE — SoftServe client/Internal+ meetings stay in local tiers (T1 regex + T2 Ollama) only; Servy reads the transcript in-session ONLY for personal/public content.
---

# Meeting HUD — near-real-time meeting intelligence

Servy's adaptation of the **MeetingHUD pattern** (see `references/local-first-agentic-patterns.md`): keep sensitive context close, give the model bounded evidence, make output visible enough for a human to verify. Plumbing is shared with `/cowatch` (`scripts/live_capture.py`); the analysis layer is `scripts/meeting_hud.py`.

## Step 0 — The SoftServe gate (NEVER skip)

Ask Gera: **"Is this meeting SoftServe client / Internal+ content?"**

- **Yes (SENSITIVE mode):** everything runs on-device only. Capture + whisper + T1 regex + T2 Ollama. **I never read the transcript or HUD into our conversation** — Claude on a personal sub is not a SoftServe-approved channel (`references/softserve-ai-usage-policy.md`). I only manage the processes and point Gera at the HUD file.
- **No (PERSONAL mode):** full stack. I read the rolling transcript on demand (T3), answer questions about the meeting, and produce the final digest in-session (scribe-style: decisions + action items).

Transcripts land in `knowledge/live/` which is gitignored — they never reach the remote either way.

## Step 1 — Pick the audio source

| Source | When | Mechanism |
|---|---|---|
| `system` | Headphones / any meeting app — captures what the Mac plays (both sides minus Gera's own voice) | `audiotee` (Core Audio taps, macOS 14.2+) |
| `mic` | In-room meetings, or speakers-on calls (catches both sides + Gera) | `ffmpeg avfoundation` |

`system` needs the audiotee binary at `~/.local/bin/audiotee`. If missing, hand Gera:
```bash
cd ~/.local/src/audiotee && swift build -c release && ln -sf ~/.local/src/audiotee/.build/release/audiotee ~/.local/bin/audiotee
```
First run of each source triggers a one-time macOS permission prompt (System Audio Recording / Microphone) — tell Gera to expect it.

Limitation worth stating: `system` alone misses Gera's own mic. For full both-sides capture on a headphones call, v2 needs an aggregate device or audiotee's mic mode (tracked in `pending.md`).

## Step 2 — Start capture + HUD (background)

```bash
SESSION="$(date +%F)-<meeting-slug>"
# capture (pick --source system|mic; --lang es + --model base for Spanish meetings)
python3 scripts/live_capture.py --source system --session "$SESSION" --chunk 60 &
# HUD: re-renders knowledge/live/$SESSION.hud.md every 60s until capture ends
python3 scripts/meeting_hud.py --session "$SESSION" --watch [--t2 gpt-oss:20b] &
```

- Run both via Bash `run_in_background: true`.
- `--t2 <model>` adds the local-LLM rolling summary **only if** `ollama list` shows a model. Skip silently if none.
- Tell Gera to open `knowledge/live/$SESSION.hud.md` (it re-renders in place; VS Code auto-refreshes).

## Step 3 — During the meeting

- **SENSITIVE mode:** I monitor process health only (state.json `status`, segment lag). I do not read transcript content.
- **PERSONAL mode:** on "what did they just say about X" / "summarize so far", I read `knowledge/live/$SESSION.jsonl` from the cursor and answer. `/loop` cadence optional for proactive reactions (like `/cowatch` co-watch mode).

## Step 4 — End of meeting

1. Stop capture (`kill` the producer; the consumer drains remaining segments — wait for `status: ended`).
2. Run `python3 scripts/meeting_hud.py --session "$SESSION"` once more for the final HUD.
3. **PERSONAL mode:** produce a scribe-style digest in-session (decisions, action items with owners, open questions) and offer to file it into `knowledge/`.
   **SENSITIVE mode:** point Gera at the final HUD file; offer the T2 Ollama summary command he can run himself. Nothing enters our chat.
4. Offer cleanup: the `.segments/` dir is already pruned; jsonl + hud stay local for Gera to keep or delete.

## Feedback loop

Every run is data — after each real meeting, ask Gera one question ("what did the HUD miss?") and patch the T1 cues in `scripts/meeting_hud.py` the same session.
