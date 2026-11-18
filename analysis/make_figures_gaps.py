#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第 18、22 章的第二张图（2026-11-17 加）。

为什么单独一个脚本
  `make_figures.py` 出十张数据图、`make_figures_body.py` 出各章正文图，两者重跑都会
  改动已发布的文件（AGENTS §9 第 6 条：改前先 diff）。本脚本**只新增**，不碰任何既有图，
  名字带 `c18_sched` / `c22_grid` 一眼可认。

两张图的性质不同
  c18_sched：**数据图**（B 级）。美国侧 21,063 条事实核查的滞后分布 + mod 7 相位剖面，
             把表 18.2 那四个"7 的倍数"变成一个可以看见的齿。
  c22_grid：**判据图**（C 级）。表 22.6 的 2×2 与唐宋那段轨迹——静态投影与轨迹的差别，
             表只能并排，图能画"穿过去"。

用法
    "$PY" analysis/make_figures_gaps.py
"""
from __future__ import annotations

import csv
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
    fig.savefig(SVG / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)
    print("  ", name)


# ---------------------------------------------------------------- 第 18 章
def fig_c18_sched() -> None:
    p = ROOT / "data" / "derived" / "tau_politifact.csv"
    lags = np.array([int(r["lag_days"]) for r in csv.DictReader(open(p, encoding="utf-8"))])
    n = len(lags)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.4),
                                   gridspec_kw={"width_ratios": [1.55, 1]})

    # 左：0—34 天的条数，7 的倍数染色
    hi = 34
    cnt = np.bincount(lags[lags <= hi], minlength=hi + 1)
    x = np.arange(hi + 1)
    mult = (x > 0) & (x % 7 == 0)
    ax1.bar(x[~mult], cnt[~mult], color=C_GREY, width=0.72, label="其余")
    ax1.bar(x[mult], cnt[mult], color=C_ALT, width=0.72, label="7 的倍数")
    for k in (7, 14, 21, 28):
        nb = (cnt[k - 1] + cnt[k + 1]) / 2 if k + 1 <= hi else cnt[k - 1]
        ax1.annotate(f"{k}天 ×{cnt[k]/nb:.2f}", (k, cnt[k]), textcoords="offset points",
                     xytext=(0, 4), ha="center", fontsize=7.2, color=C_ALT)
    ax1.set_xlabel("滞后（天）：曝光 → 有结论")
    ax1.set_ylabel("条数")
    ax1.set_title("一周七个齿：多出来的那几根柱子", fontsize=10)
    ax1.legend(frameon=False, fontsize=8, loc="upper right")
    ax1.set_xlim(-0.8, hi + 0.8)

    # 右：mod 7 相位剖面（观测 / 期望）
    m = np.bincount(lags % 7, minlength=7)
    exp = n / 7
    ax2.bar(np.arange(7), m / exp, color=C_MAIN, width=0.66)
    ax2.axhline(1.0, color=C_ALT, lw=1.2, ls="--")
    ax2.set_xticks(range(7))
    ax2.set_xlabel("滞后 mod 7")
    ax2.set_ylabel("观测 ÷ 期望")
    ax2.set_title("相位：质量压在 0 与 1 上", fontsize=10)
    for i, v in enumerate(m / exp):
        ax2.text(i, v + 0.03, f"{v:.2f}", ha="center", fontsize=7.2, color=C_MAIN)
    ax2.set_ylim(0, max(m / exp) * 1.25)

    ax1.text(0.02, 0.94, f"n = {n:,}（有结论的条目）", transform=ax1.transAxes,
             fontsize=8, color=C_GREY)
    save(fig, "c18_sched")


# ---------------------------------------------------------------- 第 22 章
def fig_c22_grid() -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)

    # 四格：换不换码（行）× C 高低（列）
    cells = [
        (0, 1, "法国 1789—1880\n换了五次，未被抬高", 0.34, False),
        (1, 1, "明治日本\n三十年内完成换码", 0.13, False),
        (0, 0, "（空）\n换得起，却没人换", 0.50, True),
        (1, 0, "苏联 1960s 末—1991\n拖到一次性位移", 0.50, False),
    ]
    for cx, cy, label, dy, empty in cells:
        ax.add_patch(plt.Rectangle((cx, cy), 1, 1, facecolor="#f2f2f2" if not empty else "#ffffff",
                                   edgecolor=C_MAIN, lw=0.9,
                                   hatch="///" if empty else None))
        ax.text(cx + 0.5, cy + dy, label, ha="center", va="center", fontsize=8.2,
                color=C_MAIN, bbox=dict(fc="white", ec="none", alpha=0.85, pad=2.2)
                if empty else None)

    # 唐宋：从“换了码、C 低”穿到“换了码、C 高”
    ax.annotate("", xy=(1.88, 1.74), xytext=(1.10, 1.40),
                arrowprops=dict(arrowstyle="-|>", color=C_ALT, lw=2.2, shrinkA=0, shrinkB=0))
    ax.text(1.50, 1.94, "唐宋 875—1000：C 从低走到高", ha="center", va="top",
            fontsize=7.8, color=C_ALT)

    ax.set_xticks([0.5, 1.5]); ax.set_xticklabels(["C 低", "C 高"], fontsize=9)
    ax.set_yticks([1.5, 0.5]); ax.set_yticklabels(["换了码", "没换码"], fontsize=9,
                                                 rotation=90, va="center")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    save(fig, "c22_grid")


# ---------------------------------------------------------------- 第 6 章
def fig_c06_scales() -> None:
    """两个把 δ 写进制度的旋钮：地图比例尺、公差等级。

    左幅用同一张 200 mm × 200 mm 的图幅，三种比例尺**嵌套**画出：
    1:5 万覆盖 10 km，1:5000 覆盖 1 km，1:500 覆盖 100 m；
    1 mm 分别代表 50 m／5 m／0.5 m。于是「放大」不是看得更清，
    是拿覆盖换精度——Δ 与 δ 被同一个数（比例尺）锁住。
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.6),
                                   gridspec_kw={"width_ratios": [1.05, 1]})

    # 左：三张同样大小的图幅，三种比例尺（并排，不按面积比，避免误读）
    levels = [("1:5 万", "覆盖 10 km", "1 mm = 50 m", C_GREY),
              ("1:5000", "覆盖 1 km", "1 mm = 5 m", C_MAIN),
              ("1:500", "覆盖 100 m", "1 mm = 0.5 m", C_ALT)]
    for k, (name, cov, mm, col) in enumerate(levels):
        x0 = 0.04 + k * 0.325
        ax1.add_patch(plt.Rectangle((x0, 0.34), 0.26, 0.26, facecolor="none",
                                    edgecolor=col, lw=1.5))
        ax1.text(x0 + 0.13, 0.66, name, ha="center", fontsize=9, color=col)
        ax1.text(x0 + 0.13, 0.27, cov, ha="center", fontsize=8, color=col)
        ax1.text(x0 + 0.13, 0.21, mm, ha="center", fontsize=8, color=col)
    ax1.plot([0.06, 0.88], [0.15, 0.15], color=C_GREY, lw=0.8)
    ax1.text(0.47, 0.10, "图幅同为 200 mm × 200 mm", ha="center", fontsize=8, color=C_GREY)
    ax1.text(0.47, 0.03, "放大的不是分辨率，是拿覆盖换精度", ha="center",
             fontsize=8.4, color=C_ALT)
    ax1.set_xlim(0, 0.95); ax1.set_ylim(0, 0.82)
    ax1.axis("off")

    # 右：IT 等级阶梯（名义尺寸 50 mm 的容差，µm；ISO 286 标准值）
    grades = ["IT6", "IT7", "IT8", "IT9", "IT10", "IT11", "IT12", "IT13"]
    tol = [16, 25, 39, 62, 100, 160, 250, 390]
    ax2.semilogy(range(len(grades)), tol, "o-", color=C_MAIN, lw=1.8, ms=5)
    for i, v in enumerate(tol):
        ax2.annotate(f"{v}", (i, v), textcoords="offset points", xytext=(0, 6),
                     ha="center", fontsize=7.4, color=C_MAIN)
    ax2.set_xticks(range(len(grades))); ax2.set_xticklabels(grades, fontsize=8)
    ax2.set_ylabel("容差 δ（µm，名义 50 mm）")
    ax2.set_xlabel("公差等级")
    ax2.text(0.03, 0.88, "每降一级 ≈ ×1.6；δ 的每一格都有价",
             transform=ax2.transAxes, fontsize=8.2, color=C_GREY)
    save(fig, "c06_scales")


