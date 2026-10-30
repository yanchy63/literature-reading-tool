# 项目定位

本项目 **主要面向 AI（Cursor Agent）**，不是普通文档工具。目标是让 AI 充分理解 PDF 文献内容，辅助用户进行长期文献阅读。

## 目录约定

```
papers/unread/   ← @ 提交 PDF（单篇）或文件夹（正文+SI）
papers/read/     ← 已读
output/<slug>/   # 编码型 PDF → s42256-026-01229-5_论文标题slug
notes/<slug>/    # 与 output 同名
```

**新对话零开场白**，按首条消息自动识别情景，见 `auto-start.mdc`：

| 情景 | 触发 |
|------|------|
| A 新文献 | @ PDF / 文件夹 → 解析 → notes |
| B 继续文献 | @ notes / output 或问已有文献 |
| C 直接提问 | 不 @ 文件 → 导师对话（方向、课题、专业问题） |

## AI 阅读文献时的数据源优先级

1. `output/<slug>/content.md` — 正文主文件
2. `output/<slug>/supporting/content.md` — SI 合并（若有）
3. `output/<slug>/manifest.json` — 元数据与资源索引
3. `output/<slug>/images/` — 图表（复杂 figure 必看）
4. `output/<slug>/tables/` — 表格
5. `output/<slug>/formulas/` — 公式

若 output 不存在：单 PDF 用 `process_pdf.py`；含 SI 的文件夹用 `process_paper_folder.py`（见 `supporting-information.mdc`）。

## 技术栈

- Python 3.10+；通过 `scripts/check_env.py` 自动发现本机可用环境（conda/venv 均可）
- 解析：`pymupdf4llm` + `pdfplumber`
- 内部搜索：`scripts/web_search.py` 或 Cursor WebSearch（静默，不对用户展示）

