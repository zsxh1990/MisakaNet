#!/usr/bin/env python3
"""Gap analyzer — clusters zero-result search queries and outputs top gaps.

Usage:
    python3 scripts/gap_analyzer.py [--top N] [--since DAYS] [--json]

Reads data/search_gaps.jsonl, clusters similar queries by fuzzy match,
and outputs prioritized gaps by frequency.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GAP_FILE = REPO_ROOT / "data" / "search_gaps.jsonl"


def load_gaps(since_days: int | None = None) -> list[dict]:
    """Load gap entries, optionally filtered by recency."""
    if not GAP_FILE.exists():
        return []
    entries = []
    cutoff = None
    if since_days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)
    with open(GAP_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if cutoff and "timestamp" in entry:
                try:
                    ts = datetime.fromisoformat(entry["timestamp"])
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    if ts < cutoff:
                        continue
                except (ValueError, TypeError):
                    pass
            entries.append(entry)
    return entries


def normalize_query(q: str) -> str:
    """Normalize query for clustering — lowercase, strip punctuation."""
    import re
    q = q.lower().strip()
    q = re.sub(r"[^\w\s]", " ", q)
    q = re.sub(r"\s+", " ", q).strip()
    return q


def cluster_queries(entries: list[dict]) -> list[dict]:
    """Cluster similar queries using normalized form as key."""
    clusters: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        key = normalize_query(entry.get("query", ""))
        if key:
            clusters[key].append(entry)

    results = []
    for key, items in clusters.items():
        # Pick the most recent original query as representative
        items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        results.append({
            "query": items[0].get("query", key),
            "normalized": key,
            "count": len(items),
            "sources": dict(Counter(e.get("source", "unknown") for e in items)),
            "first_seen": min(e.get("timestamp", "") for e in items),
            "last_seen": max(e.get("timestamp", "") for e in items),
        })

    results.sort(key=lambda x: x["count"], reverse=True)
    return results


def suggest_lesson_type(query: str) -> str:
    """Heuristic lesson type suggestion based on query keywords."""
    q = query.lower()
    if any(w in q for w in ["error", "fail", "crash", "bug", "issue"]):
        return "failure"
    if any(w in q for w in ["how", "setup", "config", "install"]):
        return "guide"
    if any(w in q for w in ["best", "pattern", "practice"]):
        return "pattern"
    return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze search gaps")
    parser.add_argument("--top", type=int, default=20, help="Show top N gaps")
    parser.add_argument("--since", type=int, default=None, help="Only queries from last N days")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    entries = load_gaps(since_days=args.since)
    if not entries:
        print("No gap queries found.", file=sys.stderr)
        sys.exit(0)

    clusters = cluster_queries(entries)
    top = clusters[: args.top]

    for c in top:
        c["suggested_type"] = suggest_lesson_type(c["query"])

    if args.json:
        print(json.dumps(top, indent=2, ensure_ascii=False))
    else:
        print(f"Top {len(top)} search gaps (from {len(entries)} queries, {len(clusters)} unique)\n")
        for i, c in enumerate(top, 1):
            print(f"  {i:2d}. [{c['count']:3d}x] {c['query']}")
            print(f"      type={c['suggested_type']}  sources={c['sources']}")
            print(f"      first={c['first_seen'][:10]}  last={c['last_seen'][:10]}")
            print()


if __name__ == "__main__":
    main()
