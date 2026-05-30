---
{"title": "静态页面多组件宽度一致性——不同 max-width 导致视觉割裂", "domain": "frontend", "tags": ["css", "layout", "ux", "responsive"]}
---

## 背景
页面各个功能区块宽度不一致：搜索栏 `max-width: 800px`，Agent 注册栏 `max-width: 600px`，注册表单 `display: inline-block; min-width: 360px`，而统计卡片和列表又是全宽。页面看起来像拼凑的，没有统一感。

## 根因
不同开发阶段各自设置了独立的宽度约束，没有统一的容器规范。实际容器宽度由 `.container { max-width: 960px; padding: 0 20px; }` 决定，内宽约 920px，但子组件各自定义了自己的 max-width。

## 修复
1. 搜索栏：移除 `max-width: 800px` 和额外 padding，自然继承容器宽度
2. Agent 注册栏：移除 `max-width: 600px`
3. 注册表单：移除 `display: inline-block` 和 `min-width: 360px`，块级元素自动 100%
4. 所有区块统一使用容器宽度，不再各自为政

## 验证
- 页面各 section 左边缘对齐
- 缩放浏览器宽度时各区块行为一致
- 无水平滚动条出现

## 反思
静态页面的视觉统一性首先来自**宽度的一致性**。如果每个组件都有自己的 max-width，用户会明显感到"拼凑感"。最佳实践：所有内容区块应直接继承容器宽度，只有特殊元素（如弹窗、代码块）才使用独立的 max-width。
