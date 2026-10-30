#!/usr/bin/env python
"""网页搜索 CLI（供 AI 内部调用，输出 JSON，不对用户展示）。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.search import search_related, search_term, search_web


def main() -> int:
    parser = argparse.ArgumentParser(
        description="内部网页搜索（AI 校验知识用，结果 JSON 输出到 stdout）",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-q", "--query", type=str, help="自由查询")
    mode.add_argument("-t", "--term", type=str, help="专业术语检索")
    mode.add_argument("-r", "--related", type=str, help="相关背景知识检索")

    parser.add_argument("--context", type=str, default="", help="术语/主题上下文（配合 -t/-r）")
    parser.add_argument("--field", type=str, default="", help="学科领域（配合 -r）")
    parser.add_argument("-n", "--max-results", type=int, default=5)
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    try:
        if args.query:
            results = search_web(
                args.query,
                max_results=args.max_results,
                use_cache=not args.no_cache,
            )
            payload = {"mode": "query", "input": args.query, "results": results}
        elif args.term:
            results = search_term(
                args.term,
                context=args.context,
                max_results=args.max_results,
                use_cache=not args.no_cache,
            )
            payload = {
                "mode": "term",
                "input": args.term,
                "context": args.context,
                "results": results,
            }
        else:
            results = search_related(
                args.related,
                field=args.field or args.context,
                max_results=args.max_results,
                use_cache=not args.no_cache,
            )
            payload = {
                "mode": "related",
                "input": args.related,
                "field": args.field or args.context,
                "results": results,
            }
    except Exception as exc:
        print(json.dumps({"error": str(exc), "results": []}, ensure_ascii=False), file=sys.stdout)
        return 1

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
