"""Portable Python environment detection.

Priority: bundled runtime/python → skill .venv → optional conda → system.
Never requires conda. Never auto-creates conda environments.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

from src.config import SKILL_ROOT

ENV_CACHE = SKILL_ROOT / ".cache" / "python_env.json"
REQUIRED_MODULES = ("pymupdf", "pymupdf4llm", "pdfplumber", "ddgs", "docx")
MIN_PYTHON = (3, 10)


def _run(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def _python_exe_in_env(env_root: Path) -> Path:
    if platform.system() == "Windows":
        # conda / some envs put python.exe at root; venv uses Scripts/
        scripts = env_root / "Scripts" / "python.exe"
        if scripts.is_file():
            return scripts
        return env_root / "python.exe"
    return env_root / "bin" / "python"


def _parse_version(version_str: str) -> tuple[int, int] | None:
    for token in version_str.replace(",", " ").split():
        if token.lower().startswith("python"):
            token = token.split("python", 1)[-1]
        if token and token[0].isdigit():
            parts = token.split(".")
            try:
                return int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
            except ValueError:
                continue
    return None


def _verify_python(python: Path) -> dict[str, Any] | None:
    if not python.is_file():
        return None
    ver = _run([str(python), "--version"])
    if not ver or ver.returncode != 0:
        return None
    version = ver.stdout.strip() or ver.stderr.strip()
    parsed = _parse_version(version)
    if parsed and parsed < MIN_PYTHON:
        return None

    import_cmd = f"import {','.join(REQUIRED_MODULES)}; print('OK')"
    deps = _run([str(python), "-c", import_cmd])
    deps_ok = bool(deps and deps.returncode == 0 and "OK" in (deps.stdout or ""))
    missing: list[str] = []
    if not deps_ok:
        for mod in REQUIRED_MODULES:
            check = _run([str(python), "-c", f"import {mod}"])
            if not check or check.returncode != 0:
                missing.append(mod)

    return {
        "python": str(python.resolve()),
        "version": version,
        "deps_ok": deps_ok,
        "missing_modules": missing,
    }


def _list_conda_envs() -> list[tuple[str, Path]]:
    """Optional: reuse existing conda envs if present. Never required."""
    conda = shutil.which("conda")
    if not conda:
        return []
    result = _run([conda, "env", "list", "--json"])
    if not result or result.returncode != 0:
        return []
    try:
        env_paths: list[str] = json.loads(result.stdout).get("envs", [])
    except json.JSONDecodeError:
        return []
    envs: list[tuple[str, Path]] = []
    for env_path in env_paths:
        root = Path(env_path)
        exe = _python_exe_in_env(root)
        if exe.is_file():
            envs.append((root.name, exe))
    return envs


def skill_venv_python() -> Path | None:
    venv = SKILL_ROOT / ".venv"
    if platform.system() == "Windows":
        exe = venv / "Scripts" / "python.exe"
    else:
        exe = venv / "bin" / "python"
    return exe if exe.is_file() else None


def bundled_runtime_python() -> Path | None:
    """Optional portable CPython under runtime/python/ (see fetch_portable_python.py)."""
    root = SKILL_ROOT / "runtime" / "python"
    if not root.is_dir():
        return None
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
    if platform.system() == "Windows":
        found = next(root.rglob("python.exe"), None)
        return found if found and found.is_file() else None
    for name in ("python3", "python"):
        found = next(root.rglob(name), None)
        if found and found.is_file():
            return found
    return None


def _shell_pythons() -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()

    def add(path: Path | None) -> None:
        if path is None:
            return
        key = str(path.resolve()).lower() if path.is_file() else ""
        if key and key not in seen and path.is_file():
            seen.add(key)
            found.append(path)

    # Windows py launcher: try 3.12 / 3.11 / 3.10 explicitly
    if platform.system() == "Windows":
        py = shutil.which("py")
        if py:
            for flag in ("-3.12", "-3.11", "-3.10", "-3"):
                probe = _run([py, flag, "-c", "import sys; print(sys.executable)"])
                if probe and probe.returncode == 0:
                    line = (probe.stdout or "").strip().splitlines()
                    if line:
                        add(Path(line[0].strip()))

    for name in ("python3", "python"):
        which = shutil.which(name)
        if which:
            add(Path(which))

    return found


def _candidate_pythons() -> list[tuple[str, Path]]:
    ordered: list[tuple[str, Path]] = []
    seen: set[str] = set()

    def add(label: str, path: Path) -> None:
        if not path.is_file():
            return
        key = str(path.resolve()).lower()
        if key not in seen:
            seen.add(key)
            ordered.append((label, path))

    # 1. Bundled portable runtime (works offline after first fetch / USB copy)
    bundled = bundled_runtime_python()
    if bundled:
        add("bundled_runtime", bundled)

    # 2. Cache from last successful run
    if ENV_CACHE.is_file():
        try:
            cached = json.loads(ENV_CACHE.read_text(encoding="utf-8"))
            if cached.get("python"):
                add("cache", Path(cached["python"]))
        except (json.JSONDecodeError, OSError):
            pass

    # 3. Skill-local venv
    venv_py = skill_venv_python()
    if venv_py:
        add("skill_venv", venv_py)

    # 4. Optional conda (never required)
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        add("conda_active", _python_exe_in_env(Path(conda_prefix)))

    for env_name, exe in _list_conda_envs():
        add(f"conda:{env_name}", exe)

    # 5. System PATH
    for exe in _shell_pythons():
        add("shell", exe)

    return ordered


def _suggest_action(
    ready: dict[str, Any] | None,
    checked: list[dict[str, Any]],
) -> str:
    if ready:
        return "use_existing"

    installable = [c for c in checked if c.get("status") == "no_deps" and c.get("python")]
    if installable:
        return "install_deps"

    # No usable interpreter at all → fetch portable runtime then create venv
    return "fetch_python"


def _pick_install_target(checked: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [c for c in checked if c.get("status") == "no_deps" and c.get("python")]
    priority = ("bundled_runtime", "skill_venv", "cache", "conda_active")
    for pref in priority:
        for c in candidates:
            if pref in c.get("source", ""):
                return c
    return candidates[0] if candidates else None


def detect_environment() -> dict[str, Any]:
    checked: list[dict[str, Any]] = []
    ready: dict[str, Any] | None = None
    ready_source: str | None = None

    for source, candidate in _candidate_pythons():
        info = _verify_python(candidate)
        entry: dict[str, Any] = {
            "source": source,
            "path": str(candidate),
            "status": "missing",
        }
        if info is None:
            checked.append(entry)
            continue
        entry["status"] = "ok" if info["deps_ok"] else "no_deps"
        entry.update(info)
        if info["deps_ok"] and ready is None:
            ready = info
            ready_source = source
        checked.append(entry)

    install_target = _pick_install_target(checked) if ready is None else None
    action = _suggest_action(ready, checked)

    return {
        "ready": ready is not None,
        "recommended_python": ready["python"] if ready else None,
        "recommended_version": ready["version"] if ready else None,
        "recommended_source": ready_source,
        "install_target_python": install_target["python"] if install_target else None,
        "install_target_source": install_target.get("source") if install_target else None,
        "skill_root": str(SKILL_ROOT),
        "venv_path": str(SKILL_ROOT / ".venv"),
        "bundled_runtime_path": str(SKILL_ROOT / "runtime" / "python"),
        "checked": checked,
        "action": action,
        "policy": {
            "never_auto_conda_create": True,
            "prefer_bundled_runtime": True,
            "prefer_skill_venv_for_new": True,
            "reuse_any_ready_env": True,
            "conda_optional": True,
            "fetch_portable_python_script": "scripts/fetch_portable_python.py",
            "bootstrap_windows": "scripts/bootstrap.ps1",
            "bootstrap_unix": "scripts/bootstrap.sh",
        },
    }


def save_cache(result: dict[str, Any]) -> None:
    if not result.get("ready"):
        return
    ENV_CACHE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "python": result["recommended_python"],
        "version": result.get("recommended_version"),
        "source": result.get("recommended_source"),
    }
    ENV_CACHE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_cached_python() -> str | None:
    if not ENV_CACHE.is_file():
        return None
    try:
        data = json.loads(ENV_CACHE.read_text(encoding="utf-8"))
        py = data.get("python")
        if py and Path(py).is_file():
            info = _verify_python(Path(py))
            if info and info["deps_ok"]:
                return py
    except (json.JSONDecodeError, OSError):
        pass
    return None
