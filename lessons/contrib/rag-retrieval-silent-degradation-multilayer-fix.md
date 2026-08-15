---
domain: "rag"
title: "RAG Retrieval: Silent BM25 Degradation and Multi-Layer Truncation Hide Valid Results"
status: "draft"
verification: "metadata-normalized"
---
{"title": "RAG Retrieval: Silent BM25 Degradation and Multi-Layer Truncation Hide Valid Results", "domain": "rag", "tags": ["rag", "retrieval", "bm25", "hybrid-search", "chromadb", "silent-degradation", "tokenization"], "status": "published", "confidence": "0.95", "created": "2026-08-15", "updated": "2026-08-15", "source": "self-grow-wiki RAG retrieval incident — M-900iB/330L 'does not exist' misjudgment (commits 4db44ef, a579e5c, plus follow-up fixes)", "verified_date": "2026-08-14", "domain_expert": "", "language": "en"}

# RAG Retrieval: Silent BM25 Degradation and Multi-Layer Truncation Hide Valid Results

## Problem

A RAG knowledge base contained the full spec table for the FANUC M-900iB/330L robot (source PDF §3.1 spec list, page 36-37: 330kg load, J1-J6 speeds 100/85/85/90/85/165°/s). Yet the query "M-900iB 330L 比 280L 慢多少" returned nothing relevant, and the agent answered **"M-900iB/330L does not exist"** — a confident, wrong answer.

The data was never missing. Two compounding failures broke retrieval:

1. The retrieval chain **silently degraded** to a pure vector path that cannot recall table-formatted spec data.
2. Multiple independent filters/truncations each discarded the valid chunk, so even after the first fix the correct chunk stayed outside the top-k window.

## Root Cause

Layered — fixing any single layer was insufficient:

- **A. Silent dependency failure (environment).** `rag_core.py` hybrid retrieval requires `rank_bm25` + `jieba`. Both were uninstalled, so `_BM25_AVAILABLE = False` and the BM25 index (a 615MB cached pkl) never loaded. Retrieval fell back to pure vector search with **no log and no error**. Spec tables score low on embeddings; only BM25 exact matching on "330L" / "最大动作速度" can recall them.
- **B. Warmup had no retry.** The MCP server warmup called `rag_search_raw`, whose first call hit a ChromaDB `RustBindingsAPI` singleton bug (`'bindings'` AttributeError). Warmup failed once and never retried, so BM25 stayed unloaded even after the deps were installed.
- **C. Variant search used `$contains` FTS.** ChromaDB tokenized "330L" into "330"+"L"; the single-character token "L" matched 31 candidates, most without a real "330L".
- **D. Multi-layer truncation compounded.** `max_per_file=3` let high-vector-score pages evict the spec table; a rerank overwrote variant scores; a source-based dedup dropped the spec chunk because an entity-exact hit already claimed the same PDF; `vec_results[:5]` and `top_k=5` both cut before the spec chunk at rank #6.
- **E. Score scales were mixed.** `_rrf_fusion` returns rank-fusion scores (measured peak ~0.492), but the spam filter compared them against `MIN_SCORE = 0.50` on the semantic scale — wiping out every RRF result for queries with no exact-match chunk.
- **F. Broken Chinese tokenization in overlap-guard.** The "unrelated recall guard" used `re.findall(r'[\w\u4e00-\u9fff]+', query)`, which matched a continuous Chinese query as one giant token; no chunk contained that token, so overlap = 0 for all candidates and everything was filtered (score=0).

## Solution

Six fixes, applied and verified end-to-end on the production path:

### Step 1 — Restore BM25 and make warmup retry

```bash
pip install jieba==0.42.1 rank-bm25==0.2.2
```

Retry warmup once after a failure instead of continuing silently; log the retry result.

### Step 2 — Exact substring match for variants

Replace `$contains` FTS with BM25 in-memory **exact substring matching** for model variants; keep `$contains` only as a fallback.

### Step 3 — Dedup by text, not by source

When merging entity/SAG results with vector results, dedup on chunk **text**, not on `source`, so two different chunks from the same PDF both survive.

```python
seen_texts = set()
merged = []
for r in entity_exact + vector_results:
    if r["document"] in seen_texts:
        continue
    seen_texts.add(r["document"])
    merged.append(r)
```

### Step 4 — Raise the production top_k

`rag_answer` used `rag_search_raw(query, top_k=5)` while the spec chunk ranked #6. Bump to `top_k=10`.

### Step 5 — Exempt RRF results from MIN_SCORE

Tag RRF-fused results and skip the `score >= MIN_SCORE` spam filter for them (keep the text-quality check):

```python
for r in merged:
    if r.get("_rrf") or r["score"] >= MIN_SCORE:
        keep(r)  # text-quality check still applies
```

### Step 6 — Use jieba in overlap-guard

When `_BM25_AVAILABLE`, tokenize the query with jieba instead of the whole-block regex; fall back to the regex only when jieba is absent.

## Verification

Production-path (`rag_search_raw`) checks after all fixes:

| Query | Before | After |
|---|---|---|
| "M-900iB/330L 最大动作速度是多少" | no spec table | ✅ 330L spec table at #6 (2/2) |
| "M-900iB 330L 比 280L 慢多少" | no spec table | ✅ spec tables #5 + #6 (1/1 + 2/2) |
| "fanuc机器人负载推算报腕部受限报警如何处理" | 0 results | ✅ 6 results incl. load-limit + SRVO-045/059 |

Gates all green: py_compile 44 files, gitleaks clean, helper consistency, F1 hook.

## Notes

- **"Not retrieved" ≠ "does not exist."** Never infer non-existence from an empty recall; answer "knowledge base does not cover X's [attribute]" and list the chunks actually searched (prompt rule 5c).
- **Silent degradation is a hidden bomb.** Dependency checks and warmup must fail loudly — log/raise on missing `rank_bm25`/`jieba` and on warmup failure, never fall back silently.
- **Table/spec content needs an exact-match fallback.** Embeddings are weak on tables; keep BM25/FTS as a safety net for model codes, alarm codes, and parameter tables.
- **Multi-layer defenses compound to kill valid results.** Each filter (dedup, truncation, MIN_SCORE, overlap-guard) is reasonable alone; stacked, they removed every relevant chunk. Tests must cover semantic queries with no exact match, not only model-code queries.
- **Verify at the production interface.** Fixes that passed at `retrieve()` still failed at `rag_search_raw` (top_k=5) and `rag_answer`. Always verify the full production path.
- Related lessons: `fanuc-r-2000ic-retrieval-fix` (keyword forced recall), `rag-alarm-code-mandatory-recall` (alarm-code keyword recall).