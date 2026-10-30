"""网页搜索模块（供 AI 内部校验与补充知识，不对用户展示）。"""

from .web import search_related, search_term, search_web

__all__ = ["search_web", "search_term", "search_related"]
