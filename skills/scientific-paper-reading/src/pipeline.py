"""PDF 文献处理主流水线。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import OUTPUT_DIR, PAPERS_DIR, collect_paper_pdfs
from src.extractors import (
    extract_formulas,
    extract_images,
    extract_metadata,
    extract_markdown,
    extract_structured_json,
    extract_tables,
)
from src.utils import ensure_dir, paper_slug, slugify


@dataclass
class ProcessResult:
    pdf_path: Path
    output_dir: Path
    manifest: dict[str, Any] = field(default_factory=dict)


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _normalize_image_paths(markdown: str) -> str:
    """将 Markdown 中的图片路径统一为相对路径 images/<filename>。"""

    def repl(match: re.Match[str]) -> str:
        raw = match.group(1)
        filename = Path(raw).name
        return f"![](images/{filename})"

    return re.sub(r"!\[\]\(([^)]+)\)", repl, markdown)


def process_pdf(
    pdf_path: Path,
    output_root: Path | None = None,
    *,
    output_dir: Path | None = None,
) -> ProcessResult:
    """
    处理单篇 PDF，生成 AI 可读的 Markdown 与结构化附件。

    output_dir 若指定，则直接写入该目录（用于文献文件夹内的 SI 分册）。
    """
    pdf_path = pdf_path.resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 不存在: {pdf_path}")

    out_root = output_root or OUTPUT_DIR

    if output_dir is None:
        metadata = extract_metadata(pdf_path)
        dir_name = paper_slug(pdf_path.name, metadata.get("title"))
        paper_dir = ensure_dir(out_root / dir_name)
    else:
        paper_dir = ensure_dir(output_dir)
        metadata = extract_metadata(pdf_path)

    images_dir = ensure_dir(paper_dir / "images")
    tables_dir = ensure_dir(paper_dir / "tables")
    formulas_dir = ensure_dir(paper_dir / "formulas")

    markdown = _normalize_image_paths(extract_markdown(pdf_path, images_dir))
    structured = extract_structured_json(pdf_path, images_dir)
    tables = extract_tables(pdf_path)
    images = extract_images(pdf_path, images_dir)
    formulas = extract_formulas(pdf_path, formulas_dir)

    # 写入主 Markdown
    _write_text(paper_dir / "content.md", markdown)

    # 写入结构化 JSON
    _write_json(paper_dir / "structured.json", structured)

    # 写入独立表格
    for table in tables:
        table_path = tables_dir / table["filename"]
        header = f"<!-- Page {table['page']}, Table {table['table_index']} -->\n\n"
        _write_text(table_path, header + table["markdown"])

    # 写入公式索引
    if formulas:
        _write_json(formulas_dir / "index.json", formulas)

    manifest: dict[str, Any] = {
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "slug": paper_dir.name,
        "source_file": pdf_path.name,
        "metadata": metadata,
        "output": {
            "content_md": "content.md",
            "structured_json": "structured.json",
            "images_dir": "images/",
            "tables_dir": "tables/",
            "formulas_dir": "formulas/",
        },
        "stats": {
            "tables": len(tables),
            "images": len(images),
            "formulas": len(formulas),
            "markdown_chars": len(markdown),
        },
        "tables": [
            {
                "page": t["page"],
                "table_index": t["table_index"],
                "file": f"tables/{t['filename']}",
            }
            for t in tables
        ],
        "images": images,
        "formulas_preview": formulas[:20],
    }
    _write_json(paper_dir / "manifest.json", manifest)

    return ProcessResult(pdf_path=pdf_path, output_dir=paper_dir, manifest=manifest)


@dataclass
class PaperFolderResult:
    folder_path: Path
    output_dir: Path
    main: ProcessResult
    supporting: list[ProcessResult]
    manifest: dict[str, Any] = field(default_factory=dict)


def _merge_supporting_content(paper_dir: Path, supporting: list[ProcessResult]) -> Path:
    """合并各 SI 分册 content.md 为 supporting/content.md，修正图片相对路径。"""
    supporting_dir = ensure_dir(paper_dir / "supporting")
    parts: list[str] = [
        "# Supporting Information（合并索引）\n",
        "> 各分册原文见 supporting/<分册名>/content.md\n",
    ]
    index: list[dict[str, str]] = []

    for result in supporting:
        rel_part = result.output_dir.relative_to(paper_dir).as_posix()
        part_content_path = result.output_dir / "content.md"
        if not part_content_path.exists():
            continue
        body = part_content_path.read_text(encoding="utf-8")
        # 图片路径：images/ -> supporting/<part>/images/
        body = body.replace("](images/", f"]({rel_part}/images/")
        parts.append(f"\n\n---\n\n## 分册：{result.pdf_path.name}\n\n")
        parts.append(f"<!-- 源文件: {result.pdf_path.name} -->\n\n")
        parts.append(body)
        index.append(
            {
                "filename": result.pdf_path.name,
                "content": f"{rel_part}/content.md",
                "manifest": f"{rel_part}/manifest.json",
            }
        )

    merged_path = supporting_dir / "content.md"
    _write_text(merged_path, "".join(parts))
    _write_json(supporting_dir / "index.json", index)
    return merged_path


def process_paper_folder(
    folder_path: Path,
    output_root: Path | None = None,
) -> PaperFolderResult:
    """
    处理「正文 + Supporting Information」文献文件夹。

    输出结构::
        output/<folder_slug>/
            content.md              # 正文
            manifest.json           # 含 supporting 索引
            supporting/
                content.md          # 全部 SI 合并（便于 AI 阅读）
                index.json
                <si_slug>/          # 各 SI 分册完整解析结果
                    content.md
                    images/ ...
    """
    from src.paper_folder import resolve_paper_pdfs

    folder_path = folder_path.resolve()
    if not folder_path.is_dir():
        raise NotADirectoryError(f"不是文件夹: {folder_path}")

    main_pdf, si_pdfs = resolve_paper_pdfs(folder_path)
    out_root = output_root or OUTPUT_DIR
    main_meta = extract_metadata(main_pdf)
    dir_name = paper_slug(folder_path.name, main_meta.get("title"))
    paper_dir = ensure_dir(out_root / dir_name)

    main_result = process_pdf(
        main_pdf,
        out_root,
        output_dir=paper_dir,
    )

    si_results: list[ProcessResult] = []
    for si_pdf in si_pdfs:
        si_dir = ensure_dir(paper_dir / "supporting" / slugify(si_pdf.stem))
        si_results.append(
            process_pdf(si_pdf, out_root, output_dir=si_dir)
        )

    merged_si: Path | None = None
    if si_results:
        merged_si = _merge_supporting_content(paper_dir, si_results)

    folder_manifest: dict[str, Any] = {
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "slug": paper_dir.name,
        "type": "paper_folder",
        "source_folder": str(folder_path),
        "main_pdf": main_pdf.name,
        "supporting_pdfs": [p.name for p in si_pdfs],
        "output_dir": str(paper_dir),
        "main": {
            "content": "content.md",
            "manifest_detail": main_result.manifest,
        },
        "supporting": {
            "merged_content": "supporting/content.md" if merged_si else None,
            "index": "supporting/index.json" if si_results else None,
            "parts": [
                {
                    "filename": r.pdf_path.name,
                    "dir": r.output_dir.relative_to(paper_dir).as_posix(),
                    "manifest_detail": r.manifest,
                }
                for r in si_results
            ],
        },
    }
    _write_json(paper_dir / "manifest.json", folder_manifest)

    return PaperFolderResult(
        folder_path=folder_path,
        output_dir=paper_dir,
        main=main_result,
        supporting=si_results,
        manifest=folder_manifest,
    )


def process_all(
    papers_dir: Path | None = None,
    output_root: Path | None = None,
) -> list[ProcessResult]:
    """批量处理 papers 目录下所有 PDF（含 unread/ 与 read/）。"""
    root = papers_dir or PAPERS_DIR
    pdfs = collect_paper_pdfs(root)
    if not pdfs:
        raise FileNotFoundError(f"未在 {root}（含 unread/、read/）找到 PDF 文件")

    results: list[ProcessResult] = []
    for pdf in pdfs:
        results.append(process_pdf(pdf, output_root))
    return results
