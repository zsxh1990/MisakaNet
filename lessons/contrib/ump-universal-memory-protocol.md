---
domain: "contrib"
title: "universal memory protocol ump for agent interoperability"
verification: "metadata-normalized"
{"title": "Universal Memory Protocol (UMP) — Agent Memory Interoperability", "domain": "agent", "subdomain": "memory", "tags": ["ump", "memory-protocol", "interoperability", "mcp", "a2a", "portable-memory"], "source": "universalmemoryprotocol.io", "status": "draft", "confidence": "0.8", "created": "2026-07-01", "verified_date": "", "domain_expert": ""}
---

## Problem

Agent memory is scattered across Claude/Codex project notes, Obsidian folders, Postgres, Redis, SQLite, and vector databases. Each harness reinvents memory privately and non-portably. New agents start from zero.

## Root Cause

There is no standard protocol for agent memory. MCP standardized tools, A2A standardized agent-to-agent communication, but memory has no equivalent.

## Solution

### The Three Interoperability Layers

| Protocol | Standardizes | Analogy |
|----------|-------------|---------|
| **MCP** | Agent ↔ Tools | Function calls |
| **A2A** | Agent ↔ Agent | RPC |
| **UMP** | Agent ↔ Memory | Database protocol |

### UMP Design Principles

- **Transport-neutral**: MCP server / TypeScript SDK / HTTP all work
- **Portable records**: Signed, bi-temporal (event time + ingestion time)
- **Negotiable operations**: New agents and stores extend the same memory, not restart
- **Vendor-independent**: Works across Claude, Codex, Cursor, etc.

### Implementation

1. Use the MCP server for immediate agent memory
2. Use the TypeScript SDK for memory-aware apps
3. Use HTTP for Python/Go/Swift/browser clients

## Verification

1. Export memory from Claude Code project notes
2. Import into a different agent via UMP
3. Verify all statements, timestamps, and metadata preserved
4. Test cross-vendor: Claude → Codex → Cursor

## Notes

- UMP is new (2026-06) and not yet widely adopted
- Complementary to MCP and A2A, not a replacement
- Source: https://universalmemoryprotocol.io/
