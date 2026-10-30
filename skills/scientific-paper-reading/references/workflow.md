# 文献阅读工作流程

## 最简用法

### 读新文献（@ 提交）

1. 将 PDF 或文献文件夹放入 `papers/unread/`（也可 @ 任意路径）
2. **新开 Cursor 对话**
3. **仅 @ 提交文件**，无需任何文字
4. AI 自动：解析 → 笔记 + 译文 → **文献答疑**

### 直接提问（不 @ 文件）

1. **新开 Cursor 对话**
2. 直接文字提问（研究方向、课题、专业概念等）
3. AI 以**导师身份**对话，不跑解析流程
4. 若需结合某篇论文，可在对话中 @ PDF 或 `notes/`

---

## 文献生命周期

```
PDF/文件夹 → 新对话 @ 提交 → 自动解析 output/ → 自动 notes/ → 答疑 → papers/read/
```

| 阶段 | 位置 |
|------|------|
| 待读 | `papers/unread/` |
| 解析 | `output/<slug>/`（编码型 PDF 为 `编码_论文标题`） |
| 笔记/译文 | `notes/<slug>/`（与 output 同名） |
| 已读 | `papers/read/` |

## AI 自动步骤

**情景 A（@ 新文献）**：

1. `check_env.py` / 缓存
2. `start_reading.py <路径>`
3. 生成 `reading_note.md`、`translation_zh.md`、`translation_si_zh.md`（若有 SI）
4. `export_notes_docx.py notes/<slug>` → 同步 Word 副本
5. 告知路径，进入文献答疑

**情景 C（直接提问）**：不跑上述脚本，直接以导师身份回答。

## 脚本

```bash
# 统一入口（AI 优先使用）
<recommended_python> scripts/start_reading.py papers/unread/某文献.pdf
<recommended_python> scripts/start_reading.py papers/unread/某文件夹/

# 或分步
<recommended_python> scripts/process_pdf.py ...
<recommended_python> scripts/process_paper_folder.py ...
```

## Cursor 预设

| 规则 | 作用 |
|------|------|
| `auto-start.mdc` | **零开场白自动全流程** |
| `reading-note-depth.mdc` | 笔记深度 |
| `translation.mdc` | 完整译文 |
| `mentor-qa.mdc` | 答疑角色 |

## 读完归档

整文件/文件夹移至 `papers/read/`。
