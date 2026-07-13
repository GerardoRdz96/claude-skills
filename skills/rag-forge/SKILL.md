---
name: rag-forge
description: Use when Gera wants retrieval-with-citations over a private corpus — scaffold a real RAG pipeline that chunks docs, embeds them locally, and answers with cited sources. Triggers — "build a RAG", "rag-forge", "retrieval over these docs", "search my notes with citations", "index this corpus", "contextual retrieval", "hybrid search BM25 + embeddings", "answer from my documents", "/rag-forge". Builds a LOCAL-first contextual-retrieval pipeline (chunk by content type -> local Ollama embeddings + BM25 -> reciprocal rank fusion -> optional LLM re-rank -> cited answer). The retrieval front door — distinct from /graphify (knowledge graph) and context-mode (codebase index).
argument-hint: "[the corpus folder, or what you want to retrieve over]"
---

# /rag-forge — scaffold a contextual-retrieval RAG pipeline

## Why this exists

Servy had **zero** retrieval-with-citations pipeline. `/graphify` builds a knowledge
graph, `context-mode` indexes a codebase, `qwen3-embedding` is a bare embed endpoint —
none of them answer *"find the passages in my corpus that bear on this question, and
cite them."* `rag-forge` is that. It builds a **real, runnable, LOCAL-first** pipeline
straight off the RAG module of the Bedrock/Vertex + Claude-API courses and the RAG
rules in `references/anthropic-best-practices.md`:

- store the **original chunk text** with every embedding (so you can cite it),
- **chunk by content type** (structure / sentence / size-with-overlap),
- prepend an **LLM situating snippet** before embedding (contextual retrieval),
- **hybrid** semantic + BM25 merged with **reciprocal rank fusion**,
- an optional **LLM re-rank** pass, then a **cited answer**.

Local-first is deliberate: embeddings run on the local Ollama model, so the corpus
never leaves the Mac. That is the strongest privacy posture and it is what keeps this
Gate-0 safe for personal/public work.

## Gate 0 — SoftServe refusal (read first)

This pipeline ingests and indexes whatever folder you point it at. So the data
boundary is hard: **personal Servy indexes generic / public / personal / Penguin-Alley
corpora only.** If the corpus is, or might contain, SoftServe customer IP, code,
Internal+ documents, client deliverables, or Jumpstart engagement specifics — **refuse
and redirect**: *"That corpus is SoftServe-scoped — it belongs in Claude Desktop
(Enterprise), not personal Servy. The bytes must not enter here, even though the
embeddings are local."* When unsure whether the corpus is public,
ask one classification question and wait. (Rule: `references/softserve-ai-usage-policy.md`.)

## What you RUN (do not hand-roll, do not READ-and-reimplement)

The pipeline is four tested scripts under `scripts/`. Tell Claude to **run** them; the
deterministic cores (chunking, BM25, RRF, cosine) are unit-tested in `.claude/skills/rag-forge/tests/test_rag.py`
— never regenerate that logic as tokens. House style and the WAT split (AI decides,
code executes) match `scripts/prompt_eval.py`.

Prereq for the semantic half: `ollama serve` up with `qwen3-embedding:0.6b` pulled
(`references/local-llms.md`). The whole thing still runs BM25-only offline if Ollama is
down — pass `--no-embed` at index time and `--no-semantic` at query time.

## The walk (question 0 + 5 steps)

### 0 — Storage-fit gate (ask before building anything)

One question decides whether this pipeline should exist for this corpus (Nate 6h
course, 2026-07-11 [4:11:37]): **what shape are the answers you will ask for?**

