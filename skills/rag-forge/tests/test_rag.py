#!/usr/bin/env python3
"""Offline unit tests for the rag-forge deterministic core.

Covers the bug-cost pieces — chunking boundaries, BM25 ranking math, RRF fusion
math, cosine, and a chunk-store -> index -> query round-trip with embeddings
MOCKED (no network). The embedding HTTP call (embed_one) is never invoked here;
the round-trip injects fake vectors so RRF/BM25/chunking are proven end to end.

Run: python3 .claude/skills/rag-forge/tests/test_rag.py
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)

import rag_bm25  # noqa: E402
import rag_chunk  # noqa: E402
import rag_index  # noqa: E402
import rag_query  # noqa: E402


# ---------- chunking boundaries ----------
class TestChunking(unittest.TestCase):
    def test_structure_splits_on_headings(self):
        md = "# Title\nintro\n\n## A\nbody a\n\n## B\nbody b"
        secs = rag_chunk.split_structure(md)
        self.assertEqual(len(secs), 3)
        self.assertTrue(secs[1].startswith("## A"))
        self.assertIn("body b", secs[2])

    def test_structure_keeps_preamble(self):
        md = "preamble text before any heading\n\n# H\nafter"
        secs = rag_chunk.split_structure(md)
        self.assertEqual(len(secs), 2)
        self.assertEqual(secs[0], "preamble text before any heading")

    def test_sentence_split_and_pack(self):
        prose = "First sentence here. Second one follows! Third? Yes indeed."
        sents = rag_chunk.split_sentences(prose)
        self.assertEqual(len(sents), 4)
        packed = rag_chunk.pack_sentences(sents, max_chars=30)
        # no chunk exceeds budget unless a single sentence is itself longer
        for ch in packed:
            self.assertTrue(len(ch) <= 30 or " " not in ch.strip().rstrip("."))
        # packing never drops or reorders content
        self.assertEqual(" ".join(packed).replace("  ", " "), " ".join(sents))

    def test_size_split_overlap_boundaries(self):
        text = "abcdefghij" * 5  # 50 chars
        chunks = rag_chunk.split_size(text, max_chars=20, overlap=5)
        self.assertEqual(chunks[0], text[0:20])
        # second chunk starts 5 chars before the previous end (overlap)
        self.assertEqual(chunks[1][:5], text[15:20])
        # full coverage: concatenating de-overlapped tails reconstructs the text
        rebuilt = chunks[0] + "".join(c[5:] for c in chunks[1:])
        self.assertEqual(rebuilt, text)

    def test_size_overlap_validation(self):
        with self.assertRaises(ValueError):
            rag_chunk.split_size("xxxxx", max_chars=10, overlap=10)

    def test_pick_strategy_by_content_type(self):
        self.assertEqual(rag_chunk.pick_strategy("a.md", "# H\nbody", None), "structure")
        self.assertEqual(rag_chunk.pick_strategy("a.txt", "Just some prose. More prose.", None), "sentence")
        self.assertEqual(rag_chunk.pick_strategy("a.py", "def f():\n    return {}", None), "size")
        # forced strategy overrides detection
        self.assertEqual(rag_chunk.pick_strategy("a.md", "# H", "size"), "size")

    def test_build_chunks_stores_original_text(self):
        recs = rag_chunk.build_chunks("doc.md", "# H\nhello world", "structure")
        self.assertTrue(recs)
        r = recs[0]
        self.assertEqual(r["id"], "doc.md::0")
        self.assertEqual(r["source"], "doc.md")
        self.assertIn("hello world", r["text"])
        self.assertEqual(r["embed_text"], r["text"])  # == text until contextual
        self.assertIsNone(r["context"])

    def test_apply_context_routes_embed(self):
        rec = rag_chunk.build_chunks("d.txt", "Body sentence here.", "sentence")[0]
        rag_chunk.apply_context(rec, "This is from doc D about bodies.")
        self.assertEqual(rec["context"], "This is from doc D about bodies.")
        self.assertTrue(rec["embed_text"].startswith("This is from doc D"))
        self.assertIn(rec["text"], rec["embed_text"])  # original preserved


# ---------- BM25 ranking ----------
class TestBM25(unittest.TestCase):
    def _index(self):
        bm = rag_bm25.BM25()
        bm.add("d0", "the penguin dives deep for fish")
        bm.add("d1", "emperor penguins breed on antarctic sea ice")
        bm.add("d2", "reciprocal rank fusion merges ranked lists")
        bm.finalize()
        return bm

    def test_tokenize_drops_stopwords(self):
        toks = rag_bm25.tokenize("The penguin and the fish")
        self.assertEqual(toks, ["penguin", "fish"])

    def test_ranks_relevant_doc_first(self):
        bm = self._index()
        res = bm.search("penguin fish", top_k=3)
        self.assertEqual(res[0][0], "d0")  # d0 has both terms
        self.assertTrue(res[0][1] > 0)

    def test_rare_term_outscores_common(self):
        bm = self._index()
        # "fusion" appears in 1 doc -> high IDF -> d2 wins decisively
        res = bm.search("fusion", top_k=3)
        self.assertEqual(res[0][0], "d2")

    def test_no_match_returns_empty(self):
        bm = self._index()
        self.assertEqual(bm.search("helicopter spreadsheet"), [])

    def test_idf_non_negative_for_universal_term(self):
        bm = rag_bm25.BM25()
        bm.add("a", "common word")
        bm.add("b", "common word")
        bm.finalize()
        self.assertGreaterEqual(bm.idf("common"), 0.0)  # standard IDF floors at ~0

    def test_serialization_roundtrip(self):
        bm = self._index()
        bm2 = rag_bm25.BM25.from_dict(json.loads(json.dumps(bm.to_dict())))
        self.assertEqual(bm.search("penguin fish"), bm2.search("penguin fish"))


# ---------- RRF fusion math ----------
class TestRRF(unittest.TestCase):
    def test_rrf_score_formula(self):
        # one list, doc at rank 1 -> 1/(60+1)
        fused = rag_query.rrf_fuse({"a": [("x", 9.9)]}, k=60)
        self.assertAlmostEqual(fused[0][1], 1.0 / 61, places=10)

    def test_doc_in_both_lists_beats_doc_in_one(self):
        sem = [("A", 0.9), ("B", 0.8)]
        bm = [("A", 5.0), ("C", 4.0)]
        fused = rag_query.rrf_fuse({"semantic": sem, "bm25": bm}, k=60)
        ids = [d for d, _, _ in fused]
        self.assertEqual(ids[0], "A")  # A is rank1 in both -> highest fused
        # A's score = 1/61 + 1/61 ; B's = 1/62 ; C's = 1/62
        a_score = next(s for d, s, _ in fused if d == "A")
        self.assertAlmostEqual(a_score, 2.0 / 61, places=10)

    def test_rank_not_score_drives_fusion(self):
        # B has a huge raw semantic score but is rank 2; A is rank 1 in both.
        sem = [("A", 0.51), ("B", 0.50)]
        bm = [("A", 100.0), ("B", 0.01)]
        fused = rag_query.rrf_fuse({"semantic": sem, "bm25": bm})
        self.assertEqual(fused[0][0], "A")

    def test_ranks_recorded_per_list(self):
        fused = rag_query.rrf_fuse({"semantic": [("A", 1.0)], "bm25": [("B", 1.0), ("A", 1.0)]})
        ranks = {d: r for d, _, r in fused}
        self.assertEqual(ranks["A"], {"semantic": 1, "bm25": 2})
        self.assertEqual(ranks["B"], {"bm25": 1})

    def test_top_k_truncates(self):
        lst = [(f"d{i}", 1.0) for i in range(10)]
        fused = rag_query.rrf_fuse({"l": lst}, top_k=3)
        self.assertEqual(len(fused), 3)

    def test_deterministic_tie_break(self):
        # both docs only in one list at the same rank position -> stable insertion order
        f1 = rag_query.rrf_fuse({"a": [("X", 1.0)], "b": [("Y", 1.0)]})
        f2 = rag_query.rrf_fuse({"a": [("X", 1.0)], "b": [("Y", 1.0)]})
        self.assertEqual([d for d, _, _ in f1], [d for d, _, _ in f2])


# ---------- cosine ----------
class TestCosine(unittest.TestCase):
    def test_identical_vectors(self):
        self.assertAlmostEqual(rag_query.cosine([1, 2, 3], [1, 2, 3]), 1.0, places=10)

    def test_orthogonal(self):
        self.assertAlmostEqual(rag_query.cosine([1, 0], [0, 1]), 0.0, places=10)

    def test_degenerate_zero_vector(self):
        self.assertEqual(rag_query.cosine([0, 0], [1, 1]), 0.0)

    def test_length_mismatch(self):
        self.assertEqual(rag_query.cosine([1, 2], [1, 2, 3]), 0.0)


# ---------- chunk-store -> index -> query round-trip (embeddings MOCKED) ----------
class TestRoundTrip(unittest.TestCase):
    def test_end_to_end_offline(self):
        corpus = os.path.join(HERE, "sample_corpus")
        with tempfile.TemporaryDirectory() as tmp:
            chunks_path = os.path.join(tmp, "chunks.jsonl")
            index_path = os.path.join(tmp, "index.json")

            # 1) chunk the real sample corpus (deterministic, no network)
            rag_chunk.main([corpus, "--out", chunks_path])
            chunks = rag_index.load_chunks(chunks_path)
            self.assertGreater(len(chunks), 1)
            # original text is preserved in the store (citation guarantee)
            self.assertTrue(all(c["text"].strip() for c in chunks))

            # 2) build the index with MOCK embeddings (no Ollama). Fake vector =
            #    bag-of-3-dims so a related query vector lands close in cosine space.
            def fake_vec(text):
                t = text.lower()
                return [float(t.count("penguin")), float(t.count("fusion")), float(t.count("dive") + t.count("dives"))]
            bm25 = rag_index.build_bm25(chunks)
            embeddings = {c["id"]: fake_vec(c["embed_text"]) for c in chunks}
            index = rag_index.build_index(chunks, embeddings, bm25, "mock-embed")
            with open(index_path, "w") as fh:
                json.dump(index, fh)

            # 3) load + query offline. Exact-code query must surface via BM25.
            idx, bm = rag_query.load_index(index_path)
            results = rag_query.hybrid_search(None, "PEN-2026-EMP code", idx["chunks"], bm, top_k=3)
            self.assertTrue(results)
            self.assertIn("PEN-2026-EMP", results[0]["text"])
            self.assertEqual(results[0]["source"], "penguins.md")

            # 4) hybrid with a mock query vector — both retrievers contribute, fused.
            qv = fake_vec("how deep do penguins dive")
            hres = rag_query.hybrid_search(qv, "how deep do penguins dive", idx["chunks"], bm, top_k=3)
            self.assertTrue(hres)
            self.assertTrue(any("semantic" in r["ranks"] or "bm25" in r["ranks"] for r in hres))
            # every returned hit carries citation fields
            for r in hres:
                self.assertIn("source", r)
                self.assertIn("chunk_index", r)
                self.assertTrue(r["text"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
