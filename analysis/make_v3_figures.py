#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3 第五部分配图（第 18—22 章）。

与 make_v2_figures.py 同一套视觉语言（同 rcParams、同 6.4 in 版心、同 dpi 220），
但**单独成文件**：不改已发布的 v2_fig_*，避免"重生成时几何悄悄变"。见 AGENTS.md §9 第 6 条。

本文件现有：
  v3_fig_threshold.png   图18.1　错误阈值：允许的错数与基因组长度
  （第 19—22 章的图在写作时逐个加进来，函数名 fig_*，产出 v3_fig_*）

用法
  "$PY" -X utf8 analysis/make_v3_figures.py
"""
from pathlib import Path

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
CHARTS = ROOT / "assets" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

INK = "#2b2b2b"
OCHRE = "#b7791f"
BLUE = "#2b6cb0"
RED = "#b03a2e"
GREEN = "#2f855a"
GRAY = "#718096"
CREAM = "#f7f3ea"
LIGHT = "#e8e2d6"

mpl.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "SimHei"],
    "axes.unicode_minus": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "font.size": 9,
    "axes.titlesize": 9.5,
    "axes.labelsize": 8.2,
    "legend.fontsize": 7.6,
    "savefig.facecolor": "white",
})


def save(fig, name):
    fig.savefig(CHARTS / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


def _clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def fig_threshold():
    """图18.1　错误阈值：一个基因组每代能带几个错。

    左幅是 Eigen 条件 U* = lnσ / L（教科书式子，A 级；σ 取 1.5／2 两个示意值）。
    右幅是本书的读法：把 (K, ρ_ret) 分成三段——噪声、累积、僵化。
    """
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.0),
                             gridspec_kw={"width_ratios": [1.15, 1]})

    # 左：允许的错数随基因组长度下降
    ax = axes[0]
    L = np.logspace(2, 8, 400)
    for sigma, col, lab in ((1.5, BLUE, "σ = 1.5（优势小）"), (2.0, RED, "σ = 2（优势大）")):
        U = np.log(sigma) / L
        ax.plot(L, U, color=col, lw=1.8, label=lab)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1e-7, 1e-1)
    ax.set_xlabel("基因组长度 $L$（位点，对数轴）", fontsize=7.8)
    ax.set_ylabel("每代每基因组允许的错数 $U^*$", fontsize=7.8)
    ax.set_title("越长的基因组，越付不起错", fontsize=9.0, loc="left")
    ax.legend(frameon=False, loc="upper right")
    ax.tick_params(labelsize=7)
    _clean(ax)
    # 病毒量级的位置（示意的输入，不是读数）
    ax.axvspan(5e3, 3e4, color=OCHRE, alpha=0.10)
    ax.text(1.2e4, 3e-7, "RNA 病毒\n量级", ha="center", fontsize=6.4, color=OCHRE)
    ax.text(0.03, 0.06, "线上方：散架\n线下方：可存续\n（σ 为示意值）",
            transform=ax.transAxes, fontsize=6.4, color=GRAY, linespacing=1.5)

    # 右：本书的读法（定性，不给刻度）
    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.annotate("", xy=(0.97, 0.06), xytext=(0.08, 0.06),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1))
    ax.annotate("", xy=(0.08, 0.95), xytext=(0.08, 0.06),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1))
    ax.text(0.5, -0.02, "变异供给 $K$ →", ha="center", fontsize=7.6)
    ax.text(0.005, 0.5, "保留 $ρ_{ret}$ →", va="center", rotation=90, fontsize=7.6)
    ax.add_patch(plt.Rectangle((0.08, 0.06), 0.28, 0.89, color=GRAY, alpha=0.10))
    ax.add_patch(plt.Rectangle((0.36, 0.06), 0.30, 0.89, color=GREEN, alpha=0.12))
    ax.add_patch(plt.Rectangle((0.66, 0.06), 0.31, 0.89, color=RED, alpha=0.10))
    ax.text(0.22, 0.52, "僵化\n错得太少", ha="center", fontsize=7.4, color=INK)
    ax.text(0.51, 0.52, "累积\n错得起", ha="center", fontsize=7.4, color=GREEN)
    ax.text(0.815, 0.52, "噪声\n错得太多", ha="center", fontsize=7.4, color=RED)
    ax.set_title("三段，两个门槛", fontsize=9.0, loc="left")

    fig.tight_layout()
    save(fig, "v3_fig_threshold")


def fig_redqueen():
    """图19.1　负频率依赖：三种斜率，与一条没有固定周期的轨迹。

    左幅：同一类型的适应度对它自己频率的斜率。下斜＝红皇后（越常见越吃亏）；
          水平＝拥挤（只跟总量有关）；上斜＝规模报酬（越常见越占便宜）。
    右幅：两类码的份额互相追赶——只表示“绕圈”，**不给周期**（本书没有周期读数）。
    """
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.9),
                             gridspec_kw={"width_ratios": [1.1, 1]})

    # 左
    ax = axes[0]
    x = np.linspace(0.05, 0.95, 200)
    ax.plot(x, 1.0 - 0.62 * x, color=RED, lw=2.0, label="下斜：负频率依赖（红皇后）")
    ax.plot(x, np.full_like(x, 0.52), color=BLUE, lw=1.6, ls="--", label="水平：只是拥挤")
    ax.plot(x, 0.28 + 0.55 * x, color=GREEN, lw=1.6, ls=":", label="上斜：规模报酬")
    ax.set_xlim(0, 1)
    ax.set_ylim(0.1, 1.05)
    ax.set_xlabel("这一类型在群体里的频率 $P$", fontsize=7.8)
    ax.set_ylabel("相对适应度 $π$（示意）", fontsize=7.8)
    ax.set_title("“竞争激烈”不是红皇后；斜率才是", fontsize=9.0, loc="left")
    ax.legend(frameon=False, fontsize=6.4, loc="lower left")
    ax.tick_params(labelsize=7)
    _clean(ax)
    ax.annotate("停 = 相对退", xy=(0.30, 1 - 0.62 * 0.30), xytext=(0.05, 0.66),
                fontsize=6.8, color=RED,
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.9))

    # 右：绕圈，但没有固定周期
    ax = axes[1]
    t = np.linspace(0, 10, 400)
    a = 0.5 + 0.24 * np.sin(1.15 * t) + 0.07 * np.sin(2.6 * t + 1.0)
    b = 1 - a
    ax.plot(t, a, color=OCHRE, lw=1.8, label="$P_A$（码 A 的份额）")
    ax.plot(t, b, color=INK, lw=1.2, ls="--", label="$P_B$（码 B 的份额）")
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("时间（示意，无刻度）", fontsize=7.8)
    ax.set_ylabel("份额", fontsize=7.8)
    ax.set_title("互相追赶：绕圈，不是周期", fontsize=9.0, loc="left")
    ax.set_xticks([])
    ax.tick_params(labelsize=7)
    _clean(ax)
    ax.legend(frameon=False, fontsize=6.4, loc="upper right")
    ax.text(0.03, 0.05, "两条线一直不落定，\n也没有固定长度", transform=ax.transAxes,
            fontsize=6.4, color=GRAY, linespacing=1.5)

    fig.tight_layout()
    save(fig, "v3_fig_redqueen")


def fig_field():
    """图20.1　场域不是第三种冲击，是让冲击成为冲击的那张桌子。

    左：同一个冲击 ε，进三张不同的桌子（Φ），出来三个不同的名字。
    右：场域复制子——码的分布喂给桌子，桌子再喂回适应度（一个环，不是一个箭头）。
    """
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.0),
                             gridspec_kw={"width_ratios": [1.12, 1]})

    # 左：一个冲击，三张桌子，三个名字
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.1, 4.1), 1.5, 1.8, facecolor=CREAM, edgecolor=INK, lw=1.0))
    ax.text(0.85, 5.0, "冲击\n$ε_t$", ha="center", va="center", fontsize=7.4)
    rows = [(7.9, "桌子 A：命名权集中、桥少", "“黑天鹅”"),
            (5.0, "桌子 B：命名权分散、可比较", "“灰犀牛”"),
            (2.1, "桌子 C：没人有资格命名", "“噪声”")]
    for y, lab, name in rows:
        ax.add_patch(plt.Rectangle((3.1, y - 0.62), 3.5, 1.24, facecolor=LIGHT, edgecolor=INK, lw=0.8))
        ax.text(4.85, y, lab, ha="center", va="center", fontsize=6.2, linespacing=1.4)
        ax.annotate("", xy=(3.05, y), xytext=(1.7, 5.0),
                    arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=0.9,
                                    connectionstyle="arc3,rad=0.18"))
        ax.annotate("", xy=(8.55, y), xytext=(6.65, y),
                    arrowprops=dict(arrowstyle="-|>", color=OCHRE, lw=1.0))
        ax.text(8.7, y, name, ha="left", va="center", fontsize=7.2, color=OCHRE)
    ax.set_title("同一个冲击，三张桌子，三个名字", fontsize=9.0, loc="left")

    # 右：场域复制子
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    nodes = {"码的分布 $P^{field}_t$": (5.0, 8.0),
             "桌子 $Φ_{t+1}$": (8.2, 4.4),
             "适应度 $π$": (5.0, 1.4),
             "场域份额": (1.7, 4.4)}
    for lab, (x, y) in nodes.items():
        ax.add_patch(plt.Circle((x, y), 1.25, facecolor=CREAM, edgecolor=INK, lw=0.9))
        ax.text(x, y, lab, ha="center", va="center", fontsize=6.3, linespacing=1.3)
    pairs = [((5.0, 8.0), (8.2, 4.4)), ((8.2, 4.4), (5.0, 1.4)),
             ((5.0, 1.4), (1.7, 4.4)), ((1.7, 4.4), (5.0, 8.0))]
    for (x1, y1), (x2, y2) in pairs:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0,
                                    shrinkA=26, shrinkB=26,
                                    connectionstyle="arc3,rad=0.22"))
    ax.set_title("桌子也在被选：一圈，不是一条线", fontsize=9.0, loc="left")

    fig.tight_layout()
    save(fig, "v3_fig_field")


def fig_culture():
    """图21.1　第二种遗传：保留率决定了能攒多厚。

    左：可维持的技能复杂度随“有效连接”（人多、联系密）上升而饱和；两个点分别示意
        隔离的小群体（塔斯马尼亚）与连通的大群岛（波利尼西亚）。形状取自 Henrich 2004
        的模型，**刻度自拟，不是读数**。
    右：三种保留装置（教学／档案／平台）各自把损失率压到什么程度——高度是示意。
    """
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.9),
                             gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    x = np.linspace(0, 10, 300)
    y = 1 - np.exp(-x / 3.2)
    ax.plot(x, y, color=INK, lw=2.0)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("有效连接：人多 × 联系密（示意）", fontsize=7.8)
    ax.set_ylabel("可维持的技能复杂度（示意）", fontsize=7.8)
    ax.set_title("攒得住多厚，看连接有多密", fontsize=9.0, loc="left")
    ax.set_xticks([])
    ax.set_yticks([])
    _clean(ax)
    ax.plot([1.4], [1 - np.exp(-1.4 / 3.2)], "o", color=RED, ms=5)
    ax.annotate("隔离的小群体\n（塔斯马尼亚）", xy=(1.4, 1 - np.exp(-1.4 / 3.2)),
                xytext=(2.2, 0.12), fontsize=6.6, color=RED,
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.8))
    ax.plot([6.8], [1 - np.exp(-6.8 / 3.2)], "o", color=GREEN, ms=5)
    ax.annotate("连通的大群岛\n（波利尼西亚）", xy=(6.8, 1 - np.exp(-6.8 / 3.2)),
                xytext=(6.0, 0.55), fontsize=6.6, color=GREEN,
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=0.8))
    ax.text(0.98, 0.06, "曲线形状取 Henrich 2004 的模型；\n刻度自拟，只读方向",
            transform=ax.transAxes, ha="right", fontsize=6.2, color=GRAY, linespacing=1.5)

    ax = axes[1]
    labs = ["教学\n（人对人）", "档案\n（跨代存）", "平台\n（大规模复制）"]
    vals = [0.55, 0.75, 0.9]
    bars = ax.bar(labs, vals, color=[OCHRE, BLUE, GREEN], width=0.55, alpha=0.85)
    # 不在柱上标数值：三档是示意，标上数字就会被读成读数
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("保留率 $ρ_{ret}$（示意）", fontsize=7.8)
    ax.set_title("三种保留装置，谁压得住损失", fontsize=9.0, loc="left")
    ax.tick_params(labelsize=6.8)
    _clean(ax)
    ax.text(0.5, -0.30, "三档高度是示意，不是读数", transform=ax.transAxes,
            ha="center", fontsize=6.4, color=GRAY)

    fig.tight_layout()
    save(fig, "v3_fig_culture")


def fig_limits():
    """图22.1　四道门：方程的定义域，与“收不进／还没算”的判据。

    左：一个大框是方程能算的地方（K、ρ_ret、π 都在同一个空间里），四个箭头指向门外四件事。
        门外的不是“更难算”，是“不该用这条方程算”。
    右：一个两问的判据——缺的是哪个量，能不能说出来。
    """
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.0),
                             gridspec_kw={"width_ratios": [1.15, 1]})

    # 左：定义域与四道门
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((2.6, 2.6), 4.4, 4.4, facecolor=CREAM, edgecolor=INK, lw=1.2))
    ax.text(4.8, 5.6, "方程的定义域", ha="center", fontsize=7.8)
    ax.text(4.8, 4.6, "$K$、$ρ_{ret}$、$π$\n都在同一个空间里", ha="center", va="center",
            fontsize=6.6, color=GRAY, linespacing=1.5)
    doors = [(4.8, 8.4, "① 第一个复制子\n（$P_t$ 怎么来的）"),
             (8.5, 4.8, "② 新维度\n（$K$ 的支撑从哪来）"),
             (4.8, 1.2, "③ 冲击的时刻\n（哪一年）"),
             (1.1, 4.8, "④ 为什么是这一个\n（偶然与人事）")]
    for x, y, lab in doors:
        ax.annotate("", xy=(x, y), xytext=(4.8, 4.8),
                    arrowprops=dict(arrowstyle="-|>", color=OCHRE, lw=1.0,
                                    shrinkA=40, shrinkB=14))
        ax.text(x, y, lab, ha="center", va="center", fontsize=6.2, color=INK, linespacing=1.4)
    ax.set_title("四道门：门外的不是失败，是定义域", fontsize=9.0, loc="left")

    # 右：两问判据
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.6, 7.4), 8.8, 1.6, facecolor=LIGHT, edgecolor=INK, lw=0.8))
    ax.text(5.0, 8.2, "缺的是哪一个量？说得出吗", ha="center", fontsize=7.0)
    ax.add_patch(plt.Rectangle((0.6, 4.4), 4.0, 2.0, facecolor=CREAM, edgecolor=INK, lw=0.8))
    ax.text(2.6, 5.4, "说得出：\n“还没算”", ha="center", fontsize=7.0, linespacing=1.5)
    ax.add_patch(plt.Rectangle((5.4, 4.4), 4.0, 2.0, facecolor="#f6e9e6", edgecolor=RED, lw=0.9))
    ax.text(7.4, 5.4, "说不出：\n“收不进”", ha="center", fontsize=7.0, color=RED, linespacing=1.5)
    ax.annotate("", xy=(2.6, 6.4), xytext=(4.4, 7.4),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0,
                                connectionstyle="arc3,rad=0.15"))
    ax.annotate("", xy=(7.4, 6.4), xytext=(5.6, 7.4),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0,
                                connectionstyle="arc3,rad=-0.15"))
    ax.text(2.6, 3.5, "欠账：可以立项", ha="center", fontsize=6.4, color=GRAY)
    ax.text(7.4, 3.5, "边界：只能写情景", ha="center", fontsize=6.4, color=GRAY)
    ax.add_patch(plt.Rectangle((1.2, 0.9), 7.6, 1.8, facecolor="white", edgecolor=GRAY, lw=0.7, ls="--"))
    ax.text(5.0, 1.8, "判据：能不能指出\n“缺的那个量叫什么、怎么测”", ha="center", fontsize=6.2,
            color=GRAY, linespacing=1.5)
    ax.set_title("两个词，一种判据", fontsize=9.0, loc="left")

    fig.tight_layout()
    save(fig, "v3_fig_limits")


if __name__ == "__main__":
    fig_threshold()
    fig_redqueen()
    fig_field()
    fig_culture()
    fig_limits()
