#!/usr/bin/env python3
"""rag-forge stage 1 — chunk a corpus by content type into a JSONL chunk store.

Operationalizes the RAG-module chunking rule (references/anthropic-best-practices.md):
choose chunking by content type — STRUCTURE-based when you control the format
(markdown headings), SENTENCE-based for general prose, SIZE-based with overlap as
the fallback that works on anything including code. Bad chunking poisons retrieval.

Two more course rules live here:
- Store the ORIGINAL chunk text (plus source + metadata) with every chunk — the
  retriever returns it verbatim for citation. We never discard the source text.
- CONTEXTUAL RETRIEVAL (optional, --contextual): prepend a short LLM-generated
  situating snippet ("this chunk is from <doc>, the section on X; it follows Y")
  BEFORE embedding, so an isolated chunk keeps its document context. The situating
  text is stored separately ("context") from the original ("text"); embedding uses
  context + text, citation shows text. The LLM call is the ONLY non-deterministic
  part and is isolated in one function (situate_chunk) so the chunking core is
  unit-testable offline.

Output: one JSON object per line (JSONL). Schema per chunk:
  {"id", "source", "chunk_index", "strategy", "text", "context", "embed_text", "meta"}

This file follows scripts/prompt_eval.py house style: a deterministic core
(splitters, build_chunks) isolated from the one model-touching function.
"""
import argparse
import json
import os
import re
import subprocess
import sys

DEFAULT_MAX_CHARS = 1200      # ~300 tokens, a sane retrieval chunk
DEFAULT_OVERLAP = 150         # size-fallback overlap so a sentence is not cut blind
DEFAULT_EXTS = (".md", ".txt", ".markdown")


# ---------- deterministic core (unit-tested) ----------
def split_structure(text):
    """STRUCTURE-based: split a markdown doc on its headings (# .. ######).
    Each chunk is a heading plus the body until the next heading of the same or
    higher level. Preamble before the first heading becomes its own chunk."""
    lines = text.split("\n")
    sections, cur = [], []
    for line in lines:
        if re.match(r"^#{1,6}\s+\S", line):
            if cur and any(s.strip() for s in cur):
                sections.append("\n".join(cur).strip())
            cur = [line]
        else:
            cur.append(line)
    if cur and any(s.strip() for s in cur):
        sections.append("\n".join(cur).strip())
    return [s for s in sections if s]


_SENT_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")


def split_sentences(text):
    """Split prose into sentences. Conservative: breaks on ./!/? followed by
    whitespace and a capital/quote/digit, so abbreviations rarely over-split."""
    text = text.strip()
    if not text:
        return []
    parts = _SENT_END.split(text)
    return [p.strip() for p in parts if p.strip()]


def pack_sentences(sentences, max_chars=DEFAULT_MAX_CHARS):
    """SENTENCE-based: greedily pack whole sentences up to max_chars, never
    splitting a sentence. A lone sentence longer than max_chars stands alone."""
    chunks, cur, cur_len = [], [], 0
    for s in sentences:
        add = len(s) + (1 if cur else 0)
        if cur and cur_len + add > max_chars:
            chunks.append(" ".join(cur))
            cur, cur_len = [s], len(s)
        else:
            cur.append(s)
            cur_len += add
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def split_size(text, max_chars=DEFAULT_MAX_CHARS, overlap=DEFAULT_OVERLAP):
    """SIZE-based fallback with overlap — works on anything, including code.
    Slides a window of max_chars with `overlap` chars of carry-over so context
    spanning a boundary is not lost."""
    text = text.strip()
    if not text:
        return []
    if overlap < 0 or overlap >= max_chars:
        raise ValueError("overlap must be >=0 and < max_chars")
    chunks, start, n = [], 0, len(text)
    while start < n:
        end = min(start + max_chars, n)
        chunks.append(text[start:end])
        if end >= n:
            break
        start = end - overlap
    return chunks


