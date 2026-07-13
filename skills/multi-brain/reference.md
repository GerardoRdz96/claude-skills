# Multi-Brain Reference — model roster, roles, and the research behind them

> **Status note (2026-06-06, updated 2026-06-17):** OpenCode sub cancelled after zero documented usage in ~30 days. The active stack is Claude + Codex + Gemini + **GLM-5.2** (added 2026-06-17 as an opt-in long-horizon / open-coding specialist via `scripts/glm.sh` → OpenRouter `z-ai/glm-5.2`, a DIRECT route, NOT the retired gateway). Everything below about Grok/DeepSeek/MiniMax/Qwen/Nemotron/GLM-5.1/Kimi is preserved as the original research record — useful if Servy ever reinstates the gateway (live web, multilingual long-doc), but the routing in `SKILL.md` only fires Codex, Gemini, and (opt-in, paid) GLM-5.2.
>
> **⚠️ Gemini route change (2026-06-22):** Google killed the consumer `gemini`-CLI "Login with Google" OAuth on 2026-06-18 (free/Pro/Ultra all `UNSUPPORTED_CLIENT`), and there is no `GEMINI_API_KEY` in `.env`. So the **Gemini CLI is dark** — its multimodal *and* whole-repo routes no longer fire. Google's migration target (Antigravity IDE) is GUI-only, no headless CLI ([[antigravity]]), so it does not restore the brain. **Servy's multimodal reviewer now runs LOCALLY on `gemma4:12b` via `scripts/local-vision.sh`** ([[local-vision]]) — free/private/offline. Re-arm the Gemini CLI/SDK only if a billed `GEMINI_API_KEY` lands.
>
> **➕ `agy` (Antigravity CLI) — SIGNED IN + LIVE 2026-06-22** ([[agy-cli]]): Google's consumer successor to the gemini CLI — FREE Gemini-3.5-Flash brain, headless `agy -p`. Models incl. Gemini 3.5 Flash / 3.1 Pro / Claude Sonnet+Opus 4.6 / GPT-OSS 120B. **TWO opt-in roles:** (1) **FRONTIER multimodal reviewer** via `scripts/agy-vision.sh` (image/PDF/video — `view_file` decodes all three; catches flaws gemma misses) — the quality escalation above local-vision, but ~20 req/day quota so local stays default; (2) **agentic coding** (Google-lineage consensus 3rd voice + delegated coding). NOT a default (overlaps Claude+Codex). SoftServe-forbidden (Google collects Interactions data).
Why these brains, why these roles, and the sources. Researched 2026-05-28. Treat exact benchmark percentages as directional — most come from vendor or aggregator pages, and the `-free` OpenCode tiers sit below their flagship/Pro numbers.

## Design principles (from orchestration research)

