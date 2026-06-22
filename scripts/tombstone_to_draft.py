#!/usr/bin/env python3
"""
Tombstone → Draft Lesson 转换器

将 fatal-guard 输出的 4-field JSON 墓碑转换为 MisakaNet draft lesson。

输入: fatal-guard 墓碑 JSON（stdin 或文件）
输出: lessons/drafts/<slug>.md + 可选自动提 PR

用法:
    # 从文件读取
    python3 scripts/tombstone_to_draft.py --from-file tombstone.json

    # 从 stdin 读取（管道接入 fatal-guard）
    fatal-guard -- node app.js 2>&1 | python3 scripts/tombstone_to_draft.py --stdin

    # 预览模式（不写文件）
    python3 scripts/tombstone_to_draft.py --from-file tombstone.json --dry-run

    # 自动创建悬赏 Issue
    python3 scripts/tombstone_to_draft.py --from-file tombstone.json --create-bounty
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DRAFTS_DIR = REPO / "lessons" / "drafts"

# 4-field tombstone protocol fields
REQUIRED_FIELDS = {"pid", "timestamp", "reason", "exit_code"}
OPTIONAL_FIELDS = {"snippet", "signal", "host", "node_id"}


def _slugify(text: str, max_len: int = 60) -> str:
    """生成文件名友好的 slug。"""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_len]


def _parse_tombstone(data: dict) -> dict:
    """验证并规范化墓碑 JSON。"""
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        raise ValueError(f"Missing required tombstone fields: {missing}")

    return {
        "pid": int(data["pid"]),
        "timestamp": str(data["timestamp"]),
        "reason": str(data["reason"]),
        "exit_code": int(data["exit_code"]),
        "snippet": str(data.get("snippet", ""))[:500],
        "signal": str(data.get("signal", "")),
        "host": str(data.get("host", "")),
        "node_id": str(data.get("node_id", "unknown")),
    }


def _infer_domain(reason: str) -> str:
    """从崩溃原因推断领域标签。"""
    reason_lower = reason.lower()
    domain_map = {
        "node": "javascript",
        "npm": "javascript",
        "vite": "devops",
        "docker": "devops",
        "pip": "python",
        "python": "python",
        "import": "python",
        "module": "python",
        "chromadb": "python",
        "openclaw": "cli",
        "e2b": "cli",
        "git": "devops",
        "permission": "security",
        "denied": "security",
        "timeout": "devops",
        "oom": "devops",
        "memory": "devops",
        "segfault": "devops",
        "signal": "devops",
    }
    for keyword, domain in domain_map.items():
        if keyword in reason_lower:
            return domain
    return "general"


def _generate_draft(tombstone: dict, source_file: str = "") -> str:
    """从验证后的墓碑生成 draft lesson markdown。"""
    now = datetime.now(timezone.utc)
    ts = tombstone["timestamp"]
    reason = tombstone["reason"]
    exit_code = tombstone["exit_code"]
    snippet = tombstone["snippet"]
    domain = _infer_domain(reason)
    node = tombstone.get("node_id", "unknown")

    # 生成唯一标识
    tombstone_json = json.dumps(tombstone, sort_keys=True, default=str)
    tombstone_hash = hashlib.sha256(tombstone_json.encode()).hexdigest()[:12]

    # 文件名
    slug = _slugify(f"draft-{reason[:40]}-{tombstone_hash}")
    filename = f"{slug}.md"

    # 标题
    title = f"Fix: {reason[:80]}"

    # Frontmatter
    frontmatter = {
        "title": title,
        "domain": domain,
        "tags": ["draft", "auto-generated", "bounty", f"exit-code-{exit_code}"],
        "status": "draft",
        "source": "fatal-guard",
        "node_id": node,
        "tombstone_hash": tombstone_hash,
        "tombstone_ref": source_file if source_file else f"tombstone:{tombstone_hash}",
        "created": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "crash_timestamp": ts,
    }

    body = f"""---
{json.dumps(frontmatter, ensure_ascii=False, indent=2)}
---

