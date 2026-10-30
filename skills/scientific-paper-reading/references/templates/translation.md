# 原文中文翻译模板

> **正文**保存至：`notes/<slug>/translation_zh.md`  
> **SI** 保存至：`notes/<slug>/translation_si_zh.md`（若有 Supporting Information）  
> 与 `reading_note.md` 同时生成。**完整、无省略**。

---

# [论文标题 — 中文译名]

> **原文标题**：[English Title]  
> **作者**：[作者列表]  
> **出处**：[期刊 / 会议] | [年份]  
> **翻译日期**：[YYYY-MM-DD]  
> **解析源文件**：`output/<slug>/content.md`  
> **说明**：正文忠实译文；解读见 `reading_note.md`；中文规范见 `docs/CHINESE_STYLE.md`

---

## 摘要（Abstract）

（**逐段**忠实翻译，一段不漏）

---

## [Section 中文译名（English Section Title）]

（按原文**每一段落**翻译，禁止合并、省略、「……（略）」）

### [Subsection 中文译名（English Subsection Title）]

（译文）

> **标题格式**：各级章节标题均为 **中文（English）**，便于阅读时对照 PDF；正文句中普通词仍应中译。

---

## 图表标题与说明

### Figure 1. [中文译名（Figure 1. English caption title）]

**Caption 译文**：（完整）

### Table 1. [中文译名（Table 1. English caption title）]

**Caption 译文**：（完整）

---

## [直至全文所有 Section 译完]

---

## 术语对照表

| 英文 | 中文译名 | 备注 |
|------|----------|------|

---

# Supporting Information 译文模板 → `translation_si_zh.md`

> **解析源文件**：`output/<slug>/supporting/content.md`  
> **说明**：SI 独立文件，**全文**翻译，结构与 SI 原文一致

---

# [文献标题] — 补充材料（Supporting Information）

## Supplementary Note 1

（逐段完整译文）

## Fig. S1

**Caption 译文**：（完整）

## Table S1

**Caption 译文**：（完整）

---

## 完整性自检（AI 内部）

- [ ] 正文每个 Section 均有对应译文
- [ ] 无「略」「省略」「参见原文」
- [ ] 有 SI 时已生成 `translation_si_zh.md` 且覆盖 SI 全部 Section/Note
- [ ] 译文篇幅与 `content.md` 信息量相当
