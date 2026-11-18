#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Seshat 拆分检验 v2：形式化规则（A）与道德化规范（B）是否错开。

v1 的错误：把世纪网格插值后做互相关，结果所有滞后都在 −0.20 附近——
那是插值造成的自相关，不是历史信号。v2 只用**观测到的相邻行**，不做任何插值。

四个检验
  1) 首现次序：同一 NGA 里，A 与 B 谁先 >0；
  2) 同行相关：相邻观测的 ΔA 与 ΔB 的相关（同期）；
  3) 领先检验：ΔB(t) 对 ΔA(t+1) 的相关（下一观测）；
  4) 同步跳变：|ΔA|≥1 的转移中，|ΔB|≥1 的比例 vs 全体比例（置换基线）。

输出 data/derived/seshat_split_v2.json + seshat_pairs.csv
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

    # 1) 首现次序
    order = {}
    for nga, g in df.groupby("NGA"):
        ag = g[g["A"] > 0]["year"]
        bg = g[g["B"] > 0]["year"]
        if len(ag) and len(bg):
            order[nga] = {"A_first": int(ag.min()), "B_first": int(bg.min())}
    b_before_a = sum(1 for v in order.values() if v["B_first"] < v["A_first"])
    a_before_b = sum(1 for v in order.values() if v["A_first"] < v["B_first"])
    same = len(order) - b_before_a - a_before_b

    # 2/3) 相邻观测的差分
    rows = []
    for nga, g in df.groupby("NGA"):
        g = g.sort_values("year").reset_index(drop=True)
        dA, dB, dy = g["A"].diff(), g["B"].diff(), g["year"].diff()
        for i in range(1, len(g)):
            if pd.isna(dA[i]) or pd.isna(dB[i]):
                continue
            rows.append({"NGA": nga, "year": int(g["year"][i]), "dt": int(dy[i]),
                         "dA": dA[i], "dB": dB[i],
                         "A": g["A"][i], "B": g["B"][i]})
    p = pd.DataFrame(rows)
    p.to_csv(OUT / "seshat_pairs.csv", index=False, encoding="utf-8")

    same_period = float(p["dA"].corr(p["dB"]))
    # 领先：把同一 NGA 的 dB 上移一行，对应下一观测的 dA
    lead = []
    for nga, g in p.groupby("NGA"):
        g = g.sort_values("year")
        lead.append(pd.DataFrame({"dB_t": g["dB"].values[:-1], "dA_t1": g["dA"].values[1:]}))
    lp = pd.concat(lead).dropna()
    lead_corr = float(lp.corr().iloc[0, 1]) if len(lp) > 20 else None

    # 4) 同步跳变 vs 基线
    ja = p["dA"].abs() >= 1
    jb = p["dB"].abs() >= 1
    base = float(jb.mean())
    cond = float(jb[ja].mean()) if ja.sum() else None
    # 置换基线
    rng = np.random.default_rng(7)
    null = [float(jb.sample(frac=1, random_state=int(s)).values[ja.values].mean()) for s in rng.integers(0, 10**6, 500)]

    summary = {
        "source": "Seshat axial_dataset.05.2018.csv",
        "n_transitions": int(len(p)),
        "first_appearance_order": {
            "n_nga": len(order),
            "B_before_A": b_before_a, "A_before_B": a_before_b, "same_year": same,
            "detail": order,
        },
        "corr_dA_dB_same_transition": round(same_period, 3),
        "corr_dB_t_with_dA_next": round(lead_corr, 3) if lead_corr is not None else None,
        "jump_sync": {
            "share_any_dB_jump": round(base, 3),
            "share_dB_jump_given_dA_jump": round(cond, 3) if cond is not None else None,
            "permutation_mean": round(float(np.mean(null)), 3),
            "permutation_p_two_sided": round(float(np.mean(np.abs(np.array(null) - base) >= abs(cond - base))), 3) if cond is not None else None,
        },
        "caveat": "两组指标来自同一批专家编码，且样本仅 10 个 NGA；"
                  "相关不能当因果，只能当'两条线是否同拍'的粗检。",
    }
    (OUT / "seshat_split_v2.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
