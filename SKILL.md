---
name: brand-pr-geo-intelligence
description: |
  品牌 PR 的 GEO/SEO 策略、AI 可见度审计、舆情巡检、KOL/分析师推荐、行业观点补给、
  活动策划、竞品横纵分析、GEO 文章优化、事件驱动选题，一体化工作流。
  基于 E-E-A-T + V 五维评估框架，多租户数据物理隔离，追加式落盘 + 证据硬卡。
  🔑 贴出任意官网 URL 即自动进入「10 道题 GEO 策略确认」流程，答完才开始采集。
  触发方式：/geo、贴出官网 URL、以及「GEO」「SEO」「AI 可见度」「关键词排名」「KOL 推荐」
  「舆情监测」「负面」「竞品分析」「横纵分析」「改文章」「这个热点能写什么」「周报/月报」
  「发布会/沙龙策划」等。
  Brand PR GEO/SEO intelligence: AI visibility audit, sentiment monitoring, KOL outreach,
  competitive analysis, article optimization, event-driven topic planning.
  Trigger: /geo, pasting any company URL (auto-starts a 10-question GEO strategy intake),
  "GEO", "SEO", "AI visibility", "KOL", "competitor analysis".
---

# 📡 Brand PR GEO Intelligence · 清洁分享版

**定位**：品牌 PR 的 GEO/SEO、AI 可见度、舆情巡检、KOL 推荐、行业观点、活动策划、竞品分析一体化工作流。
**框架**：E-E-A-T + V 五维体系 · **交付引擎**：证据快照 → 诊断/策略内容 → 白话化带图 PDF（HTML 可选）
**工作模式**：快速诊断 · 完整策略 · 持续监测。模式只决定本次任务深度，不代表价格或使用权限，详见 `references/work-modes.md`。
**说明**：本版本为通用分享版——不含任何具体公司数据、客户情报与预置定时任务。
所有租户参数、KOL 词库、API 凭证由使用者首次运行时自行填写，见 `references/setup.md`。

---

## ⛔ 第 0 步：确认服务对象（不可跳过）

每次任务开始，先确认本次服务的租户（一个租户 = 一个客户 / 一个项目）。
租户清单见 `configs/tenants.yaml`（分享版为空，首次使用请自行添加）。

- 用户已说明 → 记录 tenant slug，继续。
- 用户未说明 → **先问，不要猜**：「这次是哪家？（列出 tenants.yaml 里的候选）」
- 只有一个租户已配置 → 可直接使用，但在输出首行标注当前租户。
- 一个租户都没配 → 引导用户先填 `configs/tenants.yaml`，或用模块1 的 10 道题现场建档。

确认后，本次会话所有落盘路径固定为 `data/{tenant}/`，**不得跨租户读写**。

---

## 🔑 URL 自动触发规则（最高优先级）

只要用户输入里出现**任意官网 URL**（`http(s)://`、`www.` 或裸域名如 `example.com`），
或提到一家尚未建档的公司 → **立即进入模块1，先问 10 道题**。

不要先去爬站、不要先给建议、不要先猜行业。详见 `references/url-intake-workflow.md`。

> 唯一例外：用户明确说「不用问了，直接爬」——此时跳过提问，但必须在报告首节注明
> 「口径未确认，结论仅供参考」。

---

## 智能路由表

| 用户输入特征 | 路由目标 | 依赖 |
|------|------|------|
| **贴出任意 URL / 新公司** | **模块1** URL Intake（自动触发 10 道题） | 独立 |
| SEO / GEO / AI搜索 / 关键词 / 排名 / 内容策略 / 可见度 | **模块2** GEO/SEO 策略生成 | 模块1 |
| KOL / 分析师 / 推荐 / 触达 / 谁适合 / 大V | **模块3** KOL & 分析师推荐 | 模块2 |
| 监测 / 负面 / 舆情 / 告警 / 有人骂 / 黑稿 / 风险 | **模块4** 舆情巡检与告警 | 独立 |
| X动态 / 社交竞争情报 / 竞品日报 | **模块5** 社交竞争情报 | 独立 |
| 最近行业有什么 / 周报 / 月报 / 趋势 | **模块6** 行业观点与叙事补给 | 独立 |
| 发布会 / 沙龙 / 直播 / 活动 / 峰会 | **模块7** 活动策划 & GEO 联动 | 可选依赖 |
| 横纵分析 / 竞品研究 / 深度研究 | **模块8** 竞品横纵分析 | 建议先做模块2 |
| 改文章 / GEO优化 / 这篇稿子 / SEO评估 | **模块9** GEO 文章优化 | 独立 |
| 热点 / 这个新闻 / 这个事件 / 能写什么 / 借势 | **模块10** 事件驱动选题 | 独立 |

### 多意图处理优先级

同一条输入命中多个模块时，按此顺序串行执行，先出风险再出策略：

