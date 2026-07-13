#!/usr/bin/env python3
"""rag-forge stage 3 — hybrid query with RRF fusion + citation.

The retrieval pipeline (references/anthropic-best-practices.md, RAG module):
  1. SEMANTIC top-k  — cosine over the qwen3-embedding vectors (query embedded
     by the same local model the index used).
  2. BM25 top-k      — lexical, from the persisted index.
  3. RECIPROCAL RANK FUSION — merge the two ranked lists by RANK POSITION, not by
     score (the scales differ), then sort by fused score.
  4. (optional) LLM RE-RANK  — --rerank shells to Claude to reorder the fused
     top-N by true relevance (an extra pass the course recommends).
  5. (optional) CITED ANSWER — --answer shells to Claude to synthesize a grounded
     answer that cites [source::chunk] ids; the deterministic core already returns
     each chunk's ORIGINAL text + source so a citation is always possible.

DETERMINISTIC + OFFLINE-TESTABLE CORE: cosine, rrf_fuse, hybrid_search (given a
query vector). Only embed_query (network) and the --rerank/--answer flags touch a
model; they are isolated. With --no-semantic (or a BM25-only index) the whole
query runs offline.

This is the bug-cost file — rrf_fuse and the BM25 ranking are unit-tested.
"""
import argparse
import json
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag_bm25 import BM25  # noqa: E402
from rag_index import embed_one, DEFAULT_EMBED_MODEL, DEFAULT_HOST  # noqa: E402

RRF_K = 60   # the standard RRF damping constant (Cormack et al. 2009)


# ---------- deterministic core (unit-tested) ----------
def cosine(a, b):
    """Cosine similarity of two equal-length vectors. 0 if either is degenerate."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = na = nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def semantic_rank(query_vec, chunks, top_k):
    """[(id, cosine)] desc over chunks that carry an embedding. Stable on ties."""
    scored = []
    for i, c in enumerate(chunks):
        emb = c.get("embedding")
        if emb:
            scored.append((c["id"], cosine(query_vec, emb), i))
    scored.sort(key=lambda x: (-x[1], x[2]))
    return [(cid, sc) for cid, sc, _ in scored[:top_k]]


def rrf_fuse(ranked_lists, k=RRF_K, top_k=None):
    """Reciprocal Rank Fusion. Each input is a ranked [(id, score)] list (rank 1 =
    best). Fused score of a doc = Σ_lists 1/(k + rank), summed only over lists that
    contain it. Returns [(id, fused_score, {list_name: rank})] sorted desc.

    Merging by RANK (not raw score) is the point: cosine and BM25 live on different
    scales, so you cannot add their scores — but you can add reciprocals of rank.

    Input shape: dict {list_name: [(id, score), ...]} or a list of such lists.
    Deterministic tie-break: higher fused score, then fewer total docs seen first
    encountered order (insertion-stable)."""
    if isinstance(ranked_lists, dict):
        items = list(ranked_lists.items())
    else:
        items = [(f"list{i}", lst) for i, lst in enumerate(ranked_lists)]
    fused = {}        # id -> fused score
    ranks = {}        # id -> {list_name: rank}
    order = {}        # id -> first-seen ordinal (stable tie-break)
    seen = 0
    for name, lst in items:
        for rank, (doc_id, _score) in enumerate(lst, start=1):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k + rank)
            ranks.setdefault(doc_id, {})[name] = rank
            if doc_id not in order:
                order[doc_id] = seen
                seen += 1
    merged = [(doc_id, fused[doc_id], ranks[doc_id]) for doc_id in fused]
    merged.sort(key=lambda x: (-x[1], order[x[0]]))
    # top_k=0 means zero results (not "no limit"); None means no limit. Guard negatives.
    return merged[:top_k] if (top_k is not None and top_k >= 0) else merged


def hybrid_search(query_vec, query_text, chunks, bm25, k_each=10, top_k=5, k_rrf=RRF_K):
    """Run both retrievers and fuse. query_vec may be None (BM25-only / offline).
    Returns the fused list enriched with each chunk's original text + source."""
    by_id = {c["id"]: c for c in chunks}
    lists = {}
    if query_vec is not None:
        sem = semantic_rank(query_vec, chunks, k_each)
        if sem:
            lists["semantic"] = sem
    bm = bm25.search(query_text, top_k=k_each)
    if bm:
        lists["bm25"] = bm
    if not lists:
        return []
    fused = rrf_fuse(lists, k=k_rrf, top_k=top_k)
    out = []
    for doc_id, score, ranks in fused:
        c = by_id.get(doc_id, {})
        out.append({
            "id": doc_id, "rrf_score": score, "ranks": ranks,
            "source": c.get("source"), "chunk_index": c.get("chunk_index"),
            "text": c.get("text", ""), "context": c.get("context"),
        })
    return out


