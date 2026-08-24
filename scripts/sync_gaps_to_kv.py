#!/usr/bin/env python3
"""Sync search gap data from local JSONL to Cloudflare KV via Worker endpoint.

Usage:
    python3 scripts/sync_gaps_to_kv.py [--top N] [--worker-url URL] [--sync-token TOKEN]

Requires:
    SYNC_TOKEN env var or --sync-token flag (must match Worker's SYNC_TOKEN)
    MISAKANET_WORKER_URL env var or --worker-url flag
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.gap_analyzer import cluster_queries, load_gaps


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync search gaps to KV")
    parser.add_argument("--top", type=int, default=20, help="Top N gaps to sync")
    parser.add_argument("--worker-url", default=os.environ.get("MISAKANET_WORKER_URL", ""),
                        help="Worker endpoint URL")
    parser.add_argument("--sync-token", default=os.environ.get("SYNC_TOKEN", ""),
                        help="Sync auth token")
    parser.add_argument("--since", type=int, default=30, help="Only queries from last N days")
    parser.add_argument("--dry-run", action="store_true", help="Print without syncing")
    args = parser.parse_args()

    entries = load_gaps(since_days=args.since)
    if not entries:
        print("No gap queries found.", file=sys.stderr)
        sys.exit(0)

    clusters = cluster_queries(entries)
    top = clusters[: args.top]

    # Add suggested type
    from scripts.gap_analyzer import suggest_lesson_type
    for c in top:
        c["suggested_type"] = suggest_lesson_type(c["query"])

    print(f"Top {len(top)} gaps from {len(entries)} queries ({len(clusters)} unique)")

    if args.dry_run:
        print(json.dumps(top, indent=2, ensure_ascii=False))
        return

    if not args.worker_url:
        print("Error: --worker-url or MISAKANET_WORKER_URL required", file=sys.stderr)
        sys.exit(1)
    if not args.sync_token:
        print("Error: --sync-token or SYNC_TOKEN required", file=sys.stderr)
        sys.exit(1)

    import urllib.request
    url = f"{args.worker_url.rstrip('/')}/api/insights/search-gaps"
    data = json.dumps({"gaps": top}).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json",
        "X-Sync-Token": args.sync_token,
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            print(f"Synced {result.get('stored', '?')} gaps to KV")
    except Exception as e:
        print(f"Sync failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
