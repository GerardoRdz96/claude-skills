---
name: multi-brain
description: |
  Multi-LLM auto-router: Claude Code drives every turn and hands a sub-task to a specialist brain (Codex review/rescue, local vision, agy/Gemini-lineage, GLM-5.2) ONLY when that brain fits the job better than Claude alone — the other brains are tools Claude calls, and Claude stays in front of the user. MUST-FIRE — the No-Self-Review Law (CLAUDE.md Hard Rule 2): when Gera asks to "check / review / look over / proof / verify / audit / sanity-check / double-check / second-opinion" ANY work Claude just produced, route the review to Codex — never self-review. Also fires on: image/screenshot/slide/PDF/video reads and OCR ("what does this show"), whole-repo scans ("find every place X / map the architecture"), video generation / image-to-video / I2V, edits touching risky paths (auth/billing/migrations/deploy), Claude failing the same operation 2+ times ("I'm stuck / hand it off"), and explicit cross-architecture consensus ("ask all the models / before I commit to this"). Stays asleep for normal Q&A, drafting/building on safe paths, and reviews of content GERA wrote (not Claude). Full routing table, roster, and cost rules in the body; roster history + rationale in reference.md.
---

# Multi-Brain Auto-Router

Many brains, one terminal. Claude drives and stays in front of the user; it hands a sub-task to whichever brain is genuinely better for it, then integrates the result. Routing should be invisible and rare — most turns are Claude direct.

**Canonical decision rule (the gated version of this routing): `references/model-routing-framework.md`** — Gate 0 SoftServe data-classification (hard stop) → Gate 1 No-Self-Review (→ Codex, terminal) → Gate 2 specialist-beats-Claude-direct → one named route. This skill is the roster + reflexes; that page is the rule to walk when unsure where a task goes.

| Brain | Lineage | Role | How to call | Cost |
|---|---|---|---|---|
| **Claude** (you) | Anthropic | orchestrator, builder, driver | — | — |
| **Codex** | OpenAI/GPT | review, adversarial, rescue | `codex` CLI / `/codex:*` | plan |
| **Gemini** | Google | multimodal, 1M whole-repo | `gemini` CLI (**OAuth dark** — needs `GEMINI_API_KEY`/Vertex) | plan |
| **`agy`** (Antigravity CLI) | Google (Gemini 3.5 Flash) | agentic coding; Google-lineage consensus voice; successor to gemini CLI | `agy -p "…"` (after one-time sign-in) | **free** + opt-in/announce |
| **local vision** | local Ollama (Qwen2.5-VL default; Gemma alternate) | image/video OCR + scene reads | `scripts/local-vision.sh` | free/local |
| **GLM-5.2** | Z.ai (Zhipu) | long-horizon / open-coding specialist (1M ctx) | `scripts/glm.sh` (OpenRouter `z-ai/glm-5.2`) | **paid** + announce |
**GLM-5.2 (wired 2026-06-17)** is a DIRECT OpenRouter route via `scripts/glm.sh` — separate from, and not part of, the retired OpenCode gateway. Opt-in only: it overlaps Claude+Codex on coding, so it fires only when Gera explicitly delegates a big autonomous coding/refactor/long-horizon task or wants a frontier open-weights coding opinion. Paid per-token (OpenRouter; currently low balance → cap output with `--max-tokens`, or load credit / add a Z.ai key to "make the most of" it). **SoftServe rail: Z.ai-hosted (China) + OpenRouter = NOT a SoftServe-approved channel; never pipe Internal+ / customer IP here** (Gate 0 of `references/model-routing-framework.md`).

OpenCode gateway (Grok/DeepSeek/MiniMax/Qwen/Nemotron) retired 2026-06-06 — zero documented usage, sub cancelled; historical roster + per-brain prompt patterns in `reference.md`. Reinstate only if a task genuinely needs live web (Grok) or multilingual long-doc (Qwen) again.

## Routing table — when to fire

