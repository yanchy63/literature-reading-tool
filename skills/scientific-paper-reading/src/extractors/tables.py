"""表格提取（pdfplumber 补充 pymupdf 版面解析）。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pdfplumber


def _table_to_markdown(rows: list[list[str | None]]) -> str:
    if not rows:
        return ""

    cleaned: list[list[str]] = []
    for row in rows:
        cleaned.append([(cell or "").replace("\n", " ").strip() for cell in row])

    if not cleaned or not any(any(c for c in row) for row in cleaned):
        return ""

    col_count = max(len(row) for row in cleaned)
    for row in cleaned:
        while len(row) < col_count:
            row.append("")

    header = cleaned[0]
    sep = ["---"] * col_count
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in cleaned[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def extract_tables(pdf_path: Path) -> list[dict[str, Any]]:
    """
    逐页提取表格，返回带页码与 Markdown 的列表。
    同一页可能有多张表，按出现顺序编号。
    """
    results: list[dict[str, Any]] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables() or []
            for table_idx, table in enumerate(tables, start=1):
                md = _table_to_markdown(table)
                if not md:
                    continue
                results.append(
                    {
                        "page": page_idx + 1,
                        "table_index": table_idx,
                        "row_count": len(table),
                        "col_count": max(len(row) for row in table) if table else 0,
                        "markdown": md,
                        "filename": f"page{page_idx + 1:03d}_table{table_idx:02d}.md",
                    }
                )
    return results
