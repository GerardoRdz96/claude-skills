---
name: nate-watch
description: Use to check Nate Herk's video DB for new uploads and ingest them into Servy's knowledge wiki. Triggers - "check for new Nate videos", "any new Nate Herk content", "did Nate post anything", "ingest Nate's latest video", "watch the new Nate video", a weekly Nate/knowledge sweep, or when Gera names a specific Nate video/row to ingest. Watches the video, reads its resources where reachable, and files the knowledge following the wiki protocol.
---

## What this skill does

Gera learns from Nate Herk's content. Nate maintains a public Google Sheet ("content DB") where every upload appears as a row with a YouTube link and (usually) a Google Drive folder of resources. This skill keeps Servy current with that DB: **detect new uploads → watch them → read their resources → file the knowledge into the wiki.**

It is the *judgment* half of the capability. The *detection* half is the deterministic script `scripts/nate-watch.py`. The actual filing follows `references/wiki-protocol.md` (this skill does not reinvent it).

**Autonomy = training wheels (the Bike Method).** Keep Gera in the loop: surface takeaways before/while writing, let him direct emphasis. Don't silently bulk-ingest. This is L2/L3 on the autonomy spectrum — earn trust before any hands-off cadence (see `references/four-cs.md`, `references/3ms-framework.md`).

## When to use

- Gera asks if Nate posted anything new, or asks to ingest a specific Nate video.
- A recurring knowledge sweep (manual, `/loop`, weekly ritual, or a future detect-only routine).

## The pipeline

### Step 0 — Reconcile cloud-routine output (pull before you detect)

The cloud nate-watch routine pushes its ingested wiki pages + the updated manifest to a `claude/nate-watch/<date>` branch that never merges to main. Pull the latest first, or detection dedupes against a stale manifest and you re-ingest videos the cloud already filed:

```
scripts/sync-cloud-routine.sh nate-watch            # preview what the routine added
scripts/sync-cloud-routine.sh nate-watch --apply    # reconcile if there's an unmerged branch
```

Safe by design: preview-first, union-merges `scripts/nate-watch-state.json` by video ID (never drops a video), brings in only pages the routine *added*, leaves `index.md`/`log.md` for manual review, never commits. If it brought in pages Gera hasn't seen, recap them before detecting. "Nothing to reconcile" → continue.

### Step 1 — Detect

Run from Gera's Mac (the live fetch works on residential IPs):
```
python3 scripts/nate-watch.py --check
```
Reports videos whose ID isn't in the manifest (`scripts/nate-watch-state.json`) and records them.

If the live fetch fails (network down, Google throttling), the script auto-falls back to `scripts/nate-sheet-cache.json` — kept fresh by the `nate-watch-detect` GitHub Action so the cloud routine has data. You can force the fallback explicitly with `--from scripts/nate-sheet-cache.json`.

Variants:
- `--pending` — known-but-not-yet-ingested (backlog Gera may want).
- `--list` — full catalog with ingest status.
- Gera may instead name a specific video/URL — just ingest that one.

If nothing is new and Gera didn't name one, say so and stop. Don't manufacture work.

### Step 2 — Triage relevance (one video at a time)
Not every Nate video earns a wiki page. Judge against Gera's world: AI-focused R&D Engineer at SoftServe, agentic AI systems, the Jumpstart Program, Claude Code / Codex / multi-brain, and the topics already in `references/index.md`. 
- **Clearly relevant** (Claude Code technique, agent patterns, AIOS method, model releases, automation): full ingest.
- **Marginal / off-topic** (pure crypto-trading stunts, unrelated creative-tool demos): note a one-line skip in the log and mark ingested so it stops surfacing — unless Gera wants it anyway. Ask if unsure.

### Step 3 — Watch (pull the transcript)

**Local path (default):** `yt-dlp` + the VTT cleaner — most reliable from a residential IP.
```
yt-dlp --js-runtimes deno --skip-download --write-auto-subs --write-subs \
  --sub-langs "en.*,en" --sub-format "vtt/best" \
  -o "knowledge/<slug>.%(ext)s" "<youtube-url>"
python3 scripts/clean-vtt.py "knowledge/<slug>.en.vtt" "knowledge/<slug>.md" \
  --title "<title>" --url "<youtube-url>"
```

