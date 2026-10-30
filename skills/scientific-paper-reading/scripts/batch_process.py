#!/usr/bin/env python
"""批量处理 papers/ 目录下所有 PDF。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import OUTPUT_DIR, PAPERS_DIR
from src.pipeline import process_all


def main() -> int:
    parser = argparse.ArgumentParser(description="批量解析 papers/ 下的 PDF 文献")
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=PAPERS_DIR,
        help=f"PDF 输入目录（默认: {PAPERS_DIR}）",
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
        results = process_all(args.input, args.output)
    except Exception as exc:
        print(f"批量处理失败: {exc}", file=sys.stderr)
        return 1

    print(f"共处理 {len(results)} 篇文献:\n")
    for r in results:
        stats = r.manifest.get("stats", {})
        print(f"  {r.pdf_path.name}")
        print(f"    -> {r.output_dir}")
        print(
            f"       表格 {stats.get('tables', 0)} | "
            f"图片 {stats.get('images', 0)} | "
            f"公式 {stats.get('formulas', 0)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