- **[MUST] review / check / verify ANY work Claude just produced → Codex review.** Trigger phrases (not exhaustive): "check over your work" / "check your work", "review what you just did" / "review your code" / "review the code you wrote", "look over this", "give it a once-over", "is this right?", "anything wrong with this?", "second opinion", "sanity check", "double-check", "proof this", "audit this", "make sure this works". Do NOT silently self-review; do NOT say "I'll review it inline." Route via Bash: `git diff | codex exec --skip-git-repo-check "Review this. Find bugs, risks, missing tests."` (or `/codex:review`). For high-stakes code, add a non-GPT brain for cross-architecture diversity and diff the findings. After Codex returns, integrate findings and end with: "(Routed via multi-brain → Codex.)" Same architecture = same blind spots — that's the failure mode this route prevents.
- "tear apart / stress test / find what's wrong / break this / poke holes" → Codex adversarial.
- "I'm stuck / can't figure this out / hand it off / try another model", OR the Failure-detection rule below trips → Codex rescue.
- Active edit touches a risky path → forced Codex adversarial review BEFORE saying "done" (announce it) — paths in Risk-path detection below.
- image / screenshot / UI / slide / diagram / video / PDF → read it, "what does this show", OCR → **DEFAULT: local** `scripts/local-vision.sh <img|video|url>` (default model `qwen2.5vl:7b`; free/private/offline/no-quota; video = frame-sample). **FRONTIER escalation** for the hard reads where quality matters → `scripts/agy-vision.sh <img|pdf|video|url>` (agy / Gemini 3.5 Flash; `view_file` decodes image+PDF+video natively; cloud + ~20/day quota → use sparingly, public data only). See [[local-vision]] / [[agy-cli]].
- "scan the whole repo / find every place X / pattern across the codebase / map the architecture" → Gemini 1M whole-repo needs a key/Vertex now (CLI OAuth dark); or `agy -p` reads files agentically; local fallback = qwen3.5:35b-a3b (256K) or Claude + ripgrep.
- "generate / make a video, text→video, **animate this image / image-to-video / I2V**" → `scripts/i2v.sh <image> [prompt]` ([[i2v]]) — auto-routes higgsfield (free credits, needs `higgsfield auth login`) → Veo via `gemini-veo.sh --image` (billed key) → kenburns ffmpeg fallback (procedural, always works). "Google Vids" has NO API; Veo is the model.
- needs CURRENT info past the knowledge cutoff — "latest / today / this week / recent / what shipped" → no active web-grounded brain (OpenCode/Grok retired). Tell the user, then fall back to WebSearch or a wiki lookup; reinstate OpenCode only if this keeps recurring.
- "ask all the models / cross-architecture consensus / before I commit to this" → consensus panel — see Parallel consensus mode below.
- Gera EXPLICITLY wants a Gemini-lineage take / delegates an agentic coding/refactor to "let Gemini try it" → **`agy -p "<prompt>"`** (FREE, Gemini-3.5-Flash agent harness; SIGNED IN; opt-in, announce). NOT a default — overlaps Claude+Codex; ~20/day quota; SoftServe-forbidden (Google collects Interactions data). See [[agy-cli]].
- Gera EXPLICITLY asks to delegate a big autonomous coding / refactor / long-horizon build, OR wants a frontier open-weights coding opinion → GLM-5.2 (opt-in, PAID, announce first) via `scripts/glm.sh`. NOT a default route — never auto-fire on "big refactor" language alone.

## Do NOT fire — Claude direct

- "Explain / what is / how does / walk me through" → Claude direct.
- "Write / draft / build / make / edit / change / refactor / plan / design" on non-risky paths → Claude direct (but if the user then says "now check your work" — MUST-FIRE applies).
- "Review my notes / my draft email / my doc" — content the USER wrote, not Claude → Claude direct.
- Conversational chat, greetings, status questions, file ops, git/bash/grep, normal Q&A → Claude direct.
- "Recall / what did we decide / look up" → memory + decisions log, not multi-brain.
- "Save this / wrap up" → other skills' territory.

When uncertain outside the review-verb case: stay asleep. Under-firing is fine; over-firing breaks trust and burns money.

## Ambiguity + cost rules

