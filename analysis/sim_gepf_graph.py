#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GEPF 三层的图论模拟（附录 A.6 用）。

为什么有这个脚本
  附录 A.6 说：底层=底图、中层=边权、上层=节点中心性；三句关系（F 改边权、
  E 改预算、G 设上限）可估但未估。没有史料数据，就造一个**可复算**的最小模型，
  看三件事会不会自己长出来：
    ① 正反馈有没有上限（边权不能低于地理底线）
    ② 重置的顺序（中心性先动、边权后动、底图不动）
    ③ 识别问题（边权与中心性共线时，"路带来钱"与"钱修了路"分不开）

模型（全部构造，C 级）
  节点：单位方格上 N 个点（G）。边：k 近邻（几何邻接）。
  边权 w_e ≥ 地理底线 d_e（欧氏距离）——这就是"G 设上限"。
  流量：E_e ∝ 1/w_e。
  财政：F ← (1-β)F + β·(税基)；税基 ∝ Σ E_e。
  投资：F 投给"与自己相连的边"，把 w_e 往底线压：w_e ← max(d_e, w_e·(1-α·F))。

用法
    "$PY" analysis/sim_gepf_graph.py
产出
    data/derived/sim_gepf.csv, assets/charts/apA_gepf.png
"""
from __future__ import annotations

import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "derived")
CHART = os.path.join(ROOT, "assets", "charts")

C_MAIN, C_ALT, C_GREY = "#1f3b57", "#b5651d", "#8c8c8c"
plt.rcParams.update({
    "font.sans-serif": ["Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False, "figure.dpi": 300, "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
})


def build(rng, n=60, k=3):
    xy = rng.random((n, 2))
    d = np.linalg.norm(xy[:, None, :] - xy[None, :, :], axis=2)
    np.fill_diagonal(d, np.inf)
    edges = set()
    for i in range(n):
        for j in np.argsort(d[i])[:k]:
            edges.add((min(i, int(j)), max(i, int(j))))
    edges = sorted(edges)
    base = np.array([d[i, j] for i, j in edges])
    return xy, edges, base


def centrality(n, edges, w):
    """按 1/w 的边权算特征向量中心性（与 E 的流一致）。"""
    A = np.zeros((n, n))
    for (i, j), ww in zip(edges, w):
        A[i, j] = A[j, i] = 1.0 / ww
    deg = (A @ np.ones(n))
    return deg / deg.max() if deg.max() > 0 else deg


def gini(x):
    x = np.sort(np.asarray(x, float))
    n = len(x)
    if x.sum() == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * idx - n - 1).dot(x) / (n * x.sum()))


def main():
    rng = np.random.default_rng(20261117)
    n, k = 60, 3
    xy, edges, base = build(rng, n, k)
    w = base * 3.0          # 起步：路很差（3 倍地理距离）
    F = 0.15                # 财政能力
    alpha, beta = 0.22, 0.25
    rows = []
    for t in range(300):
        cen = centrality(n, edges, w)
        flow = 1.0 / w
        tax = flow.sum()
        F = (1 - beta) * F + beta * min(tax / 25.0, 1.0)
        # 投资：中心性高的节点的边被优先改造
        for e, (i, j) in enumerate(edges):
            pull = alpha * F * ((cen[i] + cen[j]) / 2.0) ** 2
            w[e] = max(base[e], w[e] * (1 - pull))
        rows.append({
            "t": t, "F": F, "tax": tax,
            "gini_cen": gini(cen),
            "mean_w_over_base": float(np.mean(w / base)),
            "mean_flow": float(flow.mean()),
        })

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "sim_gepf.csv"), "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)

    t = [r["t"] for r in rows]
    fig, ax = plt.subplots(1, 3, figsize=(10.2, 3.2))

    ax[0].plot(t, [r["F"] for r in rows], color=C_MAIN, lw=1.6, label="财政 F")
    ax[0].plot(t, [r["mean_flow"] for r in rows], color=C_ALT, lw=1.6, label="流量 E")
    ax[0].plot(t, [r["gini_cen"] for r in rows], color=C_GREY, lw=1.4, ls="--", label="中心性基尼")
    ax[0].set_title("① 正反馈与它的上限", fontsize=9.5, color=C_MAIN)
    ax[0].set_xlabel("期（模拟步）"); ax[0].legend(frameon=False, fontsize=7.2)

    ax[1].plot(t, [r["mean_w_over_base"] for r in rows], color=C_MAIN, lw=1.6)
    ax[1].axhline(1.0, color=C_ALT, lw=1.1, ls="--")
    ax[1].text(3, 1.04, "地理底线（G 设的上限）", fontsize=7.4, color=C_ALT)
    ax[1].set_title("② 边权压向底线，不再下降", fontsize=9.5, color=C_MAIN)
    ax[1].set_xlabel("期"); ax[1].set_ylabel("平均边权 ÷ 地理距离")

    cen = centrality(n, edges, w)
    xs = np.array([cen[i] + cen[j] for i, j in edges])
    ys = 1.0 / w                     # 最终流量（不受“改造到顶”截断）
    ax[2].scatter(xs, ys, s=14, color=C_MAIN, alpha=0.75)
    r = np.corrcoef(xs, ys)[0, 1]
    ax[2].set_title(f"③ 流量与中心性共线：r = {r:.2f}", fontsize=9.5, color=C_MAIN)
    ax[2].set_xlabel("两端中心性之和"); ax[2].set_ylabel("最终流量（1 / 边权）")

    fig.tight_layout()
    os.makedirs(CHART, exist_ok=True)
    fig.savefig(os.path.join(CHART, "apA_gepf.png"), bbox_inches="tight")
    print("wrote", os.path.join(OUT, "sim_gepf.csv"))
    print("final: F=%.3f  mean_w/base=%.3f  corr(cen,infra)=%.3f" %
          (rows[-1]["F"], rows[-1]["mean_w_over_base"], r))


if __name__ == "__main__":
    main()
