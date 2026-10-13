#!/usr/bin/env python3
"""GEO 情报数据持久化层。

两条铁律：
  1. 追加，永不重写
  2. 先存证据，再做分析

三道硬卡（代码层拦截，不靠 prompt 自觉）：
  - 租户白名单：跨租户写入 raise TenantViolation
  - 证据硬卡：append_record 校验 snapshot 路径真实存在，否则 raise MissingEvidence
  - 原子化：snapshot 写成功才允许写 record
"""
from __future__ import annotations

import csv
import datetime as _dt
import json
import os
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parent.parent
TENANTS_FILE = SKILL_DIR / "configs" / "tenants.yaml"


class TenantViolation(RuntimeError):
    """试图写入未注册的租户，或跨租户写入。"""


class MissingEvidence(RuntimeError):
    """记录缺少可核验的 snapshot 证据。"""


def _config() -> dict:
    if not TENANTS_FILE.exists():
        raise TenantViolation(f"租户配置缺失：{TENANTS_FILE}")
    return yaml.safe_load(TENANTS_FILE.read_text(encoding="utf-8")) or {}


def data_root() -> Path:
    cfg = _config()
    root = os.environ.get("GEO_AGENT_DATA_ROOT") or cfg.get("data_root", "~/geo-agent-data")
    return Path(root).expanduser()


def tenant_slugs() -> list[str]:
    return [t["slug"] for t in _config().get("tenants", []) if t.get("slug")]


def tenant_config(tenant: str) -> dict:
    for t in _config().get("tenants", []):
        if t.get("slug") == tenant:
            return t
    raise TenantViolation(
        f"租户 '{tenant}' 不在白名单中。已注册：{tenant_slugs() or '（无）'}。"
        f"请先在 {TENANTS_FILE} 注册。"
    )


def tenant_dir(tenant: str) -> Path:
    tenant_config(tenant)  # 白名单校验，未注册直接 raise
    d = data_root() / "data" / tenant
    for sub in ("daily", "monthly", "ledger", "snapshots"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    return d


def _today() -> str:
    return _dt.date.today().isoformat()


# ---------------------------------------------------------------- snapshots

def save_snapshot(tenant: str, filename: str, content, date: str | None = None) -> Path:
    """先存证据。返回 snapshot 绝对路径，用于随后的 append_record。"""
    date = date or _today()
    d = tenant_dir(tenant) / "snapshots" / date
    d.mkdir(parents=True, exist_ok=True)
    path = d / filename
    if isinstance(content, (dict, list)):
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        path.write_text(str(content), encoding="utf-8")
    if path.stat().st_size == 0:
        path.unlink()
        raise MissingEvidence(f"snapshot 内容为空，已删除：{path}")
    return path


# ---------------------------------------------------------------- ledger

def append_record(tenant: str, ledger: str, row: dict, snapshot: str | Path) -> Path:
    """追加一条结构化记录。snapshot 必须真实存在，否则拒绝写入。"""
    snap = Path(snapshot).expanduser()
    if not snap.is_absolute():
        snap = tenant_dir(tenant) / "snapshots" / snap
    if not snap.exists():
        raise MissingEvidence(
            f"证据硬卡：snapshot 不存在 → {snap}\n"
            "记录被拒绝写入。请先 save_snapshot() 落原始证据，再写记录。"
        )

    path = tenant_dir(tenant) / "ledger" / ledger
    row = {"date": row.get("date", _today()), "tenant": tenant, **row,
           "snapshot": str(snap.relative_to(data_root())) if str(snap).startswith(str(data_root())) else str(snap)}
    if row.get("tenant") != tenant:
        raise TenantViolation(f"跨租户写入被拒绝：row.tenant={row.get('tenant')} != {tenant}")

    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if is_new:
            w.writeheader()
        w.writerow(row)
    return path


def append_missing(tenant: str, source: str, error: str, date: str | None = None) -> Path:
    """采集失败占位——不静默跳过，缺口必须看得见。

    这是唯一免除证据硬卡的写入路径：缺采本身就意味着没有证据。
    """
    path = tenant_dir(tenant) / "ledger" / "capture_health.csv"
    row = {"date": date or _today(), "tenant": tenant, "source": source,
           "status": "MISSING", "items": 0, "error": error}
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if is_new:
            w.writeheader()
        w.writerow(row)
    return path


# ---------------------------------------------------------------- narrative

def append_daily(tenant: str, task: str, body: str, date: str | None = None) -> Path:
    """每天一个独立文件 + 同步追加进当月 master。"""
    date = date or _today()
    path = tenant_dir(tenant) / "daily" / f"{date}_{task}.md"
    stamp = _dt.datetime.now().strftime("%H:%M")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n<!-- appended {date} {stamp} -->\n{body}\n")
    monthly = tenant_dir(tenant) / "monthly" / f"{date[:7]}_master.md"
    with monthly.open("a", encoding="utf-8") as f:
        f.write(f"\n\n## {date} · {task}\n{body}\n")
    return path


def read_series(tenant: str, ledger: str) -> list[dict]:
    path = tenant_dir(tenant) / "ledger" / ledger
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


if __name__ == "__main__":
    print("data_root:", data_root())
    print("tenants  :", tenant_slugs() or "（未配置）")
