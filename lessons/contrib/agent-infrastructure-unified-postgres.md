---
domain: "contrib"
title: "agent infrastructure unified postgres ghost"
verification: "metadata-normalized"
{"title": "Agent Infrastructure — Unified Postgres (Ghost)", "domain": "agent", "subdomain": "infrastructure", "tags": ["postgres", "agent-infra", "memory", "sandbox", "search", "ghost"], "source": "dev.to", "status": "draft", "confidence": "0.8", "created": "2026-07-01", "verified_date": "", "domain_expert": ""}
---

## Problem

Current agent infrastructure is "duct tape" — 5+ separate services that can't talk to each other:

| Service | Purpose |
|---------|---------|
| Neon/Supabase | Database |
| Mem0/Zep | Memory |
| Pinecone/pgvector | Search |
| S3 | Files |
| E2B | Sandboxed execution |

Memory can't query its own database. Sandbox can't read agent's files. Glue code dissolves.

## Root Cause

Each component is a separate service with its own API, auth, and data format. Cross-service communication requires custom glue code that breaks.

## Solution

### Unified Postgres Architecture

Ghost provides all agent infrastructure in one Postgres instance:

| Component | Implementation |
|-----------|---------------|
| Memory Engine | Postgres-native memory |
| pg_textsearch | Full-text search |
| TigerFS | File storage |
| Ox | Sandboxed execution |
| Unlimited databases | Per-agent isolation |
| Unlimited forks | State snapshots |

### Benefits

- Memory can query the same database it stores in
- Sandbox can read agent files directly
- No cross-service latency
- No glue code to maintain

## Verification

1. Agent stores a fact in memory → queries it via SQL in the same session
2. Agent writes a file → sandbox reads it without copy
3. Fork a database → verify instant snapshot

## Notes

- "Agents are getting smarter every day. We haven't spent nearly enough time giving them somewhere to be productive."
- Ghost is free: unlimited databases, unlimited forks, 1TB storage
- Source: https://dev.to/ghostbuild/your-agent-can-think-it-cant-remember-5e1o
