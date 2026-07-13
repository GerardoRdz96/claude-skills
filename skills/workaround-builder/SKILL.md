---
name: workaround-builder
description: Use when a build is BLOCKED by an external wall and Gera (or Servy mid-task) needs a clever alternate route — an API is gated/paywalled, a tool is broken or missing a runtime, a service bans automation, a quota/limit bites, a platform lacks the feature, access is denied. Triggers — "find a workaround", "we're blocked", "there has to be another way", "X is gated/broken/down, what now", "how do we get around this", "/workaround-builder". Runs constraint-driven creative research: frame the wall → question if it's real → wiki/memory-first prior-art sweep → generate candidates through the 7 doors → ethics gate → score → smallest spike → register it. NOT for bugs in our own code (that's superpowers:systematic-debugging) and NOT for designing new features (that's brainstorming) — this fires when the obstacle is EXTERNAL.
argument-hint: "[the blocker: what you're trying to do and what wall you hit]"
---

# /workaround-builder — the alternate-route engine

## Why this exists

Servy's history is a museum of walls that fell to lateral moves: yt-dlp lost its JS runtime → the oembed endpoint + HTTP transcript path; Veo had no API access → the human-in-the-loop `veo-bridge`; cloud TTS was forbidden for confidential work → local Kokoro; Google throttled the sheet → a cached fallback the CI keeps fresh; generative i2v unavailable → procedural ken-burns. Untrained, the default failure modes are: give up and ask Gera, grab the FIRST workaround found without questioning the wall, re-derive a fix we already discovered last month, and never write it down. This skill fixes all four.

A workaround is a **route**, not a hack. The output is a ranked set of routes with an honest cost/risk read, never a way to cheat a boundary that exists for a reason.

## Gate 0 — the ethics gate (read before generating anything)

Some walls are load-bearing. **A "workaround" that bypasses these is a violation, not a solution — refuse it and say why:**

- Security boundaries, authentication, or access controls that aren't ours.
- Licenses, DRM, paywalls, anti-scraping measures, or platform ToS (the claude.ai-automation ban and Workana no-links rule are house precedents).
- The SoftServe rails: Internal+ data never routes through personal Servy or multi-brain, no matter how clever the route. A blocked SoftServe task's only "workaround" is the approved channel (Claude Desktop / Cowork).
- Anything where the wall's OWNER would reasonably object if they could see the route.

When the direct path is banned but the goal is legitimate, reach for the **compliant-bridge pattern** (house precedent: `veo-bridge` — the human does the gated step in their own session, Servy automates everything around it). That is always the first candidate against a policy wall.

## Steps

### 1. Frame the wall
Restate in one line: the GOAL one level up (the ask behind the ask), the EXACT failure (verbatim error / limit / denial), and what was already tried. If `$ARGUMENTS` is thin, pull the failure from the current session context before asking anything.

### 2. Classify the wall
Name its type — it points at which doors open:
- **Physics** (compute, bandwidth, model capability) → doors 5, 6, 7
- **Product gap** (feature doesn't exist, no API) → doors 1, 3, 7
- **Broken/missing tool** (dependency, runtime, outage) → doors 2, 6
- **Permission/policy** (auth walls, ToS, data class) → Gate 0 first, then door 4
- **Price/quota** (credits, rate limits, tiers) → doors 5, 6, 2
- **Knowledge** (we don't know how) → this is research, route to `/storm-research` or `deep-research` instead

### 3. Question the wall (cheapest move in the stack)
Before routing around it, spend 5 minutes testing whether it's real:
- Is it *actually* enforced, or documented-but-stale? (Reproduce it once, cleanly.)
- Does it apply to OUR case? (A geo-block from MX may not exist on a mirror; a "deprecated" endpoint may still serve.)
- Is it transient? (Outage vs. permanent removal — check status pages before building a route.)
A wall that evaporates under one probe needs no workaround.

### 4. Prior-art sweep (wiki first, then the world)
Run in parallel — spawn sub-agents when the wall is gnarly:
1. **House memory first** (check-wiki-before-web law): grep `references/` + memory + `references/workarounds.md` (the registry this skill maintains). We may have solved this exact wall.
2. **Web**: how did others route around this? Search the error verbatim, the "X alternative" phrasing, and GitHub issues of the blocking tool (maintainers discuss escape hatches in issues, not docs).
3. **The tool itself**: `--help`, man pages, config files, undocumented flags, exposed local state (wacli reading its own store; app SQLite/JSON caches on disk).

### 5. Generate candidates through the 7 doors
Force at least 3 candidates from different doors (one-door thinking is how you land on the first mediocre fix). House-proven examples anchor each door:

| # | Door | The move | House precedent |
|---|------|----------|-----------------|
| 1 | **Different door** | Same resource, another entrance: mirror, export, secondary endpoint | YouTube `oembed` for metadata when yt-dlp lacked a runtime |
| 2 | **Different tool** | Same job, another implement | `fetch-transcript.py` (pure HTTP) when yt-dlp needed deno; qwen2.5vl when gemma squashed tall shots |
| 3 | **Different layer** | Go under/over the abstraction: filesystem instead of app, API instead of UI, file instead of clipboard | reading Drive's public-folder HTML for file IDs; wacli reading the store directly |
| 4 | **Human bridge** | Split the gated step out to the human, automate everything around it | `veo-bridge`; launchd arming = Gera's paste |
| 5 | **Reduce the ask** | Need less than you think: smaller scope, lower fidelity, subset | poster-frame review instead of full-video; 720p ship instead of 4k |
| 6 | **Precompute / mirror** | Get it before you need it, or from where it already landed | `nate-sheet-cache.json` kept fresh by CI; R2 CDN when Supabase storage capped |
| 7 | **Emulate** | Build a good-enough substitute yourself | ken-burns ffmpeg fallback when generative i2v was unavailable |

### 6. Score and recommend
Table with one row per candidate: **Effort** (hours) · **Durability** (one-off / weeks / permanent — workarounds rot) · **Blast radius** (what breaks if it breaks) · **Ethics** (Gate 0 clean?). Then ONE recommendation with the reasoning, plus the runner-up as fallback. If the boring official path exists at similar total cost, recommend THAT (`/ponytail` composition: the cleverest workaround is the one you don't build).

### 7. Spike it
Define the smallest test that proves the route end-to-end (one curl, one file, one render) and run it if it's in-session cheap. A workaround that hasn't moved one real payload is a theory.

### 8. Register it (the compounding step)
When a workaround ships, append to **`references/workarounds.md`** (create on first use):
```
## <date> | <wall in 5 words> → <route in 5 words>
Wall: <what blocked us, verbatim error if short>. Door: <1-7>. Route: <what we did>.
Fragile if: <what change breaks this>. Revisit: <when to check if the official path opened>.
```
If it's load-bearing for a recurring flow, also drop a memory pointer. This is why the third identical wall costs zero.

## Rules

- **Gate 0 wins every time.** No exceptions for "just this once" or "it's only internal."
- Effort proportional to the wall: a broken CLI gets 10 minutes and door 2; a strategic platform gap gets the full sweep with sub-agents.
- Never present a workaround without its **rot profile** (durability + fragile-if). Undated workarounds become mystery infrastructure.
- Cross-references: our own code misbehaving → `superpowers:systematic-debugging`. Exploring what to build → `superpowers:brainstorming`. Validating whether the goal is worth it → `/roast`. Proving a chosen route at depth → `/spark`.
- After each run, note what worked/missed and improve this skill same-session (every skill run is data).