# ---------------------------------------------------------------- 第 4 章
def fig_c04_ladder() -> None:
    """四层尺度：通、半通、断。"""
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    steps = [
        (0, "个体", "有式子（第 3 章）\n有最优化", "通", C_MAIN, "solid"),
        (1, "群体", "有方程＋有博弈\n（复制子／势）", "通", C_MAIN, "solid"),
        (2, "社会", "有方程、无博弈\n（A 与 q 未联立）", "半通", C_ALT, "half"),
        (3, "文明", "只搭了框\n（μ 与 Φ 之间还没有桥）", "断", C_GREY, "none"),
    ]
    for i, name, desc, tag, col, style in steps:
        h = 0.55 + i * 0.30
        if style == "none":
            ax.add_patch(plt.Rectangle((i * 0.95, h - 0.52), 0.80, 0.34, facecolor="white",
                                       edgecolor=col, lw=1.2, ls="--"))
        else:
            ax.add_patch(plt.Rectangle((i * 0.95, h - 0.52), 0.80, 0.34,
                                       facecolor=col, alpha=0.16, edgecolor=col, lw=1.2,
                                       hatch="///" if style == "half" else None))
        ax.text(i * 0.95 + 0.40, h - 0.35, name, ha="center", va="center", fontsize=9,
                color=col)
        ax.text(i * 0.95 + 0.40, h - 0.72, desc, ha="center", va="center", fontsize=7.4,
                color="#333333")
        ax.text(i * 0.95 + 0.40, h - 0.05, tag, ha="center", fontsize=8.6, color=col)
    # 断口：第三层与第四层之间画一道缺口
    ax.plot([3 * 0.95 - 0.18, 3 * 0.95 - 0.02], [0.55 + 2 * 0.30 + 0.05, 0.55 + 3 * 0.30 - 0.20],
            color=C_ALT, lw=1.4, ls=":")
    ax.text(2.95, 1.62, "这里断了：不是没算，是没得算", fontsize=8.2, color=C_ALT, ha="center")
    ax.set_xlim(-0.15, 3.95); ax.set_ylim(0.20, 1.80)
    ax.axis("off")
    save(fig, "c04_ladder")


