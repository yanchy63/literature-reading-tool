#!/usr/bin/env python
"""
将 notes/<slug>/ 下的阅读笔记与译文 Markdown 导出为 Word (.docx)。

默认转换：
  reading_note.md      → reading_note.docx
  translation_zh.md    → translation_zh.docx
  translation_si_zh.md → translation_si_zh.docx（若存在）

用法：
  python scripts/export_notes_docx.py notes/<slug>
  python scripts/export_notes_docx.py notes/<slug>/reading_note.md
  python scripts/export_notes_docx.py --all-notes
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import config as cfg
from src.config import refresh_workspace_paths
from src.md_to_docx import NOTE_BASENAMES, convert_md_file, export_notes_dir


def _resolve_notes_dir(path: Path) -> Path:
    refresh_workspace_paths()
    path = path.resolve()
    if path.is_file() and path.suffix.lower() == ".md":
        return path.parent
    if path.is_dir():
        return path
    # Treat as slug under notes/
    candidate = cfg.NOTES_DIR / path.name
    if candidate.is_dir():
        return candidate
    raise FileNotFoundError(f"无法解析笔记目录: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="导出阅读笔记/译文为 Word (.docx)")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="notes/<slug> 目录、某 .md 文件，或 slug 名",
    )
    parser.add_argument(
        "--all-notes",
        action="store_true",
        help="批量转换 notes/ 下所有含 Markdown 的子目录",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="若 docx 已存在则跳过",
    )
    args = parser.parse_args()

    try:
        refresh_workspace_paths()
        if args.all_notes:
            if not cfg.NOTES_DIR.is_dir():
                raise FileNotFoundError(f"notes 目录不存在: {cfg.NOTES_DIR}")
            batch: dict[str, dict[str, str | None]] = {}
            for child in sorted(cfg.NOTES_DIR.iterdir()):
                if not child.is_dir():
                    continue
                if not any((child / f"{n}.md").is_file() for n in NOTE_BASENAMES):
                    continue
                batch[child.name] = export_notes_dir(
                    child, overwrite=not args.no_overwrite
                )
            print(json.dumps({"ok": True, "exported": batch}, ensure_ascii=False, indent=2))
            return 0

        if args.path is None:
            parser.error("请提供 notes 目录/文件，或使用 --all-notes")

        path = args.path.resolve()
        # Single md file → only that file
        if path.is_file() and path.suffix.lower() == ".md":
            out = convert_md_file(path)
            print(json.dumps({
                "ok": True,
                "source": str(path),
                "docx": str(out),
            }, ensure_ascii=False, indent=2))
            return 0

        notes_dir = _resolve_notes_dir(args.path)
        results = export_notes_dir(notes_dir, overwrite=not args.no_overwrite)
        print(json.dumps({
            "ok": True,
            "notes_dir": str(notes_dir),
            "docx": results,
        }, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
