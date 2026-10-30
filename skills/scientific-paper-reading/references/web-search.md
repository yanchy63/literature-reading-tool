# 网页搜索（AI 内部使用）

> **用户不可见**：本功能仅供 AI 校验和补充知识，不在对话或阅读笔记中呈现。

## 目的

- 确保术语定义、背景知识、通用原理的**正确性**
- 拓宽 AI 对领域知识的理解
- **不改变**「以本地文献为主」的原则

## 调用方式

### 方式 1：Cursor 内置 WebSearch（推荐）

在生成笔记或答疑前，AI 直接使用 WebSearch 工具，无需用户感知。

### 方式 2：项目脚本

输出 JSON 到 stdout，供 AI 解析：

```bash
python scripts/check_env.py
<recommended_python> scripts/web_search.py -t "graph neural network" --context "molecular generation"
<recommended_python> scripts/web_search.py -r "scaffold-based molecular generation" --field "drug discovery"
<recommended_python> scripts/web_search.py -q "non-fullerene acceptor charge transfer"
```

## 结果格式

```json
{
  "mode": "term",
  "input": "graph neural network",
  "context": "molecular generation",
  "results": [
    {"title": "...", "url": "...", "snippet": "..."}
  ]
}
```

## 使用原则

| 场景 | 信息来源 |
|------|----------|
| 论文方法、实验、结论、数据 | 仅 `output/` 本地文献 |
| 术语定义、领域背景、通用原理 | 本地文献 + 网页校验 |
| 作者未提及的延伸 | 可内部搜索，回答时说明「超出本文范围」 |

## 缓存

- 路径：`.cache/web_search/`
- TTL：72 小时
- 禁用：`--no-cache`

## 优先级

结果按来源可信度排序（维基、Distill、Nature/ACS、arXiv、.edu 等优先）。
