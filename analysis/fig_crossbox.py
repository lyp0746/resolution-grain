#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图 26.1（跨格章）：两格与一条通道；套利的可得性随通道宽度的形状。

左幅：两套码（两套不同的格子）与它们之间的通道；通道上的人是"跨格者"，
      他在两边都有签名权。**不给刻度**：这是结构示意，不是测量。
右幅：套利可得性随通道宽度先升后降——太窄收不到（信息过不来），
      太宽价差被抹平（两边用同一套码）。峰的位置是设定值，只演示形状。

输出：assets/charts/c26_crossbox.png / .svg
"""
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
CHARTS = ROOT / "assets" / "charts"
SVG = ROOT / "assets" / "svg"
CHARTS.mkdir(parents=True, exist_ok=True)
SVG.mkdir(parents=True, exist_ok=True)

INK = "#2b2b2b"
OCHRE = "#b7791f"
BLUE = "#2b6cb0"
RED = "#b03a2e"
GRAY = "#718096"
LIGHT = "#e8e2d6"

mpl.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "SimHei"],
    "axes.unicode_minus": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "text.color": INK,
    "font.size": 9,
    "axes.titlesize": 10,
})

fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.1),
                               gridspec_kw={"width_ratios": [1.15, 1]})

# ---------------- 左幅：两套格子，一条通道
axL.set_xlim(0, 10); axL.set_ylim(0, 6.4); axL.axis("off")

# 左格：4×4
for i in range(4):
    for j in range(4):
        axL.add_patch(Rectangle((0.35 + i * 0.62, 1.6 + j * 0.62), 0.62, 0.62,
                                fill=False, lw=0.7, ec=BLUE, alpha=0.75))
# 右格：3×5（切法不同）
for i in range(3):
    for j in range(5):
        axL.add_patch(Rectangle((6.35 + i * 0.82, 1.05 + j * 0.5), 0.82, 0.5,
                                fill=False, lw=0.7, ec=OCHRE, alpha=0.75))
axL.text(1.6, 4.9, "甲 的 码", ha="center", fontsize=10, color=BLUE)
axL.text(7.6, 4.9, "乙 的 码", ha="center", fontsize=10, color=OCHRE)
axL.text(1.6, 0.9, "切点：按“怎么做”", ha="center", fontsize=7.5, color=GRAY)
axL.text(7.6, 0.55, "切点：按“谁负责”", ha="center", fontsize=7.5, color=GRAY)

# 通道
axL.add_patch(Rectangle((3.15, 2.15), 3.0, 1.35, fc=LIGHT, ec=GRAY, lw=0.8, ls=(0, (4, 3))))
axL.text(4.65, 3.86, "通　道", ha="center", fontsize=8, color=GRAY)

# 跨格者
axL.plot([4.65], [2.82], marker="o", ms=11, mfc=RED, mec="white", mew=1.6, zorder=5)
axL.text(4.65, 2.28, "跨格者", ha="center", fontsize=8.5, color=RED)
axL.text(4.65, 1.85, "两边都有签名权", ha="center", fontsize=7, color=RED)

# 三条通道上的量
axL.annotate("", xy=(3.05, 3.25), xytext=(1.35, 3.25),
             arrowprops=dict(arrowstyle="->", lw=0.9, color=INK))
axL.annotate("", xy=(6.25, 3.25), xytext=(6.05, 3.25),
             arrowprops=dict(arrowstyle="->", lw=0.9, color=INK))
axL.text(1.05, 3.25, "τ", fontsize=9, va="center")
axL.text(5.55, 5.6, "通道宽度 = 2C", ha="center", fontsize=8, color=INK)
axL.annotate("", xy=(3.15, 5.3), xytext=(6.15, 5.3),
             arrowprops=dict(arrowstyle="<->", lw=0.9, color=INK))
axL.text(4.65, 0.15, "谁有权定名（Φ 的集中度）决定通道开在哪", ha="center",
         fontsize=7.5, color=GRAY)

# ---------------- 右幅：可得性随通道宽度
x = np.linspace(0, 1, 400)
y = x * (1 - x) * 4.0          # 归一化到峰值 1
axR.plot(x, y, lw=1.9, color=RED)
axR.fill_between(x, 0, y, color=RED, alpha=0.08)
axR.set_xlabel("通道宽度（示意，无刻度）")
axR.set_ylabel("套利可得性")
axR.set_title("太窄收不到，太宽没有价差", fontsize=9.5)
axR.set_xticks([0, 0.5, 1])
axR.set_xticklabels(["0\n（格不相通）", "适中", "1\n（码合并）"], fontsize=8)
axR.set_yticks([0, 1])
axR.set_yticklabels(["0", "峰"], fontsize=8)
axR.set_ylim(0, 1.25)
axR.annotate("价差被磨平：\n只剩一套码", xy=(0.94, 0.23), xytext=(0.62, 0.08),
             fontsize=7.5, color=GRAY,
             arrowprops=dict(arrowstyle="->", lw=0.7, color=GRAY))
axR.annotate("信息过不来：\n没有可比的两个价", xy=(0.07, 0.26), xytext=(0.02, 0.60),
             fontsize=7.5, color=GRAY,
             arrowprops=dict(arrowstyle="->", lw=0.7, color=GRAY))
axR.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
fig.savefig(CHARTS / "c26_crossbox.png", dpi=300, bbox_inches="tight")
print("wrote", CHARTS / "c26_crossbox.png")
