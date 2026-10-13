#!/usr/bin/env python3
"""TikHub 社媒检索驱动（模块3/4/5 的一等信源）。

覆盖平台：twitter / reddit / xiaohongshu / weibo / zhihu
外加 twitter 用户资料查询——模块3 KOL 验证的硬证据来源。

用法:
    python3 tikhub_client.py search twitter "<your brand or keyword>" [--limit 20]
    python3 tikhub_client.py search reddit  "<your keyword>"
    python3 tikhub_client.py search xhs     "<中文关键词>"
    python3 tikhub_client.py search weibo   "<中文关键词>"
    python3 tikhub_client.py search zhihu   "<中文关键词>"
    python3 tikhub_client.py profile <twitter_handle>
    python3 tikhub_client.py posts   <twitter_handle>

    --raw   输出原始 JSON（落 snapshot 用，先存证据再分析）

需要 TIKHUB_API_KEY。未配置时明确报错退出——不静默返回空结果假装成功。

字段映射全部基于 2026-08-22 实测响应，不是猜的。API 改版后归一化会 raise
ShapeChanged 而不是静默返回空列表——宁可报错，也不交一份看着完整的空报告。
"""
from __future__ import annotations

import json
import os
import re
import sys

from pathlib import Path

import requests

BASE = "https://api.tikhub.io"

ENDPOINTS = {
    "twitter": ("/api/v1/twitter/web/fetch_search_timeline", {"keyword": None, "search_type": "Top"}),
    "reddit":  ("/api/v1/reddit/app/fetch_dynamic_search",   {"query": None, "search_type": "post", "need_format": "true"}),
    "xhs":     ("/api/v1/xiaohongshu/app_v2/search_notes",   {"keyword": None, "page": 1}),
    "weibo":   ("/api/v1/weibo/web_v2/fetch_advanced_search", {"q": None, "search_type": "all"}),
    "zhihu":   ("/api/v1/zhihu/web/fetch_article_search_v3", {"keyword": None, "limit": "20"}),
}
ALIASES = {"x": "twitter", "xiaohongshu": "xhs", "rednote": "xhs", "小红书": "xhs",
           "微博": "weibo", "知乎": "zhihu"}

PROFILE_EP = "/api/v1/twitter/web/fetch_user_profile"
POSTS_EP = "/api/v1/twitter/web/fetch_user_post_tweet"


class ShapeChanged(RuntimeError):
    """响应结构与实测基线不符——归一化拒绝猜测。"""


ENV_FILE = Path(os.environ.get("GEO_AGENT_DATA_ROOT", "~/geo-agent-data")).expanduser() / ".env"


def _key() -> str:
    """优先环境变量，其次 ~/geo-agent-data/.env。

    密钥刻意不放在 skill 目录里——那个目录会被打包成分发包。
    """
    k = os.environ.get("TIKHUB_API_KEY")
    if not k and ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("TIKHUB_API_KEY"):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    if not k:
        raise RuntimeError(
            f"TIKHUB_API_KEY 未配置。请 export TIKHUB_API_KEY=... "
            f"或写入 {ENV_FILE}（不返回空结果冒充成功）"
        )
    return k


def _get(path: str, params: dict) -> dict:
    """熔断：重试 2 次仍失败即终止，不用模型记忆编造数据顶上。"""
    last = None
    for attempt in (1, 2):
        try:
            r = requests.get(
                BASE + path,
                params={k: v for k, v in params.items() if v not in (None, "")},
                headers={"Authorization": f"Bearer {_key()}", "accept": "application/json"},
                timeout=60,
            )
            r.raise_for_status()
            j = r.json()
            if j.get("code") != 200:
                raise RuntimeError(f"TikHub code={j.get('code')} msg={j.get('message')}")
            return j
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"⚠️  第 {attempt} 次失败：{e}", file=sys.stderr)
    raise RuntimeError(f"信源熔断：TikHub 重试 2 次仍失败 → {last}")


# ---------------------------------------------------------------- 取数

def search_raw(platform: str, query: str, **over) -> dict:
    platform = ALIASES.get(platform, platform)
    if platform not in ENDPOINTS:
        raise ValueError(f"不支持的平台 '{platform}'。可选：{', '.join(ENDPOINTS)}")
    path, tpl = ENDPOINTS[platform]
    params = dict(tpl)
    for k, v in params.items():
        if v is None:
            params[k] = query
    params.update(over)
    return _get(path, params)


