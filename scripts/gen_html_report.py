#!/usr/bin/env python3
"""JSON → Jinja2 → HTML 仪表盘（可选 Playwright 导 PDF）。

用法:
    python3 gen_html_report.py payload.json out.html [--pdf]

payload.json 结构见 scripts/payload_example.json。
缺采维度用 null，脚本会从总分计算中剔除并在报告标注——不以 0 充数。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jinja2 import Template

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates" / "geo-visibility-dashboard.html"

DIM_LABELS = [("e1", "E₁ 经验"), ("e2", "E₂ 专业度"), ("a", "A 权威度"),
              ("t", "T 信任度"), ("v", "V AI可见度")]


def grade(total: float, n_present: int) -> str:
    """缺采超过 2 维时不给等级——2 个维度算不出一家公司的成绩。
    缺 1–2 维时等级加 ? 后缀，提醒这是不完整样本。"""
    if n_present < 3:
        return "缺采"
    base = "A" if total >= 85 else "B" if total >= 70 else "C" if total >= 50 else "D"
    return base if n_present == 5 else base + "?"


def build(payload: dict) -> str:
    scores = payload.get("scores", {})
    dims, values, missing = [], [], list(payload.get("missing", []))
    for key, label in DIM_LABELS:
        s = scores.get(key)
        dims.append({"key": key, "label": label, "score": s})
        values.append(s)
        if s is None and not any(label in m for m in missing):
            missing.append(label)

    present = [v for v in values if v is not None]
    if len(present) == 5:
        total = round(sum(present), 1)
    elif present:
        # 缺采维度剔除后归一化到 100，并明确标注
        total = round(sum(present) / (len(present) * 20) * 100, 1)
    else:
        total = 0.0

    series = [{"name": payload.get("company", "本品牌"), "value": values}]
    for c in payload.get("competitors", []):
        series.append({"name": c["name"],
                       "value": [c.get("scores", {}).get(k) for k, _ in DIM_LABELS]})
    for p in payload.get("periods", []):  # 多期叠加
        series.append({"name": p["label"],
                       "value": [p.get("scores", {}).get(k) for k, _ in DIM_LABELS]})

    ctx = {
        "title": f"{payload.get('company','')} GEO 仪表盘",
        "company": payload.get("company", ""),
        "tenant": payload.get("tenant", ""),
        "date": payload.get("date", ""),
        # mode 为新字段；保留 tier 回退以兼容旧 payload。
        "mode": payload.get("mode", payload.get("tier", "快速诊断")),
        "mode_meta": payload.get("mode_meta", payload.get("tier_meta", {})),
        "enabled_features": payload.get("enabled_features", []),
        "excluded_features": payload.get("excluded_features", []),
        "summary": payload.get("summary", ""),
        "dims": dims, "total": total, "grade": grade(total, len(present)),
        "n_present": len(present),
        "radar_series": series,
        "ai_snapshots": payload.get("ai_snapshots", []),
        "keywords": payload.get("keywords", []),
        "actions": payload.get("actions", []),
        "evidence": payload.get("evidence", []),
        "missing": missing,
    }
    return Template(TEMPLATE.read_text(encoding="utf-8")).render(**ctx)


def to_pdf(html_path: Path) -> Path | None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("⚠️  playwright 未安装，跳过 PDF。安装：pip install playwright && playwright install chromium",
              file=sys.stderr)
        return None
    pdf = html_path.with_suffix(".pdf")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(html_path.resolve().as_uri())
        pg.wait_for_timeout(2500)  # 等 ECharts 渲染
        pg.pdf(path=str(pdf), format="A4", print_background=True,
               margin={"top": "12mm", "bottom": "12mm", "left": "10mm", "right": "10mm"})
        b.close()
    return pdf


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    out.write_text(build(payload), encoding="utf-8")
    print(f"✅ HTML → {out}")
    if "--pdf" in sys.argv:
        pdf = to_pdf(out)
        if pdf:
            print(f"✅ PDF  → {pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
