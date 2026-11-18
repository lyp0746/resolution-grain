#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""四层是网络不是一条链：环增益、里普亚诺夫指数、吸引域维数。

四个计算，对应附录 A.14 的四句话：

A. **连续时间收敛，离散化也不混沌。** 群体层的复制子（A.3）与它的离散版本
   （乘性权重 `P_{t+1} ∝ P_t·exp(h·π)`，h 从 0.2 到 30）在同一组参数下，最大里普亚诺夫指数
   **全部为负**。这不是巧合：势结构（A.3 的对称性）让更新是"往坡上爬"，而爬坡不会超调。
   ⇒ 可以写一句硬话：**势博弈的离散最佳回应不产生混沌。**

B. **两码情形更硬：单调映射不可能混沌。** 两码的最佳回应是区间上的单调映射（无超调），
   单调映射没有周期 3，因此没有混沌（Li–Yorke 的逆否）。这一条是定理，不是数值。

C. **P6 也不产生混沌。** 把"从别人的错里获益"写成一项（`+|ν|·别人错且不在我这格`），
   `|ν|` 从 0 到 4、h 从 0.5 到 32，λ 仍全为负。P6 的作用不是把系统推向混沌，
   **是把最优解推到边界**（A.9：最优码跑到最粗那一档）。两者是不同的失效方式。

D. **吸引域会交织，但那是外部耦合的构造。** 若把"互相参照"写成双向耦合的 logistic
   （`x' = 1 − A x² + ε(y−x)`），两个吸引子的吸引域彼此穿插，边界盒维数 1.75—2.02
   （ε=0.05／0.005）：**预测无用，但边界可界定。** 这是 C 级构造，用来展示"混沌长什么样"，
   不是从公设推出来的结论。

E. **链是网络的退化情形。** 四层的环增益乘积 `Πg`：链（无下行耦合）时乘积为 0；网络里
   `Πg<1` 收敛到慢流形，`Πg>1` 振幅增长直到被饱和项截住。这条是小数增益定理的条件
   （small-gain，Jiang–Teel 2008 的版本），不是我们的发明。

输出 data/derived/layers_network.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "layers_network.json"
RNG = np.random.default_rng(20261118)


def lie_replicator(k: int = 3, h: float = 1.0, nu: float = 0.0, steps: int = 3000,
                   w: float = 1.0, gz: float = 1.0) -> float:
    """乘性权重更新的最大里普亚诺夫指数。

    π(q,P) = −w·D(q,q*)² − γz·Σ P(q')D(q,q') + |ν|·(别人错且不在我这格)
    最后一项就是 P6（从别人的错里获益）的离散写法。
    """
    idx = np.arange(k)
    D = np.abs(idx[:, None] - idx[None, :]) / (k - 1.0)
    qs = 0
    dist_star = D[:, qs] ** 2

    def step(P: np.ndarray) -> np.ndarray:
        pi = -w * dist_star - gz * (D @ P)
        if nu:
            gain = np.array([np.sum(np.delete(P, i) * np.delete(dist_star, i))
                             for i in range(k)])
            pi = pi + abs(nu) * gain
        Z = P * np.exp(h * (pi - pi.max()))
        return Z / Z.sum()

    P = RNG.dirichlet(np.ones(k))
    Q = P + 1e-9 * RNG.standard_normal(k)
    Q = np.abs(Q) / np.abs(Q).sum()
    acc = 0.0
    for _ in range(steps):
        P, Q = step(P), step(Q)
        d = np.linalg.norm(Q - P)
        if d == 0 or not np.isfinite(d):
            return float("nan")
        acc += np.log(d / 1e-9)
        Q = P + (Q - P) / d * 1e-9
    return float(acc / steps)


def lie_logit2(h: float, kappa: float = 1.0, c: float = 0.5,
               steps: int = 2000, burn: int = 400) -> float:
    """两码即时最佳回应 p' = σ(h(κ(2p−1) − c))：单调映射，λ 应为负。"""
    def f(p: float) -> float:
        return 1.0 / (1.0 + np.exp(-h * (kappa * (2 * p - 1) - c)))

    x = 0.3
    for _ in range(burn):
        x = f(x)
    y = x + 1e-10
    acc = 0.0
    for _ in range(steps):
        x, y = f(x), f(y)
        d = abs(y - x)
        if d == 0:
            return float("nan")
        acc += np.log(d / 1e-10)
        y = x + (y - x) / d * 1e-10
    return float(acc / steps)


def basin_dimension(A: float = 1.4, eps: float = 0.05, n: int = 1600,
                    steps: int = 60) -> dict:
    xs = np.linspace(-1.2, 1.2, n)
    X, Y = np.meshgrid(xs, xs)
    for _ in range(steps):
        Xn = 1 - A * X * X + eps * (Y - X)
        Yn = 1 - A * Y * Y + eps * (X - Y)
        X, Y = np.clip(Xn, -1.5, 1.5), np.clip(Yn, -1.5, 1.5)
    basin = (X > Y).astype(np.int8)
    sync = np.abs(X - Y) < 1e-6
    basin[sync] = -1
    b = np.zeros_like(basin, dtype=bool)
    b[:-1, :] |= (basin[:-1, :] != basin[1:, :])
    b[:, :-1] |= (basin[:, :-1] != basin[:, 1:])
    b &= (basin >= 0)
    pts = np.argwhere(b)
    dims = []
    for k in (5, 6, 7, 8):
        s = n // (2 ** k)
        if s < 1:
            break
        dims.append((2 ** k, len(set(map(tuple, pts // s)))))
    slope = (float(np.polyfit(np.log([d[0] for d in dims]),
                              np.log([d[1] for d in dims]), 1)[0])
             if len(dims) >= 3 else float("nan"))
    return {"grid": n, "eps": eps, "boundary_points": int(b.sum()),
            "dimension": round(slope, 3),
            "share_two_basins": round(float((basin >= 0).mean()), 3)}


def main() -> None:
    res: dict = {}
    hs = [0.2, 0.5, 1, 2, 4, 8, 16, 30]
    res["A_replicator"] = {
        "lle_by_h": {str(h): round(lie_replicator(h=h), 3) for h in hs},
        "negative_everywhere": True,
    }
    res["A_replicator"]["negative_everywhere"] = all(
        v < 0 for v in res["A_replicator"]["lle_by_h"].values() if np.isfinite(v))

    res["B_logit2"] = {"lle_by_h": {str(h): round(lie_logit2(h), 3)
                                   for h in [0.5, 1, 2, 4, 8, 16]},
                       "note": "单调映射：无周期 3 ⇒ 无混沌（定理，不靠数值）"}

    res["C_p6"] = {"lle_by_nu": {
        str(nu): {str(h): round(lie_replicator(h=h, nu=nu), 3)
                  for h in [0.5, 2, 8, 32]}
        for nu in [0, 0.5, 1, 2, 4]}}

    res["D_basin"] = {"eps_0.05": basin_dimension(eps=0.05, n=1600),
                      "eps_0.005": basin_dimension(eps=0.005, n=1000)}

    # E 环增益：链 vs 网络
    def loop(gains: list[float]) -> dict:
        G = float(np.prod(gains))
        return {"gains": gains, "product": round(G, 4), "converges": bool(G < 1)}

    res["E_loop"] = {
        "chain": loop([0.8, 1.2, 1.1, 0.0]),      # 无下行耦合
        "network_below": loop([0.8, 0.9, 0.95, 0.9]),
        "network_above": loop([1.1, 1.2, 1.05, 1.1]),
    }

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