- **Needle-in-haystack snippets** — a specific passage out of tons of text ("remind
  me what rule 17 was?" over a thousand stored rules) → **build the pipeline**;
  reading the whole corpus per question wastes time and tokens.
- **Full-context summaries or aggregations over bounded docs** — "summarize the
  March 5th meeting", "which week had the highest sales?" → **STOP — keep whole
  markdown files and read them entire.** Similarity-retrieved chunks structurally
  miss these: the aggregation trap [4:10:05] pulls one slice of the table and
  answers "week 6" while weeks 14 and 19 were actually higher.

When unsure, delegate the call (Nate's meta-technique [4:12:07]): "I have this data,
here's how I want to use it — markdown files or semantic search?" Storage-fit
doctrine: `references/second-brain-levels.md`.

### 1 — Pick the corpus

Confirm the folder of `.md` / `.txt` to index (or a single file). Re-confirm Gate 0
on the actual contents. Default sample to prove the wiring: `tests/sample_corpus/`.

### 2 — Chunk by content type

```
python3 .claude/skills/rag-forge/scripts/rag_chunk.py <corpus> --out chunks.jsonl
```

`--strategy auto` (default) picks per file: **structure** for markdown with headings,
**sentence** for prose, **size**+overlap for code or anything else. Force one with
`--strategy {structure,sentence,size}`. Tune `--max-chars` / `--overlap`.

**Contextual retrieval (recommended):** add `--contextual` to prepend a short
LLM-generated situating snippet to each chunk before embedding (runs on the local
`gpt-oss:20b` via Ollama; degrades to plain chunks if it is down). The original text is
always stored separately for citation; only the *embedded* text gets the context.

Output is a JSONL chunk store: each line carries `id`, `source`, `chunk_index`,
`strategy`, the **original `text`**, the situating `context`, and `embed_text`.

### 3 — Build the index (embeddings + BM25)

```
python3 .claude/skills/rag-forge/scripts/rag_index.py chunks.jsonl --out index.json
```

Embeds every chunk via the **local** Ollama endpoint
(`POST http://localhost:11434/api/embeddings`, model `qwen3-embedding:0.6b`, 1024-dim)
**and** builds a BM25 lexical index. Both persist into one `index.json`. If Ollama is
down, `--no-embed` builds a BM25-only index you can still query.

### 4 — Query (hybrid -> RRF -> cite)

```
python3 .claude/skills/rag-forge/scripts/rag_query.py index.json "your question" --top-k 5
```

Runs semantic top-k **and** BM25 top-k, merges them with **reciprocal rank fusion**
(merge by rank, not score — the scales differ), and returns ranked chunks with their
**original text + `[source::chunk_index]`** for citation. Flags:
- `--rerank` — an LLM re-rank pass (shells to `claude -p`) over the fused top-N.
- `--answer` — synthesize a grounded answer that cites each claim's `[source::chunk]`.
- `--no-semantic` — BM25-only, fully offline.
- `--json` — structured output.

The core (RRF, cosine, BM25) is deterministic and offline; only `--rerank`/`--answer`
and the query embedding touch a model.

### 5 — The mandatory eval-first step (do NOT skip)

A RAG pipeline that is not evaluated is a guess. Before trusting it for real answers,
**build a small eval set first** (Anthropic rule: score before you ship —
`references/anthropic-best-practices.md`):

1. Write 5–10 real questions whose answers you know live in the corpus, each with the
   `source::chunk` (or the source file) that *should* be retrieved.
2. Run each through `rag_query --json` and check **retrieval hit-rate** — did the
   gold chunk land in the top-k? This is the deterministic, code-gradeable signal.
3. Only after retrieval is solid, judge the **cited answer** with `--answer`. Route
   that answer-quality judgment to a different lineage via `/prompt-eval` (No-Self-Review
   Law) — and eval on the **production model** (`--target` / `SERVY_PROD_MODEL`), never a
   cheaper stand-in.
4. Change **one** thing at a time (chunk size, `--contextual` on/off, `--rerank` on/off),
   re-score, keep the delta. That is the course's improvement loop.

Report the retrieval hit-rate number, not a vibe.

## Verify it works (run this first on any new setup)

```
python3 .claude/skills/rag-forge/tests/test_rag.py        # 25 offline unit tests
```

Then prove the live pipeline end to end on the sample corpus (steps 2–4 above against
`tests/sample_corpus/`). The exact-code query `PEN-2026-EMP` must surface via BM25; a
conceptual query must surface via embeddings — that contrast is the whole reason the
retrieval is hybrid.

## Notes — where rag-forge sits

| You want to… | Use |
|---|---|
| **retrieve passages from a corpus and cite them** | **`/rag-forge`** |
| turn input into a queryable knowledge graph (entities, paths, communities) | `/graphify` |
| index *this codebase* for the agent to search | `context-mode` |
| just get an embedding vector for some text | the bare `qwen3-embedding` endpoint |
| research a topic across the web with verified citations | `/storm-research` / `/deep-research` |

- **Local-first is the privacy guarantee.** Keep the corpus on-disk and embeddings
  local; that is what makes a private corpus safe here. Cloud embedding APIs would
  break Gate 0 for anything non-public.
- **RRF merges by rank, not score.** Resist the urge to add cosine and BM25 scores —
  they live on different scales. That bug is exactly what `rag_query.rrf_fuse` (and its
  tests) prevent.
- **Contextual retrieval is the biggest quality lever** in the course; turn it on
  (`--contextual`) for any corpus where chunks lose meaning out of context.
- Every run is data — note what to sharpen (chunking, k values, rerank) and update this
  skill the same session. Source: `references/anthropic-best-practices.md` (RAG),
  `references/local-llms.md` (the local embed model).
