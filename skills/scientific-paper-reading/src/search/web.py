"""网页搜索核心逻辑。"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from ddgs import DDGS

from src.search.cache import get_cached, set_cached

# 科研场景优先考虑的来源类型（用于结果排序，非过滤）
_TRUSTED_DOMAINS = (
    "wikipedia.org",
    "scholar.google",
    "nature.com",
    "science.org",
    "acs.org",
    "rsc.org",
    "wiley.com",
    "springer.com",
    "sciencedirect.com",
    "arxiv.org",
    "nih.gov",
    "nist.gov",
    "distill.pub",
    "github.com",
    "microsoft.com",
    "openreview.net",
)


def _domain_score(url: str) -> int:
    host = urlparse(url).netloc.lower()
    for i, domain in enumerate(_TRUSTED_DOMAINS):
        if domain in host:
            return len(_TRUSTED_DOMAINS) - i
    if host.endswith(".edu") or host.endswith(".ac.uk"):
        return 5
    return 0


def _normalize_result(item: dict[str, Any]) -> dict[str, str]:
    return {
        "title": (item.get("title") or "").strip(),
        "url": (item.get("href") or item.get("url") or "").strip(),
        "snippet": (item.get("body") or item.get("snippet") or "").strip(),
    }


def _rank_results(results: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(results, key=lambda r: _domain_score(r["url"]), reverse=True)


def search_web(
    query: str,
    *,
    max_results: int = 5,
    use_cache: bool = True,
) -> list[dict[str, str]]:
    """
    通用网页搜索。返回 title / url / snippet 列表（已按来源可信度排序）。
    """
    if use_cache:
        cached = get_cached(query, "web")
        if cached is not None:
            return cached

    raw = DDGS().text(query, max_results=max_results)
    results = _rank_results([_normalize_result(r) for r in raw if r])
    results = [r for r in results if r["title"] or r["snippet"]]

    if use_cache and results:
        set_cached(query, "web", results)
    return results


def search_term(
    term: str,
    *,
    context: str = "",
    max_results: int = 4,
    use_cache: bool = True,
) -> list[dict[str, str]]:
    """检索专业术语定义与背景（自动构造学术向查询）。"""
    ctx = f" {context}" if context else ""
    query = f"{term} definition scientific{ctx}"
    if use_cache:
        cached = get_cached(query, "term")
        if cached is not None:
            return cached

    results = search_web(query, max_results=max_results, use_cache=False)
    if use_cache and results:
        set_cached(query, "term", results)
    return results


def search_related(
    topic: str,
    *,
    field: str = "",
    max_results: int = 5,
    use_cache: bool = True,
) -> list[dict[str, str]]:
    """检索与主题相关的背景知识、综述性材料。"""
    field_part = f" {field}" if field else ""
    query = f"{topic}{field_part} review overview"
    if use_cache:
        cached = get_cached(query, "related")
        if cached is not None:
            return cached

    results = search_web(query, max_results=max_results, use_cache=False)
    if use_cache and results:
        set_cached(query, "related", results)
    return results
