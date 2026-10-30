#!/usr/bin/env python
"""Detect a usable Python for this skill; cache path under .cache/python_env.json.

Prefer skill-local .venv. Conda is optional and never auto-created.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from src.env_detect import detect_environment, save_cache


def main() -> int:
    result = detect_environment()
    if result["ready"]:
        save_cache(result)
    else:
        result = {
            **result,
            "hint": (
                "环境未就绪。请运行: python scripts/setup_env.py "
                "(或 Windows: py -3 scripts/setup_env.py)。无需 conda。"
            ),
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
