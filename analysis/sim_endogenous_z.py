#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A18：把 `z` 写成网络的函数——全链最后一处“从外面借参数”的收口。

问题：群体层的门槛是 `γ·z > δ`，社会层的一切（χ、迟滞、预警）都通过 `z` 接进来，
但 `z`（能把码传出去、能看见你偏离的人数）一直是一个外生参数。这一节把它写成
**网络 + 可分辨度**的函数，并检查它会不会让系统出现两个稳定构型。

写法（一条式子）
    z_i(q) = Σ_j W_ij · 1{ |q_i − q_j| ≥ d }
  —— 只有**能被看出来的差别**才算执行范围：分辨率粗到看不出差别的邻居，
     不会罚你。于是"粗码"自带一个副作用：**它更难被检查**。

模拟（60 人环 + 双向重连，粒度 k 从 {2,3,4,6,8,12} 里选）
  收益 = −w·c/k² − τ·log₂k − γ·z_i
  异步最优回应，随机次序，跑到不动点；从"全粗"与"全细"两个初值各跑一遍。

判法（先写死）
  P-Z1：两个初值收敛到不同不动点 ⇒ 双稳（“粗码 + 低执行”与“细码 + 高执行”各是一个解）；
  P-Z2：把可分辨阈值 d 从 1 抬到 2（粗码之间看不出差别），粗不动点更容易被逃出
        ⇒ “粗码自我加固”是 d 的函数；
  P-Z3：d 越低（观测越清），细不动点越占优 ⇒ **提高可观测性会把均衡推向细码**。

输出 data/derived/endogenous_z.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "endogenous_z.json"

GRID = [2, 3, 4, 6, 8, 12]
W_COST = 1.0      # w·c：失真项的系数
TAU = 0.05        # 描述费 τ（每块的 log 成本）
GAMMA = 0.15      # 每有一个"看得出差别"的邻居所付的一致性代价


def build_graph(n: int = 60, rewire: float = 0.1, hubs: int = 3,
                seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    W = np.zeros((n, n))
    for i in range(n):
        W[i, (i + 1) % n] = W[(i + 1) % n, i] = 1.0
    for _ in range(int(rewire * n)):
        i, j = rng.integers(0, n, 2)
        if i != j:
            W[i, j] = W[j, i] = 1.0
    for h in rng.choice(n, hubs, replace=False):
        for j in rng.choice(n, 6, replace=False):
            if j != h:
                W[h, j] = W[j, h] = 1.0
    return W


def payoff(k_i: float, ks: np.ndarray, W_i: np.ndarray, d: int, wi: float = 1.0) -> float:
    z = float(np.sum(W_i * (np.abs(ks - k_i) >= d)))
    dist = wi * W_COST / k_i ** 2
    cost = TAU * np.log2(k_i)
    return -dist - cost - GAMMA * z


def run(k0: int, d: int = 1, n: int = 60, sweeps: int = 120, seed: int = 0) -> dict:
    W = build_graph(n=n, seed=seed)
    rng = np.random.default_rng(seed + 100)
    w = np.exp(rng.normal(0, 0.8, n))          # 每个人的“错了多疼”不同
    k = np.full(n, float(k0))
    for s in range(sweeps):
        changed = 0
        order = rng.permutation(n)
        for i in order:
            best, bestv = k[i], payoff(k[i], k, W[i], d, w[i])
            for cand in GRID:
                v = payoff(float(cand), k, W[i], d, w[i])
                if v > bestv + 1e-12:
                    best, bestv = float(cand), v
            if best != k[i]:
                k[i] = best
                changed += 1
        if changed == 0:
            break
    z = np.array([np.sum(W[i] * (np.abs(k - k[i]) >= d)) for i in range(n)])
    return {"start_k": k0, "d": d, "mean_k": round(float(k.mean()), 2),
            "sd_k": round(float(k.std()), 2), "mean_z": round(float(z.mean()), 2),
            "share_at_start": round(float(np.mean(k == k0)), 2),
            "distribution": {str(g): int((k == g).sum()) for g in GRID}}


def main() -> None:
    res: dict = {}
    # P-Z1 双稳：两个初值
    res["bistability_d1"] = [run(2, d=1, seed=1), run(8, d=1, seed=1)]
    # P-Z2/P-Z3 可分辨阈值
    res["by_threshold"] = {str(d): [run(2, d=d, seed=1), run(8, d=d, seed=1)]
                           for d in (1, 2, 3)}
    # 观测变清（d 降到 0＝任何差别都看得见）会让细码占优吗
    res["perfect_observability"] = [run(2, d=0, seed=1), run(8, d=0, seed=1)]
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()