**Cloud / fallback path:** `youtube-transcript-api` (pure HTTP, no JS runtime). Used by the cloud routine in `routines/nate-watch.md` and as a fallback when `yt-dlp` isn't available.
```
python3 scripts/fetch-transcript.py "<youtube-url>" "knowledge/<slug>-<id>.md" --title "<title>"
```
`<slug>` = short kebab title + the 11-char video ID (e.g. `nate-token-hacks-tXtCK66fPj8`). Read the cleaned `.md`, understand it, draft takeaways. (Transcript captures speech, not on-screen demos — lean on the resources for code/commands.)

### Step 4 — Read the resources (best-effort)
If the row has resources (`has_resources`), the URL is in the manifest / `--check` output. Fetch what's reachable:
- **GitHub repo** → `gh repo view` / clone / read the README + key files.
- **Public Google Doc / PDF / web page** → fetch it; use `pandoc` (docx→md) or `qpdf`+read (PDF) per the media-tools in `CLAUDE.md`.
- **Google Drive *folder*** (the common case — ~33/34 resources) → **try the curl path first** (proven 2026-06-10 on folder `1F4Zovw…`): (1) `curl -sL "<folder-url>"` → the public folder's HTML embeds every file's ID — extract with regex `[-\w]{25,}` near `data-id=`/entry blobs, and file names + MIME types sit within ~600 chars of each ID; (2) download each via `curl -sL "https://drive.google.com/uc?export=download&id=<fileId>"` into `knowledge/<slug>-<filename>`. Works for public folders with normal files (md/pdf/png); Google-native Docs/Sheets need an export endpoint instead. **If the folder is private or the parse comes up empty, fall back to surfacing the URL to Gera for a manual drop into `knowledge/`.** (Phase-2 fix: a printed Drive CLI, CLI-first — see `references/printing-press.md`.) Don't pretend to have read a folder you couldn't open.

### Step 5 — File it (wiki protocol)
Follow `references/wiki-protocol.md` exactly:
1. Discuss takeaways with Gera (don't just dump).
2. Write/update the relevant `references/` page(s) — fold into existing pages where the topic already exists (e.g. a new Opus video enriches `opus-4.8.md`); cross-link, don't duplicate.
3. Update `references/index.md` (new/changed entries).
4. Register the raw transcript (and any resource files) in `knowledge/README.md`.
5. Append a `## [date] ingest | <title>` line to `references/log.md`.

### Step 6 — Lint + record
- Run the **`warden`** agent (read-only) over the wiki after edits — it catches contradictions, broken links, index drift.
- Mark the video ingested so it stops surfacing:
```
python3 scripts/nate-watch.py --mark-ingested <videoId>
```

### Step 7 — Report
Tell Gera: what was ingested (and which wiki pages moved), what was skipped and why, and any resource folders that need his manual drop into `knowledge/`.

## Cadence

This skill runs two ways:

- **Manual / interactive (this file):** Gera invokes `/nate-watch` (or asks "any new Nate videos?"). The skill walks through the steps above with him in the loop.
- **Cloud routine (`routines/nate-watch.md`):** twice-daily autonomous run in Anthropic's cloud. Same SOP, executed unattended against a fresh clone of the repo. Uses `scripts/fetch-transcript.py` (cloud-friendly) instead of `yt-dlp`. Pushes wiki updates to a `claude/nate-watch/<date>` branch — never to `main`. Gera reviews the claude.ai session and decides whether to merge.

Both paths share the same scripts and the same wiki protocol — only the trigger differs.

## Notes

- The sheet's text is double-encoded; the script repairs the mojibake (`â€¦` → `…`). Use the script's cleaned titles, not raw sheet text.
- Already-ingested-elsewhere: if `--check` later flags a video Servy already has a page for (e.g. it appears in the sheet after we ingested it directly), confirm the page exists, then just `--mark-ingested` it — don't rewrite.
- Gera-supplied same-day URLs (the common /goal case) aren't in the sheet yet, so `--mark-ingested` warns "not in manifest". Standing pattern (4th occurrence 2026-07-12): add the entry to `scripts/nate-watch-state.json` manually (`title/date/youtube/resource/has_resources/first_seen/ingested: true` + a `note`) so the next `--check` dedupes instead of re-surfacing it.
- Commit wiki changes only when Gera asks (standing git-safety rule in `CLAUDE.md`).
