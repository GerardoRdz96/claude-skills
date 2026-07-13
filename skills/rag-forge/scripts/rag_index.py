#!/usr/bin/env python3
"""rag-forge stage 2 — build the dual index from a JSONL chunk store.

Builds BOTH halves of hybrid retrieval (references/anthropic-best-practices.md:
combine semantic + BM25, merged later with reciprocal rank fusion):

1. SEMANTIC — embed each chunk's `embed_text` via the LOCAL Ollama embedding model
   (qwen3-embedding:0.6b, 1024-dim) on the singular legacy endpoint
   POST http://localhost:11434/api/embeddings  body {"model","prompt"} -> {"embedding"}.
   Local = private + Gate-0 safe (bytes never leave the Mac). Persisted as plain
   JSON vectors (no native dep) so rag_query can cosine-rank offline.

2. LEXICAL — a BM25 index over the same chunks, built with the tokenizer +
   posting lists from rag_bm25.py (pure stdlib, deterministic, unit-tested).

Output: one index file (JSON) holding chunk metadata + original text + embeddings
+ the serialized BM25 model. rag_query loads it and never re-touches the network.

House style (scripts/prompt_eval.py): the ONLY network function (embed_one) is
isolated; everything else — load, BM25 build, persist — is deterministic.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag_bm25 import BM25  # noqa: E402

DEFAULT_EMBED_MODEL = "qwen3-embedding:0.6b"
DEFAULT_HOST = "http://127.0.0.1:11434"


# ---------- isolated model call ----------
def embed_one(text, model=DEFAULT_EMBED_MODEL, host=DEFAULT_HOST, timeout=120):
    """One embedding via the local Ollama /api/embeddings endpoint. Returns a
    list[float]. Raises on failure (the caller decides whether to abort the run)."""
    import urllib.request
    import urllib.error
    body = json.dumps({"model": model, "prompt": text}).encode()
    req = urllib.request.Request(f"{host}/api/embeddings", data=body,
                                 headers={"content-type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"embeddings HTTP {e.code}: {e.read().decode()[:200]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"cannot reach Ollama at {host} ({e}). Is `ollama serve` running?")
    vec = data.get("embedding")
    if not isinstance(vec, list) or not vec:
        raise RuntimeError(f"no embedding in response: {str(data)[:200]}")
    return [float(x) for x in vec]


# ---------- deterministic core ----------
def load_chunks(path):
    chunks = []
    with open(path, encoding="utf-8") as fh:
        for ln, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{ln} not valid JSON: {e}")
            for k in ("id", "text"):
                if k not in obj:
                    raise ValueError(f"{path}:{ln} chunk missing '{k}'")
            obj.setdefault("embed_text", obj["text"])
            chunks.append(obj)
    if not chunks:
        raise ValueError(f"no chunks in {path}")
    return chunks


def build_bm25(chunks):
    """BM25 over the original chunk text (lexical match on the real words)."""
    bm = BM25()
    for c in chunks:
        bm.add(c["id"], c["text"])
    bm.finalize()
    return bm


def build_index(chunks, embeddings, bm25, model):
    """Assemble the persisted index. embeddings is id -> vector (or None if the
    embed step was skipped, e.g. Ollama down). BM25 always present."""
    return {
        "embed_model": model,
        "dim": next((len(v) for v in embeddings.values() if v), 0),
        "embedded": sum(1 for v in embeddings.values() if v),
        "chunks": [
            {"id": c["id"], "source": c.get("source"), "source_path": c.get("source_path"),
             "chunk_index": c.get("chunk_index"), "strategy": c.get("strategy"),
             "text": c["text"], "context": c.get("context"),
             "embedding": embeddings.get(c["id"]), "meta": c.get("meta", {})}
            for c in chunks
        ],
        "bm25": bm25.to_dict(),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rag_index", description="embed + BM25-index a chunk store")
    ap.add_argument("chunks", help="JSONL chunk store from rag_chunk.py")
    ap.add_argument("--out", required=True, help="output index JSON")
    ap.add_argument("--model", default=DEFAULT_EMBED_MODEL)
    ap.add_argument("--host", default=os.environ.get("OLLAMA_HOST", DEFAULT_HOST))
    ap.add_argument("--no-embed", action="store_true",
                    help="build BM25 only, skip embeddings (offline / Ollama down). "
                         "Semantic search will be unavailable until re-indexed.")
    args = ap.parse_args(argv)

    chunks = load_chunks(args.chunks)
    bm25 = build_bm25(chunks)

    embeddings = {}
    if args.no_embed:
        print(f"[rag_index] --no-embed: BM25-only index over {len(chunks)} chunks", file=sys.stderr)
        embeddings = {c["id"]: None for c in chunks}
    else:
        ok = 0
        for i, c in enumerate(chunks):
            try:
                embeddings[c["id"]] = embed_one(c["embed_text"], args.model, args.host)
                ok += 1
            except RuntimeError as e:
                # first failure usually means Ollama is down — fail loud, BM25 still built
                print(f"[rag_index] embed failed on chunk {c['id']}: {e}", file=sys.stderr)
                print("[rag_index] aborting embeddings; re-run with `ollama serve` up, "
                      "or use --no-embed for a BM25-only index.", file=sys.stderr)
                embeddings = {c2["id"]: None for c2 in chunks}
                break
            if (i + 1) % 20 == 0:
                print(f"[rag_index] embedded {i + 1}/{len(chunks)}", file=sys.stderr)
        if any(embeddings.values()):
            print(f"[rag_index] embedded {ok}/{len(chunks)} chunks", file=sys.stderr)

    index = build_index(chunks, embeddings, bm25, args.model)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False)
    print(f"wrote index -> {args.out}")
    print(f"  chunks={len(index['chunks'])}  embedded={index['embedded']}  "
          f"dim={index['dim']}  bm25_docs={len(index['bm25']['doc_ids'])}")


if __name__ == "__main__":
    main()
