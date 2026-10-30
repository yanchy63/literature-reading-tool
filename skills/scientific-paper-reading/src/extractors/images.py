"""图片与图表提取。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pymupdf

from src.config import IMAGE_FORMAT, PDF_DPI


def extract_images(
    pdf_path: Path,
    output_dir: Path,
    *,
    dpi: int = PDF_DPI,
    min_width: int = 50,
    min_height: int = 50,
) -> list[dict[str, Any]]:
    """
    提取 PDF 内嵌图片及整页渲染图（便于理解复杂图表）。
    返回图片清单，含页码、尺寸与相对路径。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    manifest: list[dict[str, Any]] = []

    try:
        # 1. 内嵌位图 / 矢量图块
        img_counter = 0
        for page_idx in range(doc.page_count):
            page = doc[page_idx]
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                img_counter += 1
                try:
                    base = doc.extract_image(xref)
                    ext = base.get("ext", IMAGE_FORMAT)
                    width = base.get("width", 0)
                    height = base.get("height", 0)
                    if width < min_width or height < min_height:
                        continue
                    filename = f"embedded_p{page_idx + 1:03d}_{img_counter:03d}.{ext}"
                    filepath = output_dir / filename
                    filepath.write_bytes(base["image"])
                    manifest.append(
                        {
                            "type": "embedded",
                            "page": page_idx + 1,
                            "filename": filename,
                            "relative_path": f"images/{filename}",
                            "width": width,
                            "height": height,
                            "format": ext,
                        }
                    )
                except Exception:
                    continue

        # 2. 每页整页渲染（捕获矢量图、复杂 figure）
        zoom = dpi / 72.0
        matrix = pymupdf.Matrix(zoom, zoom)
        for page_idx in range(doc.page_count):
            page = doc[page_idx]
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            filename = f"page_render_{page_idx + 1:03d}.{IMAGE_FORMAT}"
            filepath = output_dir / filename
            pix.save(str(filepath))
            manifest.append(
                {
                    "type": "page_render",
                    "page": page_idx + 1,
                    "filename": filename,
                    "relative_path": f"images/{filename}",
                    "width": pix.width,
                    "height": pix.height,
                    "format": IMAGE_FORMAT,
                    "note": "整页渲染，用于理解版面与图表布局",
                }
            )
    finally:
        doc.close()

    return manifest