1. 舆情/告警（先看风险） 2. **画像确认（缺时必须补——含 10 道题）** 3. 社交竞争情报 4. 行业观点
5. GEO/SEO 策略 6. 竞品横纵分析 7. KOL 推荐 8. 活动策划 9. GEO 文章优化 10. 事件驱动选题

---

## 模块索引与参考文件

按需读取，**不要一次性全读**：

| 模块 | 参考文件 |
|:---:|------|
| 1 | `references/url-intake-workflow.md` + `templates/company-profile-confirmation.md` |
| 2 | `references/report-modules.md` + `references/aivo-framework.md` + `templates/geo-seo-report-outline.md` + `references/pdf-delivery.md` |
| 3 | `references/kol-analyst-outreach.md` + `configs/kol_radar_dict.yaml` |
| 4 | `references/monitoring-and-alerting.md` + `templates/crisis-alert-template.md` + `references/alert-delivery.md` |
| 5 | `references/social-competitive-intelligence.md` |
| 6 | `references/industry-viewpoints.md` |
| 7 | `references/event-geo-pr-planner.md` + `templates/event-plan-output.md` |
| 8 | `references/hv-analysis-bridge.md`（调用 `hv-analysis` skill） |
| 9 | `references/geo-article-optimizer.md` |
| 10 | `references/event-driven-topic-planner.md` |
| 全局 | `references/work-modes.md`、`references/aivo-framework.md`、`references/data-persistence.md`、`references/pdf-delivery.md`、`references/setup.md` |

---

## E-E-A-T + V 五维框架（速查）

| 维度 | 核心问题 | 满分 |
|------|------|:---:|
| **E₁** Experience | 品牌是否有第一手行业实践证据？ | 20 |
| **E₂** Expertise | 团队是否具备公认的专业能力？ | 20 |
| **A** Authoritativeness | 外部权威信源如何评价品牌？ | 20 |
| **T** Trustworthiness | 信息是否准确、透明、可验证？ | 20 |
| **V** Visibility | AI 搜索引擎在关键 query 中是否推荐？ | 20 |

等级：**A** 85+ / **B** 70–84 / **C** 50–69 / **D** <50。评分细则与取证要求见 `references/aivo-framework.md`。

---

## 工作模式与流程深度

| 模式 | 适合场景 | 交付形式 | 已包含 | 本次不展开 |
|------|------|------|------|------|
| **快速诊断** | 先看清现状和最大问题 | 白话化带图 PDF（HTML 可选） | 10 道题基线、E-E-A-T + V 雷达图、AI 可见度快照、体检结论、最多 3 条优先动作 | 完整关键词矩阵、90 天路线图、具体 KOL 名单、持续监测 |
| **完整策略** | 需要从诊断走到具体执行方案 | 白话化带图 PDF + Markdown 策略包（HTML 可选） | 快速诊断全部内容、完整 GEO/SEO 策略、竞品分析、KOL/分析师分层名单、路线图 | 持续盯盘、自动告警、周期报告 |
| **持续监测** | 需要长期跟踪和周期汇报 | 动态仪表盘 + 周期 PDF | 完整策略全部内容、舆情与社媒监测、告警、日报/周报/月报、时间序列 | 未确认渠道的外发动作 |

模式执行细则见 `references/work-modes.md`。所有模式均可使用，不与价格绑定。用户明确要求“完整流程”时直接使用**完整策略**；未指定时默认**快速诊断**，需要更多深度时再继续，不使用“付费升级”口径。

### 模式边界

- **快速诊断**：只做一次性体检；最多给 3 条优先动作，不展开完整路线图，不创建任何定时任务。
- **完整策略**：可以启用模块2、模块3、模块8；可准备触达建议，但不得自动外发。
- **持续监测**：可以启用模块4、模块5、模块6 与定时任务；创建任务前仍需确认时间、时区、渠道和失败告警方式。

### PDF 交付收尾（快速诊断/完整策略必做）

画像、评分和关键结论确认后，执行 `references/pdf-delivery.md`：

1. 默认生成一份**中文白话化、带图 PDF**；HTML 只作为用户明确需要时的补充，不替代 PDF。
2. 保留原始分数、证据和“不确定/未采集”标记，不得为了版面完整而补猜。
3. 专业术语第一次出现时必须用一句人话解释；英文搜索问题保留原文，同时给中文释义。
4. 快速诊断仍最多给 3 条优先动作；生成 PDF 不得借机扩展到关键词矩阵、90 天路线图或 KOL 名单。
5. 使用可用的 PDF 专用 skill/工具生成并逐页渲染验收；发现截字、重叠、乱码或误导性图表必须修复后再交付。

---

## ⏰ 定时任务

**本分享版不含任何预置定时任务。**

