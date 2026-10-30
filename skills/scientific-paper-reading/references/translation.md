# 中文翻译规范

每篇文献除 `reading_note.md` 外，必须生成**完整、无省略**的中文翻译。

## 输出文件

| 文件 | 内容 | 何时必须 |
|------|------|----------|
| `translation_zh.md` | **正文**全文译文 | 始终 |
| `translation_si_zh.md` | **Supporting Information** 全文译文 | 存在 SI 时 |
| 对应 `.docx` | Word 副本（同名） | 与 md 同步导出 |

**禁止**：摘要式翻译、跳节、用「……（略）」代替段落、合并多段为一句。

Markdown 审校完成后执行：`scripts/export_notes_docx.py notes/<slug>`。

## 与阅读笔记的区别

| 文件 | 性质 |
|------|------|
| `reading_note.md` | 讲解、解读、原理展开 |
| `translation_zh.md` / `translation_si_zh.md` | **忠实全文译文**，不添加讲解 |

## 完整性要求（不可妥协）

1. **逐段对应**：原文每一段、每一小节、每一图注/表注均有译文，顺序一致
2. **章节标题**：**中文译名（English Title）**，各级 `##` / `###` 均附原文标题于括号内，便于对照 PDF
3. **不省略**：Methods 步骤、Results 数据描述、Discussion 论证、SI 中的实验细节与 Supplementary Note 全文均须译出
4. **不概括代替翻译**：禁止用「作者讨论了 X」代替原文具体表述
5. **SI 独立成文件**：`translation_si_zh.md` 须覆盖 `output/<slug>/supporting/content.md` 全部内容；按 SI 内 Section / Note / Fig. S1 等结构组织
6. **参考文献**：条目可保留英文原文；正文中的引用语句须译

## 质量要求

- **准确**：理解全文语境后再译
- **术语**：静默网页校验；专业术语可 **中文（English）**
- **中文表达**：句中避免残留本可中译的普通英文词（见 `translation-chinese.mdc`）
- **公式**：人类可读纯文本，不用 LaTeX（见 `docs/FORMULA_STYLE.md`）

## 译文审校（生成后必做，第二遍）

1. **通读原文**（`content.md` + SI）理解全文
2. **通读译文**全文，检查漏译普通词、误译、不通顺
3. 可选：跑 `check_translation_chinese.py` 作**参考**，结合语境决定是否修改
4. 修正后再次快速通读

## 篇幅自检

- 译文篇幅应接近 `content.md` 对应部分的信息量（通常为原文中文译文的 0.8–1.5 倍，视句式而定）
- 若 `translation_zh.md` 明显短于 `content.md` 的 1/3，视为**不合格**，须补全
- 有 SI 时若缺少 `translation_si_zh.md`，视为**未完成**

## 生成时机

用户要求「开始阅读 / 生成笔记」时，与 `reading_note.md` **同一任务内**全部交付。

