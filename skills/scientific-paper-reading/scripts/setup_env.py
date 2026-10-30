#!/usr/bin/env python
"""
Bootstrap a portable Python environment for this skill.

Paths (in order):
  1. Bundled runtime/python (optional portable CPython)
  2. Skill-local .venv created from any host Python >= 3.10
  3. Optional: --fetch-python downloads portable CPython first

No conda required. Conda is never auto-created.

Usage:
  python scripts/setup_env.py
  python scripts/setup_env.py --fetch-python
  python scripts/setup_env.py --prefer-bundled
  py -3 scripts/setup_env.py
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

REQUIREMENTS = SKILL_ROOT / "requirements.txt"
VENV_DIR = SKILL_ROOT / ".venv"
MIN_PYTHON = (3, 10)


def _run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=check,
    )


def _venv_python() -> Path:
    if platform.system() == "Windows":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _version_ok(python: Path) -> tuple[bool, str]:
    proc = _run([str(python), "--version"])
    text = (proc.stdout or proc.stderr or "").strip()
    if proc.returncode != 0:
        return False, text
    parts = text.replace("Python", "").strip().split(".")
    try:
        major, minor = int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return False, text
    return (major, minor) >= MIN_PYTHON, text


def find_bootstrap_python(*, prefer_bundled: bool = False) -> Path:
    """Find a host Python to create the venv / install deps."""
    from src.env_detect import bundled_runtime_python

    candidates: list[Path] = []

    bundled = bundled_runtime_python()
    if prefer_bundled and bundled:
        return bundled.resolve()
    if bundled:
        candidates.append(bundled)

    if platform.system() == "Windows":
        py = shutil.which("py")
        if py:
            for flag in ("-3.12", "-3.11", "-3.10", "-3"):
                proc = _run([py, flag, "-c", "import sys; print(sys.executable)"])
                if proc.returncode == 0:
                    line = (proc.stdout or "").strip().splitlines()
                    if line:
                        candidates.append(Path(line[0].strip()))

    for name in ("python3", "python"):
        which = shutil.which(name)
        if which:
            candidates.append(Path(which))

    candidates.insert(0, Path(sys.executable))

    seen: set[str] = set()
    for cand in candidates:
        if not cand.is_file():
            continue
        key = str(cand.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        ok, _ver = _version_ok(cand)
        if ok:
            return cand.resolve()

    raise RuntimeError(
        "未找到 Python 3.10+。可选方案：\n"
        "  1) Windows:  .\\scripts\\bootstrap.ps1\n"
        "  2) macOS/Linux: bash scripts/bootstrap.sh\n"
        "  3) 若已有任意 Python: python scripts/setup_env.py --fetch-python\n"
        "  4) 或从 python.org 安装系统 Python（无需 conda）"
    )


def create_venv(host_python: Path) -> Path:
    VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
    if _venv_python().is_file():
        return _venv_python()
    print(f"[setup_env] Creating venv at {VENV_DIR} with {host_python}")
    proc = _run([str(host_python), "-m", "venv", str(VENV_DIR)])
    if proc.returncode != 0:
        raise RuntimeError(
            "创建 .venv 失败:\n"
            + (proc.stderr or proc.stdout or "")
            + "\n可改用: python scripts/setup_env.py --prefer-bundled"
            "（直接向便携 Python 装依赖）"
        )
    py = _venv_python()
    if not py.is_file():
        raise RuntimeError(f"venv 已创建但找不到解释器: {py}")
    return py


def pip_install(python: Path) -> None:
    if not REQUIREMENTS.is_file():
        raise FileNotFoundError(f"缺少 {REQUIREMENTS}")
    print(f"[setup_env] Upgrading pip with {python}")
    _run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    print(f"[setup_env] Installing {REQUIREMENTS.name}")
    proc = _run([str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)])
    if proc.returncode != 0:
        raise RuntimeError("pip install 失败:\n" + (proc.stderr or proc.stdout or ""))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create skill env: bundled runtime and/or .venv (no conda)"
    )
    parser.add_argument("--reinstall", action="store_true", help="Force pip reinstall")
    parser.add_argument(
        "--use-host",
        action="store_true",
        help="Install into the current interpreter instead of .venv",
    )
    parser.add_argument(
        "--prefer-bundled",
        action="store_true",
        help="Install deps into runtime/python directly (skip creating .venv)",
    )
    parser.add_argument(
        "--fetch-python",
        action="store_true",
        help="Download portable CPython into runtime/python first",
    )
    args = parser.parse_args()

    try:
        from src.env_detect import (
            bundled_runtime_python,
            detect_environment,
            save_cache,
        )

        if args.fetch_python:
            print("[setup_env] Fetching portable Python into runtime/python ...")
            fetch_script = SKILL_ROOT / "scripts" / "fetch_portable_python.py"
            cmd = [str(Path(sys.executable)), str(fetch_script)]
            if bundled_runtime_python() is not None:
                cmd.append("--force")
            proc = _run(cmd)
            print(proc.stdout or "")
            if proc.returncode != 0:
                raise RuntimeError(
                    "自动下载便携 Python 失败。请改用无 Python 引导脚本：\n"
                    "  Windows: .\\scripts\\bootstrap.ps1\n"
                    "  Unix:    bash scripts/bootstrap.sh\n"
                    f"详情: {proc.stderr or proc.stdout}"
                )

        existing = detect_environment()
        if existing.get("ready") and not args.reinstall and not args.use_host:
            save_cache(existing)
            print(json.dumps({
                "ok": True,
                "action": "use_existing",
                "message": "环境已就绪，无需重建",
                **{k: existing[k] for k in (
                    "recommended_python",
                    "recommended_version",
                    "recommended_source",
                    "skill_root",
                    "venv_path",
                    "bundled_runtime_path",
                ) if k in existing},
            }, ensure_ascii=False, indent=2))
            return 0

        if args.use_host:
            python = Path(sys.executable).resolve()
            ok, ver = _version_ok(python)
            if not ok:
                raise RuntimeError(f"当前解释器版本不足: {ver}")
        elif args.prefer_bundled:
            host = find_bootstrap_python(prefer_bundled=True)
            python = host
            ok, ver = _version_ok(python)
            if not ok:
                raise RuntimeError(f"便携解释器版本不足: {ver}")
        else:
            host = find_bootstrap_python(prefer_bundled=bool(bundled_runtime_python()))
            # Prefer creating .venv from host; if venv module missing, fall back to host
            try:
                python = create_venv(host)
            except RuntimeError:
                print("[setup_env] venv 不可用，改为向宿主解释器安装依赖")
                python = host
            ok, ver = _version_ok(python)
            if not ok:
                raise RuntimeError(f"解释器版本不足: {ver}")

        need_install = args.reinstall or args.use_host or args.prefer_bundled
        if not need_install:
            probe = _run([
                str(python),
                "-c",
                "import pymupdf, pymupdf4llm, pdfplumber, ddgs, docx; print('OK')",
            ])
            need_install = probe.returncode != 0

        if need_install:
            pip_install(python)

        os.environ.setdefault("PYTHONPATH", str(SKILL_ROOT))
        result = detect_environment()
        if result.get("ready"):
            save_cache(result)
        print(json.dumps({
            "ok": bool(result.get("ready")),
            "action": "setup_complete",
            "venv_python": str(python),
            "recommended_python": result.get("recommended_python") or str(python),
            "recommended_version": result.get("recommended_version"),
            "recommended_source": result.get("recommended_source") or "skill_venv",
            "skill_root": str(SKILL_ROOT),
            "bundled_runtime_path": result.get("bundled_runtime_path"),
            "hint": "之后请始终用 recommended_python 运行 scripts/*.py",
        }, ensure_ascii=False, indent=2))
        return 0 if result.get("ready") else 1

    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