# ---------- index load ----------
def load_index(path):
    with open(path, encoding="utf-8") as fh:
        idx = json.load(fh)
    bm25 = BM25.from_dict(idx["bm25"])
    return idx, bm25


# ---------- isolated model calls (optional flags) ----------
def llm_rerank(query, results, timeout=120):
    """Optional LLM re-rank pass. Shells to Claude (claude -p) to reorder the fused
    results by true relevance to the query. Returns reordered results; on any
    failure returns the input unchanged (degrade gracefully)."""
    numbered = "\n\n".join(f"[{i}] (source {r['source']})\n{r['text'][:600]}"
                           for i, r in enumerate(results))
    prompt = (
        "Re-rank these retrieved chunks by how well each ANSWERS the query. "
        "Return ONLY a JSON array of the indices in best-first order, e.g. [2,0,1].\n\n"
        f"Query: {query}\n\nChunks:\n{numbered}"
    )
    try:
        proc = subprocess.run(["claude", "-p", prompt], stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr[:200])
        raw = proc.stdout
        start, end = raw.find("["), raw.rfind("]")
        order = json.loads(raw[start:end + 1])
        seen, reordered = set(), []
        for i in order:
            if isinstance(i, int) and 0 <= i < len(results) and i not in seen:
                reordered.append(results[i])
                seen.add(i)
        for i, r in enumerate(results):     # append any the LLM dropped
            if i not in seen:
                reordered.append(r)
        return reordered
    except Exception as e:
        print(f"[rag_query] rerank skipped ({e})", file=sys.stderr)
        return results


def llm_answer(query, results, timeout=120):
    """Optional cited-answer synthesis. Shells to Claude with the retrieved chunks
    as the ONLY evidence; the model must cite [source::chunk_index]. Returns text."""
    ctx = "\n\n".join(f"[{r['source']}::{r['chunk_index']}]\n{r['text']}" for r in results)
    prompt = (
        "Answer the question using ONLY the sources below. Cite each claim with its "
        "[source::chunk] tag. If the sources do not contain the answer, say so.\n\n"
        f"Question: {query}\n\nSources:\n{ctx}"
    )
    try:
        proc = subprocess.run(["claude", "-p", prompt], stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr[:200])
        return proc.stdout.strip()
    except Exception as e:
        return f"[rag_query] answer synthesis failed ({e}); retrieved chunks above."


def format_results(query, results):
    lines = [f"QUERY: {query!r}   ({len(results)} hits)", ""]
    for rank, r in enumerate(results, 1):
        ranks = " ".join(f"{k}#{v}" for k, v in sorted(r["ranks"].items()))
        lines.append(f"{rank}. [{r['source']}::{r['chunk_index']}]  rrf={r['rrf_score']:.4f}  ({ranks})")
        snippet = " ".join(r["text"].split())[:200]
        lines.append(f"   {snippet}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rag_query", description="hybrid RRF query over a rag-forge index")
    ap.add_argument("index", help="index JSON from rag_index.py")
    ap.add_argument("query", help="the question / search string")
    ap.add_argument("--top-k", type=int, default=5, help="final results to return")
    ap.add_argument("--k-each", type=int, default=10, help="candidates from each retriever before fusion")
    ap.add_argument("--no-semantic", action="store_true",
                    help="BM25 only (offline; no Ollama call). Auto-on if the index has no embeddings.")
    ap.add_argument("--model", default=DEFAULT_EMBED_MODEL)
    ap.add_argument("--host", default=os.environ.get("OLLAMA_HOST", DEFAULT_HOST))
    ap.add_argument("--rerank", action="store_true", help="LLM re-rank pass (shells to claude)")
    ap.add_argument("--answer", action="store_true", help="synthesize a cited answer (shells to claude)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if args.top_k < 0 or args.k_each < 0:
        ap.error("--top-k and --k-each must be non-negative")

    idx, bm25 = load_index(args.index)
    has_emb = any(c.get("embedding") for c in idx["chunks"])

    query_vec = None
    if not args.no_semantic and has_emb:
        try:
            query_vec = embed_one(args.query, args.model, args.host)
        except RuntimeError as e:
            print(f"[rag_query] semantic disabled — {e}", file=sys.stderr)
    elif not has_emb and not args.no_semantic:
        print("[rag_query] index has no embeddings; BM25-only.", file=sys.stderr)

    results = hybrid_search(query_vec, args.query, idx["chunks"], bm25,
                            k_each=args.k_each, top_k=args.top_k)
    if args.rerank and results:
        results = llm_rerank(args.query, results)

    answer = llm_answer(args.query, results) if (args.answer and results) else None

    if args.json:
        print(json.dumps({"query": args.query, "results": results, "answer": answer}, ensure_ascii=False, indent=2))
    else:
        print(format_results(args.query, results))
        if answer is not None:
            print("\n--- CITED ANSWER ---\n" + answer)


if __name__ == "__main__":
    main()
