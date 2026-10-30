# Supporting Information 处理指南

## 适用场景

文献除正文 PDF 外，还有 **Supporting Information（SI / 补充材料 / ESM）**，用户以**文件夹**形式提交。

## 文件夹结构

```
papers/unread/Author2024_ShortTitle/
  main.pdf
  supporting_information.pdf
```

或多个 SI 文件：

```
papers/unread/Author2024_ShortTitle/
  main.pdf
  SI_figures.pdf
  SI_tables.pdf
  SI_methods.pdf
```

## 命名建议

| 文件 | 推荐名 |
|------|--------|
| 正文 | `main.pdf` |
| 补充材料 | `supporting_information.pdf` 或 `SI.pdf` |

脚本也识别文件名中含：support, supplementary, si, esm, appendix, 补充 等关键词。

## 解析

```bash
python scripts/check_env.py
<recommended_python> scripts/process_paper_folder.py papers/unread/Author2024_ShortTitle/
```

## 输出

```
output/Author2024_ShortTitle/
  content.md              # 正文
  manifest.json           # 总索引（type: paper_folder）
  supporting/
    content.md            # 全部 SI 合并（@ 此文件读 SI）
    index.json
    supporting_information/
      content.md
      images/ tables/ formulas/
```

## AI 阅读与笔记

| 输出文件 | 要求 |
|----------|------|
| `translation_zh.md` | 正文**完整**译文，无省略 |
| `translation_si_zh.md` | SI **完整**译文，无省略 |
| `reading_note.md` | 正文 + SI **详尽解读**（见 `reading-note-depth.mdc`） |

- 文件名含 supplementary / SI 等关键词者**一律视为 SI**（不受 PDF 体积影响）
- 用户问 SI 图表/数据时，必须读取 `supporting/content.md`

## 读完归档

将整个文件夹移至 `papers/read/<同名>/`。
