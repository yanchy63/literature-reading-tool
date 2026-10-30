# Supporting Information（补充材料）

用户可能提交**文件夹**而非单个 PDF，内含正文与 Supporting Information（SI）。

## 文件夹放置位置

```
papers/unread/<文献文件夹名>/
  main.pdf                      # 正文（推荐命名）
  supporting_information.pdf    # 补充材料（推荐命名）
  # 或多个 SI：SI_figures.pdf, SI_tables.pdf ...
```

读完后整文件夹移至 `papers/read/<文献文件夹名>/`。

## PDF 命名约定

| 类型 | 推荐文件名 | 识别关键词 |
|------|-----------|-----------|
| 正文 | `main.pdf` / `paper.pdf` | main, paper, article, manuscript, 正文 |
| SI | `supporting_information.pdf` / `SI.pdf` | support, si, supplementary, esm, 补充 |

若无明确 `main.pdf`：文件名含 SI 关键词者**一律视为 SI**（不受体积影响）；其余 PDF 为正文。

## 解析命令

```bash
python scripts/process_paper_folder.py papers/unread/<文献文件夹>/
```

## 输出结构

```
output/<folder_slug>/
  content.md                 # ★ 正文（AI 阅读主文件）
  manifest.json              # 含 SI 索引
  supporting/
    content.md               # ★ 全部 SI 合并（AI 读 SI 时用）
    index.json
    <si_slug>/               # 各 SI 分册完整解析
      content.md
      images/ tables/ formulas/
```

## AI 阅读顺序

1. 正文：`output/<slug>/content.md`
2. SI：`output/<slug>/supporting/content.md`（合并版）
3. 某分册细节：`output/<slug>/supporting/<si_slug>/content.md`
4. 笔记/译文：正文与 SI **均需覆盖**（SI 可单独成章「Supporting Information」）

## 生成笔记与译文时（均须完整、无省略）

| 文件 | 内容 |
|------|------|
| `translation_zh.md` | 正文**全文**忠实译文 |
| `translation_si_zh.md` | SI **全文**忠实译文（若有） |
| `reading_note.md` | 正文 + SI **详尽解读**（见 `reading-note-depth.mdc`） |

- 禁止用「详见 SI」「从略」跳过内容
- 用户引用的 SI 图表/数据必须读取 `supporting/content.md`