# ---------------------------------------------------------------- 第 26 章
def fig_c26_gaps() -> None:
    """九处空白：补起来要多久 × 补上后结论会变多少。

    横轴是补法的代价（一次复算 → 换工具），纵轴是补上之后结论会变多少。
    位置是本书的判读（C 级），四个角的意思由图注说明；图只做一件事：
    把「欠账」与「边界」放在同一张纸上，让「先做哪一件」变成一句话。
    """
    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    items = [
        ("9 第六条检验", 1.2, 0.88, C_ALT, "r"),
        ("3 折损系数", 3.05, 0.90, C_ALT, "l"),
        ("1 分辨率分布", 2.0, 0.52, C_MAIN, "r"),
        ("2 陷阱门槛", 2.6, 0.46, C_MAIN, "r"),
        ("8 多层算子", 3.10, 0.56, C_MAIN, "r"),
        ("7 多期", 3.60, 0.78, C_GREY, "l"),
        ("4 为什么奏效", 3.95, 0.86, C_GREY, "l"),
        ("5 新码从哪来", 3.95, 0.64, C_GREY, "l"),
        ("6 为什么是这一个", 3.95, 0.30, C_GREY, "l"),
    ]
    for name, x, y, col, side in items:
        ax.scatter([x], [y], s=54, color=col, zorder=3)
        if side == "l":
            ax.annotate(name, (x, y), textcoords="offset points", xytext=(-9, -3),
                        fontsize=8.0, color=col, ha="right")
        else:
            ax.annotate(name, (x, y), textcoords="offset points", xytext=(9, -3),
                        fontsize=8.0, color=col, ha="left")
    ax.axhline(0.70, color=C_GREY, lw=0.9, ls="--")
    ax.axvline(2.15, color=C_GREY, lw=0.9, ls="--")
    ax.text(0.80, 0.94, "便宜而要紧 → 先做", fontsize=8.0, color=C_ALT)
    ax.text(2.28, 0.94, "贵，但仍要有人做", fontsize=8.0, color=C_ALT)
    ax.text(0.80, 0.24, "便宜但小：可以等", fontsize=8.0, color=C_GREY)
    ax.text(2.28, 0.24, "换工具才谈得上：这是边界", fontsize=8.0, color=C_GREY)
    ax.set_xlim(0.75, 4.25); ax.set_ylim(0.18, 1.00)
    ax.set_xticks([1.2, 2.0, 2.6, 3.2, 3.9])
    ax.set_xticklabels(["一次复算", "一次调查", "一个序列", "一个项目", "换工具"], fontsize=8)
    ax.set_yticks([0.30, 0.55, 0.85])
    ax.set_yticklabels(["小", "中", "大"], fontsize=8)
    ax.set_xlabel("补起来要多久")
    ax.set_ylabel("补上后结论会变多少")
    save(fig, "c26_gaps")