## Problem

进程崩溃，退出码 {exit_code}。

```
{ts} | pid={tombstone['pid']} | reason={reason} | exit_code={exit_code}
```

"""
    if snippet:
        body += f"""### 崩溃现场（最后 4 行 stderr）

```text
{snippet}
```

"""
    body += f"""## Root Cause

<!-- TODO: Agent 需补全根本原因分析 -->
<!-- 原始墓碑数据: {tombstone_json} -->

## Solution

<!-- TODO: Agent 需提供修复方案 -->

## Verification

<!-- TODO: Agent 需添加验证步骤 -->

## Notes

- 由 fatal-guard 自动捕获
- 节点: {node}
- 墓碑哈希: `{tombstone_hash}`
"""

    return filename, body


def main():
    parser = argparse.ArgumentParser(
        description="Tombstone → Draft Lesson 转换器"
    )
    parser.add_argument("--from-file", dest="source_file", help="墓碑 JSON 文件路径")
    parser.add_argument("--stdin", action="store_true", help="从 stdin 读取墓碑 JSON")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写文件")
    parser.add_argument("--create-bounty", action="store_true",
                        help="生成悬赏 Issue 元数据")
    args = parser.parse_args()

    # 读取输入
    raw_data = None
    source_label = ""
    if args.source_file:
        source_label = args.source_file
        with open(args.source_file, "r", encoding="utf-8", errors="replace") as f:
            raw_data = f.read()
    elif args.stdin:
        source_label = "stdin"
        raw_data = sys.stdin.read()
    else:
        print("错误: 需要 --from-file 或 --stdin", file=sys.stderr)
        sys.exit(1)

    if not raw_data.strip():
        print("错误: 输入为空", file=sys.stderr)
        sys.exit(1)

    # 解析 JSON
    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError:
        # 尝试从混合文本中提取 JSON
        json_match = re.search(r'\{[^{}]*"pid"[^{}]*\}', raw_data)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
            except json.JSONDecodeError:
                print("错误: 无法解析输入为 JSON，也找不到墓碑对象", file=sys.stderr)
                sys.exit(1)
        else:
            print("错误: 无法解析输入为 JSON", file=sys.stderr)
            sys.exit(1)

    # 验证墓碑
    try:
        tombstone = _parse_tombstone(data)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 生成 draft
    filename, body = _generate_draft(tombstone, args.source_file)

    if args.dry_run:
        print(f"[DRY RUN] 将生成: {filename}")
        print("=" * 60)
        print(body)
        print("=" * 60)
        return

    # 写入文件
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DRAFTS_DIR / filename
    output_path.write_text(body, encoding="utf-8")
    print(f"draft lesson: {filename}")
    print(f"  domain: {_infer_domain(tombstone['reason'])}")
    print(f"  reason: {tombstone['reason'][:80]}")
    print(f"  tombstone_hash: {tombstone.get('node_id', '?')}")
    print(f"  -> {output_path}")

    if args.create_bounty:
        bounty_meta = {
            "title": f"Bounty: Complete Root Cause for {tombstone['reason'][:60]}",
            "draft_file": f"lessons/drafts/{filename}",
            "tombstone_hash": data.get("tombstone_hash", ""),
            "reward": "search_quota_reset + 20_credit_points",
            "status": "open",
        }
        bounty_path = DRAFTS_DIR / f"{Path(filename).stem}.bounty.json"
        bounty_path.write_text(
            json.dumps(bounty_meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"  bounty: {bounty_path}")

    # 提示下一步
    print()
    print("  下一步:")
    print(f"  1. 审核 draft: cat lessons/drafts/{filename}")
    print(f"  2. 编辑补全 Root Cause + Solution + Verification")
    print(f"  3. 提交 PR: git add lessons/drafts/ && git commit && git push")
    print(f"  4. 或标记为悬赏: 在 Issue body 中 @agent 认领")


if __name__ == "__main__":
    main()
