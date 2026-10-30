#!/usr/bin/env python3
"""
全 Agent 通用安装器（Agent Skills / Cursor / Claude / Codex …）

将本仓库的 skills/scientific-paper-reading 安装到各 Agent 会扫描的技能目录。
仅依赖 Python 标准库。

用法（在仓库根目录）:
  python install_agent_skill.py
  python install_agent_skill.py --all
  python install_agent_skill.py --agents agents,cursor,claude,codex
  python install_agent_skill.py --project
  python install_agent_skill.py --with-env
  python install_agent_skill.py --list-targets
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SKILL_NAME = "scientific-paper-reading"
SKILL_SRC = REPO_ROOT / "skills" / SKILL_NAME
REPO_URL = "https://github.com/yanchy63/literature-reading-tool"

# (id, display, path relative to home or special)
USER_TARGETS = {
    "agents": ("Agent Skills 通用", Path(".agents") / "skills" / SKILL_NAME),
    "cursor": ("Cursor", Path(".cursor") / "skills" / SKILL_NAME),
    "claude": ("Claude Code / Claude", Path(".claude") / "skills" / SKILL_NAME),
    "codex": ("Codex", Path(".codex") / "skills" / SKILL_NAME),
}

PROJECT_TARGETS = {
    "agents": Path(".agents") / "skills" / SKILL_NAME,
    "cursor": Path(".cursor") / "skills" / SKILL_NAME,
    "claude": Path(".claude") / "skills" / SKILL_NAME,
    "codex": Path(".codex") / "skills" / SKILL_NAME,
}

IGNORE_NAMES = {
    ".venv",
    ".cache",
    "__pycache__",
    "runtime/python",
    ".git",
}


def _home() -> Path:
    return Path.home()


def _should_ignore(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}:
        return True
    if path.name == ".venv":
        return True
    if rel.startswith("runtime/python"):
        return True
    if path.name == ".cache":
        return True
    return False


def copy_skill(src: Path, dest: Path) -> None:
    if not src.is_dir() or not (src / "SKILL.md").is_file():
        raise FileNotFoundError(f"技能源不存在或不完整: {src}")
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    def _ignore(directory: str, names: list[str]) -> set[str]:
        base = Path(directory)
        skipped: set[str] = set()
        for name in names:
            p = base / name
            try:
                if _should_ignore(p, src):
                    skipped.add(name)
            except ValueError:
                pass
            if name in {".venv", "__pycache__", ".cache"}:
                skipped.add(name)
        return skipped

    shutil.copytree(src, dest, ignore=_ignore)


def resolve_user_targets(agents: list[str]) -> list[tuple[str, str, Path]]:
    home = _home()
    out: list[tuple[str, str, Path]] = []
    for key in agents:
        if key not in USER_TARGETS:
            raise SystemExit(f"未知 agent: {key}；可选: {', '.join(USER_TARGETS)}")
        label, rel = USER_TARGETS[key]
        out.append((key, label, home / rel))
    return out


def resolve_project_targets(agents: list[str], cwd: Path) -> list[tuple[str, str, Path]]:
    out: list[tuple[str, str, Path]] = []
    for key in agents:
        if key not in PROJECT_TARGETS:
            raise SystemExit(f"未知 agent: {key}")
        label = USER_TARGETS[key][0]
        out.append((key, f"{label}（项目级）", cwd / PROJECT_TARGETS[key]))
    return out


def install_cursor_plugin_local() -> Path:
    """Optional: full repo as Cursor local plugin for marketplace-style load."""
    dest = _home() / ".cursor" / "plugins" / "local" / "literature-reading-tool"
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    def _ignore(directory: str, names: list[str]) -> set[str]:
        skip = {".git", ".venv", "__pycache__", ".cache"}
        return {n for n in names if n in skip}

    shutil.copytree(REPO_ROOT, dest, ignore=_ignore)
    return dest


def maybe_setup_env(skill_dest: Path, *, fetch_python: bool) -> dict:
    setup = skill_dest / "scripts" / "setup_env.py"
    if not setup.is_file():
        return {"ok": False, "error": "setup_env.py missing"}
    cmd = [sys.executable, str(setup)]
    if fetch_python:
        cmd.append("--fetch-python")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(skill_dest)
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(skill_dest),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=600,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "")[-2000:],
            "stderr": (proc.stderr or "")[-1000:],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install literature-reading-tool skill into agent skill directories"
    )
    parser.add_argument(
        "--agents",
        default="agents,cursor,claude,codex",
        help="Comma-separated: agents,cursor,claude,codex (default: all)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Install to all known user-level agent skill dirs (same as default agents)",
    )
    parser.add_argument(
        "--project",
        action="store_true",
        help="Also install into current project .agents/.cursor/.claude/.codex skills",
    )
    parser.add_argument(
        "--project-only",
        action="store_true",
        help="Only install project-level skills (cwd)",
    )
    parser.add_argument(
        "--cursor-plugin",
        action="store_true",
        help="Also copy full repo to ~/.cursor/plugins/local/literature-reading-tool",
    )
    parser.add_argument(
        "--with-env",
        action="store_true",
        help="After install, run setup_env.py on the primary agents copy",
    )
    parser.add_argument(
        "--fetch-python",
        action="store_true",
        help="With --with-env, also download portable Python",
    )
    parser.add_argument(
        "--list-targets",
        action="store_true",
        help="Print target paths and exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be installed without copying",
    )
    args = parser.parse_args()

    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    if args.all:
        agents = list(USER_TARGETS.keys())

    user_targets = [] if args.project_only else resolve_user_targets(agents)
    project_targets = (
        resolve_project_targets(agents, Path.cwd())
        if (args.project or args.project_only)
        else []
    )

    if args.list_targets:
        print(json.dumps({
            "repo": str(REPO_ROOT),
            "skill_src": str(SKILL_SRC),
            "repo_url": REPO_URL,
            "user_targets": [
                {"id": i, "label": l, "path": str(p)} for i, l, p in user_targets
            ],
            "project_targets": [
                {"id": i, "label": l, "path": str(p)} for i, l, p in project_targets
            ],
        }, ensure_ascii=False, indent=2))
        return 0

    if not SKILL_SRC.is_dir():
        print(json.dumps({
            "ok": False,
            "error": f"找不到技能目录: {SKILL_SRC}",
            "hint": f"请先 git clone {REPO_URL} 并在仓库根目录运行本脚本",
        }, ensure_ascii=False, indent=2))
        return 1

    installed: list[dict] = []
    for key, label, dest in user_targets + project_targets:
        entry = {"agent": key, "label": label, "path": str(dest)}
        if args.dry_run:
            entry["action"] = "dry_run"
        else:
            copy_skill(SKILL_SRC, dest)
            entry["action"] = "installed"
            entry["has_skill_md"] = (dest / "SKILL.md").is_file()
        installed.append(entry)
        print(f"[install] {label} -> {dest}")

    plugin_path = None
    if args.cursor_plugin:
        if args.dry_run:
            plugin_path = str(_home() / ".cursor" / "plugins" / "local" / "literature-reading-tool")
            print(f"[install] (dry-run) Cursor local plugin -> {plugin_path}")
        else:
            plugin_path = str(install_cursor_plugin_local())
            print(f"[install] Cursor local plugin -> {plugin_path}")

    env_result = None
    if args.with_env and not args.dry_run:
        # Prefer agents copy, else first installed
        primary = None
        for item in installed:
            if item.get("agent") == "agents" and item.get("action") == "installed":
                primary = Path(item["path"])
                break
        if primary is None and installed:
            primary = Path(installed[0]["path"])
        if primary:
            print(f"[install] Running setup_env in {primary} ...")
            env_result = maybe_setup_env(primary, fetch_python=args.fetch_python)

    result = {
        "ok": True,
        "repo_url": REPO_URL,
        "skill_name": SKILL_NAME,
        "installed": installed,
        "cursor_plugin_local": plugin_path,
        "setup_env": env_result,
        "next_steps": [
            "重启 / Reload Agent 窗口以便发现技能",
            "对话中可用 /scientific-paper-reading 或提交 PDF 触发",
            "若未 --with-env：进入已安装目录运行 scripts/setup_env.py 或 bootstrap.ps1/sh",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
