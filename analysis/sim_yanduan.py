#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""「厌倦」的模型：冲击的卷积 → 阈值 → 权重排序反转 → 迟滞。

为什么要有这个脚本
  作者指出：屠杀带来的不是线性累积的情绪，而是**卷积作用突破阈值之后的「反向」**——
  也就是从「求胜」翻到「求序」，而且翻了之后不容易翻回来。
  这在数学上不是单调衰减，是**双稳态 + 迟滞**。没有这个结构，"厌倦"就只能写成形容词。

模型（三段，全部标 C 级示意，参数未估计）
  1. 冲击卷积：`A(t) = Σ_k S_k · exp(-(t-t_k)/τ_s)`，τ_s 是「记忆的衰减时间」。
  2. 阈值的 S 形：`w_序(t) = w0 + Δw · σ((A - A*)/s)`。未过阈值时 `w_胜 > w_序`。
  3. 反转与迟滞：码的切换要付成本 `C`，所以只有当 `w_序` **超过** `w_胜 + C` 才翻；
     翻回去要 `w_序 < w_胜 - C`。于是形成一个迟滞环——**同一条 `A`，上行与下行给出不同的码。**

输出
  assets/charts/fig10_yanduan.png
  data/derived/sim_yanduan.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PNG = ROOT / "assets" / "charts"
OUT_SVG = ROOT / "assets" / "svg"
OUT_CSV = ROOT / "data" / "derived" / "sim_yanduan.csv"

# 十世纪兵变/交战（仅作示意刻度，不是史料估值）
SHOCKS = [(884, 3.0), (905, 2.0), (923, 3.0), (926, 3.0), (936, 4.0),
          (947, 4.0), (950, 3.0), (960, 2.0)]
TAU_S, W0, DW, A_STAR, S_SLOPE = 9.0, 1.0, 2.6, 2.6, 0.35
C_FORWARD, C_BACK = 0.25, 2.5   # 翻回去更贵：换码成本被制度化抬高（宋初做的事）


def A_of(t: np.ndarray) -> np.ndarray:
    a = np.zeros_like(t, dtype=float)
    for tk, s in SHOCKS:
        a += np.where(t >= tk, s * np.exp(-(t - tk) / TAU_S), 0.0)
    return a


def w_order(a: np.ndarray) -> np.ndarray:
    return W0 + DW / (1.0 + np.exp(-(a - A_STAR) / S_SLOPE))


def simulate() -> pd.DataFrame:
    """三层时间尺度：A（冲击的卷积，快）→ S（泄漏积分，慢）→ w（S 形，翻转）。"""
    t = np.arange(875, 1001, 0.25)
    a = A_of(t)
    # 慢变量 S：dS/dt = (A - S)/τ_S，用欧拉积分
    tau_S, dt = 26.0, 0.25
    s = np.zeros_like(t)
    s[0] = a[0]
    for i in range(1, len(t)):
        s[i] = s[i - 1] + dt * (a[i] - s[i - 1]) / tau_S
    w_o = W0 + DW / (1.0 + np.exp(-(s - A_STAR) / S_SLOPE))
    w_v = np.full_like(t, W0 + DW * 0.45)

    code, out = 0, []
    for i in range(len(t)):
        if code == 0 and w_o[i] > w_v[i] + C_FORWARD:
            code = 1
        elif code == 1 and w_o[i] < w_v[i] - C_BACK:
            code = 0
        out.append(code)
    code = np.array(out)

    T, lam = 1.0, 1.0
    w_eff = np.where(code == 1, w_o, w_v)
    v = (T + lam) / (2 * w_eff)
    return pd.DataFrame({"year": t, "A": a, "S": s, "w_order": w_o, "w_victory": w_v,
                         "code": code, "v": v})


def main() -> None:
    d = simulate()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    plt.rcParams.update({"font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
                         "axes.unicode_minus": False, "figure.dpi": 300, "font.size": 8.5,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 2.5))

    ax = axes[0]
    ax.plot(d.year, d.A, color="#8c8c8c", lw=0.9, label="A：冲击的卷积（快）")
    ax.plot(d.year, d.S, color="#1f3b57", lw=1.7, label="S：泄漏积分（慢）")
    ax.axhline(A_STAR, color="#b5651d", ls="--", lw=1)
    ax.text(878, A_STAR + 0.12, "阈值 A*", fontsize=6.5, color="#b5651d")
    ax.legend(frameon=False, fontsize=6.5)
    ax.set_title("① 冲击的卷积：越积越高", fontsize=8.5, loc="left")
    ax.set_xlabel("年"); ax.set_ylabel("累积显著度")

    ax = axes[1]
    ax.plot(d.year, d.w_order, color="#b5651d", lw=1.5, label="w（秩序）")
    ax.plot(d.year, d.w_victory, color="#8c8c8c", lw=1.2, ls="--", label="w（求胜）")
    ax.fill_between(d.year, d.w_victory + C_FORWARD, d.w_victory - C_BACK, color="#b5651d", alpha=0.07)
    ax.set_title("② 权重排序反转（带 C 的切换带）", fontsize=8.5, loc="left")
    ax.set_xlabel("年"); ax.legend(frameon=False, fontsize=6.5)

    ax = axes[2]
    ax.plot(d.year, d.v, color="#1f3b57", lw=1.6)
    flips = d[d.code.diff().fillna(0) != 0]
    for _, r in flips.iterrows():
        ax.axvline(r.year, color="#b5651d", lw=0.9, ls=":")
    ax.set_title("③ 分辨率随之下降（程序变细、覆盖变窄）", fontsize=8.5, loc="left")
    ax.set_xlabel("年"); ax.set_ylabel("v*（相对）")
    ax.invert_yaxis()

    fig.suptitle("「厌倦」不是情绪：卷积过阈值后权重反转，且因切换成本而不可逆（C 级示意）",
                 fontsize=9, x=0.01, ha="left")
    fig.tight_layout()
    for d_ in (OUT_PNG, OUT_SVG):
        d_.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG / "fig10_yanduan.png", bbox_inches="tight")
    fig.savefig(OUT_SVG / "fig10_yanduan.svg", bbox_inches="tight")

    flip_years = flips.year.tolist()
    print("翻转年:", [round(x, 1) for x in flip_years])
    print("→", OUT_PNG / "fig10_yanduan.png")


if __name__ == "__main__":
    main()
