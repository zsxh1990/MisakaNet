---
{"title": "静态页面直接调用 GitHub API 的 403 限流处理", "domain": "frontend", "tags": ["github-api", "rate-limit", "static-site", "error-handling"]}
---

## 背景
MisakaNet 前端页面（纯静态 HTML，无后端代理）通过 GitHub REST API 加载注册记录、贡献排行、活跃节点等数据。未认证请求有 60 req/hour 硬限制。页面加载时会发起 10+ 个并发请求（issues 列表 + 每个 issue 的 comments），经常触发 403。

## 根因
1. `fetchJSON` 没有超时机制——慢请求永久挂起
2. `loadStats` 使用嵌套 try/catch——counter.json 失败则整个函数跳过，后续三个子功能全部不执行
3. 所有 GitHub API 请求共享同一个 60 req/hour 配额，静态页面无法使用认证 token 提升配额

## 修复
1. **超时控制**：用 AbortController 实现 8s 超时，防止请求永久挂起
   ```js
   async function fetchWithTimeout(url, timeoutMs = 8000) {
     const ctrl = new AbortController();
     const timer = setTimeout(() => ctrl.abort(), timeoutMs);
     try {
       const r = await fetch(url, { signal: ctrl.signal });
       clearTimeout(timer);
       if (!r.ok) throw new Error(`HTTP ${r.status}`);
       return r.json();
     } catch(e) { clearTimeout(timer); throw e; }
   }
   ```
2. **并行独立容错**：counter.json 和 lessons.json 用 `Promise.all` 并行请求，各自 `catch(() => null)`，单个失败不蔓延
3. **子功能独立执行**：`loadRecentRegistrations()`、`loadContributors()`、`loadActiveNodes()` 不再被外层 try/catch 包裹，始终执行
4. **403 友好提示**：捕获 `HTTP 403` 时显示"GitHub API 频率限制，请稍后刷新重试"，而非原始错误信息

## 验证
- 页面加载时 counter.json 超时不影响 lessons 显示
- 贡献墙 / 时间线 / 活跃节点各自独立加载，互不影响
- 触发限流时显示友好消息而非裸错误

## 反思
纯静态页面直接消费 GitHub API 时，限流是不可避免的。核心设计原则：
1. **任何外部请求都可能失败**——每个接口调用都应有独立容错
2. **不要用 try/catch 包裹多个逻辑块**——一个失败不应该连带其他功能一起失效
3. **非关键数据失败不应阻断关键数据加载**——统计数字和贡献墙应该互不影响
4. **没有超时的 fetch 是永久挂起的隐患**——即使是静态文件请求也应有超时