是否建立、建立哪些，取决于模块1 中 **Q7（巡检频率与报告周期）** 与 **Q8（报告受众与投递渠道）**：

| Q7 答案 | 建议 |
|---|---|
| A / B（每 3h） | 建议建立高频巡检任务 + 失败重试任务 |
| C（每日） | 建议建立每日巡检任务 |
| D（每周） | 建议建立周度回顾任务 |
| E（一次性诊断） | **不建立任何定时任务** |

创建前必须先向用户确认：**执行时间（含时区）、投递渠道、失败时如何告警**。
**未经用户明确同意，不得自动创建任何定时任务。**

---

## 🔴 硬约束与红线

| 约束 | 内容 |
|------|------|
| 🔴 **租户隔离** | 各租户数据绝不互通；每次任务先确认服务对象；跨租户写入由 `scripts/data_ledger.py` 白名单校验直接拒绝 |
| 🔴 **10 道题前置** | 贴出 URL 后必须先完成 10 道题口径确认，才可开始采集；先爬后问会把采集范围搞错 |
| 🔴 **信源熔断** | API 报错 + 重试 2 次仍失败 → 终止 + 红色告警，**不得用记忆编造数据顶上**。定时任务场景：失败则写「当日缺失」占位，不中断时间序列 |
| 🔴 **KOL 真实性** | Handle 必须经 `x.com/{handle}` 实际导航验证；禁止凭 LLM 记忆猜测账号、粉丝数、认证状态 |
| 🔴 **X 搜索频率** | TikHub 可用时无配额限制；降级到 Playwright 时恢复「每日一次」红线，且仅对本次点名要查 X 的租户/竞品执行 |
| 🔴 **证据硬卡** | 任何记录写入前，代码强制校验 snapshot 证据路径存在，否则拒绝写入 |
| 🔴 **原子化落盘** | snapshot 保存 + record 写入同事务完成；半截不入库 |
| 🟡 **数据连续性** | 监测失败写「当日缺失」占位（不静默跳过）；采集一律「先存证据，再做分析」 |
| 🟡 **Token 控制** | 模块8 关键洞察 ≤500 字；模块6 每条观点 ≤200 字 |
| 🟡 **输出语言** | 中文为主，海外专有名词保留原文 |
| 🟡 **隐私** | 不编造联系人邮箱/私人信息；推断内容标注「需验证」 |
| 🟡 **合规表达** | 严格遵守模块1 Q10 确认的红线；涉披露/强监管场景不得写前瞻性承诺 |

**未获授权不得对外发送**：邮件、Slack 消息、DM、发帖等外发动作，须先在对话里确认再执行。

---

## 数据采集能力与降级链

| 信源 | 首选 | 降级 |
|------|------|------|
| X/Twitter、Reddit、微博、小红书、知乎 | **TikHub** (`scripts/tikhub_client.py`) | Playwright → 内置浏览器 → 标注「未采集」 |
| LinkedIn、Stocktwits | Playwright + Cookie（单账号低调潜行） | 内置浏览器工具 → 明确标注「未采集」 |
| 新闻 / 官网 | WebFetch / WebSearch | Tavily (`scripts/tavily_searcher.py`) |
| AI 引擎占位快照 | WebSearch 四引擎 query | 逐引擎标注可用性 |
| 通用搜索 | Tavily API | WebSearch |

⚠️ **首次使用先自检**（缺哪条就走对应降级链，并在报告中标注实际采集方式）：

```bash
python3 -c "import playwright" 2>/dev/null && echo "playwright ✅" || echo "playwright ❌"
python3 -c "
import sys; sys.path.insert(0,'scripts')
import tikhub_client as t
try: t._key(); print('tikhub ✅')
except Exception as e: print('tikhub ❌', e)
"
[ -n "$TAVILY_API_KEY" ] && echo "tavily ✅" || echo "tavily ❌（走 WebSearch，多数场景够用）"
```

`TIKHUB_API_KEY` 缺失 → 社媒检索降级到 Playwright，且「X 每日一次配额」红线重新生效。
`playwright` 缺失 → LinkedIn/Stocktwits 采集与 PDF 导出不可用。
补齐步骤见 `references/setup.md`。

---

## 落盘规范（每个模块结束都要做）

```
data/{tenant}/
├── daily/YYYY-MM-DD_{task}.md    # 每天一个独立文件
├── monthly/YYYY-MM_master.md     # 按月追加
├── ledger/*.csv                  # 结构化时间序列
└── snapshots/YYYY-MM-DD/         # 原始证据留痕
```

**两条铁律**：① 追加，永不重写 ② 先存证据，再做分析。
调用 `scripts/data_ledger.py`，细则见 `references/data-persistence.md`。

---

## 相关 skill

- `hv-analysis` — 横纵分析深度研究（模块8 调用）
- `neat-freak` — 会话收尾时的文档与记忆同步
