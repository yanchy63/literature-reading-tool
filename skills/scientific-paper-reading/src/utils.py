"""路径与命名工具。"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

# 明显为文献 ID / DOI 片段的文件名（无可读标题）
_OPAQUE_PATTERNS = (
    re.compile(r"^s\d{5}-\d{5}-\d$"),  # Nature: s42256-026-01229-5
    re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$"),  # arXiv: 2301.12345
    re.compile(r"^10\.\d{4,}/"),  # DOI 作文件名
    re.compile(r"^[a-f0-9]{32}$"),  # MD5
)


_KNOWN_FILE_EXTENSIONS = {".pdf", ".md", ".txt", ".json", ".doc", ".docx"}


def slugify(name: str, max_len: int = 80) -> str:
    """将文件名或标题转为安全目录名（字母数字、下划线、连字符）。"""
    p = Path(name)
    stem = p.stem if p.suffix.lower() in _KNOWN_FILE_EXTENSIONS else name
    slug = re.sub(r"[^\w\s\-]", "", stem, flags=re.UNICODE)
    slug = re.sub(r"\s+", "_", slug.strip())
    slug = re.sub(r"_+", "_", slug).strip("_")
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("_")
    if not slug:
        slug = hashlib.md5(name.encode()).hexdigest()[:12]
    return slug


def normalize_title(title: str | None) -> str:
    """清洗 PDF 元数据标题，过滤无效占位。"""
    if not title:
        return ""
    t = title.strip()
    if len(t) < 5:
        return ""
    lower = t.lower()
    if lower.startswith("microsoft word") or lower in {"untitled", "无标题"}:
        return ""
    return t


def is_opaque_identifier(stem: str) -> bool:
    """
    判断文件名是否仅为编码/ID（如 s42256-026-01229-5），
    而非已含可读论文信息的描述性名称。
    """
    s = Path(stem).stem
    if any(p.match(s) for p in _OPAQUE_PATTERNS):
        return True
    if len(s) > 35:
        return False
    if not re.fullmatch(r"[\w\-]+", s):
        return False
    parts = [p for p in re.split(r"[-_]", s) if p]
    if not parts:
        return True
    long_words = [p for p in parts if len(p) >= 5 and p.isalpha()]
    if long_words:
        return False
    return all(len(p) <= 8 for p in parts)


def paper_slug(
    source_name: str,
    title: str | None = None,
    *,
    max_len: int = 100,
) -> str:
    """
    生成 output/notes 目录 slug。

    - 描述性文件名（如 Liu_等_-_Bright_...）：沿用文件名 slug
    - 编码型文件名（如 s42256-026-01229-5）：``{编码}_{论文标题slug}``
    """
    file_stem = Path(source_name).stem
    file_slug = slugify(file_stem, max_len=40)
    clean_title = normalize_title(title)

    if not clean_title or not is_opaque_identifier(file_stem):
        return file_slug

    title_slug = slugify(clean_title, max_len=55)
    if not title_slug or title_slug == file_slug:
        return file_slug

    combined = f"{file_slug}_{title_slug}"
    if len(combined) > max_len:
        combined = combined[:max_len].rstrip("_")
    return combined


def find_existing_output_dir(output_root: Path, source_name: str) -> Path | None:
    """
    按源 PDF/文件夹名查找已解析的 output 目录。
    兼容旧版纯编码 slug 与新版 ``编码_标题`` slug。
    """
    if not output_root.is_dir():
        return None

    file_stem_slug = slugify(Path(source_name).stem)
    candidates: list[Path] = []
    for d in output_root.iterdir():
        if not d.is_dir() or not (d / "content.md").is_file():
            continue
        if d.name == file_stem_slug or d.name.startswith(f"{file_stem_slug}_"):
            candidates.append(d)

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    return max(candidates, key=lambda p: p.stat().st_mtime)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
