#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""J4 的误差倍率：平均场把谱半径换成平均度，差多少？

读法（与附录 A.3／A.19 一致）：
- 群体层的复制子是在"份额"上写的，等价于假设每个人看得到全体（平均场）。
- 放到图上，一致性项经由邻居平均，临界条件里的 <k> 应换成 A 的谱半径 λ_max。
- 所以"平均场错多少"＝ λ_max / <k>：这个倍率就是封口时要写的误差项。

算：ER(n, <k>) 与 WS(n, <k>, β) 上的 λ_max/<k>；WS 用 β 控制聚类。
只输出倍率，不做动力学模拟（那是 A.19 的事）。
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "meanfield_error.json"


def er(n, k, rng):
    p = k / (n - 1)
    A = (rng.random((n, n)) < p).astype(float)
    A = np.triu(A, 1); A = A + A.T
    return A


def ws(n, k, beta, rng):
    # 环上的 k 近邻 + 以 beta 概率重连
    A = np.zeros((n, n))
    half = k // 2
    for i in range(n):
        for j in range(1, half + 1):
            A[i, (i + j) % n] = 1
            A[(i + j) % n, i] = 1
    for i in range(n):
        for j in range(1, half + 1):
            if rng.random() < beta:
                a, b = i, (i + j) % n
                if A[a, b]:
                    cand = rng.integers(0, n)
                    while cand == a or A[a, cand]:
                        cand = rng.integers(0, n)
                    A[a, b] = A[b, a] = 0
                    A[a, cand] = A[cand, a] = 1
    return A


def clustering(A):
    n = len(A)
    tri = np.trace(A @ A @ A) / 2.0
    deg = A.sum(1)
    denom = np.sum(deg * (deg - 1))
    return (2 * tri / denom) if denom > 0 else float("nan")


def ratio(A):
    deg = A.sum(1).mean()
    lam = float(np.linalg.eigvalsh(A)[-1])
    return lam, deg, lam / deg, clustering(A)


def main():
    rng = np.random.default_rng(20261119)
    n = 600
    rows = []
    for k in (4, 8, 16):
        lam, d, r, c = ratio(er(n, k, rng))
        rows.append({"graph": f"ER <k>={k}", "lambda_max": round(lam, 2), "mean_k": round(d, 2),
                     "ratio": round(r, 3), "clustering": round(c, 4)})
        for beta in (0.0, 0.05, 0.3):
            lam, d, r, c = ratio(ws(n, k, beta, rng))
            rows.append({"graph": f"WS <k>={k} beta={beta}", "lambda_max": round(lam, 2),
                         "mean_k": round(d, 2), "ratio": round(r, 3), "clustering": round(c, 4)})
    for x in rows:
        print(f"{x['graph']:22s} λmax={x['lambda_max']:6.2f}  <k>={x['mean_k']:5.2f}  "
              f"λmax/<k>={x['ratio']:5.3f}  C={x['clustering']:.3f}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"n": n, "rows": rows,
        "note": "λmax/<k> 是平均场临界条件的误差倍率。误差源是度分布的不均匀（ER：<k> 越小倍率越大），不是聚类（WS：倍率≈1，聚类不抬高谱半径）。"},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
