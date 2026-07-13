---
name: cowatch
description: Use when Gera wants to watch/hear a live event WITH Servy in near-real-time — a keynote, conference, launch, or any public live stream — and react together as it happens, or catch up on demand. Also when he drops a YouTube live URL and says "watch this with me", "co-watch this", "attend this event", "tell me what they announce", or asks mid-event "what did they just say about X". Triggers — "co-watch", "watch this live", "watch with me", "what's happening in the event", "what did they just announce", "/cowatch".
argument-hint: <youtube-or-stream-url> [--mode cowatch|catchup] [--model base.en] [--ingest]
---

# /cowatch — live event co-watching

Servy watches a live event WITH Gera in near-real-time. A background capturer
(`scripts/live_capture.py`) turns the stream's audio into a rolling JSONL
transcript via local whisper; this skill reads new transcript past a cursor and
either reacts when something notable lands (**co-watch**) or answers on demand
(**catch-up**). Near-real-time means ~1.5-2.5 min behind live — chunk length plus
whisper time. Full design: `docs/superpowers/specs/2026-06-02-cowatch-live-event-design.md`.

## Scope (v1)
- **Source:** `web` only (public YouTube/stream URLs via yt-dlp). `system` audio and
  `mic` are designed but NOT built yet — if Gera asks for those, say so and point to the spec.
- **Engine:** whisper.cpp (`whisper-cli`), models at `~/.local/whisper.cpp/models/`
  (`base.en` default, `small.en` for more accuracy / slower).

## Hard rules
- **Never fabricate.** Only react to text that is actually in the transcript file.
  Auto-captions garble names/numbers — flag uncertainty, do not "correct" to what you assume.
- **SoftServe boundary:** v1 is `web`/public only, so it is unrestricted. (When `system`/`mic`
  land, confirm it is not a client/Internal+ meeting before capturing — see spec §3.)
- **External publishing stays gated.** If Gera wants a LinkedIn post from the event, draft it
  and show him first (voice rules); never auto-publish.

## Step 0 — args
Parse `<url> [--mode cowatch|catchup] [--model base.en] [--ingest] [--interval 60]`.
Default `--mode cowatch`, `--model base.en`, `--interval 60`, ingest OFF.

## Step 1 — verify the stream + launch the capturer
1. Confirm it is a real live stream and a legit channel:
   `yt-dlp --no-warnings --print "%(live_status)s|%(channel)s|%(channel_is_verified)s|%(title)s" <url>`
   - If `live_status` is not `is_live`/`post_live`, tell Gera it is not live and stop.
   - Surface the channel + verified flag so Gera knows the source is trustworthy.
2. Derive a session id: `<today>-<slug-of-title>` (use `live_capture.session_id` / `slugify`).
3. Launch the capturer in the background (Bash `run_in_background: true`):
   `python3 scripts/live_capture.py --source web --url "<url>" --session "<sid>" --model <model>`
4. Wait until the first record appears in `knowledge/live/<sid>.jsonl` (capturer healthy).
   If the state file flips to `status: error` or no record appears, fail fast and report.

## Step 2a — co-watch mode (it talks)
Drive an interval loop (use the `/loop` skill at `--interval` seconds, or self-pace). Each tick:
1. Read cursor: `read_cursor(knowledge/live/<sid>.cursor)`.
2. `recs, new_cursor = read_new_records(knowledge/live/<sid>.jsonl, cursor)`.
3. **Judge notability** through Gera's lens — react only if a record contains: an announcement,
   a product/feature/version name, a number/benchmark, a demo, or anything touching his stack
   (LangChain/LangGraph, Claude Code, Cursor, agents, Azure AI) or Jumpstart/R&D. If notable,
   post a short reaction with a *why-it-matters-to-Gera* line. If not, stay silent.
4. `write_cursor(...)` to the new cursor.
5. **Max-quiet:** if 3 ticks pass with no reaction, drop one light check-in so you never vanish.
6. Read `knowledge/live/<sid>.state.json`; when `status == ended`, leave the loop → Step 3.

Read the JSONL/state via small `python3 -c "import live_capture as lc; ..."` calls (cheap), not by
loading the whole file into context.

## Step 2b — catch-up mode (it waits)
No loop. Tell Gera capturing is live ("ask me anything — 'what did they just say about X', or
'summarize the last 10 min'"). On each question, read new records / the buffer and answer from the
transcript only. Notice `status == ended` opportunistically and offer Step 3.

## Step 3 — end of event
When the capturer reports `status: ended`:
- **If `--ingest`:** run the wiki-ingest tail (the nate-watch pattern) — write a digest page in
  `references/`, update `references/index.md`, append `references/log.md`, register the raw
  transcript in `knowledge/README.md`, run the build-a-capability gate. Then offer a LinkedIn draft.
- **If not:** save the transcript, tell Gera where it lives (`knowledge/live/<sid>.jsonl`), and
  offer ingestion as a follow-up. The transcript is gitignored (`knowledge/*`), so it stays local.

## Files
- Engine: `scripts/live_capture.py` (tested: `python3 scripts/tests/test_live_capture.py`).
- Output: `knowledge/live/<sid>.jsonl` (transcript), `.state.json` (capturer state),
  `.cursor` (skill read-cursor), `.segments/` (temp WAVs, auto-cleaned).
- To stop early: terminate the background capturer process; it flips `status: ended` on SIGTERM.
