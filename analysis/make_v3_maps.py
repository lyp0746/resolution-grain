#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3 三张判据图（随 knowledge-map.html 一起看）。

  v3_map_evoloop.png    演化环：K → π → ρ_ret → Φ/H/A → K，四个箭头各带一句可查判据
  v3_map_limits.png     极限退化矩阵：表 A.4 的可视化（点的大小只表示“退化强度”，不标数值）
  v3_map_field.png      场域竞争图：战争／贸易／模仿 × C／K／ρ，右下角画场域复制子的小环

为什么单写一个脚本：`make_theory_map.py` 负责章节网络与理论地图（3D + SVG），
这三张图是“判据的另一种写法”，与网络结构无关；分开写，重生成时互不影响。

每张图都自带一行“不能主张什么”。可视化不是装饰。

用法
  "$PY" -X utf8 analysis/make_v3_maps.py
"""
from pathlib import Path

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle

ROOT = Path(__file__).resolve().parents[1]
CHARTS = ROOT / "assets" / "charts"
SVG = ROOT / "assets" / "svg"
CHARTS.mkdir(parents=True, exist_ok=True)
SVG.mkdir(parents=True, exist_ok=True)

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
    "savefig.facecolor": "white",
})


def save(fig, name):
    fig.savefig(CHARTS / f"{name}.png", dpi=220, bbox_inches="tight")
    try:
        fig.savefig(SVG / f"{name}.svg", bbox_inches="tight")
    except Exception:
        pass
    plt.close(fig)
    print("saved", name)


def _node(ax, x, y, label, w=2.3, h=0.95, fc=CREAM, fs=7.2):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.06,rounding_size=0.12",
                                facecolor=fc, edgecolor=INK, lw=0.9))
    ax.text(x, y, label, ha="center", va="center", fontsize=fs, linespacing=1.35)


def _arrow(ax, p, q, color=INK, rad=0.18, lw=1.1):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11,
                                 color=color, lw=lw, shrinkA=10, shrinkB=10,
                                 connectionstyle=f"arc3,rad={rad}"))


def fig_evoloop():
    """演化环：四个箭头，四句判据。"""
    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    pos = {"K": (5.0, 8.6), "π": (8.5, 5.0), "ρ": (5.0, 1.4), "Φ": (1.5, 5.0)}
    labels = {"K": "$K$：变异核\n新码从哪来", "π": "$π$：适应度\n谁留下",
              "ρ": "$ρ_{ret}$：保留\n凭什么抄下去", "Φ": "$Φ$／$H$／$A$\n谁有资格说胜利"}
    # 先箭头、后节点：节点压住箭头端点，免得线穿过字
    _arrow(ax, pos["K"], pos["π"], OCHRE, 0.32)
    _arrow(ax, pos["π"], pos["ρ"], OCHRE, 0.32)
    _arrow(ax, pos["ρ"], pos["Φ"], OCHRE, 0.32)
    _arrow(ax, pos["Φ"], pos["K"], OCHRE, 0.32)
    for k, (x, y) in pos.items():
        _node(ax, x, y, labels[k], fc=CREAM if k != "Φ" else LIGHT)

    crit = [
        (6.95, 7.35, "判据：无新码、只有频率变化\n→ 这一环是选择，不是变异"),
        (6.95, 2.65, "判据：去掉保留，累积停下\n→ 这一环是保留，不是选择"),
        (2.05, 2.65, "判据：桌子不随码变\n→ 这一环是场域，不是适应度"),
        (2.05, 7.35, "判据：场域自己也被选\n→ 这一环是引擎，不是背景"),
    ]
    for x, y, t in crit:
        ax.text(x, y, t, ha="center", va="center", fontsize=6.0, color=GRAY, linespacing=1.5)

    ax.text(5.0, 5.0, "变异—选择—保留—场域\n一圈，不是一条线", ha="center", va="center",
            fontsize=8.0, color=INK, linespacing=1.6)
    ax.set_title("演化环：四个箭头，四句判据（第 18—22 章）", fontsize=9.5, loc="left")
    ax.text(0.0, -0.04, "不能主张什么：环上四步都不是必经之路；某一步可以长期停住（锁定、僵化、外生场域）。",
            transform=ax.transAxes, fontsize=6.2, color=RED)
    save(fig, "v3_map_evoloop")


def fig_limits():
    """极限退化矩阵：表 A.4 的图形版。点的大小＝退化强度（示意）。"""
    rows = [
        ("$K$→0", "复制子", 0.85, "无新码，只改频率"),
        ("$ρ_{ret}$→0", "无保留", 0.8, "累积失败、工具集变薄"),
        ("β→0", "中性漂移", 0.55, "份额随机走"),
        ("β→∞", "最佳回应", 0.55, "多态消失"),
        ("ζ→0", "单层选择", 0.5, "群体选择项关掉"),
        ("ζ→1", "纯群体选择", 0.5, "层内差异被压平"),
        ("Φ 固定", "场域外生", 0.7, "场域不随码变"),
        ("$C$→0", "无迟滞", 0.45, "2C 带消失"),
        ("$C$→∞", "锁定", 0.75, "只有外生冲击能改"),
        ("ν＝0／>0／<0", "冷漠／亲缘／榨取", 0.6, "别人的错不进账／正／负"),
        ("$A$→0／∞", "孤立／全球", 0.5, "桥少／桥多"),
        ("$G$→0", "无生态构建", 0.45, "环境不随码变"),
        ("$ε_t$→0", "无冲击", 0.4, "时刻全由内生环定"),
    ]
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    n = len(rows)
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.6, n - 0.4)
    ax.invert_yaxis()
    ax.axis("off")
    for i, (lim, back, w, crit) in enumerate(rows):
        ax.text(0.15, i, lim, fontsize=7.4, va="center", ha="left", color=INK)
        # 用 scatter（点单位），不用 Circle：轴不等比时 Circle 会被压成椭圆
        ax.scatter([3.1], [i], s=40 + 260 * w, facecolor=OCHRE, alpha=0.30,
                   edgecolor=OCHRE, linewidth=0.7, zorder=2)
        ax.text(3.95, i, back, fontsize=7.2, va="center", ha="left", color=INK)
        ax.text(5.95, i, crit, fontsize=6.2, va="center", ha="left", color=GRAY)
    ax.set_title("极限退化：十三行，各自退回谁（点越大＝退化越“彻底”，示意）", fontsize=9.2, loc="left")
    ax.text(0.0, -0.09, "不能主张什么：这只是“参数到边界时方程退成谁”，不是“谁更根本”；点是示意，不标数值。",
            transform=ax.transAxes, fontsize=6.2, color=RED)
    save(fig, "v3_map_limits")


def fig_field():
    """场域竞争：三列（战争／贸易／模仿）× 三参（C／K／ρ），右下角场域复制子小环。"""
    fig = plt.figure(figsize=(6.6, 3.6))
    ax = fig.add_axes([0.06, 0.08, 0.92, 0.80])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    cols = [("战争", 1.9), ("贸易", 4.4), ("模仿", 6.9)]
    for name, x in cols:
        ax.text(x, 9.4, name, ha="center", fontsize=8.4, color=INK)
    rows = [("$C$ 换码成本", 7.9, ["高", "中低", "低"]),
            ("$K$ 变异核", 6.4, ["低", "高", "中"]),
            ("$ρ_{ret}$ 保留", 4.9, ["高", "中", "高"])]
    for label, y, vals in rows:
        ax.text(0.1, y, label, fontsize=7.2, va="center", ha="left", color=INK)
        for (name, x), v in zip(cols, vals):
            ax.add_patch(FancyBboxPatch((x - 0.85, y - 0.55), 1.7, 1.1,
                                        boxstyle="round,pad=0.03,rounding_size=0.1",
                                        facecolor=LIGHT, edgecolor=INK, lw=0.7))
            ax.text(x, y, v, ha="center", va="center", fontsize=7.4)
    ax.text(4.4, 3.5, "场域决定哪一种可用：高 $H$、窄 $A$ → 战争与模仿；宽 $A$、低 $C$ → 贸易",
            ha="center", fontsize=6.6, color=GRAY)

    # 右下角：场域复制子小环（一条弯箭头 + 中心式子；不用 Circle，避免被压成椭圆）
    cx, cy = 8.3, 2.3
    ax.add_patch(FancyArrowPatch((cx - 0.62, cy - 0.38), (cx + 0.62, cy - 0.38),
                                 arrowstyle="-|>", mutation_scale=10, color=OCHRE, lw=1.1,
                                 connectionstyle="arc3,rad=-1.15"))
    ax.text(cx, cy + 0.18, "$Φ_{t+1}$\n$=H_Φ(P^{field}_t)$", ha="center", va="center",
            fontsize=6.4, linespacing=1.4)
    ax.text(cx, cy - 0.95, "场域自己也是一个复制子", ha="center", fontsize=6.0, color=GRAY)

    ax.set_title("场域竞争：三种竞争 × 三个参数（序关系，不是读数）", fontsize=9.2, loc="left")
    ax.text(0.0, -0.05, "不能主张什么：三档只是序关系；同一时期常有两条同时跑，不能只用一个参数讲完。",
            transform=ax.transAxes, fontsize=6.2, color=RED)
    save(fig, "v3_map_field")


if __name__ == "__main__":
    fig_evoloop()
    fig_limits()
    fig_field()