def profile_raw(screen_name: str) -> dict:
    return _get(PROFILE_EP, {"screen_name": screen_name})


def posts_raw(screen_name: str) -> dict:
    return _get(POSTS_EP, {"screen_name": screen_name})


# ---------------------------------------------------------------- 归一化
# 统一字段：platform / id / author / text / url / created_at / likes / comments / shares / views

def _dig(d: dict, *path, required=True):
    cur = d
    for p in path:
        try:
            cur = cur[p]
        except (KeyError, IndexError, TypeError):
            if required:
                raise ShapeChanged(f"响应缺少路径 {'.'.join(map(str, path))}——TikHub 可能改版了")
            return None
    return cur


def norm_twitter(j: dict) -> list[dict]:
    out = []
    for t in _dig(j, "data", "timeline"):
        if t.get("type") != "tweet":
            continue
        sn = t.get("screen_name") or ""
        out.append({
            "platform": "twitter", "id": t.get("tweet_id"), "author": sn,
            "text": t.get("text", ""), "created_at": t.get("created_at"),
            "url": f"https://x.com/{sn}/status/{t.get('tweet_id')}" if sn else None,
            "likes": t.get("favorites"), "comments": t.get("replies"),
            "shares": t.get("retweets"), "views": t.get("views"),
        })
    return out


def norm_reddit(j: dict) -> list[dict]:
    edges = _dig(j, "data", "search", "dynamic", "components", "main", "edges")
    out = []
    for e in edges:
        for c in (_dig(e, "node", "children", required=False) or []):
            p = c.get("post") or {}
            if not p:
                continue
            out.append({
                "platform": "reddit", "id": p.get("id"),
                "author": (p.get("authorInfo") or {}).get("name"),
                "text": p.get("postTitle", ""),
                "body": ((p.get("content") or {}).get("markdown") or "")[:2000],
                "created_at": p.get("createdAt"), "url": p.get("url"),
                "subreddit": (p.get("subreddit") or {}).get("prefixedName"),
                "likes": p.get("score"), "comments": p.get("commentCount"),
                "shares": None, "views": None,
                "upvote_ratio": p.get("upvoteRatio"),
            })
    return out


def norm_xhs(j: dict) -> list[dict]:
    out = []
    for it in _dig(j, "data", "data", "items"):
        n = it.get("note")
        if not n:
            continue
        u = n.get("user") or {}
        out.append({
            "platform": "xiaohongshu", "id": n.get("id"),
            "author": u.get("nickname") or u.get("nick_name"),
            "text": n.get("title") or "", "body": n.get("desc") or "",
            "created_at": n.get("timestamp"),
            "url": f"https://www.xiaohongshu.com/explore/{n.get('id')}",
            "likes": n.get("liked_count"), "comments": n.get("comments_count"),
            "shares": n.get("shared_count"), "views": None,
            "collected": n.get("collected_count"), "note_type": n.get("type"),
        })
    return out


def norm_weibo(j: dict) -> list[dict]:
    out = []
    for w in _dig(j, "data", "parsed_data", "results"):
        ia = w.get("interaction") or {}
        pu = w.get("post_url") or ""
        out.append({
            "platform": "weibo", "id": w.get("weibo_id"),
            "author": w.get("user_name") or w.get("user_nick"),
            "text": w.get("content", ""), "created_at": w.get("publish_time"),
            "url": ("https:" + pu) if pu.startswith("//") else pu,
            "likes": ia.get("like_count"), "comments": ia.get("comment_count"),
            "shares": ia.get("repost_count"), "views": None,
            "weibo_type": w.get("weibo_type"),
        })
    return out


_EM = re.compile(r"</?em>")


def _clean(t: str) -> str:
    """知乎搜索结果把命中词包在 <em> 里，报告引用原文前必须剥掉。"""
    return _EM.sub("", t or "").strip()


