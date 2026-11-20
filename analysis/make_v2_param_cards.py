#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2 参数卡：给第 4—6 章与第 IV—V 部分备的单独配图。"""
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "charts"
INK, OCHRE, BLUE, RED, GRAY = "#2b2b2b", "#b7791f", "#2b6cb0", "#b03a2e", "#718096"
mpl.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "SimHei"], "axes.unicode_minus": False,
    "figure.facecolor": "white", "axes.facecolor": "white", "axes.edgecolor": INK,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "font.size": 10, "axes.titlesize": 11,
})


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


def card_v():
    x = np.linspace(-3, 3, 400)
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(x, np.exp(-x ** 2 / 0.18), color=RED, lw=2, label="细：v 小")
    ax.plot(x, np.exp(-x ** 2 / 1.5), color=GRAY, lw=2, label="粗：v 大")
    ax.set_title("v：在那个位置上分多细")
    ax.set_yticks([]); ax.legend(frameon=False)
    ax.text(0, -0.16, "v 是结果，不是直接可拧的旋钮", ha="center", transform=ax.transAxes, fontsize=8, color=GRAY)
    save(fig, "v2_fig_v")


def card_prices():
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.5))
    ax = axes[0]
    ax.barh([0, 1, 2], [0.3, 0.8, 1.4], color=[GRAY, OCHRE, RED], height=0.5)
    ax.set_yticks([0, 1, 2]); ax.set_yticklabels(["无关", "有点疼", "很疼"])
    ax.set_title("w：错了多疼"); ax.set_xticks([]); ax.set_xlim(0, 1.7)
    ax = axes[1]
    c = np.linspace(0.2, 3, 200)
    for w, col in [(0.6, GRAY), (1.2, BLUE), (2.4, RED)]:
        ax.plot(c, c / (2 * w), color=col, lw=1.8, label=f"w={w}")
    ax.set_title("T+λ 与 v：价格越贵，码越粗")
    ax.set_xlabel("T + λ"); ax.set_ylabel("v*"); ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); save(fig, "v2_fig_prices")


def card_C():
    y = np.linspace(-2.2, 2.2, 400)
    V = 0.25 * (y ** 2 - 1) ** 2
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(y, V, color=INK, lw=2)
    ax.axhline(0.25, color=RED, ls="--", lw=1)
    ax.text(0, 0.27, "2C：迟滞带宽", ha="center", fontsize=9, color=RED)
    ax.set_title("C：换码成本与迟滞")
    ax.set_yticks([]); ax.set_xticks([]); ax.set_ylim(0, 1.0)
    save(fig, "v2_fig_C")


def card_network():
    rng = np.random.default_rng(3)
    pts = rng.normal(0, 0.55, (14, 2))
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if np.linalg.norm(pts[i] - pts[j]) < 0.9:
                ax.plot([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]], color=GRAY, lw=0.8, alpha=0.7)
    ax.scatter(pts[:, 0], pts[:, 1], s=26, color=BLUE, zorder=3)
    ax.set_title("γ / A：一致性压力与关系网")
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    ax.text(0, -0.12, "γ 管偏离，A 管谁看得到谁", ha="center", transform=ax.transAxes, fontsize=8, color=GRAY)
    save(fig, "v2_fig_network")


def card_I():
    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    def box(x, y, w, h, t):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                    fc="#f7f3ea", ec=INK, lw=1))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=9)
    box(0.04, 0.58, 0.28, 0.22, "对象 G")
    box(0.68, 0.58, 0.28, 0.22, "特征 M")
    box(0.36, 0.20, 0.28, 0.22, "I(q;M,R)\n蕴涵集")
    ax.add_patch(FancyArrowPatch((0.32, 0.69), (0.36, 0.42), arrowstyle="-|>", mutation_scale=10, color=GRAY))
    ax.add_patch(FancyArrowPatch((0.68, 0.69), (0.64, 0.42), arrowstyle="-|>", mutation_scale=10, color=GRAY))
    ax.set_title("I(q)：切完能推出什么")
    save(fig, "v2_fig_I")


if __name__ == "__main__":
    card_v(); card_prices(); card_C(); card_network(); card_I()
