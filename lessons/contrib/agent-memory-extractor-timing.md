---
domain: "contrib"
title: "agent memory extractor timing eager vs lazy"
verification: "metadata-normalized"
{"title": "Agent Memory Extractor Timing — Eager vs Lazy", "domain": "agent", "subdomain": "memory", "tags": ["agent-memory", "extractor", "timing", "token-efficiency", "quality"], "source": "brgsk.xyz", "status": "draft", "confidence": "0.85", "created": "2026-07-01", "verified_date": "", "domain_expert": ""}
---

## Problem

Agent memory extractors that run at the wrong time waste tokens or produce low-quality extractions.

## Root Cause

The timing of the extractor is the most consequential design choice:

- **Eager** (after every message): wastes tokens on small talk, extracts noise
- **Lazy** (end of session): long transcripts degrade extraction quality — models attend worse to material placed in the middle of long contexts

## Solution

### Component Anatomy

Every agent memory library has 4 components:

| Component | Function | Key Choice |
|-----------|----------|------------|
| **Extractor** | Reads conversation, decides what to keep | Timing: eager vs lazy vs hybrid |
| **Statements** | Short abstracted facts | Granularity: atomic vs composite |
| **Retriever** | Recalls relevant memories | Strategy: vector + keyword + time decay |
| **Store** | Persistence | Backend: vector / relational / hybrid |

### Hybrid Timing Strategy

1. Extract eagerly on messages with high information density (user preferences, corrections, decisions)
2. Extract lazily on low-density messages (greetings, acknowledgments)
3. Use a lightweight classifier to decide density before invoking the full extractor

## Verification

1. Compare token usage: eager vs lazy vs hybrid on a 50-message conversation
2. Compare extraction quality: recall of key facts from each approach
3. Measure latency impact per extraction call

## Notes

- "Memory" is a misleading term — most libraries build something narrower
- Use precise terminology: statements, retrievals, extractions
- Episodic/Semantic/Procedural labels from Tulving (1972) but many libraries just贴标签 without real separation
- Source: https://brgsk.xyz/agent-memory-anatomy/
