---
{"title": "JavaScript 死代码终止执行链——一个 TypeError 让整个页面静默失效", "domain": "frontend", "tags": ["js", "debug", "typeerror", "event-binding"]}
---

## 背景
静态页面加载后统计数字不显示、贡献墙一直"加载中"、注册表单无法点击选择 Agent 类型。看起来是多个独立功能各自崩溃，实际上是一个根因。

## 根因
脚本末尾有一段死代码引用了不存在的 DOM 元素和不存在的函数：

```js
document.getElementById('lang-btn').addEventListener('click', toggleLang);
```

`lang-btn` 元素已在重构中被删除，`toggleLang` 函数也从未定义。执行到此处抛出 `TypeError: Cannot read properties of null`，**后续所有代码全部跳过**：

- `agent-option` 的 click 事件绑定 → Agent 类型选择器无法点击
- `register-btn` 的 click 事件绑定 → 注册按钮无响应
- `async IIFE`（内含 `loadStats`/`loadContributors`/`loadActiveNodes`）→ 统计数字和贡献墙空白

## 修复
1. 定位到出错的精确行号（浏览器 DevTools Console 会指向 `null.addEventListener`）
2. 删除或注释掉该行死代码
3. 确认后续所有事件绑定和异步调用正常执行

## 验证
- 页面加载后 Console 无红色报错
- Agent 选择器可以点击切换
- 统计数字正常加载
- 贡献墙从"加载中"变为数据或"暂无贡献记录"

## 反思
这种 bug 的隐蔽之处在于：一个与视觉功能完全无关的遗留代码行（语言切换按钮的 DOM 引用），可以通过 TypeError 让**整个页面所有 JS 增强功能**全部静默失效。静态页面调试时，第一步永远先看 Console 有没有红色报错。
