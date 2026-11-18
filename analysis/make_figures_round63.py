#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第六十三轮之后的两张图（只新增，不碰既有图）。

  c04_hetero   **异质性的两张脸**（判据图＋数据图，B 级）
               左：个体是阶梯、总量是平滑的（阈值离散度 0.05 vs 1.0）；
               右：参数离散度一高，一个共同体里同时活着几种码（0.29 的最大份额）。
               数据来自 analysis/sim_heterogeneity.py。

  c28_twotimes **两种时刻**（数据图，B 级）
               左：21 CFR 的 266 个节级修订间隔——比随机更规则（B=−0.20）；
               右：125 个国家的历法采纳年份——挤成四簇（B=+0.52）。
               数据来自 analysis/test_revision_bursts.py 与 test_adoption_bursts.py。

用法：  "$PY" analysis/make_figures_round63.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "charts"
SVG = ROOT / "assets" / "svg"
C_MAIN, C_ALT, C_GREY = "#1f3b57", "#b5651d", "#8c8c8c"

plt.rcParams.update({
    "font.sans-serif": ["Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False, "figure.dpi": 300, "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
})


def save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SVG.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight")
    try:                                   # 本机 matplotlib 缺 backend_svg，SVG 可选
        fig.savefig(SVG / f"{name}.svg", bbox_inches="tight")
    except Exception as e:                 # noqa: BLE001
        print(f"    (svg skipped: {type(e).__name__})")
    plt.close(fig)
    print("  ", name)


def fig_c04_hetero() -> None:
    d = json.loads((ROOT / "data" / "derived" / "heterogeneity.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(11)
    x = np.linspace(-3, 3, 400)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.5),
                                   gridspec_kw={"width_ratios": [1.15, 1]})

    # 左：个体阶梯（薄）+ 两个总量（厚）
    for s, col, lab in ((0.05, C_MAIN, "离散度 0.05：几乎一起跳"),
                        (1.0, C_ALT, "离散度 1.0：拉成一条斜坡")):
        thr = np.exp(rng.normal(0, s, 200))
        agg = np.array([np.mean(xv > thr) for xv in x])
        for t in thr[:12]:
            ax1.plot([t, t], [0, 1], color=col, lw=0.35, alpha=0.28)
        ax1.plot(x, agg, color=col, lw=2.0, label=lab)
    ax1.set_xlim(-3, 3)
    ax1.set_ylim(-0.02, 1.04)
    ax1.set_xlabel("同一条外生推力")
    ax1.set_ylabel("“已经翻过去”的比例")
    ax1.set_title("个体到点就跳，总量却是平滑的", fontsize=10)
    ax1.legend(frameon=False, fontsize=8, loc="upper left")
    ax1.text(0.98, 0.06, "细线＝个体的阶梯", transform=ax1.transAxes,
             ha="right", fontsize=7.4, color=C_GREY)

    # 右：码的种类随离散度
    keys = ["wsigma=0.0", "wsigma=0.5", "wsigma=1.0"]
    labels = ["离散度 0", "0.5", "1.0"]
    grid = ["2", "3", "4", "6", "8", "12"]
    width = 0.26
    for j, (k, lab) in enumerate(zip(keys, labels)):
        dist = d["B_partial"][k]["distribution"]
        n = sum(dist.values())
        vals = [dist.get(g, 0) / n for g in grid]
        ax2.bar(np.arange(len(grid)) + (j - 1) * width, vals, width=width * 0.92,
                color=[C_GREY, C_ALT, C_MAIN][j], label=f"{lab}（最大份额 {d['B_partial'][k]['max_share']:.2f}）")
    ax2.set_xticks(range(len(grid)))
    ax2.set_xticklabels([f"{g} 格" for g in grid])
    ax2.set_xlabel("个体选中的粒度")
    ax2.set_ylabel("占人群比例")
    ax2.set_title("离散度一高，一种码变成六种并存", fontsize=10)
    ax2.legend(frameon=False, fontsize=7.6, loc="upper right")
    save(fig, "c04_hetero")


def fig_c28_twotimes() -> None:
    # 左：法规的节级修订间隔（从缓存重算，与 test_revision_bursts.py 同口径）
    RAW = ROOT / "data" / "raw" / "ecfr_fr"
    gaps = []
    for p in sorted(RAW.glob("ecfr_title21_part*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        hist = {}
        for c in d.get("content_versions") or []:
            if c.get("type") != "section":
                continue
            dt = c.get("amendment_date") or c.get("date")
            if dt:
                hist.setdefault(c["identifier"], set()).add(dt)
        for _, ds in hist.items():
            ys = sorted(int(v[:4]) for v in ds)
            gaps += [b - a for a, b in zip(ys, ys[1:]) if b > a]
    gaps = np.array(gaps, dtype=float)

    # 右：历法采纳年份
    g = json.loads((ROOT / "data" / "derived" / "gregorian_adoption.json").read_text(encoding="utf-8"))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.4))

    hi = int(gaps.max())
    cnt = np.bincount(gaps.astype(int), minlength=hi + 1)
    ax1.bar(np.arange(hi + 1), cnt, color=C_MAIN, width=0.7)
    ax1.set_xlabel("同一节的两次修订之间隔了几年")
    ax1.set_ylabel("个数")
    ax1.set_title("成文法规：比随机更规则", fontsize=10)
    ax1.text(0.97, 0.92, f"n = {len(gaps)} 个间隔\n均值 4.1 年，突发度 B = −0.20",
             transform=ax1.transAxes, ha="right", va="top", fontsize=8, color=C_MAIN)
    ax1.set_xlim(-0.7, hi + 0.7)

    years = np.array(g["years"], dtype=int)
    yc = {y: int((years == y).sum()) for y in np.unique(years)}
    ax2.bar(list(yc.keys()), list(yc.values()), color=C_ALT, width=1.6)
    ax2.set_xlabel("采纳公历的年份")
    ax2.set_ylabel("国家数")
    ax2.set_title("历法采纳：挤成四簇", fontsize=10)
    for y, lab in ((1583, "25 国"), (1700, "14 国"), (1918, "6 国")):
        if y in yc:
            ax2.annotate(lab, (y, yc[y]), textcoords="offset points", xytext=(6, 2),
                         ha="left", fontsize=7.4, color=C_ALT)
    ax2.annotate("1582—1584\n三根挨在一起", (1583, 26.5), textcoords="offset points",
                 xytext=(-46, 6), ha="left", fontsize=7.2, color=C_GREY)
    ax2.text(0.97, 0.92, f"n = {len(years)} 国\n突发度 B = +0.52",
             transform=ax2.transAxes, ha="right", va="top", fontsize=8, color=C_ALT)
    ax2.set_xlim(1570, 1940)
    save(fig, "c28_twotimes")


def fig_c26_perc() -> None:
    """异质性的容忍上限＝可懂图的渗流阈值；阈值由接触结构定。"""
    d = json.loads((ROOT / "data" / "derived" / "perc_code.json").read_text(encoding="utf-8"))
    styles = {"ring_rewired": ("环 + 10% 重连", C_GREY, "o"),
              "square_20x20": ("20×20 方格", C_ALT, "s"),
              "random_regular_d4": ("随机 4-正则", C_MAIN, "^")}
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    for key, (lab, col, mk) in styles.items():
        rows = d["scan"][key]
        xs = [r["sigma"] for r in rows]
        ys = [r["giant"] for r in rows]
        ax.plot(xs, ys, color=col, marker=mk, ms=4.5, lw=1.6, label=lab)
        pc = d["thresholds"][key]
        ax.axhline(pc, color=col, lw=0.8, ls=":", alpha=0.7)
        ax.text(1.02, pc, f"{pc:.2f}", color=col, fontsize=7.4, va="center")
    ax.set_xlabel("参数离散度 σ（“错了多疼”有多不一样）")
    ax.set_ylabel("可懂图里最大连通块的占比")
    ax.set_title("容忍上限不是常数：它由“谁跟谁打交道”的维数定", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax.set_ylim(-0.02, 1.02)
    ax.text(0.40, 0.93, "虚线＝该结构上的渗流阈值 p_c", transform=ax.transAxes,
            fontsize=7.4, color=C_GREY)
    save(fig, "c26_perc")


if __name__ == "__main__":
    fig_c04_hetero()
    fig_c28_twotimes()
    fig_c26_perc()
