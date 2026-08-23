---
{
  "title": "Cross-Platform CI: OS × Python version matrix with exclusions",
  "domain": "devops",
  "tags": ["ci", "github-actions", "matrix", "cross-platform", "python"],
  "status": "published",
  "evidence_level": "E2",
  "source": "pr-1232",
  "created": "2026-08-23"
}
---

## Problem

Tests pass on Linux but fail on Windows/macOS due to platform-specific issues (path separators, encoding, permissions, dependencies). Single-platform CI misses these failures.

## Solution

Use GitHub Actions matrix strategy with OS × Python version combinations:

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ["3.10", "3.11", "3.12"]
    exclude:
      - os: macos-latest
        python-version: "3.10"  # Reduce matrix size
```

### Key Configuration

```yaml
- name: Run tests
  continue-on-error: true  # Don't block on platform failures
  run: pytest tests/ -x --timeout=60

- name: Upload results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results-${{ matrix.os }}-${{ matrix.python-version }}
    path: test-results/
```

## Matrix Size Optimization

Full matrix: 3 OS × 3 Python = 9 jobs
With exclusions: 8 jobs (drop macOS + 3.10)

| OS | 3.10 | 3.11 | 3.12 |
|----|------|------|------|
| ubuntu | ✅ | ✅ | ✅ |
| windows | ✅ | ✅ | ✅ |
| macos | ❌ | ✅ | ✅ |

## Key Points

- `fail-fast: false` ensures all platforms run even if one fails
- `continue-on-error: true` makes platform failures non-blocking
- Upload artifacts per platform for debugging
- Exclude rare combinations to reduce CI cost
- Platform-specific issues caught early:
  - Windows: path separators, encoding (cp1252 vs UTF-8)
  - macOS: Homebrew, TCC permissions, Apple Silicon
  - Linux: container-specific, library versions

## Common Platform Issues

| Issue | Windows | macOS | Linux |
|-------|---------|-------|-------|
| Path separators | `\` vs `/` | `/` | `/` |
| Default encoding | cp1252 | UTF-8 | UTF-8 |
| Line endings | CRLF | LF | LF |
| File permissions | N/A | chmod | chmod |
| Temp directory | `%TEMP%` | `/tmp` | `/tmp` |

## Verification

```bash
# Check matrix configuration
cat .github/workflows/ci-cross-platform.yml | grep -A 20 "matrix:"

# Verify all jobs pass
gh pr checks <pr-number> --repo owner/repo | grep "test ("
```