Bias toward FIRING on review verbs aimed at Claude's own output; bias toward STAYING ASLEEP on review verbs aimed at the user's own content. When uncertain about a review verb on Claude's work: FIRE. A 20-second call is cheap; a missed self-review bug is not.
Default to a SINGLE brain — do not stack models. Reserve the consensus panel for genuinely high-stakes, hard-to-reverse decisions, capped at 3 cross-architecture brains. Prefer FREE brains over paid ones for low-stakes work. Announce before routing to a PAID brain (GLM-5.2, or a reinstated OpenCode model) on a route the user did not explicitly request.

## Startup self-check (run once per session, before first route)

```bash
codex --version 2>&1 | head -1     # expect codex-cli 0.125+
```

Don't probe `gemini --version` — the gemini CLI is DARK (consumer OAuth dead 2026-06-18); re-add the check only after a `GEMINI_API_KEY` lands. If a tool is missing, announce once and fall back gracefully; don't retry every turn.

## Calling Codex (review / adversarial / rescue)

```bash
git diff | codex exec --skip-git-repo-check "Review this diff. Flag bugs, risks, missing tests. Be specific."
git diff | codex exec --skip-git-repo-check "Adversarial review. Challenge the design. Prove it's broken."
cat <context-bundle> | codex exec --skip-git-repo-check "Rescue mode. Claude tried 2x and failed. Solve from scratch."
```

Prefer the plugin slash commands when interactive — they have prompt engineering baked in: `/codex:review`, `/codex:adversarial-review`, `/codex:rescue`. Fall back to raw `codex exec` when piping context.

## Calling Gemini (multimodal + whole-repo)

```bash
gemini -p "<focused ask with explicit output format>" @./file
/cc-gemini-plugin:gemini --dirs <comma-separated-paths> "Find every place X. Return file:line list."
```

Always demand timestamps, page numbers, or file:line citations — never accept a flat summary.

## Calling GLM-5.2 (long-horizon / open-coding specialist)

Opt-in only, and PAID — announce before routing (Gera can say "stop"). GLM-5.2 is Z.ai's open-weights model that tops open frontend-coding benchmarks and is built for long-horizon (600+ iteration) agentic coding, with a 1M-token context.

```bash
scripts/glm.sh "Design + implement <large self-contained module>. Output full files."
git diff | scripts/glm.sh "Independent open-weights review of this refactor — find what Claude/Codex missed."
scripts/glm.sh --max-tokens 8192 --system "You are a senior <lang> engineer" "<task>"
```

- **SoftServe rail (Gate 0):** Z.ai-hosted (China) + OpenRouter is NOT a SoftServe-approved channel. Never pipe SoftServe Internal+ content or customer IP/code here. Personal/public only.
- **Cost:** paid per-token via OpenRouter; the account is currently low-balance, so default output is capped (`--max-tokens 4096`). To truly leverage it, load OpenRouter credit or wire a Z.ai key (`GLM_API_KEY`).
- **When NOT to use it:** routine edits, anything Claude/Codex already cover. Its edge is *large, self-contained, long-horizon* coding and a third-lineage coding opinion — not a default.

## Announcement protocol (REQUIRED for forced / paid routes)

Whenever the skill fires a route the user did NOT explicitly request — risk-path detection, failure-counter rescue, or any **paid** brain (GLM-5.2) — announce in one line BEFORE running so the user can interrupt with one word:

```
[multi-brain] routing to Codex (adversarial-review) — risk path: src/auth/
[multi-brain] handing to Codex rescue — Claude failed same test 2x
[multi-brain] routing to GLM-5.2 (paid) for a long-horizon coding pass — say stop to skip
```

Routes the user explicitly asked for ("yo check this", "ask Grok") need no announcement — just do it.

## Failure-detection rule (HARD, deterministic — not a vibe)

After Claude attempts the same operation and fails:
- 2× same test failure on same code path → MUST invoke Codex rescue. Announce it.
- 2× same error on same shell command → MUST invoke Codex rescue. Announce it.
- 2× same edit re-tried with no progress → MUST invoke Codex rescue. Announce it.

Reset the counter only when (a) the test/build passes, (b) the user changes the goal, or (c) the user says "keep trying." Send full context: failing output, what's been tried, relevant files.

## Media contract — vision is LOCAL now; the Gemini `@file` path is DARK

