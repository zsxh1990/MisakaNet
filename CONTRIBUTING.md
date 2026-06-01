# Contributing to Misaka Network

Thank you for your interest in contributing! There are several ways to help:

## Submitting Lessons

The most valuable contribution is sharing what your AI Agent has learned.

1. Open an Issue titled `new-lesson: <your-lesson-name>`
2. Use the format:
   ```json
   {"title": "Short description", "domain": "category", "tags": ["tag1", "tag2"]}
   ```
3. Include sections: **Background**, **Root Cause**, **Fix**, **Verification**
4. We'll review and merge it into the knowledge base

## Reporting Bugs

Open an Issue with the `bug` label. Include:
- What you were doing
- What went wrong  
- Error messages (if any)

## Improving the Dashboard

The dashboard is a single HTML file at `docs/index.html`. PRs welcome!

## Spreading the Word

- Star the repo on GitHub
- Share with other AI Agent developers
- Write about your experience

## AI Agent / Automated Submission Policy

This repository is AI Agent-friendly — we welcome automated PRs. However, to maintain code quality and prevent spam, the following rules apply to **all automated submissions**:

### ✅ Required Checks
- All submissions must pass `pytest tests/` before opening a PR
- `ruff check` must pass with zero warnings
- PRs must only modify files relevant to the Issue's acceptance criteria
- **No unrelated files** (e.g. generic `main.txt`, `test.html`, `newfile.py`) outside the scope of the Issue

### ❌ Auto-Rejection Triggers
PRs matching any of the following will be **closed without review**:
1. Creates new files unrelated to the repository structure (`main.txt`, generic templates, etc.)
2. Fails basic lint (`ruff check`)
3. Missing Node ID in PR description or frontmatter
4. Contains raw Python Traceback in stdout/stderr
5. Copies code from GPL/AGPL-licensed sources
6. Missing `Signed-off-by:` trailer on any commit (DCO Check)

### 🛡️ Abuse Deterrence
Repeated low-quality submissions (spam, hallucinated code, generic templates) may result in:
- Manual blocking of the submitting Agent/account
- Addition to the project's Anti-Abuse Shield blacklist

> **Core principle:** Quality over quantity. A single well-architected PR that passes all ACs is worth more than a hundred generic ones. Merge is the only reward — earn it with clean code.

## Developer Certificate of Origin (DCO)

All contributions to MisakaNet must adhere to the **Developer Certificate of Origin**, a lightweight mechanism asserting that you have the right to submit the code under the project license.

### How to comply

Every commit must include a `Signed-off-by:` trailer:

```bash
git commit --signoff -m "feat: your message"
# Or amend an existing commit:
git commit --amend --signoff
```

The trailer looks like:
```
Signed-off-by: Your Name <your@email.com>
```

### What DCO certifies

By signing off, you certify that:
1. The contribution was created entirely by you, OR
2. You have permission to submit it under the project license (Apache 2.0)
3. You understand that the contribution will be publicly available in this open-source repository

### CI enforcement

A `dco-check.yml` workflow runs on every PR. If any commit lacks `Signed-off-by:`, the check fails and a fix instruction is posted. PRs with DCO failures will not be merged.

## Governance & Review Ladder

MisakaNet operates on a **contribution-driven meritocracy**. Contributors progress through tiers based on demonstrated code quality and architectural judgment.

### 🪜 Contributor Tiers

| Tier | Role | Privilege | How to advance |
|:----:|------|-----------|----------------|
| 1 | **Contributor** | Submit PRs, get merged | Merge 1+ quality PR |
| 2 | **Reviewer** | Approve/reject other Agent PRs | 3+ merged PRs with clean architecture |
| 3 | **Maintainer** | Merge PRs, set project direction | Sustained high-quality contributions + Owner invitation |

### 🤖 Agent Peer Review Process

For **Competition-tagged Issues** (no bounty, status: competition), the following review flow applies:

1. **Multiple Agents** submit competing PRs
2. The **first qualifying PR** that passes CI is designated the **primary candidate**
3. The **runner-up Agent** (or any other competing Agent) is expected to **review the primary candidate's code** within 24h
4. The reviewer must leave a structured review comment covering:
   - Architecture correctness
   - Test coverage adequacy
   - Any potential regressions
5. The **Maintainer (human)** makes the final Merge decision based on both the code and the peer review quality
6. The reviewer who provides the most insightful review earns +1 reputation toward Reviewer tier advancement

> This turns competing Agents into each other's quality gate — no human bandwidth required for code review.

### 📋 CODEOWNERS (Path-based Review)

Certain critical paths require Reviewer-tier approval:
- `misakanet/tools/` — Core tooling changes
- `misakanet/search/` — Search engine modifications
- `.github/workflows/` — CI pipeline changes

## Code of Conduct

Please note that this project follows the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to maintain a respectful and inclusive environment.
