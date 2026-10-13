# 环境准备

## 依赖自检

```bash
python3 -V
python3 -c "import jinja2, yaml, requests" 2>/dev/null && echo "jinja2/yaml/requests ✅" || echo "缺依赖 ❌ → pip install jinja2 pyyaml requests"
python3 -c "import playwright" 2>/dev/null && echo "playwright ✅" || echo "playwright ❌"
python3 -c "import sys;sys.path.insert(0,'$HOME/.claude/skills/brand-pr-geo-intelligence/scripts');import tikhub_client as t;t._key();print('TIKHUB_API_KEY ✅')" 2>/dev/null || echo "TIKHUB_API_KEY ❌"
[ -n "$TAVILY_API_KEY" ] && echo "TAVILY_API_KEY ✅" || echo "TAVILY_API_KEY ❌"
```

| 依赖 | 缺失时的影响 |
|---|---|
| jinja2 / pyyaml / requests | **必需**。缺了仪表盘和落盘都跑不了 |
| `TIKHUB_API_KEY` | 社媒检索（X/Reddit/微博/小红书/知乎）降级到 Playwright，X 配额红线重新生效 |
| playwright | LinkedIn/Stocktwits 采集降级到内置浏览器；PDF 导出不可用 |
| `TAVILY_API_KEY` | 通用搜索降级到 WebSearch（多数场景够用） |

## TikHub 配置

密钥读取顺序：环境变量 `TIKHUB_API_KEY` → `~/geo-agent-data/.env`。

```bash
umask 077
echo 'TIKHUB_API_KEY="tk-xxxx"' >> ~/geo-agent-data/.env
chmod 600 ~/geo-agent-data/.env
```

**刻意不放在 skill 目录**——那个目录会被 `cp -R` 打包成分发包，密钥会跟着泄出去。

需要的 scope：`/api/v1/twitter/web/`、`/api/v1/reddit/app/`、
`/api/v1/xiaohongshu/app_v2/`、`/api/v1/weibo/web_v2/`、`/api/v1/zhihu/web/`。

计费约 $0.0026/次调用。余额与 scope 查询：

```bash
curl -s -H "Authorization: Bearer $TIKHUB_API_KEY" \
  https://api.tikhub.io/api/v1/tikhub/user/get_user_info | python3 -m json.tool
```

余额 < $2 时在报告里告警。建立定时任务前先手动跑几次估算日耗。

## 补齐 Playwright（X 采集 + PDF 导出）

```bash
python3 -m pip install playwright && python3 -m playwright install chromium
```

## 配置 Tavily（可选，通用搜索降级方案）

在 `~/.zshrc` 中加入：

```bash
export TAVILY_API_KEY="tvly-xxxxxxxx"
```

## X/Twitter Cookie

Playwright 采集需登录态 Cookie，放在 `~/.claude/skills/brand-pr-geo-intelligence/configs/x_cookies.json`（该文件已在 `.gitignore` 建议清单内，**不要提交到仓库**）。
单账号低调潜行：不并发、每账号 ≤2 页、间隔 ≥3s。

## 租户配置

编辑 `configs/tenants.yaml` 添加你的服务对象。至少填 `slug` / `name` / `site` / `competitors`。

## 数据目录

首次运行会自动在 `configs/tenants.yaml` 的 `data_root`（默认 `~/geo-agent-data`）下创建 `data/{tenant}/` 结构。
