"""文献文件夹（正文 + Supporting Information）识别与处理。"""

from __future__ import annotations

from pathlib import Path

from src.config import MAIN_PDF_KEYWORDS, SI_PDF_KEYWORDS


def _normalize_stem(path: Path) -> str:
    return path.stem.lower().replace("-", "_").replace(" ", "_")


def classify_pdf(path: Path) -> str:
    """
    将文件夹内 PDF 分类为 main / supporting / unknown。
    """
    stem = _normalize_stem(path)
    if stem in MAIN_PDF_KEYWORDS or any(stem.startswith(k) for k in MAIN_PDF_KEYWORDS):
        return "main"
    if any(k in stem for k in SI_PDF_KEYWORDS):
        return "supporting"
    return "unknown"


def resolve_paper_pdfs(folder: Path) -> tuple[Path, list[Path]]:
    """
    从文献文件夹中确定正文 PDF 与 Supporting Information PDF 列表。

    命名约定（推荐）：
    - 正文：main.pdf / paper.pdf
    - 补充材料：supporting_information.pdf / SI.pdf / supplementary.pdf

    若无法从文件名判断且有多份 PDF，则**体积最大者**视为正文，其余为 SI。
    """
    folder = folder.resolve()
    pdfs = sorted(folder.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"文件夹内无 PDF: {folder}")

    mains = [p for p in pdfs if classify_pdf(p) == "main"]
    supporting = [p for p in pdfs if classify_pdf(p) == "supporting"]
    unknown = [p for p in pdfs if classify_pdf(p) == "unknown"]

    if len(mains) == 1:
        return mains[0], supporting + unknown

    if len(mains) > 1:
        names = ", ".join(p.name for p in mains)
        raise ValueError(f"文件夹 {folder.name} 含多个正文候选，请保留唯一 main.pdf：{names}")

    if len(pdfs) == 1:
        return pdfs[0], []

    # 有明确 SI 文件名时，其余 PDF 均视为正文（不受体积影响）
    if supporting:
        non_si = [p for p in pdfs if p not in supporting]
        if len(non_si) == 1:
            return non_si[0], supporting
        if len(non_si) > 1:
            by_size = sorted(non_si, key=lambda p: p.stat().st_size, reverse=True)
            return by_size[0], supporting + by_size[1:]

    # 全部 unknown：体积最大者为正文
    by_size = sorted(pdfs, key=lambda p: p.stat().st_size, reverse=True)
    return by_size[0], by_size[1:]