# ---------------------------------------------------------------- 第 28 章
def fig_c28_cores() -> None:
    """六核心＝一条式子的六个部位（mathtext；不排假对齐，每个部位自带符号）。"""
    fig, ax = plt.subplots(figsize=(9.0, 3.9))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.0); ax.axis("off")

    ax.text(5.0, 4.62, r"$\min_{q}\;\; w\,D(q)\; +\; (T+\lambda)\,R(q)$",
            ha="center", va="center", fontsize=15, color=C_MAIN)
    ax.text(0.25, 4.62, "个体层：四个部位", fontsize=8.6, color=C_GREY, va="center")

    chips = [(1.55, r"$w$", "④ 选择", "价钱多半\n不在你手里"),
             (3.85, r"$D(q)$", "① 看见", "错看了地方\n还是分得粗"),
             (6.15, r"$(T+\lambda)$", "③ 跟上", "来不及\n还是累了"),
             (8.45, r"$R(q)$", "② 记住", "格子不够了")]
    for x, sym, q, ans in chips:
        ax.text(x, 3.86, sym, ha="center", va="center", fontsize=11.5, color=C_MAIN)
        ax.text(x, 3.34, q, ha="center", fontsize=8.8, color=C_MAIN)
        ax.text(x, 2.84, ans, ha="center", va="top", fontsize=7.2, color="#333333")

    ax.plot([0.6, 9.4], [2.28, 2.28], color=C_GREY, lw=0.7)
    ax.annotate("", xy=(5.0, 1.96), xytext=(5.0, 2.26),
                arrowprops=dict(arrowstyle="-|>", color=C_GREY, lw=1.0))
    ax.text(5.16, 2.06, "个体读数汇总成社会读数", fontsize=7.2, color=C_GREY, ha="left")

    ax.text(5.0, 1.72, r"$\gamma\,\bar D$   ＋   势垒 $C$", ha="center", va="center",
            fontsize=13, color=C_ALT)
    ax.text(0.25, 1.72, "群体层：两个部位", fontsize=8.6, color=C_GREY, va="center")
    for x, sym, q, ans in [(3.15, r"$\bar D$", "⑤ 讲述", "标签不丢事实，\n丢的是不确定"),
                           (6.95, r"$C$", "⑥ 临界", "门槛是一段斜坡：\n上坡慢、下坡更慢")]:
        ax.text(x, 1.16, q, ha="center", fontsize=8.8, color=C_ALT)
        ax.text(x, 0.62, ans, ha="center", va="top", fontsize=7.2, color="#333333")
    save(fig, "c28_cores")


