# Agent-Medici 节点接入规则

> 任何节点加入虫群后，按以下规则检索和贡献知识。

## 核心工作流

### 遇到问题时的检索顺序

```bash
# 1. 快速搜所有
python3 search_knowledge.py "你的关键词"

# 2. 只看 lessons（踩坑记录）
python3 search_knowledge.py "关键词" --lessons

# 3. 只看 reference（完整方案）
python3 search_knowledge.py "关键词" --ref

# 4. 只看标题（快速定位）
python3 search_knowledge.py "关键词" --titles
```

### 贡献新知识

```bash
# 踩坑记录（推荐）
python3 scripts/queue_lesson.py \
  -t "你的标题" -d domain \
  --tags "node:你的节点名,project:项目名" \
  "问题描述\n\n## 根因\n...\n\n## 修复\n...\n\n## 验证\n..."
```

## 保持同步

```bash
# 每次会话开始时
cd ~/Agent-Medici && git pull --ff-only
```

## 详细指南

- **检索与贡献**: 见 `docs/agents/retrieval-and-contribution.md`
- **节点规则注入**: 见 `docs/agents/node-injection.md`
- **知识库结构**: 见 `docs/agents/knowledge-structure.md`

## 优先技能

- **intuitive-init**: 初始化/刷新项目本地的 AGENTS.md / CLAUDE.md
- **intuitive-flow**: 从模糊想法到执行的完整开发流程
- **intuitive-doc**: 维护面向人类的文档
- **intuitive-refactor**: 有界的大规模重构
- **intuitive-layout**: 改善仓库/文件夹组织，在深层的架构工作前先解决布局摩擦
- **intuitive-tests**: 测试套件组织、标记、剪枝、夹具管理
- **intuitive-squash**: 将嘈杂的 agent 提交历史压缩为干净的 PR 故事