**Vision / on-screen-text / frame reads → `scripts/local-vision.sh` (local, default `qwen2.5vl:7b`, [[local-vision]]).** This is the active route. `qwen2.5vl:7b` is the DEFAULT (native dynamic resolution — it tolerates tall screenshots; the 2026-07-01 tall-shots fix); `gemma4:12b` is the opt-in ALTERNATE for richer scene description of normal-aspect frames. For a video, the script samples frames itself:

```bash
scripts/local-vision.sh "<url-or-file>" 15 "Return on-screen text, graphics, slides. TALKING_HEAD if none."
# images: scripts/local-vision.sh shot.png  ·  scene-description alternate: LOCAL_VISION_MODEL=gemma4:12b scripts/local-vision.sh shot.png
```

> **⚠️ DARK (needs a billed/free `GEMINI_API_KEY`):** the `gemini -p "@clip.mp4"` / `@doc.pdf` pipeline below stopped working when consumer OAuth died 2026-06-18. It only covers what local vision *can't*: true whole-video+audio understanding (not just frame OCR) and large PDF extraction. Re-arm by adding `GEMINI_API_KEY` to `.env` + flipping `~/.gemini/settings.json` auth, then:

```bash
# (DARK until a key lands) Video: acquire -> cap duration -> extract audio -> TIMESTAMPED findings
yt-dlp -f "best[ext=mp4][height<=720]" "<url>" -o /tmp/multi-brain/in.mp4
ffmpeg -t 120 -i /tmp/multi-brain/in.mp4 /tmp/multi-brain/clip.mp4 -y
gemini -p "Analyze frame-by-frame. Return [MM:SS] event list. Cap 800 words." @/tmp/multi-brain/clip.mp4
# (DARK) PDF: cap pages then page-numbered extraction
qpdf --pages input.pdf 1-100 -- /tmp/multi-brain/doc.pdf 2>/dev/null || cp input.pdf /tmp/multi-brain/doc.pdf
gemini -p "Extract key claims, data tables, chart findings, page-numbered. Cap 1000 words." @/tmp/multi-brain/doc.pdf
```

## Risk-path detection (path-based, not keyword-based)

Codex review is forced — without the user asking — when an active edit touches: `src/auth/**`, `src/billing/**`, `**/migrations/**`, `**/deploy/**`, `**/.env*`, `**/secrets/**`, `**/policy/**`, `infra/**`, `**/Stripe*`, `**/Plaid*`, `**/jwt*`, `**/oauth*`. Keywords alone in casual chat do NOT trigger it — it must be an active edit on those paths. Even normally-safe verbs (refactor/plan/design) fire Codex review if the target is irreversible or high-blast-radius (auth/billing/migration/deploy).

## Parallel consensus mode (high-stakes only)

Only when explicitly invoked ("ask all / cross-architecture consensus / before I commit"). With OpenCode retired and the **Gemini CLI dark** (consumer OAuth dead), the panel is **Claude (Anthropic) + Codex (OpenAI/GPT) + a Google-lineage 3rd voice**. For the Google slot, prefer **`agy -p`** (Gemini-3.5-Flash agent harness — once the one-time sign-in is done) for code/decision opinions; fall back to **local `gemma4:12b`** if agy isn't authed; or restore cloud Gemini with a `GEMINI_API_KEY`. Each returns the SAME structured template:

```
Recommendation: <one line>
Blocking risks: <bullets>
Assumptions: <bullets>
Confidence: low / medium / high
Tests required to verify: <bullets>
```

Claude diffs them — where they agree, where they disagree — and adjudicates BY EVIDENCE, not by averaging.

## Cost discipline

Default Claude-direct. Route to Codex or Gemini only when the specialist's strength is the actual bottleneck. A single strong model usually matches an ensemble at a fraction of the cost — the ensemble's real win is consistency on high-stakes, verifiable tasks, not speed.

## Output filing

Anything the skill produces goes to `./multi-brain-out/<YYYY-MM-DD>-<slug>/` (input.txt, each brain's output, Claude's build, a review file). Append one line per run to `./multi-brain-out/log.md`:

```
[2026-05-28 16:24] route=web brain=grok target=latest-langgraph files=2 cost=$0.01
```

That's the compounding ledger.
