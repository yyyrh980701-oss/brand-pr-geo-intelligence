# 模块5：社交竞争情报

**触发**：X动态 / 社交竞争情报 / 竞品日报 / 社媒检索

## 采集方式：TikHub API 优先

`scripts/tikhub_client.py` 是社媒检索的**一等信源**，覆盖 5 个平台：

| 平台 | 参数名 | 适用场景 |
|---|---|---|
| `twitter` | —— | 英文市场竞品动态、$ticker 舆情 |
| `reddit` | —— | 英文真实用户讨论、白名单 subreddit |
| `xhs` | 小红书 | 中文加密区 / 消费决策类话题 |
| `weibo` | 微博 | 中文舆情、热搜关联 |
| `zhihu` | 知乎 | 中文深度内容、行业观点 |

```bash
python3 scripts/tikhub_client.py search twitter "keyword" --limit 20
python3 scripts/tikhub_client.py search xhs "关键词" --limit 20
python3 scripts/tikhub_client.py search twitter "keyword" --raw   # 落 snapshot 用
```

归一化字段统一为 `platform / id / author / text / url / created_at / likes / comments / shares / views`，
跨平台可直接同表对比。需要原始响应存证时加 `--raw`。

**密钥**：`TIKHUB_API_KEY`，环境变量优先，回退读 `~/geo-agent-data/.env`。
刻意不放在 skill 目录——那个目录会被打包成分发包。

**成本**：约 $0.0026/次调用（2026-08-22 实测）。按每天 30 次调用估算约 $0.08/天。
余额查询：`GET /api/v1/tikhub/user/get_user_info`。**余额 < $2 时在报告里告警**。

### 为什么不再用 Cookie 潜行

旧方案是 Playwright 带单账号 Cookie 抓 X，因此有「每日仅一次配额」这条红线——
那是**风控约束**，不是业务约束。改走 TikHub 后约束变成了**成本**，
所以配额红线对上述 5 个平台不再适用，可按需多次检索。

**Playwright 仍然保留**，负责 TikHub 未覆盖的信源：Stocktwits、LinkedIn、以及 PDF 导出。
这些仍受「不并发、每账号 ≤2 页、请求间隔 ≥3s」约束。

### 熔断（未变）

TikHub 重试 2 次仍失败 → 立即终止，写 `capture_health.csv` MISSING 占位，
**不用模型记忆编造数据顶上**。归一化遇到响应结构变化 → `raise ShapeChanged`，
不静默返回空列表冒充「今天没内容」。

## 采集内容（每个竞品）

1. 近 24h 帖文（原文 + 互动数）
2. 内容主题分类（产品/融资/数据/行业观点/招聘）
3. 异常信号：发布频率突变、口径变化、新叙事词、删帖
4. 高互动帖的评论区情绪

原始 JSON → `snapshots/YYYY-MM-DD/{platform}_competitor_{slug}.json`（先存后析，不可跳过）。

## 分析产出（≤500 字）

- **今日竞品在讲什么**（一句话/家）
- **叙事变化**：谁换了口径、换成了什么
- **可借势点**：我方可切入的话题缺口
- **风险点**：竞品是否在抢我方核心词/攻击我方
- **中英差异**：同一话题在中文区与英文区的口径差（TikHub 多平台覆盖后才可得）

## 输出

`daily/YYYY-MM-DD_social-intel.md` + Slack 原文投递（外发需确认）。
