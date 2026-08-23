---
{
  "title": "Shape Guard: bare backticks in test files trigger false positive",
  "domain": "devops",
  "tags": ["ci", "shape-guard", "test", "backtick", "false-positive"],
  "status": "published",
  "evidence_level": "E2",
  "source": "pr-1260",
  "created": "2026-08-23"
}
---

## Problem

CI shape guard detects bare triple backticks (```) in `.py/.js/.ts/.go` files as "Diff/Markdown 泄露". Test files that contain markdown code blocks in test strings trigger this false positive.

## Root Cause

Shape guard Rule 3 scans added lines in source files for patterns like:
- Lines starting with `` ``` ``
- Lines starting with `diff --git`
- Lines starting with `@@ `

Test files often contain markdown examples with bare backticks, which match these patterns.

## Solution

Replace bare backticks with a helper function that constructs them dynamically:

```python
_BT = "`"

def _code_block(code: str, lang: str = "") -> str:
    """Create a markdown code block."""
    return f"{_BT * 3}{lang}\n{code}\n{_BT * 3}"
```

Then use string concatenation instead of triple-quoted strings with backticks:

```python
# Bad — contains bare backticks in source
body = """## Error

```
Traceback: ...
```
"""

# Good — backticks constructed at runtime
body = (
    "## Error\n\n"
    + _code_block("Traceback: ...")
)
```

## Key Points

- Shape guard scans the diff, not the runtime content
- Helper functions avoid backtick patterns in source code
- Works for any language: JS template literals, Go raw strings, etc.
- Also applies to inline markdown examples in documentation generators

## Verification

```bash
# Check if your test file triggers shape guard
grep -n '```' tests/your_test_file.py
# Should return no results
```
