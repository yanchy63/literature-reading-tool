#!/usr/bin/env python
"""
Download a portable CPython into skill runtime/python/ (python-build-standalone).

Does not require conda. Safe to re-run; use --force to replace.

Examples:
  python scripts/fetch_portable_python.py
  python scripts/fetch_portable_python.py --version 3.12
  py -3 scripts/fetch_portable_python.py --force
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = SKILL_ROOT / "runtime"
PYTHON_DIR = RUNTIME_DIR / "python"
META_PATH = RUNTIME_DIR / "python_version.json"

# Pinned fallback if latest-release.json is unreachable
DEFAULT_RELEASE = "20250808"
DEFAULT_VERSION = "3.12.11"
LATEST_META_URL = (
    "https://raw.githubusercontent.com/astral-sh/python-build-standalone/"
    "latest-release/latest-release.json"
)
RELEASE_BASE = "https://github.com/astral-sh/python-build-standalone/releases/download"


def _detect_target() -> str:
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Windows":
        if machine in ("arm64", "aarch64"):
            return "aarch64-pc-windows-msvc"
        return "x86_64-pc-windows-msvc"
    if system == "Darwin":
        if machine in ("arm64", "aarch64"):
            return "aarch64-apple-darwin"
        return "x86_64-apple-darwin"
    # Linux
    if machine in ("arm64", "aarch64"):
        return "aarch64-unknown-linux-gnu"
    return "x86_64-unknown-linux-gnu"


def _normalize_version(req: str) -> str:
    """'3.12' -> prefer DEFAULT_VERSION if same minor; else req as-is if full."""
    req = req.strip()
    parts = req.split(".")
    if len(parts) >= 3:
        return req
    if req.startswith("3.12"):
        return DEFAULT_VERSION
    if req.startswith("3.11"):
        return "3.11.13"
    if req.startswith("3.10"):
        return "3.10.18"
    return DEFAULT_VERSION


def _resolve_release_tag() -> str:
    try:
        with urllib.request.urlopen(LATEST_META_URL, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        tag = data.get("tag") or data.get("version") or data.get("release")
        if tag:
            return str(tag)
    except Exception:
        pass
    return DEFAULT_RELEASE


def _asset_name(version: str, release: str, target: str) -> str:
    return f"cpython-{version}+{release}-{target}-install_only.tar.gz"


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[fetch_python] Downloading:\n  {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "scientific-paper-reading-skill"})
    with urllib.request.urlopen(req, timeout=300) as resp, open(dest, "wb") as f:
        shutil.copyfileobj(resp, f)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_python_exe(root: Path) -> Path | None:
    candidates = [
        root / "python.exe",
        root / "python" / "python.exe",
        root / "bin" / "python3",
        root / "bin" / "python",
        root / "python" / "bin" / "python3",
        root / "python" / "bin" / "python",
    ]
    for c in candidates:
        if c.is_file():
            return c
    # deep search one level
    for p in root.rglob("python.exe"):
        return p
    for name in ("python3", "python"):
        for p in root.rglob(name):
            if p.is_file() and os.access(p, os.X_OK):
                return p
    return None


def _extract_install_only(archive: Path, dest: Path) -> Path:
    """Extract install_only tar.gz so dest becomes the python root."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(tmp_path)
        # Archives usually contain a top-level "python/" directory
        children = [p for p in tmp_path.iterdir() if p.name not in (".", "..")]
        if len(children) == 1 and children[0].is_dir():
            extracted = children[0]
        else:
            extracted = tmp_path
        # Move contents into dest
        for item in extracted.iterdir():
            shutil.move(str(item), str(dest / item.name))

    exe = _find_python_exe(dest)
    if not exe:
        raise RuntimeError(f"解压后未找到 python 可执行文件: {dest}")
    # Normalize: if exe is dest/python/python.exe, hoist one level when needed
    # Keep as-is; env_detect will find it.
    return exe


def fetch(
    *,
    version: str = DEFAULT_VERSION,
    release: str | None = None,
    target: str | None = None,
    force: bool = False,
) -> dict:
    version = _normalize_version(version)
    release = release or _resolve_release_tag()
    target = target or _detect_target()
    asset = _asset_name(version, release, target)
    url = f"{RELEASE_BASE}/{release}/{asset}"

    existing = _find_python_exe(PYTHON_DIR)
    if existing and not force:
        meta = {
            "ok": True,
            "action": "use_existing",
            "python": str(existing),
            "runtime_dir": str(PYTHON_DIR),
            "message": "已存在便携 Python；如需重装请加 --force",
        }
        return meta

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / asset
        try:
            _download(url, archive)
        except Exception as exc:
            # Fallback to pinned default release/version if latest tag has different version
            if release != DEFAULT_RELEASE or version != DEFAULT_VERSION:
                release = DEFAULT_RELEASE
                version = DEFAULT_VERSION
                target = target or _detect_target()
                asset = _asset_name(version, release, target)
                url = f"{RELEASE_BASE}/{release}/{asset}"
                print(f"[fetch_python] Retry pinned asset:\n  {url}")
                _download(url, archive)
            else:
                raise RuntimeError(f"下载失败: {exc}") from exc

        exe = _extract_install_only(archive, PYTHON_DIR)
        digest = _sha256(archive)

    meta = {
        "ok": True,
        "action": "fetched",
        "version": version,
        "release_tag": release,
        "target": target,
        "source": "python-build-standalone",
        "asset": asset,
        "url": url,
        "sha256_archive": digest,
        "python": str(exe.resolve()),
        "runtime_dir": str(PYTHON_DIR.resolve()),
    }
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch portable CPython into runtime/python/")
    parser.add_argument("--version", default="3.12", help="Python version, e.g. 3.12 or 3.12.11")
    parser.add_argument("--release", default=None, help="python-build-standalone release tag")
    parser.add_argument("--target", default=None, help="Override target triple")
    parser.add_argument("--force", action="store_true", help="Replace existing runtime/python")
    args = parser.parse_args()
    try:
        result = fetch(
            version=args.version,
            release=args.release,
            target=args.target,
            force=args.force,
        )
        return 0 if result.get("ok") else 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