def _zhihu_url(o: dict) -> str | None:
    """api.zhihu.com 不是人能点的地址，转成 www 站可核验链接。"""
    kind, oid = o.get("type"), o.get("id")
    if not oid:
        return o.get("url")
    if kind == "answer":
        q = (o.get("question") or {}).get("id")
        return f"https://www.zhihu.com/question/{q}/answer/{oid}" if q else f"https://www.zhihu.com/answer/{oid}"
    if kind == "article":
        return f"https://zhuanlan.zhihu.com/p/{oid}"
    if kind == "question":
        return f"https://www.zhihu.com/question/{oid}"
    return o.get("url")


# 知乎搜索结果是混合类型：answer/article/question 是内容；
# people(用户主页) / ring_box(话题圈) / ai_zhida(AI直答) / {} 不是。
# 用白名单而不是黑名单——知乎随时会加新卡片类型，黑名单会漏进 null 行。
_ZH_CONTENT = {"answer", "article", "question"}


def norm_zhihu(j: dict) -> list[dict]:
    out = []
    for it in _dig(j, "data", "data"):
        o = it.get("object") or {}
        kind = o.get("type")

        # hot_timing 是热榜卡，真正的问题裹在 description.object 里，
        # 往往是当期最重要的舆情，不能丢。
        if kind == "hot_timing":
            inner = (o.get("description") or {}).get("object") or {}
            if inner.get("id"):
                out.append({
                    "platform": "zhihu", "id": inner.get("id"), "kind": "hot_question",
                    "author": None,
                    "text": _clean(inner.get("title") or o.get("title") or ""),
                    "body": _clean(inner.get("description") or "")[:2000],
                    "created_at": None,
                    "url": f"https://www.zhihu.com/question/{inner['id']}",
                    "likes": None, "comments": None, "shares": None, "views": None,
                })
            continue

        if kind not in _ZH_CONTENT:
            continue
        a = o.get("author") or {}
        q = o.get("question") or {}
        out.append({
            "platform": "zhihu", "id": o.get("id"), "kind": o.get("type"),
            "author": a.get("name"),
            "text": _clean(q.get("name") or o.get("title") or ""),
            "body": _clean(o.get("excerpt") or "")[:2000],
            "created_at": o.get("created_time"), "url": _zhihu_url(o),
            "likes": o.get("voteup_count"), "comments": o.get("comment_count"),
            "shares": None, "views": None,
            "favorites": o.get("favorites_count"),
        })
    return out


NORMALIZERS = {"twitter": norm_twitter, "reddit": norm_reddit, "xhs": norm_xhs,
               "weibo": norm_weibo, "zhihu": norm_zhihu}


def norm_profile(j: dict) -> dict:
    """模块3 KOL 验证用。sub_count 是粉丝数，friends 是关注数（实测确认）。"""
    d = _dig(j, "data")
    return {
        "platform": "twitter", "handle": d.get("profile"), "name": d.get("name"),
        "rest_id": d.get("rest_id"), "status": d.get("status"),
        "followers": d.get("sub_count"), "following": d.get("friends"),
        "tweet_count": d.get("statuses_count"), "media_count": d.get("media_count"),
        "blue_verified": d.get("blue_verified"),
        "verification_type": d.get("verification_type"),
        "desc": d.get("desc"), "location": d.get("location"),
        "created_at": d.get("created_at"), "protected": d.get("protected"),
    }


def search(platform: str, query: str, limit: int = 20, **over) -> list[dict]:
    platform = ALIASES.get(platform, platform)
    raw = search_raw(platform, query, **over)
    return NORMALIZERS[platform](raw)[:limit]


# ---------------------------------------------------------------- CLI

def main() -> int:
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 1
    raw = "--raw" in a
    a = [x for x in a if x != "--raw"]
    limit = int(a[a.index("--limit") + 1]) if "--limit" in a else 20
    a = [x for x in a if x != "--limit" and x != str(limit)] if "--limit" in a else a

    cmd = a[0]
    if cmd == "search":
        plat, q = a[1], a[2]
        j = search_raw(plat, q)
        out = j if raw else search(plat, q, limit)
    elif cmd == "profile":
        j = profile_raw(a[1])
        out = j if raw else norm_profile(j)
    elif cmd == "posts":
        j = posts_raw(a[1])
        out = j if raw else norm_twitter({"data": {"timeline": _dig(j, "data", "timeline", required=False) or []}})
    else:
        print(__doc__)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
