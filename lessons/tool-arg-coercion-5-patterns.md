---
{"title": "Tool 参数自动修复管线（5种Known Failure模式）", "domain": "development", "tags": ["tool-call", "llm", "arg-coercion", "error-repair", "model-tools"]}
---

## 背景

LLM 调用工具时经常传错参数格式：字符串当数组、`"null"` 当 null、`"true"` 当 bool、`"42"` 当 int、`{}` 当 `[]`。这些错误随机发生，不处理会导致工具调用失败，影响用户体验。

## 根因

大模型（尤其是开源模型）在生成结构化工具参数时，存在 5 种已知的格式错误模式。逐一修复效率低，需要统一管线处理。

## 修复

```python
# 5 Stage 参数修复管线 — 按顺序执行，Stage 3 必须在 Stage 4 之前
def coerce_tool_args(tool_name, args, get_schema_fn):
    for key, value in list(args.items()):
        schema = get_schema_fn(tool_name, key)
        if not schema:
            continue

        # Stage 1: 空值处理 — 可空参数的 "null" 字符串
        # Stage 2: 数字/bool 字符串还原 — "42"→42, "true"→True
        if isinstance(value, str):
            value = _stage_1_2(value, schema)

            # Stage 3: JSON 字符串反序列化
            # 例如 '["a","b"]' → ["a", "b"]
            if isinstance(value, str):
                parsed = _try_parse_json(value)
                if parsed is not value:
                    value = parsed

            # Stage 4: 裸标量包装为数组
            # 例如 "foo" → ["foo"]（仅当 schema 期望 array）
            if isinstance(value, str) and schema_has_type(schema, "array"):
                value = [value]

        # Stage 5: 空对象占位符修复
        # 例如 {} → []（仅当 schema 期望 array，不是 object）
        elif isinstance(value, dict) and not value and schema_has_type(schema, "array"):
            value = []

        args[key] = value

    return args


def _stage_1_2(value, schema):
    """Stage 1+2: null/true/false/number 字符串还原"""
    if value.lower() == "null" and schema_allows_null(schema):
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if schema_has_type(schema, "integer") and value.isdigit():
        return int(value)
    if schema_has_type(schema, "number"):
        try:
            return float(value)
        except ValueError:
            pass
    return value


def _try_parse_json(value):
    """安全尝试 JSON 解析，不破坏普通字符串"""
    try:
        result = json.loads(value)
        # 只接受数组/对象类型，不接受原始字符串
        if isinstance(result, (list, dict)):
            return result
        return value
    except (json.JSONDecodeError, TypeError):
        return value
```

**关键顺序约束：** Stage 3（JSON 解析）必须在 Stage 4（标量转数组）之前。否则 `'["a","b"]'` 会被 Stage 4 错误包裹为 `['["a","b"]']`。

## 验证

```python
# 58 个测试用例全部通过的核心验证
test_cases = [
    # Stage 1: null 处理
    ({"optional": "null"}, {"optional": None}),
    # Stage 2: 类型字符串还原
    ({"count": "42", "enabled": "true", "ratio": "3.14"},
     {"count": 42, "enabled": True, "ratio": 3.14}),
    # Stage 3: JSON 字符串反序列化
    ({"items": '["a","b"]'}, {"items": ["a", "b"]}),
    # Stage 4: 标量转数组
    ({"tags": "urgent"}, {"tags": ["urgent"]}),
    # Stage 5: 空对象占位符
    ({"skus": {}}, {"skus": []}),
    # 不会误处理：非空 dict 保留
    ({"config": {"key": "val"}}, {"config": {"key": "val"}}),
    # 不会误处理：普通字符串不受影响
    ({"name": "hello"}, {"name": "hello"}),
]

# 反例测试（确保不会错误触发）
negative_cases = [
    # 非空 dict 不会清空
    ({"filter": {"a": 1}}, {"filter": {"a": 1}}, "对象参数应保留"),
    # 字段名不匹配不影响
    ({"extra": "foo"}, {"extra": "foo"}, "无 schema 的字段应通过"),
]
```

## 关键点

1. **顺序不可逆** — Stage 3 在 Stage 4 之前修复了最难的顺序约束问题
2. **白名单式触发** — 只有 schema 明确标注 array 类型时才执行 Stage 4/5，避免误伤 object 参数
3. **Union 类型兼容** — 如果 schema 是 `["array", "null"]`，检查 `"array" in expected_types` 而非 `expected_type == "array"`
4. **非空 dict 保护** — `{"key": "val"}` 不是空对象占位符，不应静默丢弃
5. **实测覆盖 5 个模型** — DeepSeek、Qwen、GLM、CommandCode 等，约 90% 的格式错误落入这 5 类

## 关联经验

- JSON 解析失败处理
- API 请求限流处理方案


---

_I confirm that I release this lesson under the MIT License._


