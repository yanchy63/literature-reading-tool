"""文本与版面结构提取（Markdown + JSON）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pymupdf
import pymupdf4llm

from src.config import IMAGE_FORMAT, OCR_LANGUAGE, PDF_DPI


def extract_markdown(
    pdf_path: Path,
    image_dir: Path,
    *,
    dpi: int = PDF_DPI,
    use_ocr: bool = True,
) -> str:
    """
    将 PDF 转为 LLM 友好的 Markdown。
    图片写入 image_dir，正文中保留相对路径引用。
    """
    image_dir.mkdir(parents=True, exist_ok=True)
    return pymupdf4llm.to_markdown(
        str(pdf_path),
        dpi=dpi,
        write_images=True,
        image_path=str(image_dir),
        image_format=IMAGE_FORMAT,
        page_separators=True,
        use_ocr=use_ocr,
        ocr_language=OCR_LANGUAGE,
        show_progress=False,
    )


def extract_structured_json(
    pdf_path: Path,
    image_dir: Path | None = None,
    *,
    dpi: int = PDF_DPI,
    use_ocr: bool = True,
) -> dict[str, Any]:
    """
    提取带版面信息的结构化 JSON（段落、表格、图片块等）。
    """
    kwargs: dict[str, Any] = {
        "image_dpi": dpi,
        "write_images": image_dir is not None,
        "image_format": IMAGE_FORMAT,
        "use_ocr": use_ocr,
        "ocr_language": OCR_LANGUAGE,
        "show_progress": False,
    }
    if image_dir is not None:
        image_dir.mkdir(parents=True, exist_ok=True)
        kwargs["image_path"] = str(image_dir)

    doc = pymupdf.open(pdf_path)
    try:
        raw = pymupdf4llm.to_json(doc, **kwargs)
    finally:
        doc.close()

    if isinstance(raw, str):
        return json.loads(raw)
    return raw
