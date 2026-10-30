"""Skill package paths and parsing defaults.

SKILL_ROOT: this package (scripts / src / .venv live here).
WORKSPACE_ROOT: where papers/, output/, notes/ are written — usually the
agent's current working directory, overridable via PAPER_READING_WORKSPACE.
"""

from __future__ import annotations

import os
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent


def get_workspace_root() -> Path:
    """Resolve the user project directory for papers/output/notes."""
    override = os.environ.get("PAPER_READING_WORKSPACE", "").strip()
    if override:
        return Path(override).expanduser().resolve()

    cwd = Path.cwd().resolve()
    # Prefer cwd when it already looks like a literature workspace
    markers = ("papers", "output", "notes")
    if any((cwd / name).is_dir() for name in markers):
        return cwd
    # If the agent is running inside the skill package, still use cwd so
    # data does not pollute the skill install — callers should set cwd or env.
    if cwd == SKILL_ROOT or SKILL_ROOT in cwd.parents:
        return cwd
    return cwd


# Back-compat alias used by older scripts
PROJECT_ROOT = SKILL_ROOT

WORKSPACE_ROOT = get_workspace_root()

PAPERS_DIR = WORKSPACE_ROOT / "papers"
PAPERS_UNREAD_DIR = PAPERS_DIR / "unread"
PAPERS_READ_DIR = PAPERS_DIR / "read"
OUTPUT_DIR = WORKSPACE_ROOT / "output"
NOTES_DIR = WORKSPACE_ROOT / "notes"

PDF_DPI = 150
IMAGE_FORMAT = "png"
OCR_LANGUAGE = "eng"

FORMULA_MAX_WIDTH = 800
FORMULA_MAX_HEIGHT = 120
FORMULA_MIN_WIDTH = 20
FORMULA_MIN_HEIGHT = 8

SEARCH_CACHE_DIR = WORKSPACE_ROOT / ".cache" / "web_search"
SEARCH_CACHE_TTL_HOURS = 72

MAIN_PDF_KEYWORDS = ("main", "paper", "article", "manuscript", "正文")
SI_PDF_KEYWORDS = (
    "support",
    "supporting",
    "supplementary",
    "supplement",
    "si",
    "esm",
    "esi",
    "appendix",
    "补充",
)


def refresh_workspace_paths() -> None:
    """Recompute workspace paths after cwd / env changes (rare)."""
    global WORKSPACE_ROOT, PAPERS_DIR, PAPERS_UNREAD_DIR, PAPERS_READ_DIR
    global OUTPUT_DIR, NOTES_DIR, SEARCH_CACHE_DIR
    WORKSPACE_ROOT = get_workspace_root()
    PAPERS_DIR = WORKSPACE_ROOT / "papers"
    PAPERS_UNREAD_DIR = PAPERS_DIR / "unread"
    PAPERS_READ_DIR = PAPERS_DIR / "read"
    OUTPUT_DIR = WORKSPACE_ROOT / "output"
    NOTES_DIR = WORKSPACE_ROOT / "notes"
    SEARCH_CACHE_DIR = WORKSPACE_ROOT / ".cache" / "web_search"


def collect_paper_pdfs(root: Path | None = None) -> list[Path]:
    """Collect PDFs under papers/ (unread + read) or a flat root."""
    root = root or PAPERS_DIR
    if (root / "unread").is_dir() or (root / "read").is_dir():
        pdfs: list[Path] = []
        for name in ("unread", "read"):
            sub = root / name
            if sub.is_dir():
                pdfs.extend(sorted(sub.glob("*.pdf")))
        return pdfs
    return sorted(root.glob("*.pdf"))


def collect_paper_folders(root: Path | None = None) -> list[Path]:
    """Collect folders that contain PDFs (main + optional SI)."""
    root = root or PAPERS_DIR
    folders: list[Path] = []
    for base_name in ("unread", "read"):
        base = root / base_name
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir() and list(child.glob("*.pdf")):
                folders.append(child)
    return folders
