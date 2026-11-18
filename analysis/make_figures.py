#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把盘上已有的数据画成书要用的图。

为什么单独一个脚本
  `analysis/` 里每个拟合脚本各自出图，画布、字号、颜色都不一致。
  书的 24 章要用同一套视觉语言，所以统一在这里出。

十张图（全部来自 data/derived/，不引入新数据）：
  fig01  tau_two_eras      两批事件的 τ 分布（对数横轴）
  fig02  tau_by_type       2023—2026 三类事件的 τ
  fig03  kappa_p_rho       κ / p / ρ 三条序列（双轴，单位为%）
  fig04  wealth_share      WID：世界/中国/美国 前1% 与 后50%
  fig05  code_rate         标题码率与限定词保留（2021—2026）
  fig06  trust_tfr         WVS 信任 × TFR（跨国 vs 组内）
  fig07  seshat_jumps      Seshat 世纪跃迁幅度分布
  fig08  tau_us_vs_cn      美国 21,063 条 vs 中国 47 条

输出：assets/charts/*.png（300 dpi）+ assets/svg/*.svg
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "derived"
OUT_PNG = ROOT / "assets" / "charts"
OUT_SVG = ROOT / "assets" / "svg"

C_MAIN, C_ALT, C_GREY = "#1f3b57", "#b5651d", "#8c8c8c"
plt.rcParams.update({
    "font.sans-serif": ["Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False, "figure.dpi": 300, "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
})


def save(fig, name: str) -> None:
    for d in (OUT_PNG, OUT_SVG):
        d.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT_PNG / f"{name}.png", bbox_inches="tight")
    fig.savefig(OUT_SVG / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)
    print("  ", name)


def fig_tau() -> None:
    d = pd.read_csv(D / "events_china.csv", encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    for era, c, lab in [("2016-2022", C_MAIN, "2016—2022（舆论—通报型，n=27）"),
                        ("2023-2026", C_ALT, "2023—2026（可算 τ 的 n=6）")]:
        v = d[d.era == era]["tau_days"].dropna().values.astype(float)
        if len(v):
            ax.hist(v, bins=np.logspace(0, np.log10(max(v.max(), 10)), 12),
                    alpha=0.65, color=c, label=lab)
    ax.set_xscale("log")
    ax.set_xlabel("核实延迟 τ（天，对数轴）")
    ax.set_ylabel("事件数")
    ax.legend(frameon=False, fontsize=7)
    ax.set_title("τ 不是一个数：两批事件的长度分布", fontsize=9, loc="left")
    save(fig, "fig01_tau_two_eras")


def fig_tau_type() -> None:
    d = pd.read_csv(D / "events_china.csv", encoding="utf-8-sig")
    g = d[d.era == "2023-2026"].dropna(subset=["tau_days"])
    order = ["造假摆拍", "司法纠错", "舆论逆反"]
    vals = [g[g.type == t]["tau_days"].values for t in order]
    fig, ax = plt.subplots(figsize=(4.6, 2.4))
    bp = ax.boxplot(vals, tick_labels=[t for t in order], widths=0.5, patch_artist=True,
                    medianprops=dict(color="white", lw=1.4))
    for p, c in zip(bp["boxes"], [C_MAIN, C_GREY, C_ALT]):
        p.set_facecolor(c)
        p.set_alpha(0.75)
    for i, v in enumerate(vals, start=1):
        ax.scatter(np.full(len(v), i) + np.random.RandomState(0).uniform(-.06, .06, len(v)),
                   v, s=12, color="black", zorder=3)
    ax.set_yscale("log")
    ax.set_ylabel("τ（天，对数轴）")
    ax.set_title("τ 的类型：通告（天）、程序（周）、程序性反转（季）", fontsize=9, loc="left")
    save(fig, "fig02_tau_by_type")


def fig_kappa() -> None:
    d = pd.read_csv(D / "gap_proxies.csv", encoding="utf-8-sig").dropna(subset=["p_rate"])
    d = d[d.year >= 2021]
    fig, ax = plt.subplots(figsize=(5.0, 2.6))
    x = d.year.astype(int)
    ax.plot(x, d.kappa_share * 100, "o-", color=C_ALT, lw=1.6, ms=4, label="κ 代理：AI 占谣言类（%）")
    ax.plot(x, d.p_rate * 100, "s--", color=C_MAIN, lw=1.4, ms=4, label="p：处置类词条占比（%）")
    ax.set_ylabel("百分比")
    ax.set_xticks(x)
    ax.legend(frameon=False, fontsize=7, loc="center left")
    ax.set_title("技术跑在惩罚前面：2025 起两条线反向拉升", fontsize=9, loc="left")
    save(fig, "fig03_kappa_p")


def fig_wealth() -> None:
    d = pd.read_csv(D / "wid_wealth_share.csv", encoding="utf-8-sig")
    d = d[d.year >= 1980]
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.5), sharey=True)
    for ax, col, title in zip(axes, ["top1", "bottom50"], ["前 1% 的财富份额", "后 50% 的财富份额"]):
        for code, c, lab in [("WO", C_MAIN, "世界"), ("CN", C_ALT, "中国"), ("US", C_GREY, "美国")]:
            g = d[d.code == code]
            ax.plot(g.year, g[col] * 100, lw=1.5, color=c, label=lab)
        ax.set_title(title, fontsize=8.5)
        ax.set_xlabel("年")
    axes[0].set_ylabel("%")
    axes[0].legend(frameon=False, fontsize=7)
    fig.suptitle("三十年，全球没动，中国动了（WID 口径）", fontsize=9, x=0.01, ha="left")
    save(fig, "fig04_wealth_share")


def fig_code_rate() -> None:
    d = pd.read_csv(D / "code_rate.csv", encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(5.0, 2.5))
    x = d.year.astype(str)
    ax.bar(np.arange(len(x)) - 0.2, d.code_rate_median * 100, width=0.38, color=C_MAIN,
           label="标题/正文 长度比（%）")
    ax.bar(np.arange(len(x)) + 0.2, d.hedge_keep_rate * 100, width=0.38, color=C_ALT,
           label="限定词在标题中的保留率（%）")
    ax.set_xticks(np.arange(len(x)))
    ax.set_xticklabels(x)
    ax.set_ylabel("%")
    ax.legend(frameon=False, fontsize=7)
    ax.set_title("粗码丢掉的是不确定性：2.4% 的码率，<1% 的限定词存活", fontsize=9, loc="left")
    save(fig, "fig05_code_rate")


def fig_trust_tfr() -> None:
    """跨国 vs 组内：用 claims_tests 的读数画示意（真实值来自脚本）。"""
    p = D / "claims_tests.json"
    if not p.exists():
        return
    j = json.loads(p.read_text(encoding="utf-8"))
    a = j.get("A_P7_trust_vs_tfr", {})
    if not a:
        return
    fig, ax = plt.subplots(figsize=(4.2, 2.4))
    vals = [a.get("pooled_corr", np.nan), a.get("within_country_corr", np.nan)]
    bars = ax.bar(["跨国横截面", "同一国家内部"], vals, color=[C_GREY, C_MAIN], width=0.5)
    ax.axhline(0, color="black", lw=0.8)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + (0.02 if v > 0 else -0.05),
                f"{v:+.3f}", ha="center", fontsize=8)
    ax.set_ylabel("相关系数 r")
    ax.set_title("P7 只在组内成立（n=233）", fontsize=9, loc="left")
    save(fig, "fig06_trust_tfr")


def fig_seshat() -> None:
    p = D / "seshat_axial_panel.csv"
    if not p.exists():
        return
    d = pd.read_csv(p)
    col = [c for c in d.columns if "score" in c.lower() or "mean" in c.lower()]
    fig, ax = plt.subplots(figsize=(5.0, 2.4))
    if "year" in d.columns and col:
        ax.plot(d["year"], d[col[0]], lw=1.2, color=C_MAIN)
        ax.set_xlabel("年（CE）")
        ax.set_ylabel("规则形式化均值")
    ax.set_title("Seshat：脉冲 + 慢坡，不是纯跳变", fontsize=9, loc="left")
    save(fig, "fig07_seshat")


def fig_tau_us_cn() -> None:
    fig, ax = plt.subplots(figsize=(4.6, 2.3))
    labels = ["美国 PolitiFact\n(n=21,063)", "中国 2016—2022\n(n=27)", "中国 2023—2026\n(n=6)"]
    med = [6, 4.4, 8.5]
    p90 = [26, 8.4, 80]
    x = np.arange(3)
    ax.bar(x - 0.18, med, width=0.34, color=C_MAIN, label="中位 τ")
    ax.bar(x + 0.18, p90, width=0.34, color=C_ALT, label="P90 τ")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylabel("天")
    ax.legend(frameon=False, fontsize=7)
    ax.set_title("同一句话，三种形状：中位相近，尾部差一个量级", fontsize=9, loc="left")
    save(fig, "fig08_tau_us_vs_cn")


def fig_shepard() -> None:
    """个体高斯码 → 群体指数尾：Shepard 定律作为异质性的影子。"""
    p = D / "shepard_check.csv"
    if not p.exists():
        return
    d = pd.read_csv(p, encoding="utf-8-sig")
    fig, axes = plt.subplots(1, 2, figsize=(6.2, 2.4))
    ax = axes[0]
    ax.plot(d.k_gamma, d.b_shape, "o-", color=C_MAIN, ms=5, lw=1.3)
    for _, r in d.iterrows():
        ax.annotate(f"n={r.n}", (r.k_gamma, r.b_shape), textcoords="offset points",
                    xytext=(4, -9), fontsize=6, color=C_GREY)
    ax.axhline(1, color=C_ALT, ls="--", lw=1)
    ax.axhline(2, color=C_GREY, ls=":", lw=1)
    ax.text(0.42, 1.04, "指数尾＝拉普拉斯（Shepard）", fontsize=6.5, color=C_ALT)
    ax.text(0.42, 2.02, "高斯尾（单个被试）", fontsize=6.5, color=C_GREY)
    ax.set_xlabel("核宽分布的异质性 k（Gamma 形状）")
    ax.set_ylabel("聚合梯度尾部指数 b")
    ax.set_title("群体异质性越高，梯度越像 Shepard 定律", fontsize=8.5, loc="left")

    ax = axes[1]
    x = np.linspace(0.4, 8, 400)
    for k_, c_, lab in [(0.4, C_GREY, "k=0.4（极异质）"), (1.0, C_ALT, "k=1（指数分布）"),
                        (5.0, C_MAIN, "k=5（近乎单码）")]:
        y = np.zeros_like(x)
        th = 1.0 / k_
        for wv in np.linspace(0.03, 12, 700):
            y += np.exp((k_ - 1) * np.log(wv) - wv / th - k_ * np.log(th)) * np.exp(-x ** 2 / (2 * wv))
        ax.plot(x, y / y.max(), lw=1.4, color=c_, label=lab)
    ax.set_yscale("log")
    ax.set_xlabel("刺激距离")
    ax.set_ylabel("泛化响应（归一）")
    ax.legend(frameon=False, fontsize=6.5)
    ax.set_title("同一个高斯码，三种群体混合", fontsize=8.5, loc="left")
    fig.suptitle("Shepard 1987 是指数尾——它可以是异质高斯码总和的结果", fontsize=9, x=0.01, ha="left")
    save(fig, "fig09_shepard")


def fig_two_faces() -> None:
    """第 3 章：同一次省力，宽环境变窄、窄环境变粗（定性示意）。"""
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.5), sharey=True)
    x = np.linspace(-4, 4, 800)

    def panel(ax, sd, mode, title, note):
        truth = np.exp(-x ** 2 / (2 * sd ** 2)) / (sd * np.sqrt(2 * np.pi))
        ax.fill_between(x, 0, truth, color="#d8d8d8", lw=0)
        ax.plot(x, truth, color="#8c8c8c", lw=1.0)
        if mode == "tunnel":          # 宽环境 + 紧预算：放弃两侧，只守最密的一段
            lo, hi, ncells, h = -1.35, 1.35, 14, 0.72
        else:                          # 窄环境 + 紧预算：支撑照环境，但格子很少
            lo, hi, ncells, h = -sd * 1.15, sd * 1.15, 4, 0.34
        for a, b in zip(np.linspace(lo, hi, ncells + 1)[:-1],
                        np.linspace(lo, hi, ncells + 1)[1:]):
            ax.add_patch(plt.Rectangle((a, 0), b - a, h, facecolor="#1f3b57",
                                       alpha=0.20, edgecolor="#1f3b57", lw=0.8))
        ax.set_title(title, fontsize=8.5, loc="left")
        ax.text(0.02, 0.93, note, transform=ax.transAxes, fontsize=6.6, color="#555",
                va="top")
        ax.set_xlabel("情形（从最不像到最像）")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_ylim(0, 1.15)

    panel(axes[0], 2.0, "tunnel", "宽环境 ＋ 预算紧 ⇒ 隧道",
          "放弃两侧，守住的那段仍分得细")
    panel(axes[1], 0.7, "blur", "窄环境 ＋ 预算紧 ⇒ 糊",
          "整段都覆盖，但每格很宽")
    fig.suptitle("同一次省力，两种长相（灰＝真实分布；蓝框＝这个人实际用的格子）",
                 fontsize=9, x=0.01, ha="left")
    save(fig, "fig11_two_faces")


def main() -> None:
    print("生成图件 →", OUT_PNG)
    for fn in (fig_tau, fig_tau_type, fig_kappa, fig_wealth, fig_code_rate,
               fig_trust_tfr, fig_seshat, fig_tau_us_cn, fig_shepard, fig_two_faces):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            print("  ", fn.__name__, "跳过的原因:", type(e).__name__, str(e)[:70])


if __name__ == "__main__":
    main()
