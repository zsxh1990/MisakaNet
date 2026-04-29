# MisakaNet

> **已合并到 [Agent-Medici](https://github.com/Ikalus1988/Agent-Medici)**
>
> `misakanet/` 现在是 Agent-Medici 的一个子模块，非独立仓库。

MisakaNet 作为 Agent-Medici 的通信层保留在 `misakanet/` 目录下：

```
Agent-Medici/
├── misakanet/
│   ├── scripts/
│   │   ├── feedback_report.py    # 节点侧：上报反馈
│   │   └── hub_poller.py         # Hub 侧：消费反馈 + 更新图谱
│   ├── schema/
│   ├── .github/ISSUE_TEMPLATE/
│   └── README.md
```

所有后续开发与 Issues 请移步 [Agent-Medici](https://github.com/Ikalus1988/Agent-Medici)。
