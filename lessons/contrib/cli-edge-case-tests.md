---
{
  "title": "CLI Hardening: edge-case contract tests for argument parsing",
  "domain": "testing",
  "tags": ["cli", "testing", "edge-case", "contract-test", "hardening"],
  "status": "published",
  "evidence_level": "E2",
  "source": "pr-1261",
  "created": "2026-08-23"
}
---

## Problem

Basic CLI tests cover happy path (`--help`, `--version`, success/failure), but miss edge cases that cause confusing errors or silent failures in production.

## Solution

Add contract tests for argument parsing edge cases:

### 1. Invalid Values

```javascript
check('invalid timeout value is a usage error (2)', () => {
  const result = run(['--timeout', 'abc', '--', 'echo', 'hi']);
  assert.equal(result.status, 2);
  assert.match(result.stderr, /invalid timeout/);
});
```

### 2. Missing Required Values

```javascript
check('--timeout without value is a usage error (2)', () => {
  const result = run(['--timeout']);
  assert.equal(result.status, 2);
  assert.match(result.stderr, /requires a value/);
});
```

### 3. Missing Command After Separator

```javascript
check('missing command after -- is a usage error (2)', () => {
  const result = run(['--']);
  assert.equal(result.status, 2);
  assert.match(result.stderr, /missing command/);
});
```

### 4. Conflicting Options

```javascript
check('--help combined with command is a usage error (2)', () => {
  const result = run(['--help', '--', 'echo', 'hi']);
  assert.equal(result.status, 2);
  assert.match(result.stderr, /cannot be combined/);
});
```

### 5. Inline Syntax

```javascript
check('--timeout=50 inline syntax works', () => {
  const result = run(['--timeout=50', '--', 'sleep', '1']);
  assert.equal(result.status, 3);
  assert.match(result.stderr, /timed out after 50ms/);
});
```

### 6. Environment Variable Interaction

```javascript
check('FATAL_HANDLER set on crash', () => {
  const result = spawnSync(process.execPath, [CLI, '--', 'failing-cmd'], {
    env: { ...process.env, FATAL_HANDLER: 'echo' },
  });
  assert.equal(result.status, 1);
});
```

## Key Points

- Test invalid values, missing values, and conflicting options
- Verify error messages are actionable (mention `--help`)
- Test both `--flag value` and `--flag=value` syntax
- Test environment variable interactions
- Each edge case should map to a specific exit code (0/1/2/3)

## Exit Code Contract

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | Command completed successfully |
| 1 | Error | Command failed or couldn't start |
| 2 | Usage | Invalid CLI arguments |
| 3 | Timeout | Command exceeded --timeout |

## Verification

```bash
node tests/cli-contract.js
# All checks should pass with ✓
```