- **Diversity over count.** Cross-architecture diversity (different training lineages → uncorrelated errors) is what makes a second opinion valuable, not the number of models. ([arXiv 2511.15714](https://arxiv.org/html/2511.15714v1))
- **Consensus has diminishing returns past ~3 models.** Precision gains flatten (≈73%→94% at 2 → 96% at 3 on factual/causal tasks). Cap panels at 3 cross-lineage brains. ([arXiv 2411.06535](https://arxiv.org/abs/2411.06535), [arXiv 2601.07245](https://arxiv.org/html/2601.07245))
- **Default to one strong model.** A single strong model often matches an ensemble at far lower cost; the ensemble's real win is consistency on high-stakes verifiable tasks, not speed. ([arXiv 2512.20184](https://arxiv.org/pdf/2512.20184))
- **Tier by cost/complexity.** Routing ~70% cheap / 20% mid / 10% premium cuts per-query cost 60–80%; escalate only on verification failure. ([CloudZero](https://www.cloudzero.com/blog/llm-api-pricing-comparison/))
- **Pitfalls:** latency is hostage to the slowest brain; heavy pipelines over-process simple queries; self-voting causes premature "herding" consensus. ([arXiv 2509.23537](https://arxiv.org/pdf/2509.23537))

## Capability-tier framework

| Tier | Job | Brain |
|---|---|---|
| Orchestrator | agentic driver, builder | Claude (Servy) — Fable 5 → Opus 4.8 on 2026-06-22; see [[fable-5]] |
| Code review | adversarial, rescue | Codex (GPT) via CLI/plugin |
| Agentic coding (Gemini lineage) | "let Gemini try it" + Google-lineage consensus voice | **`agy -p`** (Antigravity CLI, Gemini 3.5 Flash, FREE; opt-in/announce; one-time sign-in; [[agy-cli]]) — successor to the dead gemini CLI |
| Multimodal (vision) — DEFAULT | image/video/PDF, screenshot/UI/slide OCR | **local `gemma4:12b`** via `scripts/local-vision.sh` ([[local-vision]]) — free/private/offline, no quota |
| Multimodal (vision) — FRONTIER | the hard reads where quality matters | **`agy` (Gemini 3.5 Flash)** via `scripts/agy-vision.sh` ([[agy-cli]]) — sharper but cloud + ~20/day quota; escalate sparingly. Billed `GEMINI_API_KEY` = true whole-video via Veo |
| Whole-repo 1M ctx | huge-context scan | Gemini (CLI dark — needs API key/Vertex); local fallback = qwen3.5:35b-a3b (256K) |
| Web-grounded | live/current info | Grok |
| Deep math/reasoning | proofs, complexity | DeepSeek (free) |
| Cheap agentic | high-volume coding | MiniMax |
| Multilingual + long-doc | 201 langs, 1M ctx | Qwen |
| Cheap-bulk | classify/extract/draft | Nemotron (free) |
| Local (free/private/offline) | volume + privacy + outage fallback + local vision/RAG | Ollama: qwen3.5:35b-a3b / gpt-oss:20b / gemma4:12b (vision, now the active reviewer) / qwen2.5vl:7b (OCR/doc specialist) / qwen3-embedding |
| Consensus (≤3) | cross-arch vote | Claude + Codex + Gemini (swap in a 4th lineage for diversity) |

## Local brains (Ollama, added 2026-06-10; beast roster same day)

On-device models served by Ollama 0.30.7 (`~/.local/bin/ollama`, localhost:11434) on the M4 Pro / 48 GB. A new brain class: **free, private, always available, weaker.** Three lineages mirror the cloud trio (Claude↔Qwen, Codex↔gpt-oss, Gemini↔Gemma) — cross-architecture diversity at zero cost. Full guide + measured benchmarks: `references/local-llms.md`.

- **qwen3.5:35b-a3b** (Alibaba; MoE 3B active, 23 GB) — orchestrator/reasoner, the migration plan's #1 pick. 55.4 gen tok/s.
- **gpt-oss:20b** (OpenAI; MoE 3.6B active, 13 GB) — adversarial 2nd opinion + fastest agentic loops (209–404 prompt tok/s). Passed the drive-Servy control test.
- **gemma4:12b** (Google; unified multimodal, 7.6 GB, 256K ctx) — local eyes+ears: image/audio/video in, encoder-free. Verified reading screenshots offline. Small enough to co-load with gpt-oss (21 GB combined = two hot brains).
- **qwen3-embedding:0.6b** (639 MB, 1024-dim) — local RAG memory via `/api/embed`; verified semantic separation.
- **qwen3.5:4b** (3.4 GB) — scout for instant high-volume calls.
- *(deferred: qwen3-coder:30b-a3b — same lineage as the orchestrator + tool-call bug history; test before trust, see pending.md)*

Route here when: high-volume/low-stakes (summarize, grep-triage, scaffold, classify), privacy-first personal work (incl. **local vision on confidential screenshots** — same principle as local Kokoro TTS), Claude outage / session-limit fallback, free prompt experiments, local semantic search. Never for final-quality judgment — frontier model reviews anything that ships. `ollama run <m>` for one-offs; `ollama launch claude` / `scripts/local-llm-drive-servy.sh` to put the Claude Code harness on a local brain; `mlx_lm.server` (installed) as the Apple-native alternative. SoftServe boundary unchanged: local ≠ approved channel for customer IP.

## The OpenCode brains (chosen)

- **Grok `grok-build-0.1`** — the ONLY model in the roster with real-time web/X grounding (seconds-fresh). Zero overlap; fills Claude's Jan-2026 knowledge cutoff. Route current-info questions here. Note: `0.1` is early beta; its coding score trails GLM/MiniMax, so use it for *freshness*, not coding. ([Introducing Grok Build](https://x.ai/news/grok-build-cli))
- **DeepSeek `deepseek-v4-flash-free`** — strong math/formal-reasoning lineage independent of US labs (V4 ~96 MATH-500). Free on Zen. Use `--variant high`. ([DeepSeek V4](https://www.datacamp.com/blog/deepseek-v4))
- **MiniMax `minimax-m2.5`** — best cost-per-agentic-result: ~80% SWE-bench Verified at ~1/10–1/20 the cost of frontier ("$1/hour frontier", 230B MoE / 10B active). Route delegated/high-volume coding here. ([digitalapplied](https://www.digitalapplied.com/blog/minimax-m25-ai-model-coding-benchmarks-guide))
- **Qwen `qwen3.6-plus`** — best-in-class multilingual (201 languages) + 1M native context. Distinct on language + long-document extraction, not coding. Relevant to Gera's international SoftServe context. ([VentureBeat](https://venturebeat.com/technology/alibabas-qwen-3-5-397b-a17-beats-its-larger-trillion-parameter-model-at-a))
- **Nemotron `nemotron-3-super-free`** — efficiency/throughput (152 t/s, up to 7.5× peers). Free on Zen. Cheap-bulk fallback. ([Artificial Analysis](https://artificialanalysis.ai/models/nvidia-nemotron-3-super-120b-a12b))

## Optional / opt-in

- **GLM-5.2 `z-ai/glm-5.2`** (Z.ai / Zhipu) — **WIRED 2026-06-17** via `scripts/glm.sh` → OpenRouter. Z.ai's open-weights model that took the open frontend-coding crown (Z.ai released it ~June 13, MIT weights; per Simon Willison "probably the most powerful text-only open-weights LLM"). Built for long-horizon (600+ iteration) agentic coding; **1M-token context** on OpenRouter ($1.4/M prompt, $4.4/M completion). The active opt-in specialist for large self-contained coding/refactor and a third-lineage coding opinion. Verified live ("GLM ONLINE"). **Paid** (announce) + **SoftServe-forbidden channel** (Z.ai-hosted, China). Default output capped (`--max-tokens 4096`) because the OpenRouter balance is low — load credit or add a `GLM_API_KEY` (Z.ai coding plan) to leverage it fully. Supersedes GLM-5.1 below as the wired GLM.
- **GLM-5.1 `glm-5.1`** (Zhipu) — superseded by GLM-5.2. Tops SWE-Bench Pro (~58%), 600+ iteration / 6000+ tool-call loops. Self-reported (Claude Code harness, unverified). ([digitalapplied](https://www.digitalapplied.com/blog/zhipu-glm-5-1-coding-benchmark-claude-opus-comparison))
- **Kimi K2.6 `kimi-k2.6`** (Moonshot) — ties GPT-5.5 on coding; multimodal, 262K ctx, self-directed agent swarms / 12h runs. ([miraflow](https://miraflow.ai/blog/kimi-k2-6-explained-moonshot-ai-open-source-model-ties-gpt-5-5-coding))
Pick at most ONE long-horizon agentic brain (GLM ≈ Kimi overlap heavily). GLM-5.2 is the chosen one and is wired. Not a default route — it overlaps Claude + Codex. Fire only when Gera explicitly delegates a big autonomous coding/refactor or wants an open-weights coding opinion.

## Dropped as redundant

- **MiMo `mimo-v2.5-free`** — overlaps DeepSeek on reasoning with no unique axis; free tier underperforms its Pro numbers.
- The many GPT-5.x / Codex / Claude / Gemini variants in the OpenCode catalog — already covered better by the dedicated `codex` and `gemini` CLIs (richer integration: Codex plugin review/rescue, Gemini `@file` multimodal + 1M whole-repo). Use OpenCode for lineages those CLIs don't reach.

## Frontier-tier cheat-sheet (if routing GPT/Gemini/Claude via OpenCode anyway)

- GPT: **GPT-5.6 family since 2026-07-09** — `gpt-5.6-sol` (frontier, our codex CLI default), `gpt-5.6-terra` (balanced), `gpt-5.6-luna` (fast/cheap, `codex --profile luna`); Sol/Terra add an `ultra` effort (max reasoning + auto task delegation — quota-hungry). Legacy notes: `-pro` = more thinking compute (in 5.6 it's a Responses `reasoning.mode`, not a slug); `-codex` = coding/agentic-tuned; `mini`/`nano` = cheap bulk workers. Details: `references/codex.md`.
- Gemini: `3.5-flash` (newest, May 2026) now best for coding/agentic/multimodal + cheapest; `3.1-pro` keeps the deep-reasoning + long-context edge.
- **Vision route (updated 2026-06-22):** the active multimodal reviewer is now **local** — `scripts/local-vision.sh` on `gemma4:12b` via Ollama (free/private/offline, immune to the grep-confabulation trap since Ollama has no file tools). The old `gemini`-CLI frames-as-images path (`scripts/gemini-vision.sh`) is **dark** (consumer OAuth dead, no API key); its confabulation traps are still documented in `references/gemini-vision.md`. Full local mechanics: `references/local-vision.md`.
- Claude: haiku (fast/cheap) < sonnet (balanced daily driver) < opus (top capability; 4.8 newest, GA 2026-06-22 — see [[opus-4.8]]).

## Invocation quick-ref

```bash
opencode run -m opencode/<model> "<prompt>"                 # human-readable
opencode run -m opencode/<model> --format json "<prompt>"   # JSONL; answer = .part.text where type==text
opencode run -m opencode/<model> --variant high "<prompt>"  # reasoning effort: high|max|minimal
opencode run -m opencode/<model> -f <file> "<prompt>"       # attach a file
opencode models                                             # list everything reachable
```
