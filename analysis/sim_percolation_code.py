#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A22：异质性的容忍上限是不是渗流阈值？——把“过半”换成“巨分量”。

上一轮 A.19 用了一个粗糙的判据：**多数份额过半，公共码才在**。作者提出：这更像格点网络渗流。
这个直觉是对的，而且能写成一条更硬的式子。

改写
  把“能不能互相听懂”写成一张图：<i>i</i> 与 <i>j</i> 之间有边 ⇔ |k_i − k_j| ≤ 1。
  公共码存在 ⇔ 这张**可懂图**里有一个**巨分量**。于是判据不是“多数过半”，而是
      p ≡ P(|k_i − k_j| ≤ 1) &gt; p_c(接触结构)
  其中 p_c 是**接触结构**（谁跟谁打交道）上的键渗流阈值：
      一维链 p_c = 1；正方格 p_c = 0.5；三维格 p_c ≈ 0.25；随机 d-正则 p_c = 1/(d−1)。

所以：“容忍上限”不只由参数的离散度定，**还由交往结构的维数定**——越“平面”的社会，
容忍越少；接触渠道越多，容忍越多。

检验（脚本本文件）
  对三种接触结构（环+重连、20×20 正方格、随机 4-正则），把人按 A.19 的分布放上去，
  扫离散度 σ，量可懂图的巨分量占比；再单独量同一张图上的键渗流阈值 p_c。

输出 data/derived/perc_code.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "perc_code.json"
RNG = np.random.default_rng(20261118)
GRID = np.array([2, 3, 4, 6, 8, 12], dtype=float)


# ------------------------------------------------------------------ 图
def ring_graph(n=1000, rewire=0.1, rng=RNG):
    A = np.zeros((n, n), dtype=bool)
    for i in range(n):
        A[i, (i + 1) % n] = A[(i + 1) % n, i] = True
    for _ in range(int(rewire * n)):
        i, j = rng.integers(0, n, 2)
        if i != j:
            A[i, j] = A[j, i] = True
    return A


def square_lattice(m=20):
    n = m * m
    A = np.zeros((n, n), dtype=bool)
    for r in range(m):
        for c in range(m):
            i = r * m + c
            if c + 1 < m:
                A[i, i + 1] = A[i + 1, i] = True
            if r + 1 < m:
                A[i, i + m] = A[i + m, i] = True
    return A


def random_regular(n=1000, d=4, rng=RNG):
    A = np.zeros((n, n), dtype=bool)
    for i in range(n):
        while A[i].sum() < d:
            j = int(rng.integers(0, n))
            if j != i:
                A[i, j] = A[j, i] = True
    return A


def giant_share(A: np.ndarray) -> float:
    n = A.shape[0]
    seen = np.zeros(n, dtype=bool)
    best = 0
    for s in range(n):
        if seen[s]:
            continue
        stack, comp = [s], 0
        seen[s] = True
        while stack:
            u = stack.pop()
            comp += 1
            nbrs = np.flatnonzero(A[u] & ~seen)
            for v in nbrs:
                seen[v] = True
                stack.append(int(v))
        best = max(best, comp)
    return best / n


def percolation_threshold(make_graph, reps=6, rng=RNG) -> float:
    """在同一张图上随机删边，找巨分量消失的 p_c。"""
    A = make_graph()
    edges = np.argwhere(np.triu(A))
    out = []
    for _ in range(reps):
        keep = rng.permutation(len(edges))
        lo, hi = 0.0, 1.0
        for _ in range(12):
            mid = (lo + hi) / 2
            k = int(mid * len(edges))
            M = np.zeros_like(A)
            idx = edges[keep[:k]]
            M[idx[:, 0], idx[:, 1]] = M[idx[:, 1], idx[:, 0]] = True
            if giant_share(M) > 0.5:      # 巨分量还在 ⇒ 阈值在这个 p 之下
                hi = mid
            else:
                lo = mid
        out.append(hi)
    return float(np.mean(out))


def type_dist(sigma: float, n: int, rng=RNG) -> np.ndarray:
    w = np.exp(rng.normal(0, sigma, n))
    payoff = -w[:, None] / GRID[None, :] ** 2 - 0.05 * np.log2(GRID)[None, :]
    return GRID[np.argmax(payoff, axis=1)]


def giant_for_sigma(A: np.ndarray, sigma: float, n: int | None = None,
                    reps: int = 8, rng=RNG) -> dict:
    n = A.shape[0] if n is None else n
    gs, ps = [], []
    for _ in range(reps):
        k = type_dist(sigma, n, rng)
        diff = np.abs(k[:, None] - k[None, :])
        p = float(np.mean(diff[np.triu_indices(n, 1)] <= 1))
        M = A & (diff <= 1)
        gs.append(giant_share(M))
        ps.append(p)
    return {"sigma": sigma, "p": round(float(np.mean(ps)), 3),
            "giant": round(float(np.mean(gs)), 3)}


def degree_scan(degrees=(2, 3, 4, 6, 8), n=900, reps=6, rng=RNG) -> list[dict]:
    """接触渠道越多（度越大），容忍上限应当越高。"""
    out = []
    for d in degrees:
        A = random_regular(n, d, rng)
        pc = percolation_threshold(lambda A=A: A, reps=3, rng=rng)
        # 找巨分量掉到 0.5 以下的 σ
        lo, hi = 0.0, 1.6
        for _ in range(9):
            mid = (lo + hi) / 2
            g = np.mean([giant_for_sigma(A, mid, reps=4, rng=rng)["giant"] for _ in range(2)])
            if g > 0.5:
                lo = mid
            else:
                hi = mid
        out.append({"degree": d, "p_c": round(pc, 3), "sigma_star": round(lo, 2)})
    return out


def code_space(n_words=400, n_codes=300, sizes=(80, 100, 120, 140, 160, 200), theta=0.25,
               reps=5, rng=RNG) -> list[dict]:
    """码空间自己会不会渗流：每套码是词库的一个子集，两套码"可翻译"当且仅当重叠够。"""
    out = []
    for v in sizes:
        gs = []
        for _ in range(reps):
            C = np.zeros((n_codes, n_words), dtype=bool)
            for i in range(n_codes):
                C[i, rng.choice(n_words, v, replace=False)] = True
            inter = C.astype(np.int32) @ C.T.astype(np.int32)
            uni = 2 * v - inter
            J = inter / uni
            M = (J >= theta)
            np.fill_diagonal(M, False)
            gs.append(giant_share(M))
        out.append({"vocab_size": v, "mean_overlap_threshold": theta,
                    "giant": round(float(np.mean(gs)), 3)})
    return out


def main() -> None:
    graphs = {"ring_rewired": lambda: ring_graph(900, 0.1),
              "square_20x20": lambda: square_lattice(20),
              "random_regular_d4": lambda: random_regular(900, 4)}
    res: dict = {"thresholds": {}, "scan": {}}
    for name, mk in graphs.items():
        res["thresholds"][name] = round(percolation_threshold(mk), 3)
        A = mk()
        res["scan"][name] = [giant_for_sigma(A, s) for s in (0.0, 0.15, 0.3, 0.45, 0.6, 0.8, 1.0)]
    res["degree_scan"] = degree_scan()
    res["code_space"] = code_space()
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
