#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Seshat 拆分检验：形式化规则 vs 道德化规范，两条线是否错开。

A 形式化规则：8 成文法典、9 法律普遍适用、10 约束行政、11 常设官僚
B 道德化规范：1 道德惩罚、2 道德化规范、3 亲社会促进、4 全知超自然、
              5 统治者非神、6 精英=平民、7 统治者=平民
（12 弹劾归 A：它是程序性约束）

做法
  1) 各 NGA 的两组首次出现年代；
  2) 把年份压到世纪网格，对每个世纪取跨 NGA 的均值 → 两条世纪序列；
  3) 一阶差分后做互相关，找使相关最大的滞后 k（正 = B 领先 A）；
  4) 组内先行检验：同一 NGA 内 B 的增量能否预测 k 个世纪后的 A 增量。

输出
  data/derived/seshat_split.csv
  data/derived/seshat_split_summary.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "seshat" / "axial_dataset.05.2018.csv"
OUT = ROOT / "data" / "derived"

A = ["8. Formal legal code", "9. General applicability of law",
     "10. Constraint on executive", "11. Full-time bureaucrats", "12. Impeachment"]
B = ["1. Moralistic punishment", "2. Moralizing norms", "3. Promotion of prosociality",
     "4. Omniscient supernatural beings", "5. Rulers not gods",
     "6. Equating elites and commoners", "7. Equating rulers and commoners"]


def main() -> None:
    df = pd.read_csv(SRC, encoding="utf-8-sig").rename(columns={"Date.From": "year"})
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"]).sort_values(["NGA", "year"])
    df["A"] = df[A].sum(axis=1, min_count=1)
    df["B"] = df[B].sum(axis=1, min_count=1)
    df["century"] = (np.floor(df["year"] / 100) * 100).astype(int)

    # 1) 首次出现
    def first(col):
        s = df[(df[col] > 0) & df[col].notna()].groupby("NGA")["year"].min()
        return {"n_nga": int(s.shape[0]),
                "earliest": int(s.min()) if len(s) else None,
                "median": float(np.median(s)) if len(s) else None}

    # 2) 世纪网格均值
    grid = df.groupby("century")[["A", "B"]].mean().sort_index()
    grid = grid.reindex(range(int(grid.index.min()), int(grid.index.max()) + 1, 100))
    grid = grid.interpolate(limit_direction="both")
    dA, dB = grid["A"].diff(), grid["B"].diff()

    # 3) 互相关（正滞后 = B 领先）
    lags = range(-8, 9)
    xc = {}
    for k in lags:
        if k >= 0:
            a, b = dA.iloc[k:], dB.iloc[:len(dB) - k]
        else:
            a, b = dA.iloc[:len(dA) + k], dB.iloc[-k:]
        pair = pd.concat([a, b], axis=1).dropna()
        if len(pair) > 12:
            xc[k] = round(float(pair.corr().iloc[0, 1]), 3)
    best_k = max(xc, key=lambda k: xc[k]) if xc else None

    # 4) 组内先行（同 NGA，B 领先 k 期）
    within = {}
    for k in range(0, 5):
        pairs = []
        for _, g in df.groupby("NGA"):
            g = g.sort_values("year")
            a = g["A"].diff().values
            b = g["B"].diff().values
            if len(a) > k + 2:
                pairs.append(pd.DataFrame({"a": a[k:], "b": b[:len(b) - k]}).dropna())
        if pairs:
            p = pd.concat(pairs)
            if len(p) > 20:
                within[k] = round(float(p.corr().iloc[0, 1]), 3)

    grid.to_csv(OUT / "seshat_split.csv", encoding="utf-8")
    summary = {
        "source": "Seshat axial_dataset.05.2018.csv",
        "groups": {"A_formal": A, "B_moralizing": B},
        "first_appearance": {"A": first("A"), "B": first("B")},
        "n_centuries": int(grid.index.min() // 100), "span": [int(grid.index.min()), int(grid.index.max())],
        "crosscorr_dA_dB": {str(k): v for k, v in sorted(xc.items())},
        "best_lag_centuries": best_k,
        "best_corr": xc.get(best_k) if best_k is not None else None,
        "within_nga_B_leads_A": {str(k): v for k, v in within.items()},
        "caveat": "两组指标都来自同一批专家编码，相关可能来自编码习惯而非历史过程；"
                  "世纪网格是插值后的近似，滞后以世纪为单位。",
    }
    (OUT / "seshat_split_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
