---
name: scientific-paper-reading
description: >-
  Parses scientific PDF papers (and Supporting Information folders) into
  structured Markdown, then produces Chinese reading notes, full translations,
  and Word (.docx) copies with human-readable formulas. Use when the user
  submits a research PDF/folder, asks to parse/extract a paper, generate
  reading notes or translations, or export notes to Word.
---

# Scientific Paper Reading

Cross-agent skill for literature PDF parsing + Chinese notes/translations.

## Environment (required first; no conda needed)

Priority: **bundled `runtime/python`** → skill `.venv` → system Python. Conda optional, never auto-created.

### A. Machine already has Python 3.10+

```bash
# From this skill directory
python scripts/setup_env.py
# Optional: also download a portable CPython into runtime/python/
python scripts/setup_env.py --fetch-python
```

### B. Machine has NO Python (recommended portable path)

```powershell
# Windows PowerShell — downloads portable CPython + installs deps
.\scripts\bootstrap.ps1
```

```bash
# macOS / Linux — needs curl + tar only
bash scripts/bootstrap.sh
```

### C. Copy runtime on USB / intranet

On a networked machine run `fetch_portable_python.py` or `bootstrap.*`, then copy the whole `runtime/python/` folder to the offline PC.

Then always use the returned `recommended_python`:

```bash
<recommended_python> scripts/check_env.py
```

Details: [references/environment.md](references/environment.md), [runtime/README.md](runtime/README.md).

**Workspace vs skill root**
- Skill code / `.venv`: this skill folder
- User data `papers/`, `output/`, `notes/`: current working directory (or `PAPER_READING_WORKSPACE`)

## Workflow

### 1. Parse PDF or folder (main + SI)

```bash
<recommended_python> scripts/start_reading.py <path-to.pdf-or-folder>
```

Read primarily:
- `output/<slug>/content.md`
- `output/<slug>/supporting/content.md` (if SI exists)
- figures under `output/<slug>/images/`

### 2. Generate notes + translations (Markdown)

In the same task, write (complete, no omission):

| File | Role |
|------|------|
| `notes/<slug>/reading_note.md` | Detailed reading note |
| `notes/<slug>/translation_zh.md` | Full main-text Chinese translation |
| `notes/<slug>/translation_si_zh.md` | Full SI translation (if SI) |

Follow:
- [references/reading-notes.md](references/reading-notes.md)
- [references/reading-note-depth.md](references/reading-note-depth.md)
- [references/translation.md](references/translation.md)
- [references/translation-chinese.md](references/translation-chinese.md)
- [references/formula-style.md](references/formula-style.md) — **no LaTeX** in notes; human-readable formulas

### 3. Export Word copies (required)

For machines without Markdown readers:

```bash
<recommended_python> scripts/export_notes_docx.py notes/<slug>
```

Produces `reading_note.docx`, `translation_zh.docx`, and `translation_si_zh.docx` (if SI). Formulas use Word sub/superscripts and readable fractions.

### 4. Optional quality / knowledge checks

```bash
<recommended_python> scripts/check_translation_chinese.py notes/<slug>/translation_zh.md
<recommended_python> scripts/web_search.py -t "term" --context "topic"
```

Web search is for the agent's internal verification only — **do not show URLs or search traces to the user**. See [references/web-verification.md](references/web-verification.md).

## Auto-start behavior

When the user submits a PDF or paper folder with little/no preamble, run parse → notes → translations → docx export, then answer questions as a mentor. See [references/auto-start.md](references/auto-start.md) and [references/mentor-qa.md](references/mentor-qa.md).

## Script index

| Script | Purpose |
|--------|---------|
| `scripts/setup_env.py` | Create `.venv` / use bundled runtime + pip install |
| `scripts/fetch_portable_python.py` | Download portable CPython into `runtime/python/` |
| `scripts/bootstrap.ps1` / `bootstrap.sh` | No system Python: fetch runtime + setup |
| `scripts/check_env.py` | Detect usable Python |
| `scripts/start_reading.py` | Unified parse entry |
| `scripts/process_pdf.py` | Single PDF |
| `scripts/process_paper_folder.py` | Main + SI folder |
| `scripts/batch_process.py` | Batch parse |
| `scripts/export_notes_docx.py` | Markdown → Word |
| `scripts/web_search.py` | Internal web search |
| `scripts/check_translation_chinese.py` | Translation lint (advisory) |

## More references

- [references/workflow.md](references/workflow.md)
- [references/supporting-information.md](references/supporting-information.md)
- [references/project-context.md](references/project-context.md)
- [references/templates/reading_note.md](references/templates/reading_note.md)
- [references/templates/translation.md](references/templates/translation.md)
