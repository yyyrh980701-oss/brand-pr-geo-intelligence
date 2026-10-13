# 模块3：KOL / 行业分析师推荐

**触发**：KOL / 分析师 / 推荐 / 触达 / 谁适合 / 大V
**前置**：模块2 策略已定（否则不知道要触达什么话题）。

## 候选池

从 `configs/kol_radar_dict.yaml` 分层候选池起手，按本次话题筛选。
词库不够时扩池：中文话题走 TikHub `search xhs|weibo|zhihu` 按话题捞高互动作者，
英文话题走 `search twitter|reddit`，再用 WebSearch 补背景。
**每个新增候选都要走验证流程**，验证通过后回填 `kol_radar_dict.yaml`，越用越准。

## 契合度评分

```
契合度 = 话题匹配度×0.4 + 受众相关度×0.3 + 触达可行性×0.3
```

- **话题匹配度**：近 30 天是否实际发布过相关话题内容（要有具体推文/文章为证）
- **受众相关度**：粉丝画像是否命中目标市场/客群
- **触达可行性**：DM 是否开放、是否有共同连接、是否接商务

## 活跃度门槛

| 最近发布 | 判定 | 是否推荐 |
|---|---|---|
| 24h 内 | 高 | ✅ |
| 7 天内 | 中 | ✅ |
| 超 7 天 | 低 | ❌ 不推荐 |

## 🔴 账号验证红线

**Handle 必须经实际取数确认后才能写入卡片。**
禁止凭 LLM 记忆猜测 handle、粉丝数、认证状态、注册年份——这类字段错一个，整份名单的可信度就归零。

首选 TikHub（结构化、可存证、比页面导航更可靠）：

```bash
python3 scripts/tikhub_client.py profile {handle}   # 粉丝/关注/推文数/认证/注册时间/简介
python3 scripts/tikhub_client.py posts   {handle}   # 近期发帖，验「近30天发过相关内容」
```

返回 `followers`（粉丝）/ `following`（关注）/ `tweet_count` / `blue_verified` /
`verification_type` / `created_at` / `status` / `desc`，直接填卡片。
`--raw` 落 snapshot 存证。TikHub 不可用时回退 `x.com/{handle}` 页面导航。

**僵尸号识别**：`tweet_count` 极低 + `followers` 与头衔严重不符 + `desc` 含
"moved to" / "formerly" → 账号已迁移或废弃，剔除。
（典型形态：某上市公司的旧官号粉丝仅三位数、推文 0、简介写 "Moved to @newhandle"——
凭 LLM 记忆写 handle，就会把一个死号当成公司官号推荐出去。所以必须实际导航验证。）

验证不通过（页面 404 / 已改名 / 已封）→ 从名单剔除，并在报告里列出「已剔除及原因」。
无法验证（网络受限）→ 标注 `⚠️ 未验证`，**不得计入推荐名单**。

## 作战卡片格式

```
### 🗿 [Tier] {KOL名字} (@{Twitter_Handle})
* 当前头衔：
* 主阵地：X (Twitter) | 近期活跃度：高/中
* Twitter 账号验证：✅/❌ 认证状态 · 粉丝数 · 推文数 · 注册年份
* 匹配契合度：XX 分
* 入选认知锚点：(≤100字，说明"为什么是他"，要引用其具体观点)
* ✉️ AI 定制破冰 DM 草稿：(英文，≤20词，极简反问句起手)
* 📋 触达历史：{kol_card_annotation 产出}
```

**DM 草稿规范**：英文、≤20 词、以极简反问句起手、不吹捧、不群发感、给出一个具体的信息钩子。

## 落盘

触达记录 → `ledger/kol_outreach_log.csv`（含验证时的 snapshot 路径）。

## 红线

- 不编造联系人邮箱/私人联系方式；推断的一律标注「需验证」。
- **DM 由用户本人发送**。本 skill 只产出草稿，不代发。
