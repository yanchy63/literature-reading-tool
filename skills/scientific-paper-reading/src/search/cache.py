"""网页搜索缓存，避免重复查询。"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from src.config import SEARCH_CACHE_DIR, SEARCH_CACHE_TTL_HOURS

_TTL_SECONDS = SEARCH_CACHE_TTL_HOURS * 3600


def _cache_key(query: str, mode: str) -> str:
    raw = f"{mode}:{query.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_cached(query: str, mode: str) -> list[dict[str, Any]] | None:
    path = SEARCH_CACHE_DIR / f"{_cache_key(query, mode)}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if time.time() - data.get("cached_at", 0) > _TTL_SECONDS:
            path.unlink(missing_ok=True)
            return None
        return data.get("results")
    except (json.JSONDecodeError, OSError):
        return None


def set_cached(query: str, mode: str, results: list[dict[str, Any]]) -> None:
    SEARCH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = SEARCH_CACHE_DIR / f"{_cache_key(query, mode)}.json"
    payload = {"query": query, "mode": mode, "cached_at": time.time(), "results": results}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
