"""PDF 元数据提取。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pymupdf


def extract_metadata(pdf_path: Path) -> dict[str, Any]:
    """提取 PDF 元信息与基础统计。"""
    doc = pymupdf.open(pdf_path)
    try:
        meta = doc.metadata or {}
        return {
            "source_file": pdf_path.name,
            "source_path": str(pdf_path.resolve()),
            "page_count": doc.page_count,
            "title": meta.get("title") or "",
            "author": meta.get("author") or "",
            "subject": meta.get("subject") or "",
            "keywords": meta.get("keywords") or "",
            "creator": meta.get("creator") or "",
            "producer": meta.get("producer") or "",
            "creation_date": meta.get("creationDate") or "",
            "mod_date": meta.get("modDate") or "",
        }
    finally:
        doc.close()
