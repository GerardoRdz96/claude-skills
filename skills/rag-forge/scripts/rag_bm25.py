#!/usr/bin/env python3
"""rag-forge — BM25 Okapi lexical index (pure stdlib, deterministic).

Why a hand-rolled BM25 instead of a dep: this is the bug-cost core — it must be
unit-testable offline with no install, and serialize into the same JSON index the
rest of the pipeline persists. Standard Okapi BM25:

    score(q, d) = Σ_t IDF(t) * ( f(t,d) * (k1+1) ) / ( f(t,d) + k1 * (1 - b + b*|d|/avgdl) )
    IDF(t)      = ln( (N - n(t) + 0.5) / (n(t) + 0.5) + 1 )

where f(t,d) is term frequency of t in doc d, |d| the doc length, avgdl the mean
doc length, N the doc count, n(t) the number of docs containing t. The `+1` inside
the IDF log keeps IDF non-negative (the Lucene/standard form), so a term in every
doc gets ~0 weight rather than going negative.

Semantic search wins conceptual queries; BM25 wins exact IDs / codes / rare terms.
RRF (rag_query) merges the two by rank, not score.
"""
import math
import re

_TOKEN = re.compile(r"[A-Za-z0-9_]+")
# a tiny, fixed stop list — common words that add noise to lexical match
STOP = frozenset("a an and are as at be by for from has have in is it its of on or "
                 "that the to was were will with this these those".split())


def tokenize(text):
    """Lowercase word/number tokens, stop-words dropped. Deterministic."""
    return [t for t in (m.group(0).lower() for m in _TOKEN.finditer(text or "")) if t not in STOP]


class BM25:
    """Okapi BM25 with the standard non-negative IDF. Build by add()-ing docs then
    finalize(); query with search(). Serializes via to_dict()/from_dict()."""

    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.doc_ids = []          # parallel to doc_tokens / doc_len
        self.doc_tokens = []       # list[list[str]]
        self.doc_freqs = []        # list[dict term->count]
        self.df = {}               # term -> number of docs containing it
        self.doc_len = []
        self.avgdl = 0.0
        self.N = 0
        self._finalized = False

    def add(self, doc_id, text):
        toks = tokenize(text)
        freqs = {}
        for t in toks:
            freqs[t] = freqs.get(t, 0) + 1
        for t in freqs:                 # df counts DOCS, not occurrences
            self.df[t] = self.df.get(t, 0) + 1
        self.doc_ids.append(doc_id)
        self.doc_tokens.append(toks)
        self.doc_freqs.append(freqs)
        self.doc_len.append(len(toks))

    def finalize(self):
        self.N = len(self.doc_ids)
        self.avgdl = (sum(self.doc_len) / self.N) if self.N else 0.0
        self._finalized = True
        return self

    def idf(self, term):
        n = self.df.get(term, 0)
        # standard non-negative IDF (the +1 inside the log floors it at ~0)
        return math.log(1 + (self.N - n + 0.5) / (n + 0.5))

    def score_doc(self, query_tokens, i):
        """BM25 score of query against doc index i."""
        freqs = self.doc_freqs[i]
        dl = self.doc_len[i]
        denom_norm = self.k1 * (1 - self.b + self.b * (dl / self.avgdl if self.avgdl else 0))
        s = 0.0
        for t in query_tokens:
            f = freqs.get(t, 0)
            if f == 0:
                continue
            s += self.idf(t) * (f * (self.k1 + 1)) / (f + denom_norm)
        return s

    def search(self, query, top_k=10):
        """Return [(doc_id, score)] sorted desc, only docs with score > 0.
        Ties broken by original insertion order (stable, deterministic)."""
        if not self._finalized:
            self.finalize()
        q = tokenize(query)
        scored = []
        for i in range(self.N):
            sc = self.score_doc(q, i)
            if sc > 0:
                scored.append((self.doc_ids[i], sc, i))
        scored.sort(key=lambda x: (-x[1], x[2]))   # score desc, then stable by index
        return [(doc_id, sc) for doc_id, sc, _ in scored[:top_k]]

    # ---------- serialization (round-trips through the JSON index) ----------
    def to_dict(self):
        return {"k1": self.k1, "b": self.b, "doc_ids": self.doc_ids,
                "doc_freqs": self.doc_freqs, "df": self.df,
                "doc_len": self.doc_len, "avgdl": self.avgdl, "N": self.N}

    @classmethod
    def from_dict(cls, d):
        bm = cls(k1=d.get("k1", 1.5), b=d.get("b", 0.75))
        bm.doc_ids = list(d["doc_ids"])
        bm.doc_freqs = [dict(f) for f in d["doc_freqs"]]
        bm.df = dict(d["df"])
        bm.doc_len = list(d["doc_len"])
        bm.avgdl = d["avgdl"]
        bm.N = d["N"]
        bm.doc_tokens = [[] for _ in bm.doc_ids]   # not needed for scoring
        bm._finalized = True
        return bm
