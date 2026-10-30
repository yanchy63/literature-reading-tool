#!/usr/bin/env python
"""
检查译文中「疑似漏译」的普通英文词（辅助参考，非唯一标准）。

最终质量以 AI 通读原文+译文后的审校为准，见 docs/CHINESE_STYLE.md。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 应译成中文的普通英文词/短语（参考列表，非穷举；审校时结合全文判断）
TRANSLATABLE_WORDS = {
    "challenging", "entire", "arbitrary", "understudied", "dramatically",
    "largely", "alone", "similar", "similarly", "however", "trivial",
    "performance", "training", "inference", "sampling", "learning",
    "embedding", "decoder", "encoder", "constraint", "interpolation",
    "reconstruction", "validity", "smooth", "smoothness", "random",
    "canonical", "baseline", "filter", "quality", "valid",
    "whole", "only", "also", "approach", "method", "results",
    "experiments", "introduction", "abstract", "discussion", "conclusion",
    "figure", "table", "data", "model", "network", "graph", "loss",
    "prior",
}

TRANSLATABLE_PHRASES = [
    "off-the-shelf",
    "out-of-the-box",
    "non-trivial",
    "non trivial",
]

ALLOW_LINE_PATTERNS = [
    re.compile(r"^\s*>"),
    re.compile(r"^\s*\|"),
    re.compile(r"https?://"),
    re.compile(r"et al\."),
    re.compile(r"术语对照表|原文标题|English Title"),
    re.compile(r"^#+ "),  # 标题行允许（Introduction）对照
]

# 行内纯英文括号：专业术语，不报警
TERM_PAREN_OK = re.compile(
    r"[（(]"
    r"(?:motif|scaffold|GNN|VAE|MLP|SMILES|BFS|FCD|MSO|MLP|"
    r"Graph Neural Network[^）)]*|"
    r"acyclic bond|multi-hot|in silico|frontier|"
    r"Molecule-Level Representation[^）)]*|"
    r"Introduction|Abstract|Methods|Results|Discussion|"
    r"Data Representation|Our Approach|Training MoLeR|"
    r"Quantitative Results|Qualitative Results|"
    r"Molecule Generation Orders|The MoLeR Decoder|"
    r"Experiments|Appendix)[^）)]*"
    r"[）)]",
    re.I,
)


def _allowed_line(line: str) -> bool:
    return any(p.search(line) for p in ALLOW_LINE_PATTERNS)


def _strip_term_parens(line: str) -> str:
    """去掉已知专业术语括号后再查普通英文词。"""
    return TERM_PAREN_OK.sub("", line)


def check_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    issues: list[dict] = []

    for i, line in enumerate(text.splitlines(), start=1):
        if _allowed_line(line):
            continue
        stripped = line.strip()
        if not stripped:
            continue

        check_line = _strip_term_parens(stripped)
        lower = check_line.lower()

        for phrase in TRANSLATABLE_PHRASES:
            if phrase in lower:
                issues.append(
                    {
                        "line": i,
                        "type": "untranslated_phrase",
                        "word": phrase,
                        "text": stripped[:120],
                        "hint": f"短语「{phrase}」应译为中文",
                    }
                )
                break

        for word in TRANSLATABLE_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", lower):
                issues.append(
                    {
                        "line": i,
                        "type": "untranslated_word",
                        "word": word,
                        "text": stripped[:120],
                        "hint": f"疑似漏译的普通词「{word}」（请结合全文语境判断；专业术语括号已排除）",
                    }
                )
                break

        # 句中孤立英文单词（3+ 字母，非括号内，非常见专名）
        for m in re.finditer(r"(?<![（(/\w])\b([A-Za-z]{4,})\b(?![）)/\w])", check_line):
            word = m.group(1)
            wl = word.lower()
            if wl in TRANSLATABLE_WORDS or wl in {
                w.replace("-", " ") for w in TRANSLATABLE_PHRASES
            }:
                continue  # 已在上面报告
            # 白名单：专名、缩写、函数名
            if word.isupper() and len(word) <= 6:
                continue
            if word in (
                "MoLeR", "RDKit", "GuacaMol", "Softmax", "Sigmoid",
                "PickAtomOrMotif", "PickAttachment", "PickBond",
                "ValidFirstAtoms", "ValidNextAtoms", "END_GEN", "END_BONDS",
                "Kingma", "Welling", "Brockschmidt", "Schneider",
                "Gómez", "Bombarelli", "Winter", "Segler", "Brown",
                "Preuer", "Fréchet", "ChemNet", "HierVAE", "CGVAE",
                "PubChem", "CDDD", "Lim", "Langevin", "Arús", "Pous",
                "Schuffenhauer", "Rarey", "Dixon", "Ståhl", "Bradshaw",
                "Simonovsky", "Komodakis", "Assouel", "Kipf", "Pocha",
                "Landrum", "Muenkler", "Renz", "Bowman", "GIN", "GCN",
            ):
                continue
            issues.append(
                {
                    "line": i,
                    "type": "bare_english_word",
                    "word": word,
                    "text": stripped[:120],
                    "hint": f"检查「{word}」是否应译为中文",
                }
            )
            break

    return {
        "file": str(path),
        "issue_count": len(issues),
        "issues": issues[:60],
        "truncated": len(issues) > 60,
        "note": "仅供参考；请以通读全文后的审校为准，不标记专业术语括号",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="辅助检查译文疑似漏译的普通英文词（非唯一标准）")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    results = [check_file(p) for p in args.files]
    total = sum(r["issue_count"] for r in results)
    print(json.dumps({"total_issues": total, "files": results}, ensure_ascii=False, indent=2))
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
