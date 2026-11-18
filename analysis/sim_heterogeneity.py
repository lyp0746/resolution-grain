#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A21：异质性不是噪声——它是“变异库”，也是“平滑剂”。

作者观察：异质性在爱、创新、进化里都在起作用。这一节把它写成模型里的两件可算的事。

**第一件：异质性把总量抹平（个体成团，总量平滑）。**
  两千个个体，各有自己的翻越阈值；同一条外生推力推过来，个体是“到点就跳”，
  总量却是平滑的。⇒ **在总量上看不到“闸口”，不是因为闸口不存在，是因为它们不对齐。**
  （这正是 A15 的读数：年度总量 CV 5.4%，而节级间隔 B=−0.20。）

**第二件：异质性让“部分采纳”成为常态。**
  个体的 `w` 不同 ⇒ 最优粒度不同 ⇒ 同一个共同体里同时存在几种码。
  ⇒ **同一个共同体里几种粒度并存不是错误，是异质性的稳态。**
  这也把第 26 章第五件（新码从哪里来）从“框架内不能”改成“能给一半”：
  **变异的库是异质性的尾部；方向仍不能给。**

判法（先写死）
  P-H1：阈值离散度 σ 越大，总量曲线的最大跳幅越小 ⇒ 平滑是异质性造的；
  P-H2：`w` 的离散度越大，均衡时不同粒度的种类越多、最大一份的份额越小 ⇒ 部分采纳。

输出 data/derived/heterogeneity.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "heterogeneity.json"
RNG = np.random.default_rng(20261118)


def aggregate_smoothness(n: int = 2000, sigmas=(0.05, 0.3, 1.0), grid: int = 400) -> dict:
    """每个个体有一个翻越阈值；共同推力走过时，量总量的最大跳幅。"""
    x = np.linspace(-3, 3, grid)
    out = {}
    for s in sigmas:
        thr = np.exp(RNG.normal(0, s, n))
        # 个体在 x > thr 时“开”；总量 = 开启比例
        agg = np.array([(x > 0).sum() for _ in range(1)])  # 占位，下面逐点算
        agg = np.array([np.mean(xv > thr) for xv in x])
        jump = float(np.max(np.diff(agg)))
        out[f"sigma={s}"] = {"max_jump": round(jump, 4),
                             "sd_of_agg": round(float(agg.std()), 3),
                             "share_at_end": round(float(agg[-1]), 3)}
    return out


def partial_adoption(wsigmas=(0.0, 0.5, 1.0), n: int = 800, gamma: float = 0.15) -> dict:
    """w 不同 ⇒ 最优粒度不同；数均衡时的种类数与最大份额。"""
    grid = np.array([2, 3, 4, 6, 8, 12], dtype=float)
    out = {}
    for s in wsigmas:
        w = np.exp(RNG.normal(0, s, n))
        # 无一致性项时的最优粒度（近邻耦合先不计，只看“个体偏好”的分布）
        payoff = -w[:, None] * 1.0 / grid[None, :] ** 2 - 0.05 * np.log2(grid)[None, :]
        best = grid[np.argmax(payoff, axis=1)]
        vals, cnt = np.unique(best, return_counts=True)
        out[f"wsigma={s}"] = {"n_distinct": int(len(vals)),
                              "max_share": round(float(cnt.max() / n), 3),
                              "distribution": {str(int(v)): int(c) for v, c in zip(vals, cnt)}}
    return out


def optimal_heterogeneity(sigmas=None, n: int = 4000, reps: int = 40) -> dict:
    """异质性有最优值：太少没有变异，太多没有共享码。"""
    if sigmas is None:
        sigmas = [0.0, 0.15, 0.3, 0.45, 0.6, 0.8, 1.0, 1.2, 1.5]
    grid = np.array([2, 3, 4, 6, 8, 12], dtype=float)
    rows = []
    for s in sigmas:
        share_ok, tail = [], []
        for _ in range(reps):
            w = np.exp(RNG.normal(0, s, n))
            payoff = -w[:, None] / grid[None, :] ** 2 - 0.05 * np.log2(grid)[None, :]
            best = grid[np.argmax(payoff, axis=1)]
            vals, cnt = np.unique(best, return_counts=True)
            share_ok.append(cnt.max() / n)
            tail.append(float(np.mean(best >= 8)))     # “细”的那一端
        rows.append({"sigma": s,
                     "modal_share": round(float(np.mean(share_ok)), 3),
                     "tail_mass": round(float(np.mean(tail)), 3)})
    # 收益：共享码的价值（A=1）× P(多数一致) + 变异的收益（B/A 取几档）× 尾部质量
    # 共享码是“有／没有”：多数份额过半才有一份公共码（对应 γz>δ 的门槛）
    out = {}
    for ratio in (0.5, 1.0, 2.0, 4.0):
        vals = []
        for r in rows:
            coord = 1.0 if r["modal_share"] > 0.5 else 0.0
            vals.append((r["sigma"], coord + ratio * r["tail_mass"], coord))
        sig, v, coord = max(vals, key=lambda t: t[1])
        out[f"B_over_A={ratio}"] = {"sigma_star": sig, "value": round(v, 3),
                                    "shared_code_at_star": bool(coord > 0),
                                    "interior": bool(0 < sig < rows[-1]["sigma"])}
    return {"rows": rows, "optima": out}


def main() -> None:
    res = {"A_aggregate": aggregate_smoothness(),
           "B_partial": partial_adoption(),
           "C_optimum": optimal_heterogeneity()}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
