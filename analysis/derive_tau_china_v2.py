#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""中国侧 τ：两批事件合到一起算（2016—2022 与 2023—2026）。

两批的来源不同，精度也不同，所以**不能直接混着算中位数**：
  2016—2022（27 条）来自 `Rachel74mx/reversed_weibo_event`，字段是 begin/fbegin/fend，**全部到日**。
  2023—2026（20 条）来自作者按公开报道整理（`docs/events_china_2023-2026.tsv`），
      其中只有 6 条三个日期都到日，其余缺「首次曝光日」——**这恰恰是 τ 的结构性困难**：
      曝光时间戳只存在平台侧，新闻里只有报道日。

口径
  τ = 反转/纠错日 − 首次曝光日（天）
  只对两端都有「日」精度的事件算 τ；月/年级的另列，不并入中位数。

输出
  data/derived/events_china.csv   合并后的事件表（含精度列与 τ）
  data/derived/tau_by_era.json    两组分布 + 分类型

纪律
  样本是**便利样本**（都有明确反转），不是代表性抽样。所有分位数只读作"这批事件的形状"。
"""
from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "data" / "derived" / "tau_china.csv"           # 2016—2022（27 条）
NEW = ROOT / "docs" / "events_china_2023-2026.tsv"          # 2023—2026（20 条）
OUT = ROOT / "data" / "derived" / "events_china.csv"
SUMMARY = ROOT / "data" / "derived" / "tau_by_era.json"


def parse(d: str, prec: str) -> date | None:
    """只在精度为『日』时返回日期；月/年一律当缺失（不插值）。"""
    if prec != "日" or not d or d.count("-") != 2:
        return None
    y, m, dd = (int(x) for x in d.split("-"))
    return date(y, m, dd)


def main() -> None:
    rows = []

    old = pd.read_csv(OLD, encoding="utf-8-sig")
    for _, r in old.iterrows():
        rows.append({"era": "2016-2022", "id": f"O{len(rows) + 1:02d}", "name": r["event"],
                     "type": "舆论-通报", "expose": r["begin"],
                     "reversal": str(r["first_reversal"])[:10],
                     "tau_days": round(float(r["tau_low_days"]), 2),
                     "precision": "日", "source": "reversed_weibo_event"})

    new = pd.read_csv(NEW, sep="\t", encoding="utf-8")
    for _, r in new.iterrows():
        ex = parse(str(r["曝光日"]), str(r["曝光精度"]))
        rv = parse(str(r["反转或纠错日"]), str(r["反转精度"]))
        tau = (rv - ex).days if (ex and rv) else None
        rows.append({"era": "2023-2026", "id": r["id"], "name": r["名称"], "type": r["类型"],
                     "expose": r["曝光日"], "reversal": r["反转或纠错日"],
                     "tau_days": tau,
                     "precision": f"{r['曝光精度']}/{r['反转精度']}",
                     "source": "author-collected",
                     "missing": r["缺什么"]})

    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")

    def dist(t: np.ndarray) -> dict:
        if len(t) == 0:
            return {"n": 0}
        return {"n": int(len(t)), "median": round(float(np.median(t)), 2),
                "p25": round(float(np.percentile(t, 25)), 2),
                "p75": round(float(np.percentile(t, 75)), 2),
                "p90": round(float(np.percentile(t, 90)), 2),
                "min": round(float(t.min()), 2), "max": round(float(t.max()), 2),
                "share_le_2": round(float((t <= 2).mean()), 3),
                "share_gt_30": round(float((t > 30).mean()), 3)}

    summary = {}
    for era, g in out.groupby("era"):
        d = g["tau_days"].dropna().values.astype(float)
        summary[era] = dist(d)
        print(f"== {era}   可算 τ 的 {len(d)}/{len(g)} 条")
        if len(d):
            print(f"   中位 {np.median(d):.1f} 天 | P25 {np.percentile(d, 25):.1f} | "
                  f"P90 {np.percentile(d, 90):.1f} | 最大 {d.max():.0f} | τ≤2天 {(d <= 2).mean() * 100:.0f}%")

    g3 = out[out.era == "2023-2026"]
    summary["2023-2026_by_type"] = {}
    for t, gg in g3.groupby("type"):
        d = gg["tau_days"].dropna().values.astype(float)
        summary["2023-2026_by_type"][t] = dist(d)
        tag = f"中位 {np.median(d):.0f} 天" if len(d) else "无可算"
        print(f"   {t}: 可算 {len(d)}/{len(gg)} 条，{tag}")

    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("→", OUT)


if __name__ == "__main__":
    main()
