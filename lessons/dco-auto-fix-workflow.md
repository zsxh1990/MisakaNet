---
{"title": "DCO 自动修复工作流 — /fix-dco 命令设计与实现", "domain": "devops", "tags": ["github-actions", "dco", "signoff", "issue_comment", "auto-fix", "fork-pr"], "status": "published", "source": "codewhale", "created": "2026-06-13 00:00:00 UTC", "updated": "2026-06-13 00:00:00 UTC"}
---

## 背景

贡献者提交 PR 后 DCO（Signed-off-by）检查失败是最常见的阻塞原因之一。尤其是 AI Agent 自动提交的 PR，经常缺签。需要在 PR 评论区提供一键自动修复能力。

## 方案

利用 `issue_comment` 事件 + `pull_request_target` 安全模型，实现 `/fix-dco` 命令。

### 工作流核心逻辑

```yaml
on:
  issue_comment:
    types: [created]

jobs:
  fix-dco:
    if: |
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '/fix-dco') &&
      (github.event.comment.user.login == github.event.issue.user.login ||
       contains(fromJSON('["MEMBER","OWNER","COLLABORATOR"]'), ...))
```

### 分支处理

**同仓库 PR**（head repo = 目标仓库）：
1. 检出 PR 头部分支（`refs/pull/<num>/head`）
2. 执行 `git rebase --signoff origin/main` 或 `git rebase --signoff HEAD~N`
3. Force-push 回原分支
4. 回复 ✅ 成功

**Fork PR**（head repo ≠ 目标仓库）：
- GITHUB_TOKEN 无权 push 到 fork
- 回复手动修复指引：
  ```
  git rebase --signoff HEAD~N
  git push --force
  ```

### 安全限制

- 仅允许 PR 作者、MEMBER、OWNER、COLLABORATOR 触发
- 最多自动修复 10 个 commit（超过则要求手动修复）
- 需要 `contents: write` + `pull-requests: write` 权限

## 关键实现细节

```yaml
- name: Get PR info
  run: |
    PR_JSON=$(gh api repos/${{ github.repository }}/pulls/${{ github.event.issue.number }} \
      --jq '{headRef: .head.ref, headRepo: .head.repo.full_name, baseRef: .base.ref}')
    echo "isFork=$([ "$headRepo" != "${{ github.repository }}" ] && echo true || echo false)"
```

## 验证

在 PR 评论区输入 `/fix-dco`，等待 30 秒内 bot 回复修复结果。

## 关联

- 配套措施：`pr-welcome.yml` 欢迎语中已预置 DCO 修复命令
- 兜底方案：如自动修复失败，需贡献者本地手动执行 `git commit --amend --signoff`
