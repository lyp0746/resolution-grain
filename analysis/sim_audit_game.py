#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A20：`d`（可分辨度）从哪来——把检查者也写成一个做选择的人。

A.16 把执行范围写成 `z=Σ W·1{|Δq|≥d}`，但 `d` 还是外生。这一节把 `d` 接上去：
**`d` 就是检查者的分辨率**（差到几格才看得见），而检查者的分辨率本身是一个选择——
查得越细越贵。

两方博弈
  编码者：在自己那格粒度 k 上最优回应，付 `w·c/k² + τ·log k + γ·z(k; r)`；
  检查者：选分辨率 r，付 `α/r`（越细越贵），收益是被看出来的差别数。
  外层交替最优回应：编码者先动若干轮，检查者再动，如此交替。

判法（先写死）
  P-R1：若交替收敛到一对 (r*, k*)，则 `d` 也是内生的，全链闭合；
  P-R2：若来回摆（周期 2 或更长），那就是**可观测性的军备竞赛**——看得越清，码越细，
        查起来越贵，于是放松，于是码回粗……这是反身性在测量端的第二个后果。

输出 data/derived/audit_game.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "audit_game.json"

GRID = [2, 3, 4, 6, 8, 12]
W_COST, TAU, GAMMA = 1.0, 0.05, 0.15
ALPHA = 0.03          # 检查者：分辨率的成本 α/r
AUDIT_W = 0.05        # 每看出一处差别，检查者得的收益


def graph(n: int = 40, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    W = np.zeros((n, n))
    for i in range(n):
        W[i, (i + 1) % n] = W[(i + 1) % n, i] = 1.0
    return W


def coder_sweep(k: np.ndarray, W: np.ndarray, w: np.ndarray, r: int, sweeps: int = 30) -> np.ndarray:
    n = len(k)
    rng = np.random.default_rng(7)
    for _ in range(sweeps):
        changed = 0
        for i in rng.permutation(n):
            def val(cand: float) -> float:
                z = float(np.sum(W[i] * (np.abs(k - cand) >= r)))
                return -w[i] * W_COST / cand ** 2 - TAU * np.log2(cand) - GAMMA * z
            best, bestv = k[i], val(k[i])
            for cand in GRID:
                v = val(float(cand))
                if v > bestv + 1e-12:
                    best, bestv = float(cand), v
            if best != k[i]:
                k[i], changed = best, changed + 1
        if not changed:
            break
    return k


def auditor_best(k: np.ndarray, W: np.ndarray, r_grid=(1, 2, 3, 4)) -> tuple[int, dict]:
    best, bestv, detail = None, -1e18, {}
    for r in r_grid:
        detected = 0.0
        for i in range(len(k)):
            for j in range(len(k)):
                if W[i, j] and abs(k[i] - k[j]) >= r:
                    detected += W[i, j]
        v = AUDIT_W * detected - ALPHA / r
        detail[r] = round(v, 3)
        if v > bestv:
            best, bestv = r, v
    return int(best), detail


def main() -> None:
    W = graph()
    rng = np.random.default_rng(3)
    w = np.exp(rng.normal(0, 0.8, len(W)))
    k = np.full(len(W), 4.0)
    r = 1
    traj = []
    for outer in range(16):
        k = coder_sweep(k, W, w, r)
        r_new, detail = auditor_best(k, W)
        traj.append({"outer": outer, "r": r, "mean_k": round(float(k.mean()), 2),
                     "sd_k": round(float(k.std()), 2), "auditor_values": detail})
        if r_new == r and outer > 2:
            break
        r = r_new
    ks = [t["mean_k"] for t in traj]
    rs = [t["r"] for t in traj]
    res = {"trajectory": traj[-8:], "final_r": r, "final_mean_k": round(float(k.mean()), 2),
           "oscillates": bool(len(set(ks[-4:])) > 1),
           "k_series_tail": ks[-8:], "r_series_tail": rs[-8:]}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
