"""公式检测与提取。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pymupdf

from src.config import (
    FORMULA_MAX_HEIGHT,
    FORMULA_MAX_WIDTH,
    FORMULA_MIN_HEIGHT,
    FORMULA_MIN_WIDTH,
    IMAGE_FORMAT,
    PDF_DPI,
)

# Unicode 数学符号与常见 LaTeX 片段
MATH_UNICODE_RE = re.compile(
    r"[\u2200-\u22FF\u27C0-\u27EF\u2980-\u29FF\u2A00-\u2AFF"
    r"\u2100-\u214F\u0300-\u036F\u2070-\u209F\u00B1\u00D7\u00F7"
    r"\u2264\u2265\u2260\u2248\u221E\u2211\u222B\u2202\u2207]+"
)
MATH_LATEX_RE = re.compile(
    r"(\\(?:frac|sum|int|partial|nabla|alpha|beta|gamma|delta|epsilon|"
    r"theta|lambda|mu|sigma|pi|omega|sqrt|left|right|cdot|times|leq|geq|"
    r"neq|approx|infty|mathrm|mathbf|vec)\b|[\^_]\{[^}]+\})"
)


def _looks_like_formula(text: str) -> bool:
    text = text.strip()
    if len(text) < 2:
        return False
    if MATH_UNICODE_RE.search(text):
        return True
    if MATH_LATEX_RE.search(text):
        return True
    # 行内公式常见模式：含等号且较短、或上下标
    if "=" in text and len(text) < 200 and re.search(r"[a-zA-Z0-9]", text):
        math_chars = sum(1 for c in text if c in "=+-*/^_∑∫∂∇√")
        if math_chars >= 2:
            return True
    return False


def _is_formula_image_bbox(width: float, height: float) -> bool:
    """根据尺寸判断是否为行内/独立公式图片区域。"""
    if width < FORMULA_MIN_WIDTH or height < FORMULA_MIN_HEIGHT:
        return False
    if width > FORMULA_MAX_WIDTH or height > FORMULA_MAX_HEIGHT:
        return False
    aspect = width / max(height, 1)
    return 0.5 <= aspect <= 20


def extract_formulas(
    pdf_path: Path,
    output_dir: Path,
    *,
    dpi: int = PDF_DPI,
) -> list[dict[str, Any]]:
    """
    提取公式：
    1. 从文本块中识别含数学符号的段落；
    2. 裁剪疑似公式的小图区域保存供后续 OCR / 视觉理解。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    formulas: list[dict[str, Any]] = []
    formula_idx = 0

    try:
        zoom = dpi / 72.0
        matrix = pymupdf.Matrix(zoom, zoom)

        for page_idx in range(doc.page_count):
            page = doc[page_idx]

            # 文本层公式
            blocks = page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)["blocks"]
            for block in blocks:
                if block.get("type") != 0:
                    continue
                lines_text: list[str] = []
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    line_text = "".join(s.get("text", "") for s in spans)
                    lines_text.append(line_text)
                full_text = "\n".join(lines_text).strip()
                if _looks_like_formula(full_text):
                    formula_idx += 1
                    formulas.append(
                        {
                            "id": f"formula_{formula_idx:04d}",
                            "page": page_idx + 1,
                            "source": "text",
                            "content": full_text,
                            "bbox": block.get("bbox"),
                        }
                    )

            # 图片层：小尺寸横向块视为公式图
            for block in blocks:
                if block.get("type") != 1:
                    continue
                bbox = block.get("bbox")
                if not bbox:
                    continue
                x0, y0, x1, y1 = bbox
                w, h = x1 - x0, y1 - y0
                if not _is_formula_image_bbox(w, h):
                    continue
                formula_idx += 1
                rect = pymupdf.Rect(bbox)
                pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
                filename = f"formula_p{page_idx + 1:03d}_{formula_idx:04d}.{IMAGE_FORMAT}"
                filepath = output_dir / filename
                pix.save(str(filepath))
                formulas.append(
                    {
                        "id": f"formula_{formula_idx:04d}",
                        "page": page_idx + 1,
                        "source": "image_crop",
                        "content": "",
                        "bbox": list(bbox),
                        "image": f"formulas/{filename}",
                        "note": "公式区域截图，可结合视觉模型解读",
                    }
                )
    finally:
        doc.close()

    return formulas
