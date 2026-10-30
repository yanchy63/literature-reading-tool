#!/usr/bin/env python
"""
统一阅读入口：自动识别 PDF 或文献文件夹（正文+SI），执行解析并返回 slug。

供 AI 在新对话中用户仅 @ 提交文件时调用，无需用户写开场白。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import NOTES_DIR, OUTPUT_DIR, refresh_workspace_paths
from src.extractors.metadata import extract_metadata
from src.paper_folder import resolve_paper_pdfs
from src.pipeline import process_paper_folder, process_pdf
from src.utils import find_existing_output_dir, paper_slug


def resolve_submission(path: Path) -> tuple[str, Path]:
    """
    判断提交类型，返回 (kind, path)。
    kind: 'pdf' | 'folder'
    """
    path = path.resolve()
    if path.is_file() and path.suffix.lower() == ".pdf":
        return "pdf", path
    if path.is_dir():
        if list(path.glob("*.pdf")):
            return "folder", path
        raise FileNotFoundError(f"文件夹内无 PDF: {path}")
    raise ValueError(f"请提交 .pdf 文件或含 PDF 的文件夹: {path}")


def _predict_slug(kind: str, path: Path) -> str:
    """根据元数据预测 slug（用于 notes 路径提示）。"""
    try:
        if kind == "pdf":
            meta = extract_metadata(path)
            return paper_slug(path.name, meta.get("title"))
        main_pdf, _ = resolve_paper_pdfs(path)
        meta = extract_metadata(main_pdf)
        return paper_slug(path.name, meta.get("title"))
    except Exception:
        return paper_slug(path.name, None)


def start_reading(
    submission: Path,
    output_root: Path | None = None,
    *,
    force_reparse: bool = False,
) -> dict:
    """
    解析文献并返回结构化信息（JSON 可打印给 AI）。
    若 output 已存在且非 force_reparse，跳过解析。
    """
    refresh_workspace_paths()
    kind, path = resolve_submission(submission)
    out_root = output_root or OUTPUT_DIR

    existing = None if force_reparse else find_existing_output_dir(out_root, path.name)

    if kind == "pdf":
        has_si = False
        if existing and (existing / "content.md").exists():
            output_dir = existing
            main_pdf = path.name
            si_pdfs: list[str] = []
        else:
            result = process_pdf(path, out_root)
            output_dir = result.output_dir
            main_pdf = path.name
            si_pdfs = []
    else:
        has_si = len(list(path.glob("*.pdf"))) > 1 or any(
            "support" in p.stem.lower() or "supplement" in p.stem.lower()
            for p in path.glob("*.pdf")
        )
        if existing and (existing / "content.md").exists():
            output_dir = existing
            main_pdf = ""
            si_pdfs = []
        else:
            result = process_paper_folder(path, out_root)
            output_dir = result.output_dir
            main_pdf = result.main.pdf_path.name
            si_pdfs = [r.pdf_path.name for r in result.supporting]

    slug = output_dir.name
    notes_dir = NOTES_DIR / slug
    predicted_slug = _predict_slug(kind, path)

    return {
        "ok": True,
        "kind": kind,
        "slug": slug,
        "predicted_slug": predicted_slug if predicted_slug != slug else None,
        "submission": str(path),
        "output_dir": str(output_dir),
        "content_md": str(output_dir / "content.md"),
        "supporting_md": str(output_dir / "supporting" / "content.md")
        if (output_dir / "supporting" / "content.md").exists()
        else None,
        "has_si": has_si or (output_dir / "supporting" / "content.md").exists(),
        "notes_dir": str(notes_dir),
        "notes_files": {
            "reading_note": str(notes_dir / "reading_note.md"),
            "translation_zh": str(notes_dir / "translation_zh.md"),
            "translation_si_zh": str(notes_dir / "translation_si_zh.md"),
            "reading_note_docx": str(notes_dir / "reading_note.docx"),
            "translation_zh_docx": str(notes_dir / "translation_zh.docx"),
            "translation_si_zh_docx": str(notes_dir / "translation_si_zh.docx"),
        },
        "export_docx_cmd": f"scripts/export_notes_docx.py {notes_dir}",
        "main_pdf": main_pdf,
        "si_pdfs": si_pdfs,
        "needs_notes": not (notes_dir / "reading_note.md").exists(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="自动识别 PDF/文件夹并解析文献（AI 零开场白入口）",
    )
    parser.add_argument("path", type=Path, help="PDF 文件或文献文件夹路径")
    parser.add_argument("-o", "--output", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--force", action="store_true", help="强制重新解析")
    args = parser.parse_args()

    try:
        info = start_reading(args.path, args.output, force_reparse=args.force)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
