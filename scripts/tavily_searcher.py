#!/usr/bin/env python3
"""Tavily 搜索驱动（通用搜索降级方案）。

用法:
    python3 tavily_searcher.py "query" [--depth advanced] [--max 8]

需要 TAVILY_API_KEY。未配置时明确报错退出——不静默返回空结果假装成功。
"""
from __future__ import annotations

import json
import os
import sys

import requests

ENDPOINT = "https://api.tavily.com/search"


def search(query: str, depth: str = "basic", max_results: int = 8) -> dict:
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        raise RuntimeError(
            "TAVILY_API_KEY 未配置。请 export TAVILY_API_KEY=... "
            "或改用 WebSearch 工具。（不返回空结果冒充成功）"
        )
    last = None
    for attempt in (1, 2):  # 熔断：重试 2 次仍失败即终止
        try:
            r = requests.post(ENDPOINT, json={
                "api_key": key, "query": query, "search_depth": depth,
                "max_results": max_results, "include_answer": True,
                "include_raw_content": False,
            }, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"⚠️  第 {attempt} 次失败：{e}", file=sys.stderr)
    raise RuntimeError(f"信源熔断：Tavily 重试 2 次仍失败 → {last}")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    args = sys.argv[1:]
    query = args[0]
    depth = args[args.index("--depth") + 1] if "--depth" in args else "basic"
    mx = int(args[args.index("--max") + 1]) if "--max" in args else 8
    print(json.dumps(search(query, depth, mx), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
