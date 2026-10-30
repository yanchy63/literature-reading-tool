# 阅读笔记规范

生成路径：`notes/<slug>/reading_note.md`（slug 与 output 目录名一致）

同目录下另有 **`translation_zh.md`**（正文完整译文）、**`translation_si_zh.md`**（SI 完整译文，若有）。深度要求见 **`reading-note-depth.md`**。

## Word 导出（必须）

生成/更新 Markdown 后，必须同步导出 Word，便于无 Markdown 阅读器的电脑打开：

| Markdown | Word |
|----------|------|
| `reading_note.md` | `reading_note.docx` |
| `translation_zh.md` | `translation_zh.docx` |
| `translation_si_zh.md`（若有） | `translation_si_zh.docx` |

```bash
<recommended_python> scripts/export_notes_docx.py notes/<slug>
```

以 Markdown 为编辑主文件；Word 为交付副本，每次改完 md 后重新导出。

## 核心要求

1. **完全按文献原文章节结构**组织（标题层级与论文一致），便于用户对照 PDF 阅读
2. **逐节详尽解释**（非摘要）；每节含：原文要点 + 详细解释 + 原理深入 + 术语 + 公式/图表解读
3. **所有专业知识点**讲清机制「为什么」；前置知识充分展开（通常 ≥ 6 项）
4. 图表：**每张**重要 Fig./Table 单独解读
5. 公式：人类可读写法 + 符号表 + 物理/化学含义
6. **有 SI 时**：笔记设 **Supporting Information** 专章，逐节解读，不得省略

## 公式的人类可读写法（重要）

笔记读者是**人**，在 Markdown 预览中阅读，**禁止**用 LaTeX 语法（`$...$`、`\(...\)`、`\frac{}` 等）。

详见 `docs/FORMULA_STYLE.md`。摘要：

| 做法 | 示例 |
|------|------|
| 简单式子用纯文本 + Unicode | G = (V, E)；α、β；∂L/∂w；≤ |
| 复杂式子用「口语 + 符号表」 | 先一句话说明含义，再用表格列符号 |
| 多步推导用编号步骤 | 1. … 2. … 3. 输出 z_i = μ_i + σ_i × ε |
| 禁止 | `$...$`、`$$...$$`、`\mathbf{}`、未解释的公式块 |

生成后自检：全文不应出现 `$` 或 `\(`。

## 笔记结构（必须包含）

```markdown
# [论文标题]
> 作者 | 期刊/会议 | 年份
> 阅读笔记生成日期

## 文献概览
（研究背景、核心问题、主要贡献，2-3 段）

## 前置知识
（阅读本文需要的背景知识清单，逐项解释）

---
## [与原文一致的 Section 1 标题]
### [与原文一致的 Subsection 标题]
（该节完整解释 + 术语注释 + 公式/图表解读）

## 关键术语表
| 术语 | 英文 | 解释 |

## 个人思考与延伸（可选，用户未要求可省略）
```

## 写作风格

- 面向有理工科基础的研究生，由浅入深
- 先讲「这段在说什么」，再讲「为什么这样写/这样做」
- 不确定处标注「原文未明确说明」而非臆造
- **中文为主**：见 `chinese-style.mdc` 与 `docs/CHINESE_STYLE.md`；仅术语首次定义、缩写、专名、符号保留英文，禁止句中夹杂 thin film、ellipticity 等可中译英文词

## 知识校验（内部，不对用户展示）

- 写「前置知识」和术语解释前，**静默网页搜索**校验定义（见 `web-verification.mdc`）
- 笔记中只呈现校验后的准确内容，不出现 URL 或搜索痕迹
- 论文具体结论、数据、方法细节**仅来自本地文献**