# ---------------------------------------------------------------- 第 21 章
def fig_c21_scissors() -> None:
    """两端同时被拉宽：中国 1978—2024 的剪刀口，与世界那两条平线。"""
    import csv
    import collections
    rows = list(csv.DictReader(open(ROOT / "data" / "derived" / "wid_wealth_share.csv",
                                   encoding="utf-8-sig")))
    by = collections.defaultdict(dict)
    for r in rows:
        by[r["code"]][int(r["year"])] = (float(r["top1"]), float(r["bottom50"]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.5), sharey=True)

    def series(code, lo, hi):
        ys = sorted(y for y in by[code] if lo <= y <= hi)
        return ys, [by[code][y][0] * 100 for y in ys], [by[code][y][1] * 100 for y in ys]

    ys, t1, b50 = series("CN", 1978, 2024)
    ax1.plot(ys, t1, color=C_MAIN, lw=1.9, label="前 1%")
    ax1.plot(ys, b50, color=C_ALT, lw=1.9, label="后 50%")
    ax1.set_title("中国：一个剪刀口", fontsize=10, color=C_MAIN)
    ax1.annotate(f"{t1[0]:.1f}%", (ys[0], t1[0]), textcoords="offset points",
                 xytext=(4, 2), fontsize=7.6, color=C_MAIN)
    ax1.annotate(f"{t1[-1]:.1f}%", (ys[-1], t1[-1]), textcoords="offset points",
                 xytext=(-24, 2), fontsize=7.6, color=C_MAIN)
    ax1.annotate(f"{b50[0]:.1f}%", (ys[0], b50[0]), textcoords="offset points",
                 xytext=(4, -10), fontsize=7.6, color=C_ALT)
    ax1.annotate(f"{b50[-1]:.1f}%", (ys[-1], b50[-1]), textcoords="offset points",
                 xytext=(-24, -10), fontsize=7.6, color=C_ALT)
    ax1.set_ylim(0, 40)

    ys2, t1b, b50b = series("WO", 1995, 2023)
    ax2.plot(ys2, t1b, color=C_MAIN, lw=1.9, label="前 1%")
    ax2.plot(ys2, b50b, color=C_ALT, lw=1.9, label="后 50%")
    ax2.set_title("世界：两条平线", fontsize=10, color=C_MAIN)
    ax2.annotate(f"{t1b[0]:.1f}% → {t1b[-1]:.1f}%", (ys2[-1], t1b[-1]), textcoords="offset points",
                 xytext=(-6, 10), fontsize=7.6, color=C_MAIN, ha="right")
    ax2.annotate(f"{b50b[0]:.1f}% → {b50b[-1]:.1f}%", (ys2[-1], b50b[-1]), textcoords="offset points",
                 xytext=(-6, 10), fontsize=7.6, color=C_ALT, ha="right")

    for ax in (ax1, ax2):
        ax.set_xlabel("年份")
        ax.legend(frameon=False, fontsize=7.6, loc="upper left" if ax is ax1 else "center right")
    ax1.set_ylabel("财富份额（%）")
    save(fig, "c21_scissors")


# ---------------------------------------------------------------- 第 16 章
def fig_c16_costs() -> None:
    """三种执行方式的总成本曲线：差别不是好坏，是能撑多大。

    三条曲线是**示意**（C 级）：只要求形状对——暴力凸、程序有固定成本后走平、
    内化固定成本最高但几乎不随规模涨。交点的位置由此决定，不来自任何测量。
    """
    import numpy as np
    x = np.linspace(1, 100, 500)
    violent = 0.006 * x ** 2.1
    proced = 8 + 0.22 * x
    intern = 28 + 0.02 * x

    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    ax.plot(x, violent, color=C_ALT, lw=1.9, label="暴力：随人变贵")
    ax.plot(x, proced, color=C_MAIN, lw=1.9, label="程序：先付一笔，之后走平")
    ax.plot(x, intern, color=C_GREY, lw=1.9, ls="--", label="内化：付得最多，但几乎不随规模涨")
    ax.set_xlabel("要维持的规模")
    ax.set_ylabel("维持成本（示意单位）")
    ax.set_ylim(0, 46); ax.set_xlim(0, 100)
    ax.legend(frameon=False, fontsize=7.8, loc="upper left")
    ax.annotate("暴力在这里到头", (46, 0.006 * 46 ** 2.1), textcoords="offset points",
                xytext=(-10, -20), fontsize=7.6, color=C_ALT, ha="right")
    ax.annotate("程序在这里也要让位", (84, 8 + 0.22 * 84), textcoords="offset points",
                xytext=(6, -18), fontsize=7.6, color=C_MAIN, ha="left")
    ax.annotate("往右才是内化的地盘", (74, 28 + 0.02 * 74), textcoords="offset points",
                xytext=(0, 9), fontsize=7.6, color=C_GREY, ha="center")
    save(fig, "c16_costs")




if __name__ == "__main__":
    fig_c18_sched()
    fig_c22_grid()
    fig_c06_scales()
    fig_c04_ladder()
    fig_c26_gaps()
    fig_c28_cores()
    fig_c21_scissors()
    fig_c16_costs()
