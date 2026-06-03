---{"title": "零赏金开源项目运营 — 用 Merge 荣誉驱动 AI Agent 竞标", "domain": "devops", "tags": ["open-source", "ai-agent", "bounty", "competition", "misakanet", "community"], "status": "published", "source": "deepseek", "created": "2026-06-03 08:00:00 UTC", "updated": "2026-06-03 08:00:00 UTC"}---

## 根因

传统开源 bounty 平台（Opire、EvoMap 等）需要 Owner 掏钱挂赏金。但实践发现：**给钱引来的不是贡献者，是幻觉 Agent**（lovesxy-001 模式——创建无关 main.txt，完全没理解项目结构）。而顶层 AI Agent（zeroknowledge0x、iccccccccccccc）的核心驱动力不是钱，而是 Merge 成功率和 Hall of Fame 曝光。

## 修复方案

建立一套零赏金的 Agent 竞争工作流：

### 核心模型：4 步闭环

```
[人类] 写需求 → [LLM] 生成地狱级 AC Issue
                     ↓
          打上 [status: competition] 标签（无 Bounty 金额）
                     ↓
          野生 Agent 爬虫自动发现
                     ↓
          Agent 注册节点 → 提 PR
                     ↓
          pr-checks.yml 自动审计
                     ↓
        [人类] Merge → 评论赞赏 → 收工
```

### 关键实践

**0. 诱饵升级：标签是爬虫的第一入口**

```diff
- 之前: [Bounty $0] 或 [Agent-Welcome] 或 [status: competition]
+ 之后: [Bounty $0] + good first issue + help wanted
```

GitHub 官方推荐引擎和野生 Agent 爬虫的扫描策略：
- `good first issue` 是 GitHub 首页「推荐 Issue」的核心筛选条件，主流 AI Agent（Claude Code、Copilot 等）会优先抓取
- `help wanted` 被 GitHub 搜索 API 和 Awesome-List 爬虫广泛索引
- 自定义标签（`status: competition`、`Bounty $0`）只被**你的项目内部**注册的 Agent 识别
- **组合策略**：自定义标签（精准定位熟人 Agent）+ 官方标签（捕获野生流量）

实操规则：
- 每个 Competition Issue 必须同时设置 `good first issue` 和 `help wanted`
- 不要只用自定义标签替代官方标签——它们解决的是不同的问题

**1. 地狱级 AC（Acceptance Criteria）**
每条 Issue 必须包含 4 条硬性标准：
- CODE LOCATION: 必须修改哪个文件的哪段逻辑（约束范围，防无关文件）
- LIVE REGISTRATION: AC 强制调用 Worker 注册，获取 Node ID，写入 lesson frontmatter
- ERROR HANDLING: 禁止原始 Python Traceback 出现在 stdout/stderr
- TEST SUITE: 必须包含测试，coverage ≥ 70%

**2. 竞争性关闭（关键技巧）**
当多个 Agent 竞标同一 Issue 时：
- 合并最优实现，关闭其他 PR
- 关闭评论必须给出**具体技术败因**（如"#129 用 @contextmanager 架构更优"）
- 这些评语会成为 Agent 爬虫的 Few-shot 训练语料，间接"驯化"下一代 Agent

**3. Hall of Fame 荣誉墙**
在 README 维护贡献者表格，包含：
- Agent 名称 + 类型（Autonomous / Copilot-Assisted / Human）
- PR 编号 + 技术亮点描述
- "No bounties were paid — only Merge approval and eternal network gratitude."

**4. 行为分类与对策**

| Agent 类型 | 特征 | 对策 |
|------------|------|------|
| 幻觉 Agent (lovesxy-001) | 创建无关 main.txt，不读 AC | CI 门禁自动拦截 + Close 无解释 |
| 陪跑 Agent (kodedihp, kaartemoe) | 能完成 AC 但架构非最优 | Close + 技术败因评语，驱动进化 |
| Expert Agent (zeroknowledge0x, iccccccccccccc) | 架构正确 + 全测试 + 跨文件重构 | ✅ Merge + Hall of Fame + 竞争激励 |

**5. 自动审计门禁**
```
pr-checks.yml:
├─ DCO 预检（commit 必须 --signoff）
├─ PR 大小检查（>10 文件或 >500 行标记可疑）
├─ pytest + coverage ≥ 70%
├─ 前端 Vitest 回归（9 个 XSS 测试场景）
└─ 评论区自动审计报告
```

### Starter PR 技术（故意留 bug 触发竞争）

当 Competition 无人响应时，主动提交一个"故意有 bug 的 PR"作为诱饵：

**设计原则**：
- Bug 必须在 AC 中明确提到，确保任何读 AC 的 Agent 都能发现
- 修复面要小（移一行代码 + 加一个测试），降低 Agent 参与门槛
- 注释里显式标注 `Issue #N`，降低爬虫的上下文理解成本

**已验证的案例**（telemetry_pipeline Starter PR）：
```
Bug #1: _audit_sliding_window() 在 emit() 里同步执行
  → 违反 AC #3 "审计必须在 consumer loop 中"
  → 修复: 把调用移到 _consumer_loop 的 _flush() 之后

Bug #2: 只有 1 个测试（AC 要求 2 个）
  → 违反 AC #7
  → 修复: 补充 breach detection 测试
```

## 效果

| 指标 | 数值 |
|------|------|
| PR 合并率 | 7/11 = 63.6% |
| Expert Agent 占比 | 5/11 = 45.5% |
| 零赏金支出 | ✅ 确认 |
| 单 PR 平均代码行 | ~175 行 |
| Expert Agent 反馈时间 | < 24h |
| 幻觉 Agent 阻断率 | 100%（CI 自动拦截） |

## 陷阱

1. **不要发小额赏金（$3-$5）**——它不会引来高质量贡献，只会引来幻觉 Agent 刷量，稀释 Expert Agent 的竞争信号
2. **Force push 在 PR 工作流中是安全的**——操作范围限于贡献者自己的 fork 分支，main 有 branch protection rules，`--force-with-lease` 比裸 `--force` 更安全
3. **不要追求全自动 Merge**——"人类点 Merge"是最后的代码审查防御点，自动化到 CI 门禁即可
4. **AC 必须极度精确**——Agent 是 literal 的，AC 写"修改 docs/index.html"它就只改那一个文件，不会自己推断需要修改关联文件

## 关联资料

- 完整流程复盘: `docs/自研/misakanet/misakanet-zero-cost-bounty-workflow.md`
- 门禁流水线: `.github/workflows/pr-checks.yml`
- 贡献者规范: `CONTRIBUTING.md`
- 注册 Issue 模板: `.github/ISSUE_TEMPLATE/ai-bounty-template.md`
