#!/usr/bin/env python3
"""Test gap logging in mcp_server.py."""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.mcp_server import _log_search_gap

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}{': ' + detail if detail else ''}")


def test_gap_logging():
    """Zero-result queries are logged to data/search_gaps.jsonl."""
    print("\n-- gap logging --")
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        tmp_path = Path(f.name)

    try:
        with patch("scripts.mcp_server._GAP_LOG_PATH", tmp_path):
            _log_search_gap("nonexistent query xyz", "bm25")
            _log_search_gap("another missing lesson", "sag-lite")

        lines = tmp_path.read_text().strip().split("\n")
        check("gap log has 2 entries", len(lines) == 2)

        entry = json.loads(lines[0])
        check("gap entry has query", entry["query"] == "nonexistent query xyz")
        check("gap entry has timestamp", "timestamp" in entry)
        check("gap entry has result_count", entry["result_count"] == 0)
        check("gap entry has source", entry["source"] == "bm25")

        entry2 = json.loads(lines[1])
        check("gap entry2 source", entry2["source"] == "sag-lite")
    finally:
        tmp_path.unlink(missing_ok=True)


def test_gap_logging_disabled():
    """Gap logging respects MISAKANET_NO_GAP_LOG env var."""
    print("\n-- gap logging disabled --")
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        tmp_path = Path(f.name)

    try:
        with patch("scripts.mcp_server._GAP_LOG_DISABLED", True), \
             patch("scripts.mcp_server._GAP_LOG_PATH", tmp_path):
            _log_search_gap("should not be logged", "bm25")

        check("gap log is empty", tmp_path.read_text() == "")
    finally:
        tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    test_gap_logging()
    test_gap_logging_disabled()
    print(f"\n{'='*50}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
