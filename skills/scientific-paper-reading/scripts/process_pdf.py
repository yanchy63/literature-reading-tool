#!/usr/bin/env python
"""处理单篇 PDF 文献。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 将项目根目录加入 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import OUTPUT_DIR, PAPERS_UNREAD_DIR, collect_paper_pdfs
from src.pipeline import process_pdf


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将 PDF 文献解析为 AI 可读的 Markdown 与结构化附件",
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        help="PDF 文件路径（默认处理 papers/ 下第一篇）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help=f"输出根目录（默认: {OUTPUT_DIR}）",
    )
    args = parser.parse_args()

    if args.pdf is None:
        pdfs = collect_paper_pdfs()
        unread = sorted(PAPERS_UNREAD_DIR.glob("*.pdf")) if PAPERS_UNREAD_DIR.is_dir() else []
        pdfs = unread or pdfs
        if not pdfs:
            print("错误: papers/unread/ 与 papers/read/ 中无 PDF，请指定文件路径", file=sys.stderr)
            return 1
        pdf_path = pdfs[0]
        print(f"未指定文件，使用: {pdf_path.name}")
    else:
        pdf_path = args.pdf

    try:
        result = process_pdf(pdf_path, args.output)
    except Exception as exc:
        print(f"处理失败: {exc}", file=sys.stderr)
        return 1

    stats = result.manifest.get("stats", {})
    print(f"完成: {result.output_dir}")
    print(f"  Markdown 字符数: {stats.get('markdown_chars', 0)}")
    print(f"  表格: {stats.get('tables', 0)}  图片: {stats.get('images', 0)}  公式: {stats.get('formulas', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
