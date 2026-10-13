# 数据持久化规范

## 目录结构

```
data/{tenant}/
├── daily/                      # 每天一个独立文件，永不覆盖
│   └── 2026-08-20_geo-monitor.md
├── monthly/                    # 按月追加，用于连续通读与复盘
│   └── 2026-08_master.md
├── ledger/                     # 结构化时间序列（CSV，仅追加）
│   ├── eeatv_scores.csv        # date,tenant,e1,e2,a,t,v,total,grade,snapshot
│   ├── kol_outreach_log.csv    # date,tenant,handle,tier,action,status,snapshot
│   ├── sentiment_timeline.csv  # date,tenant,source,polarity,volume,note,snapshot
│   └── capture_health.csv      # date,tenant,source,status,items,error
└── snapshots/                  # 原始证据留痕
    └── 2026-08-20/
        ├── x_competitor_a.json
        └── site_yourbrand.md
```

## 两条铁律

1. **追加，永不重写** —— 全部 append 模式 + 日期文件名。发现写错，追加一条更正记录，不要回改历史。
2. **先存证据，再做分析** —— 原始数据先落 `snapshots/`，再进 LLM 分析。

## 证据硬卡

`append_record()` 强制校验 `snapshot` 参数指向的文件真实存在，否则 `raise`。
「禁止编造」从 prompt 约束升级为**代码层物理拦截**——写不进去，就是写不进去。

## 原子化

snapshot 落盘 + record 写入必须同一事务完成：先写 snapshot（成功才继续），再写 record；record 失败则记 `capture_health.csv` 一条 error，不留半截数据。

## 缺采占位

采集失败**不静默跳过**。写一条：
```
date,tenant,source,status,items,error
2026-08-20,yourbrand,x_twitter,MISSING,0,"playwright not installed"
```
时间序列的连续性比单日数据更值钱——缺口必须看得见。

## 用法

```python
from scripts.data_ledger import append_record, save_snapshot, append_daily

p = save_snapshot("yourbrand", "x_competitor_a.json", raw_json)   # 先存证据
append_record("yourbrand", "eeatv_scores.csv", row, snapshot=p)      # 再写记录
append_daily("yourbrand", "geo-monitor", markdown_body)
```
