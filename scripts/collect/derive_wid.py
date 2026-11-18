#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""WID（世界不平等数据库）财富份额：给「全球 1% 占 X% 财富」这句断言找口径。

为什么需要
  `CLAIMS-AUDIT.md` #12 把「全球 1% 占 43.8%、底层 50% 占 0.52%」列为**不可核**。
  这句是可核的，但它有两个口径，差 8 个百分点：
    WID（国民账户 + 财富收入比推算）
    UBS/Credit Suisse《全球财富报告》（家庭调查口径）
  不写清用哪一个，数字就永远「对不上」。

做法
  拉 WID 逐国 bulk CSV（`https://wid.world/bulk_download/WID_data_{CC}.csv`），
  取 `shwealj992`（净财富份额，等值调整），百分位 `p99p100`（前 1%）与 `p0p50`（后 50%）。

输出
  data/derived/wid_wealth_share.csv   country, year, top1, bottom50, top10

纪律
  WID 是 A 级（方法公开、逐年更新），但**不能与 UBS 的数字混用**。
  两者口径不同：WID 含公共养老金与国民账户调整，UBS 只算家庭净财富。
"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "wid"
OUT = ROOT / "data" / "derived" / "wid_wealth_share.csv"
CODES = {"WO": "世界", "CN": "中国", "US": "美国"}
# WID 的变量名并不统一：世界级用 `shwealj992`，国家级用 `shweal992j`（等值调整）
VARIANTS = ["shwealj992", "shweal992j"]


def main() -> None:
    rows = []
    for code, name in CODES.items():
        p = RAW / f"WID_data_{code}.csv"
        if not p.exists():
            print(f"missing {p}")
            continue
        d = pd.read_csv(p, sep=";", usecols=[0, 1, 2, 3, 4], on_bad_lines="skip")
        var = next((v for v in VARIANTS if v in set(d.variable.dropna())), None)
        if var is None:
            print(f"no shweal variable in {p}")
            continue
        s = d[(d.variable == var) & (d.percentile.isin(["p99p100", "p0p50", "p90p100"]))]
        w = s.pivot_table(index="year", columns="percentile", values="value")
        for y, r in w.iterrows():
            if pd.isna(r.get("p99p100")):
                continue
            rows.append({"region": name, "code": code, "year": int(y),
                         "top1": round(r.get("p99p100", float("nan")), 4),
                         "bottom50": round(r.get("p0p50", float("nan")), 4),
                         "top10": round(r.get("p90p100", float("nan")), 4)})
    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"{'地区':6}{'年份':>6}{'前1%':>9}{'后50%':>9}{'前10%':>9}")
    for code, name in CODES.items():
        g = out[out.code == code]
        if g.empty:
            continue
        first, last = g.iloc[0], g.iloc[-1]
        print(f"{name:6}{int(first.year):>6}{first.top1:>8.1%}{first.bottom50:>9.1%}{first.top10:>9.1%}")
        print(f"{'':6}{int(last.year):>6}{last.top1:>8.1%}{last.bottom50:>9.1%}{last.top10:>9.1%}")
    print("→", OUT)


if __name__ == "__main__":
    main()
