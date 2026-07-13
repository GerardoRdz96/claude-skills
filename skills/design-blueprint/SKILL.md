---
name: design-blueprint
description: Invoked explicitly via /design-blueprint <url> (model auto-invocation is disabled — natural asks like "capture this site's vibe" won't fire it). v2 — Level 7 of the website ladder. Mode A: Firecrawl /v2/scrape structured extraction + deterministic verbatim CSS-token capture (css-tokens.sh), rendered as a blueprint (colors, typography, tokens, layout, motion, copy tone) with a one-shot rebuild handoff. Mode B: /design-blueprint research <niche> in <place> — winners-vs-losers outlier research producing an evidenced conversion blueprint. URL only — no images or local files.
argument-hint: <url> | research <niche> in <place>
disable-model-invocation: true
---

# /design-blueprint — extract reusable design blueprint from a URL

Solves the "make it look modern" problem in front of every UI workflow. Instead of vague prompts, this skill produces a concrete brand artifact derived from a real inspiration site — colors, typography, layout language, motion, copy tone — that `/frontend-design`, `/gsd-ui-phase`, `/gsd-sketch`, or Claude Design can consume as their starting point.

**v2 (2026-07-05, from the [[website-design-levels]] ingest):** this is Servy's **Level 7 — design extraction**. Two things changed: (1) the blueprint now carries a **verbatim CSS-token capture** (real custom properties, font stacks, radii, shadows, load-bearing class rules — deterministic, `scripts/css-tokens.sh`) alongside the LLM read, because "nobody can verbalize great design" but tokens don't lie; (2) a **rebuild handoff** that one-shots a new site FROM the blueprint ("levels this up", never a copy). A second mode, **outlier research**, produces the Level-6 conversion blueprint. Blueprints accumulate in `artifacts/design-blueprints/` — check the library before extracting fresh ([[design-swipe-file]]).

**Mode routing:** argument starts with `research` → Mode B (outlier research, below). Otherwise → Mode A (URL extraction, Steps 0–5).

Engine: Firecrawl **/v2/scrape** REST endpoint (called directly via curl). Auth via `FIRECRAWL_BEARER_AUTH` in `.env`.

**Why direct REST and not `firecrawl-pp-cli`:** the imported CLI (hnshah's, v1.0.0) is built against Firecrawl /v1, which deprecated `/extract` mid-2026 and now returns empty payloads for structured extraction. /v2/scrape with `formats: [{type: "json", prompt: "..."}]` is the synchronous replacement. When we `/printing-press-reprint firecrawl` against the current spec, this skill can switch to `firecrawl-pp-cli` again — until then, direct REST works today.

## Step 0 — Preflight

1. **Confirm the argument is a URL.** Must start with `http://` or `https://`. If missing, ask Gera for one — do not proceed with no URL.
2. **Auth.** `FIRECRAWL_BEARER_AUTH` lives in `.env` (per CLAUDE.md "Where things live"). The extract script sources `.env` itself and errors clearly if the key is missing — if it does, point Gera to `.env` and stop.
3. **Derive slug.** From the URL: `slug = host + "-" + first-path-segment`, lowercased, non-alphanumerics → hyphens, collapsed. `https://linear.app` → `linear-app`; `https://stripe.com/payments` → `stripe-com-payments`.
4. **Derive output path.** `artifacts/design-blueprints/$(date +%Y-%m-%d)-<slug>.md`. If file exists, append `-2`, `-3`, etc.

## Step 1 — Extract via the bundled script

**RUN the bundled script — do not regenerate the curl/jq sequence inline:**

```bash
bash .claude/skills/design-blueprint/scripts/extract.sh "<URL>" "<slug>"
```

One synchronous POST. Costs ~5–20 Firecrawl credits depending on page complexity. The script owns the whole fragile call: payload build (from `extraction-prompt.txt` + `extraction-schema.json`), auth, HTTP-code handling (401 key / 402 credits / 400 bad URL / 5xx-with-one-retry), the honesty checks (missing `.data.json`, extraction `error`), and the theme-color fallback for `color_palette.primary`.

- **stdout** = the extraction JSON (`.data.json`). Capture it: `EXTRACT=$(bash ... extract.sh "<URL>" "<slug>")`.
- **stderr** = `creditsUsed`, the raw response path (`/tmp/fc-blueprint-<slug>.json`), and any notes.
- **Non-zero exit** = a human-readable error on stderr. Relay it to Gera verbatim; do NOT render.

## Step 2 — Judge the extraction

The script already refuses hard failures. One judgment call remains for you: if most top-level fields in the extraction are `null`, the page didn't give the LLM enough signal — render WITH `(not detected)` markers everywhere; do NOT fabricate values to fill the template.

Cost reporting: surface the `creditsUsed` line from the script's stderr so Gera tracks spend.

## Step 2b — Verbatim token capture (free, deterministic)

**RUN the bundled script:**

```bash
bash .claude/skills/design-blueprint/scripts/css-tokens.sh "<URL>"
```

Runs after the Step-2 judgment, before rendering — its output feeds Step 3 regardless of how thin the LLM extraction came back (tokens often survive where the LLM read fails, and vice versa).

- stdout = a ready markdown "Verbatim token capture" section: brand custom properties (framework internals like `--tw-*` filtered), `@font-face` families, font stacks by frequency, `font-variation-settings`, border-radius / box-shadow / letter-spacing values, and load-bearing rules (h1/h2/body/button/container). Costs nothing (curl, no Firecrawl). Discovered stylesheet URLs are scheme/host-vetted (http/https only; private/loopback hosts only when the page itself is local) and all fetched CSS is markdown-sanitized before rendering.
- Honest-empty is a valid result: JS-rendered sites (e.g. antigravity.google) yield "(none found)" — the blueprint then leans on the Step-1 LLM extraction, and the section says so. Never fabricate tokens.
- Non-zero exit (page unreachable) → note it in the blueprint and continue; Step 1's Firecrawl fetch may still have worked.

## Step 3 — Render the markdown blueprint

Use the template at `.claude/skills/design-blueprint/blueprint-template.md` as the structural skeleton. Substitute `{{field.path}}` placeholders from the JSON. For null fields, write `(not detected)`. For arrays of length 0, write `(none)`. Paste the Step-2b stdout verbatim into the template's "Verbatim design tokens" section (section 6).

Save to the output path from Step 0. Use the `Write` tool, not `cat > file` (the Write tool tracks file state properly for any later Edit operations).

## Step 4 — Preview to chat

Echo three things:
1. The absolute output path (Gera can `open` it).
2. A 5-line snippet: brand name + tagline + primary color hex + heading font family + density. Pulled from the parsed JSON, not the rendered markdown.
3. Credits used (from `.data.metadata.creditsUsed`).

No full file dump.

## Step 5 — Handoff offer

Ask via `AskUserQuestion`:

> "Blueprint saved. What's the next step?"
>
> 1. **One-shot rebuild ("levels this up")** — build a NEW site from the blueprint, right now (procedure below).
> 2. **`/frontend-design` — build a one-page mock** — feed the blueprint into Frontend Design to produce a polished HTML mock.
> 3. **`/gsd-ui-phase` — generate a UI-SPEC.md** — turn the blueprint into a structured design contract for a planned phase.
> 4. **Stop here** — blueprint is the deliverable; invoke a workflow manually later.

If Gera picks 2–3, invoke that skill and pass the blueprint path as input.

### The one-shot rebuild (the Level-7 move)

When Gera picks option 1 (or asked for a site up front), build FROM the blueprint with this contract:

1. **Prompt shape is three clauses** (self-brief before generating): (a) the blueprint file is the design system — obey its tokens, type pairing, spacing rhythm, motion language; (b) the goal is a site that **"levels this up" — an original that out-executes the reference, never a copy**; (c) the new site's actual subject/product.
2. **Invented placeholder brand** unless Gera named one — pick a clean name one find-replace away from a real one. Extracted design + invented brand + original copy = never plagiarism. Write brand-grade copy, not lorem.
3. **Build through the Front-End Review Law** ([[front-end-review-framework]]): `frontend-design` + `taste-skill` fire as normal; the blueprint is the "real design system" they start from. Default output for a landing one-shot: a single self-contained HTML file.
4. **Transfer report + review gate:** after building, enumerate which blueprint cues were used vs adapted, then run `scripts/frontend-review.sh` on the rendered page and iterate to PASS. Never ship on self-assessment.

## Mode B — outlier research (`/design-blueprint research <niche> in <place>`)

The Level-6 move: a beautiful site that doesn't convert is a Ferrari with no engine. This mode produces an **evidenced conversion blueprint** from live competitor data, consumable by a different model/session than the one that will build.

1. **Fill the template** at `outlier-research.md` with niche + geography (and any Gera constraints).
2. **Run the research yourself** (you are the research model): use Firecrawl REST — `/v2/search` to find ~10 strong and ~10 weak competitors, `/v2/scrape` (markdown format) on the shortlist. Budget cap: **≤25 scrape calls**; surface credits used. `.env` → `FIRECRAWL_BEARER_AUTH`, same auth pattern as `extract.sh`.
3. **Deliver the blueprint** to `artifacts/design-blueprints/<date>-research-<niche-slug>.md`: winners-vs-losers contrast (what winners have that losers don't, page/section ORDER, CTA copy), a scoring matrix defining what a great site in this niche is/isn't, and every claim traced to a scraped URL ("everything must be evidenced" — no vibes).
4. **Cross-validate before build:** offer to route the blueprint to Codex for a different-lineage sanity pass (the video's "cross validate with a different model"; our No-Self-Review Law says yes when the build will be ours).

## Cost discipline

- **Mode A: one `/v2/scrape` call per invocation.** Never loop. (`css-tokens.sh` is free — plain curl, no Firecrawl.)
- **Mode B is the sanctioned exception:** research needs many pages — capped at **≤25 scrape calls** per run, credits reported at the end.
- Typical Mode A cost: 5 credits for cache hit, 15–20 for fresh + LLM extraction.
- Extraction prompt lives in `extraction-prompt.txt` — tune there. Keep it under ~2KB; Firecrawl silently drops the `json` field if the prompt is too large.

## What this skill does NOT do (v2)

- **No image input.** URLs only. Image/screenshot support would route to Claude multimodal directly (a v3 candidate; for reference *images*, use the [[design-swipe-file]] protocol instead).
- **No multi-URL composition in Mode A.** One URL per extraction. To compose, run N times and merge artifacts manually. (Mode B scrapes many URLs by design, under its call cap.)
- **No automatic handoff execution.** Step 5 asks; it doesn't auto-fire.
- **No invented brand info in blueprints.** If extraction returns null/empty, the markdown says `(not detected)` — never fabricated. (The one-shot rebuild DOES invent a placeholder brand — that's the build, not the blueprint.)

## Files in this skill

- `SKILL.md` — this file
- `scripts/extract.sh` — the deterministic /v2/scrape call (payload build, POST, HTTP handling, honesty checks, theme-color fallback) — RUN it, don't reimplement it
- `scripts/css-tokens.sh` — deterministic verbatim CSS-token capture (Step 1b) — RUN it, don't reimplement it
- `extraction-prompt.txt` — short prompt prefix sent to Firecrawl alongside the schema
- `extraction-schema.json` — JSON Schema constraining the structured output
- `blueprint-template.md` — markdown skeleton for Step 3 rendering
- `outlier-research.md` — Mode B research-prompt template (winners-vs-losers)

## Related

- `references/website-design-levels.md` — the 7-level ladder this skill is Level 7 of (v2's source doctrine)
- `references/design-swipe-file.md` — reference intake + the blueprint library protocol
- `references/claude-design.md` — the doctrine page (Anthropic Labs Claude Design + Jack Roberts angle) that birthed this skill
- `knowledge/jack-claude-cms-Q_K3k_ge8NA.md` — Jack's video transcript + Skill-vs-Agent-vs-Routine verdict
- `knowledge/jack-7levels-websites-AFRL9dtUHeI.md` + `.frames.md` — the 7-levels video (transcript + frame analysis) behind v2
- `references/printing-press.md` — context on why we have `firecrawl-pp-cli` (and why it's currently bypassed for the extraction call)
- `.env` — `FIRECRAWL_BEARER_AUTH` lives here
