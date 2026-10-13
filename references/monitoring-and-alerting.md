# 模块4：舆情巡检与告警

**触发**：监测 / 负面 / 舆情 / 告警 / 有人骂 / 黑稿 / 风险

## 巡检范围

| 信源 | 采集方式 | 频率 |
|---|---|---|
| 新闻 / 财媒 | WebSearch + WebFetch | 每日 |
| X/Twitter 品牌词 + $ticker | **TikHub** `search twitter` | 每日 |
| Reddit（白名单 subreddit） | **TikHub** `search reddit` | 每日 |
| 微博 / 小红书 / 知乎（中文租户） | **TikHub** `search weibo\|xhs\|zhihu` | 每日 |
| Stocktwits（上市租户） | Playwright（TikHub 未覆盖） | 每日 |
| 官网/App 商店评价 | WebFetch | 每周 |

X/Reddit 不再有「每日一次」配额限制——见 `social-competitive-intelligence.md`。
中文租户务必跑微博/小红书/知乎：负面往往先在中文区起势，英文区滞后数天。

**Subreddit 白名单机制**：只监控 `configs/tenants.yaml` 里为该租户显式列出的 subreddit，避免噪音与越界抓取。

## 情绪分级

| 级别 | 判据 | 动作 |
|---|---|---|
| 🔴 **P0 危机** | 涉及欺诈/监管/安全指控，或单条 >10k 曝光的负面 | 立即告警 + 出 `crisis-alert-template.md` |
| 🟠 **P1 风险** | 有具体事实指控但曝光有限；竞品定向攻击 | 24h 内出应对建议 |
| 🟡 **P2 关注** | 情绪化吐槽、产品抱怨、无事实指控 | 计入时间线，周报汇总 |
| 🟢 **P3 正面/中性** | —— | 计入时间线 |

## 四引擎 AI 问答审计

对品牌词做 AI 引擎检索，专查**AI 生成的品牌描述是否失真**：

- AI 是否把竞品的属性安在本品牌上？
- AI 引用的信源里有没有黑稿/过时信息？
- AI 的结论与官网事实是否冲突？

失真是 GEO 问题里最隐蔽的一类——用户看不到，但每个问 AI 的人都看到了。发现失真 → 定位被引用的信源 → 进入模块2 的内容规划去覆盖。

## 输出

1. 情绪时间线 → `ledger/sentiment_timeline.csv`
2. 当日巡检报告 → `daily/YYYY-MM-DD_sentiment.md`
3. P0/P1 → 告警卡片（见 `alert-delivery.md`）

## 红线

- 每条负面必须附**原文链接 + snapshot 路径**；无法取证的传闻标注「未取证·勿据此行动」。
- 不得建议删帖、water army、买通媒体一类手段；应对建议限于事实澄清、内容补位、正规交涉。
- **外发告警前需在对话中确认**；仅创建定时任务时明确授权过的固定收件人可免确认。
