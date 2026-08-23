---
{
  "title": "Search result schema: test coupling when adding optional fields",
  "domain": "testing",
  "tags": ["test", "schema", "coupling", "search", "backward-compatible"],
  "status": "published",
  "evidence_level": "E2",
  "source": "pr-1262",
  "created": "2026-08-23"
}
---

## Problem

Adding a new optional field (e.g., `freshness`) to search results breaks the test that validates the "required schema" with an exact set comparison.

## Root Cause

Test uses exact set equality:

```python
self.assertEqual(
    set(result), {"title", "domain", "tags", "score", "path", "preview"}
)
```

Adding any new field — even optional — causes `KeyError` or assertion failure because the set now has extra keys.

## Solution

### Option A: Update the test (quick fix)

Add the new field to the expected set:

```python
self.assertEqual(
    set(result), {"title", "domain", "tags", "score", "path", "preview", "freshness"}
)
```

### Option B: Use subset check (future-proof)

```python
# Required fields must be present
required = {"title", "domain", "tags", "score", "path", "preview"}
self.assertTrue(required.issubset(set(result)))
```

### Option C: Separate required vs optional schema

```python
REQUIRED_FIELDS = {"title", "domain", "tags", "score", "path", "preview"}
OPTIONAL_FIELDS = {"freshness", "match_reason", "confidence"}

def test_required_fields_present(self):
    result = search_knowledge._json_result(0.5, doc)
    self.assertTrue(REQUIRED_FIELDS.issubset(set(result)))

def test_no_unknown_fields(self):
    result = search_knowledge._json_result(0.5, doc)
    self.assertTrue(set(result).issubset(REQUIRED_FIELDS | OPTIONAL_FIELDS))
```

## Key Points

- Exact set equality is brittle for evolving APIs
- Prefer subset checks for required fields
- Separate required vs optional field definitions
- New optional fields should fail gracefully (try/except)

## Verification

```bash
# Run the specific test
python3 -m pytest tests/test_search_knowledge_stdout.py::TestSearchKnowledgeStdout::test_json_result_uses_required_schema -v
```
