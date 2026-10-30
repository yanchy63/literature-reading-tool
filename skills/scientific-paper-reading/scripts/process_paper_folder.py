#!/usr/bin/env python
"""处理含正文 + Supporting Information 的文献文件夹。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import OUTPUT_DIR
from src.pipeline import process_paper_folder


def main() -> int:
    parser = argparse.ArgumentParser(
        description="解析文献文件夹（正文 PDF + Supporting Information PDF）",
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="文献文件夹路径，如 papers/unread/Author2024_Title/",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help=f"输出根目录（默认: {OUTPUT_DIR}）",
    )
    args = parser.parse_args()

    try:
        result = process_paper_folder(args.folder, args.output)
    except Exception as exc:
        print(f"处理失败: {exc}", file=sys.stderr)
        return 1

    print(f"完成: {result.output_dir}")
    print(f"  正文: {result.main.pdf_path.name}")
    stats = result.main.manifest.get("stats", {})
    print(
        f"    Markdown {stats.get('markdown_chars', 0)} 字符 | "
        f"表 {stats.get('tables', 0)} | 图 {stats.get('images', 0)}"
    )
    if result.supporting:
        print(f"  Supporting Information: {len(result.supporting)} 个文件")
        for si in result.supporting:
            si_stats = si.manifest.get("stats", {})
            print(f"    - {si.pdf_path.name}: {si_stats.get('markdown_chars', 0)} 字符")
        print(f"  合并索引: {result.output_dir / 'supporting' / 'content.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
