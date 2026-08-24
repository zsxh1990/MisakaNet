#!/usr/bin/env python3
"""Tests for the search gap analyzer."""
import json
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(REPO_ROOT))

import scripts.gap_analyzer as ga


def test_cluster_queries():
    """Queries are clustered by normalized form."""
    entries = [
        {"query": "Docker timeout", "timestamp": "2026-08-20T00:00:00Z", "source": "mcp"},
        {"query": "docker timeout", "timestamp": "2026-08-21T00:00:00Z", "source": "mcp"},
        {"query": "Docker Timeout!", "timestamp": "2026-08-22T00:00:00Z", "source": "web"},
        {"query": "pip install fail", "timestamp": "2026-08-20T00:00:00Z", "source": "mcp"},
    ]
    clusters = ga.cluster_queries(entries)
    assert len(clusters) == 2, f"Expected 2 clusters, got {len(clusters)}"
    docker = next(c for c in clusters if "docker" in c["normalized"])
    assert docker["count"] == 3, f"Expected 3 docker queries, got {docker['count']}"
    assert set(docker["sources"].keys()) == {"mcp", "web"}


def test_normalize_query():
    """Query normalization strips punctuation and lowercases."""
    assert ga.normalize_query("Docker Timeout!") == "docker timeout"
    assert ga.normalize_query("  MCP   auth  ") == "mcp auth"
    assert ga.normalize_query("pip-install@v2") == "pip install v2"


def test_suggest_lesson_type():
    """Lesson type suggestion based on keywords."""
    assert ga.suggest_lesson_type("docker crash error") == "failure"
    assert ga.suggest_lesson_type("how to setup MCP") == "guide"
    assert ga.suggest_lesson_type("best practice for CI") == "pattern"
    assert ga.suggest_lesson_type("random stuff") == "unknown"


def test_load_gaps_with_filter():
    """load_gaps filters by since_days."""
    entries = [
        {"query": "old query", "timestamp": "2025-01-01T00:00:00Z", "source": "mcp"},
        {"query": "new query", "timestamp": "2026-08-23T00:00:00Z", "source": "mcp"},
    ]
    # Write to temp file and patch
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
        tmp_path = Path(f.name)

    import unittest.mock
    with unittest.mock.patch.object(ga, "GAP_FILE", tmp_path):
        all_gaps = ga.load_gaps()
        assert len(all_gaps) == 2

        recent = ga.load_gaps(since_days=30)
        assert len(recent) == 1
        assert recent[0]["query"] == "new query"

    tmp_path.unlink()


if __name__ == "__main__":
    tests = [
        test_cluster_queries,
        test_normalize_query,
        test_suggest_lesson_type,
        test_load_gaps_with_filter,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    exit(1 if failed else 0)