def pick_strategy(path, text, forced=None):
    """Choose chunking by content type. Markdown with headings -> structure;
    code-ish (curly-heavy or known code ext) -> size; otherwise prose -> sentence."""
    if forced and forced != "auto":
        return forced
    ext = os.path.splitext(path)[1].lower()
    has_headings = re.search(r"^#{1,6}\s+\S", text, re.M) is not None
    if ext in (".md", ".markdown") and has_headings:
        return "structure"
    code_exts = {".py", ".js", ".ts", ".go", ".java", ".rs", ".c", ".cpp", ".sh"}
    if ext in code_exts or text.count("{") + text.count("}") > max(20, len(text) // 200):
        return "size"
    return "sentence"


def chunk_text(text, strategy, max_chars=DEFAULT_MAX_CHARS, overlap=DEFAULT_OVERLAP):
    """Apply one strategy. STRUCTURE sections that overflow max_chars are further
    size-split so no single chunk blows the budget."""
    if strategy == "structure":
        out = []
        for sec in split_structure(text):
            out.extend(split_size(sec, max_chars, overlap) if len(sec) > max_chars else [sec])
        return out
    if strategy == "sentence":
        return pack_sentences(split_sentences(text), max_chars)
    if strategy == "size":
        return split_size(text, max_chars, overlap)
    raise ValueError(f"unknown strategy: {strategy!r}")


def build_chunks(path, text, strategy, max_chars=DEFAULT_MAX_CHARS, overlap=DEFAULT_OVERLAP):
    """Deterministic: file text -> list of chunk records (no embedding yet,
    no LLM context yet). embed_text defaults to the raw text; --contextual
    overrides it later with context + text."""
    chosen = pick_strategy(path, text, strategy)
    pieces = chunk_text(text, chosen, max_chars, overlap)
    src = os.path.basename(path)
    records = []
    for i, piece in enumerate(pieces):
        records.append({
            "id": f"{src}::{i}",
            "source": src,
            "source_path": path,
            "chunk_index": i,
            "strategy": chosen,
            "text": piece,            # ORIGINAL text, returned verbatim for citation
            "context": None,          # filled by --contextual
            "embed_text": piece,      # what rag_index embeds; == text unless contextual
            "meta": {"chars": len(piece)},
        })
    return records


def apply_context(record, situating):
    """Attach a situating snippet and route the embed to context + text."""
    situating = (situating or "").strip()
    if not situating:
        return record
    record["context"] = situating
    record["embed_text"] = f"{situating}\n\n{record['text']}"
    return record


# ---------- isolated model call (contextual retrieval) ----------
def situate_chunk(doc_summary, chunk_text_, timeout=60):
    """One LLM call producing a 1-2 sentence situating snippet for a chunk.
    Routes to the LOCAL Ollama generate endpoint via curl (private, offline-ish,
    Gate-0 safe) using the agentic local model. Returns "" on any failure so the
    pipeline degrades to plain (non-contextual) chunks instead of crashing."""
    import urllib.request
    import urllib.error
    prompt = (
        "You situate a document chunk for retrieval. In ONE or TWO short sentences, "
        "say what this chunk is about and how it fits the document. No preamble, just "
        "the situating sentence.\n\n"
        f"<document_summary>\n{doc_summary[:1500]}\n</document_summary>\n\n"
        f"<chunk>\n{chunk_text_[:2000]}\n</chunk>\n\nSituating snippet:"
    )
    model = os.environ.get("RAG_CONTEXT_MODEL", "gpt-oss:20b")
    host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0.0}}).encode()
    req = urllib.request.Request(f"{host}/api/generate", data=body,
                                 headers={"content-type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        return (data.get("response") or "").strip()
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"[rag_chunk] situate failed ({e}); chunk stays non-contextual", file=sys.stderr)
        return ""


def iter_corpus(folder, exts):
    for root, _dirs, files in os.walk(folder):
        for fn in sorted(files):
            if os.path.splitext(fn)[1].lower() in exts:
                yield os.path.join(root, fn)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rag_chunk", description="chunk a corpus into a JSONL chunk store")
    ap.add_argument("corpus", help="folder of .md/.txt files (or a single file)")
    ap.add_argument("--out", required=True, help="output JSONL chunk store")
    ap.add_argument("--strategy", default="auto",
                    choices=["auto", "structure", "sentence", "size"],
                    help="chunking strategy; auto = pick by content type (default)")
    ap.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    ap.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP)
    ap.add_argument("--exts", default=",".join(DEFAULT_EXTS),
                    help="comma list of file extensions to include")
    ap.add_argument("--contextual", action="store_true",
                    help="prepend an LLM situating snippet per chunk (contextual retrieval)")
    args = ap.parse_args(argv)

    exts = tuple(e if e.startswith(".") else "." + e for e in args.exts.split(",") if e.strip())
    if os.path.isdir(args.corpus):
        paths = list(iter_corpus(args.corpus, exts))
    elif os.path.isfile(args.corpus):
        paths = [args.corpus]
    else:
        ap.error(f"corpus not found: {args.corpus}")
    if not paths:
        ap.error(f"no {exts} files under {args.corpus}")

    all_records = []
    for path in paths:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        recs = build_chunks(path, text, args.strategy, args.max_chars, args.overlap)
        if args.contextual and recs:
            doc_summary = text[:1500]
            for r in recs:
                r = apply_context(r, situate_chunk(doc_summary, r["text"]))
        all_records.extend(recs)

    with open(args.out, "w", encoding="utf-8") as fh:
        for r in all_records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    by_strat = {}
    for r in all_records:
        by_strat[r["strategy"]] = by_strat.get(r["strategy"], 0) + 1
    print(f"wrote {len(all_records)} chunks from {len(paths)} file(s) -> {args.out}")
    print(f"  strategies: {by_strat}" + ("  (contextual ON)" if args.contextual else ""))


if __name__ == "__main__":
    main()
