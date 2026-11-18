#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Seshat 古政体：规则形式化的长周期（−5300—1800）。

数据：axial_dataset.05.2018.csv，每个 NGA（自然地理区）× 世纪一行，
      12 个 0/0.5/1 指标 + 合计 sum（0—12）。
用法：不假设因果，只回答三件事——
  1) 各制度首次出现的年代分布；
  2) 变化是渐变还是跃变（每世纪增量的分布与集中度）；
  3) 哪几个世纪贡献了大部分变化。

输出
  data/derived/seshat_axial_panel.csv
  data/derived/seshat_rules_summary.json
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "seshat" / "axial_dataset.05.2018.csv"
OUT = ROOT / "data" / "derived"
KEY = ["8. Formal legal code", "9. General applicability of law",
       "10. Constraint on executive", "11. Full-time bureaucrats"]


def main() -> None:
    df = pd.read_csv(SRC, encoding="utf-8-sig")
    df = df.rename(columns={"Date.From": "year"})
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"]).sort_values(["NGA", "year"])

    OUT.mkdir(parents=True, exist_ok=True)
    keep = ["NGA", "year", "sum"] + KEY
    df[keep].to_csv(OUT / "seshat_axial_panel.csv", index=False, encoding="utf-8")

    # 1) 各制度首次出现
    first = {}
    for v in KEY:
        sub = df[(df[v] > 0) & df["year"].notna()]
        first[v] = {
            "n_nga_first": int(sub.groupby("NGA")["year"].min().shape[0]),
            "earliest_year": int(sub["year"].min()) if len(sub) else None,
            "median_first_year": float(np.median(sub.groupby("NGA")["year"].min())) if len(sub) else None,
        }

    # 2) 每世纪增量（同一 NGA 相邻观测）
    d = df.groupby("NGA")["sum"].diff()
    dt = df.groupby("NGA")["year"].diff()
    inc = (d / (dt / 100.0)).replace([np.inf, -np.inf], np.nan).dropna()
    tot_abs = float(inc.abs().sum())
    pos = inc[inc > 0]
    share_top10 = float(pos.nlargest(max(1, int(len(pos) * 0.1))).sum() / pos.sum()) if len(pos) else None
    jumps = float((inc.abs() >= 1.0).mean())

    # 3) 世纪贡献
    df["century"] = (np.floor(df["year"] / 100) * 100).astype(int)
    cent = df.groupby("century")["sum"].mean()
    top_cent = cent.diff().abs().nlargest(6)

    summary = {
        "source": "Seshat axial_dataset.05.2018.csv",
        "n_rows": int(len(df)),
        "n_nga": int(df["NGA"].nunique()),
        "year_min": int(df["year"].min()),
        "year_max": int(df["year"].max()),
        "index_range": [float(df["sum"].min()), float(df["sum"].max())],
        "first_appearance": first,
        "n_transitions": int(len(inc)),
        "mean_change_per_century": round(float(inc.mean()), 3),
        "sd_change_per_century": round(float(inc.std()), 3),
        "share_abs_change_ge_1": round(jumps, 4),
        "top10pct_share_of_positive_change": round(share_top10, 3) if share_top10 else None,
        "top_centuries_by_abs_change_in_mean_index": [
            {"century": int(c), "delta": round(float(v), 3)} for c, v in top_cent.items()],
        "caveat": "Seshat 的指标是专家编码的 0/0.5/1，且观测按世纪对齐；"
                  "'跃变'是本数据集内的增量，不等于历史上没有更慢的过程。",
    }
    (OUT / "seshat_rules_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
