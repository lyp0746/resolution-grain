#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2 配图：原理示意图、参数地图、审美、nu、VOI、创造。

输出：
  assets/charts/v2_*.png
  assets/svg/v2_*.svg
"""
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle

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
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "savefig.facecolor": "white",
})


def save(fig, name):
    fig.savefig(CHARTS / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


def box(ax, x, y, w, h, text, fc=CREAM, ec=INK, fs=8.5, lw=1.0, dashed=False):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                       linewidth=lw, edgecolor=ec, facecolor=fc,
                       linestyle="--" if dashed else "-")
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK)


def arrow(ax, x1, y1, x2, y2, color=INK, lw=1.0, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=10, linewidth=lw, color=color, linestyle=ls))


# ---------------------------------------------------------------- 1. principle map
def fig_principle():
    """纵向推导链。版心按 6.4in 宽设计：印刷时按 100% 排，图内字不再缩。"""
    fig, ax = plt.subplots(figsize=(6.4, 6.3))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.0, 0.995, "一条原理，五个假设，一个泛函", fontsize=12, fontweight="bold",
            color=INK, va="top")
    ax.text(0.0, 0.945, "实线是推导；虚线是假设。每一条实线的两端，都有一条虚线在托着。",
            fontsize=7.8, color=GRAY, va="top")

    steps = [
        (0.815, "A1　有限区分", "预算有限 · 区分有价 · 划分要被选择"),
        (0.675, "D1—D5　五个定义", "q 划分 · D 加权失真 · R 与 δ · B=(T,λ,M) · 生存"),
        (0.535, "T1—T5　条件定理", "v*=(T+λ)/2w · δ=Δ/2^R · k* 标度 · 2C 带宽 · 块分解"),
        (0.395, "四个算子", "Π 看见什么 · q 怎么切 · U 先动哪个 · I 切完推出什么"),
        (0.255, "一个泛函", "wD + (T+λ)R − VOI + γ q^T L(A) q"),
    ]
    for y, head, body in steps:
        box(ax, 0.10, y, 0.80, 0.096, "", fc=CREAM, ec=INK, fs=8)
        ax.text(0.13, y + 0.066, head, fontsize=9.2, fontweight="bold", color=INK, va="center")
        ax.text(0.13, y + 0.030, body, fontsize=7.8, color="#3c3c3c", va="center")
    for y in [0.815, 0.675, 0.535, 0.395]:
        arrow(ax, 0.50, y - 0.003, 0.50, y - 0.034, color=INK, lw=1.1)

    ax.text(0.02, 0.223, "五个建模假设（不藏在定理后面）：", fontsize=8.2, color=RED, fontweight="bold")
    ass = [
        "A2 失真形状\n二次 → v*",
        "线性响应\nw = w0 + αAP − βP",
        "语义特征集\nI(q;M,R)",
        "制度成本\nΦ, C_Φ, H",
        "核实技术\na(e,s), τ_v",
    ]
    for i, tx in enumerate(ass):
        x = 0.02 + i * 0.193
        box(ax, x, 0.090, 0.175, 0.080, tx, fc="#fdf6ec", ec=RED, fs=6.8, dashed=True)
    ax.text(0.02, 0.048, "一个网络约定：无向图＋二次型；有向图换有向拉普拉斯。",
            fontsize=7.4, color=GRAY)
    ax.text(0.02, 0.014, "四层＝同一个泛函的四个约束：网络，不是阶梯；形式类比，不是定理。",
            fontsize=7.4, color=GRAY)
    save(fig, "v2_fig_principle")


# ---------------------------------------------------------------- 2. parameter atlas
def fig_parameters():
    fig, axes = plt.subplots(5, 2, figsize=(6.4, 9.9))
    axes = axes.ravel()
    x = np.linspace(-3, 3, 400)

    # mu
    ax = axes[0]
    for c, lab in [(-1.2, "低 μ：具体"), (0.8, "高 μ：抽象")]:
        ax.plot(x, np.exp(-(x - c) ** 2 / 0.5), color=BLUE if c > 0 else OCHRE, lw=1.6)
        ax.annotate(lab, (c, 1.02), ha="center", fontsize=8)
    ax.set_title("μ：码围着什么建")
    ax.set_yticks([]); ax.set_xticks([]); ax.set_ylim(0, 1.25)
    ax.text(0, -0.18, "看哪儿，不是看多细", ha="center", transform=ax.transAxes, fontsize=8, color=GRAY)

    # v
    ax = axes[1]
    ax.plot(x, np.exp(-x ** 2 / 0.18), color=RED, lw=1.6, label="细")
    ax.plot(x, np.exp(-x ** 2 / 1.5), color=GRAY, lw=1.6, label="粗")
    ax.set_title("v：在那个位置上分多细")
    ax.set_yticks([]); ax.set_xticks([]); ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.text(0, -0.18, "v 是结果，不是直接可拧的", ha="center", transform=ax.transAxes, fontsize=8, color=GRAY)

    # T+lambda vs v
    ax = axes[2]
    c = np.linspace(0.2, 3, 200)
    for w, col in [(0.6, GRAY), (1.2, BLUE), (2.4, RED)]:
        ax.plot(c, c / (2 * w), color=col, lw=1.5, label=f"w={w}")
    ax.set_title("T+λ 与 v：价格越贵，码越粗")
    ax.set_xlabel("T + λ"); ax.set_ylabel("v*")
    ax.legend(frameon=False, fontsize=8); ax.set_xlim(0.2, 3); ax.set_ylim(0, 2.5)

    # w
    ax = axes[3]
    ax.barh([0, 1, 2], [0.3, 0.8, 1.4], color=[GRAY, OCHRE, RED], height=0.5)
    ax.set_yticks([0, 1, 2]); ax.set_yticklabels(["无关", "有点疼", "很疼"])
    ax.set_title("w：错了多疼")
    ax.set_xticks([]); ax.set_xlim(0, 1.7)
    ax.text(0, -0.2, "疼的地方，码会变细", ha="center", transform=ax.transAxes, fontsize=8, color=GRAY)

    # C double well
    ax = axes[4]
    y = np.linspace(-2.2, 2.2, 400)
    V = 0.25 * (y ** 2 - 1) ** 2
    ax.plot(y, V, color=INK, lw=1.6)
    ax.axhline(0.25, color=RED, ls="--", lw=1)
    ax.annotate("", xy=(-0.577, 0.25), xytext=(0.577, 0.25),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=1.0))
    ax.text(0, 0.285, "2C", ha="center", fontsize=8.5, color=RED)
    ax.text(-2.1, 0.10, "低窝", fontsize=7.5, color=GRAY)
    ax.text(-2.1, 0.62, "两侧阈值之差＝条带宽", fontsize=7.5, color=GRAY)
    ax.set_title("C：换码成本与迟滞")
    ax.set_yticks([]); ax.set_xticks([]); ax.set_ylim(0, 0.75)

    # gamma / A network
    ax = axes[5]
    rng = np.random.default_rng(3)
    pts = rng.normal(0, 0.55, (12, 2))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if np.linalg.norm(pts[i] - pts[j]) < 0.9:
                ax.plot([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]], color=GRAY, lw=0.8, alpha=0.7)
    ax.scatter(pts[:, 0], pts[:, 1], s=22, color=BLUE, zorder=3)
    ax.set_title("γ / A：一致性压力与关系网")
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    ax.text(0, -0.16, "γ 管偏离，A 管谁看得到谁", ha="center", transform=ax.transAxes, fontsize=8, color=GRAY)

    # nu ripples
    ax = axes[6]
    for r, a in [(0.25, 1.0), (0.5, 0.65), (0.75, 0.4), (1.0, 0.22)]:
        ax.add_patch(Circle((0, 0), r, fill=False, color=OCHRE, lw=1.4, alpha=a))
    ax.scatter([0], [0], color=RED, s=20, zorder=3)
    ax.text(0, 0.08, "己", ha="center", fontsize=8)
    ax.text(0.65, 0.55, "家", fontsize=8, color=GRAY)
    ax.text(1.05, 0.85, "乡", fontsize=8, color=GRAY)
    ax.set_title("ν（爱）：集中的，不是均匀的")
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25); ax.set_aspect("equal"); ax.axis("off")

    # VOI
    ax = axes[7]
    p = np.linspace(0.01, 0.99, 300)
    def voi(p, Lfn, Lfp, q=0.7):
        C0 = np.minimum(p * Lfn, (1 - p) * Lfp)
        pe1 = q * p + (1 - q) * (1 - p); p1 = q * p / pe1
        pe0 = (1 - q) * p + q * (1 - p); p0 = (1 - q) * p / pe0
        C1 = pe1 * np.minimum(p1 * Lfn, (1 - p1) * Lfp) + pe0 * np.minimum(p0 * Lfn, (1 - p0) * Lfp)
        return C0 - C1
    for Lfn, Lfp, col, lab in [(1, 1, GRAY, "对称"), (5, 1, RED, "怕漏"), (1, 5, BLUE, "怕误")]:
        ax.plot(p, voi(p, Lfn, Lfp), color=col, lw=1.5, label=lab)
    ax.set_title("κ / VOI：峰位随阈值移动")
    ax.set_xlabel("p"); ax.set_ylabel("VOI"); ax.legend(frameon=False, fontsize=8)

    # I(q) lattice
    ax = axes[8]
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    box(ax, 0.03, 0.55, 0.28, 0.25, "对象", fs=7.5)
    box(ax, 0.69, 0.55, 0.28, 0.25, "特征 M", fs=7.5)
    box(ax, 0.36, 0.16, 0.28, 0.25, "I(q;M,R)\n蕴涵集", fs=7.5, fc="#fdf6ec")
    arrow(ax, 0.31, 0.67, 0.36, 0.42, color=GRAY)
    arrow(ax, 0.69, 0.67, 0.64, 0.42, color=GRAY)
    ax.set_title("I(q)：切完能推出什么")

    ax = axes[9]
    ax.axis("off")
    ax.text(0.0, 0.86, "读法", fontsize=9.5, fontweight="bold", color=INK)
    ax.text(0.0, 0.70, "每一格是一只旋钮：看哪一只、往哪边动。", fontsize=8, color="#3c3c3c")
    ax.text(0.0, 0.52, "不是测量值；也不是四项账的分解。", fontsize=8, color="#3c3c3c")
    ax.text(0.0, 0.34, "后六部分轮流打开其中一两格。", fontsize=8, color=GRAY)
    fig.suptitle("参数地图：十一个量", fontsize=14, fontweight="bold", y=0.997)
    fig.tight_layout(rect=[0, 0, 1, 0.975])
    save(fig, "v2_fig_parameters")


# ---------------------------------------------------------------- 3. aesthetics
def fig_aesthetic():
    """审美：压缩 × 连贯 × 新颖。版心 6.4 in（排版轮重画：原 11.2 in 排进 140 mm 只剩一半）。"""
    fig = plt.figure(figsize=(6.4, 5.9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.18], hspace=0.52, wspace=0.35)
    # (a) W(Nov)
    ax = fig.add_subplot(gs[0, 0])
    n = np.linspace(0, 1, 400)
    w = np.exp(-((n - 0.55) ** 2) / (2 * 0.18 ** 2))
    ax.plot(n, w, color=INK, lw=1.7)
    for x, col in [(0.26, GRAY), (0.55, OCHRE), (0.86, RED)]:
        ax.axvline(x, color=col, ls=":", lw=0.8)
    ax.text(0.06, 0.22, "太旧", fontsize=7.0, color=GRAY)
    ax.text(0.50, 0.34, "刚好", fontsize=7.0, color=OCHRE)
    ax.text(0.74, 0.22, "太新", fontsize=7.0, color=RED)
    ax.set_title("W(Nov)：倒 U", fontsize=8.4, loc="left")
    ax.set_xlabel("新颖度", fontsize=7.2); ax.set_ylabel("审美值", fontsize=7.2)
    ax.set_xticks([]); ax.tick_params(labelsize=6.8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    # (b) timeline
    ax = fig.add_subplot(gs[0, 1])
    xs = np.arange(5); vals = [0.25, 0.55, 0.78, 0.86, 0.95]
    ax.plot(xs, vals, color=OCHRE, lw=1.7, marker="o", ms=4)
    ax.set_ylim(0.1, 1.15); ax.set_xticks(xs)
    ax.set_xticklabels(["1863", "1874", "1886", "1900", "2000"], fontsize=6.6)
    ax.set_title("从讥讽到正典：A 的复利", fontsize=8.4, loc="left")
    ax.set_ylabel("可见度 / A", fontsize=7.2); ax.tick_params(labelsize=6.8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    # (c) Cmp × Coh
    ax = fig.add_subplot(gs[1, :])
    c = np.linspace(0.05, 1, 220); k = np.linspace(0.05, 1, 220)
    C, K = np.meshgrid(c, k); A = C * K
    cf = ax.contourf(C, K, A, levels=12, cmap="YlOrBr", alpha=0.78)
    ax.contour(C, K, A, levels=[0.15, 0.35, 0.55], colors="white", linewidths=0.6)
    pts = {"1874 印象派": (0.78, 0.72, RED), "学院派": (0.55, 0.85, BLUE),
           "标签": (0.18, 0.85, GRAY), "伪造品": (0.75, 0.82, OCHRE)}
    offs = {"1874 印象派": (4, -11), "学院派": (-6, 7), "标签": (4, 6), "伪造品": (-30, 8)}
    for lab, (xx, yy, col) in pts.items():
        ax.scatter([xx], [yy], s=30, color=col, edgecolor="white", zorder=3)
        ax.annotate(lab, (xx, yy), xytext=offs[lab], textcoords="offset points",
                    fontsize=7.0, color=col)
    ax.set_title("Cmp × Coh：审美筛选", fontsize=8.4, loc="left")
    ax.set_xlabel("压缩 Cmp", fontsize=7.2); ax.set_ylabel("连贯 Coh", fontsize=7.2)
    ax.tick_params(labelsize=6.8)
    fig.colorbar(cf, ax=ax, fraction=0.03, pad=0.015).ax.tick_params(labelsize=6.6)
    fig.text(0.01, 0.985, "审美：压缩 × 连贯 × 新颖", fontsize=10.0, fontweight="bold")
    fig.subplots_adjust(left=0.10, right=0.95, top=0.90, bottom=0.08)
    save(fig, "v2_fig_aesthetic")


# ---------------------------------------------------------------- 4. nu
def fig_nu():
    """爱：差序与 ν 矩阵。版心 6.4 in（排版轮重画：原 9.6 in）。"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.9), gridspec_kw={"width_ratios": [1.0, 1.2], "wspace": 0.32})
    ax = axes[0]
    for r, a in [(0.18, 1.0), (0.36, 0.72), (0.54, 0.5), (0.72, 0.32), (0.9, 0.18)]:
        ax.add_patch(Circle((0, 0), r, fill=False, color=OCHRE, lw=1.5, alpha=a))
    ax.scatter([0], [0], color=RED, s=22, zorder=3)
    ax.text(0, 0.07, "己", ha="center", fontsize=7.6)
    ax.text(0.26, 0.17, "家", fontsize=7.2, color=GRAY)
    ax.text(0.46, 0.36, "乡", fontsize=7.2, color=GRAY)
    ax.text(0.66, 0.56, "国", fontsize=7.2, color=GRAY)
    ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("差序：愈推愈远，愈推愈薄", fontsize=8.2, loc="left")
    ax = axes[1]
    n = 12; M = np.zeros((n, n))
    for i_ in range(n):
        for j_ in range(n):
            M[i_, j_] = np.exp(-abs(i_ - j_) / 2.2)
    im = ax.imshow(M, cmap="YlOrBr", vmin=0, vmax=1)
    ax.set_title("爱矩阵 ν_ij：稀疏、会衰减", fontsize=8.2, loc="left")
    ax.set_xlabel("j：被爱的人", fontsize=7.2); ax.set_ylabel("i：给的人", fontsize=7.2)
    ax.tick_params(labelsize=6.6)
    fig.colorbar(im, ax=ax, fraction=0.035, pad=0.015).ax.tick_params(labelsize=6.6)
    fig.subplots_adjust(left=0.06, right=0.95, top=0.84, bottom=0.20)
    save(fig, "v2_fig_nu")


# ---------------------------------------------------------------- 5. VOI
def fig_kappa():
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    p = np.linspace(0.01, 0.99, 400)
    def voi(p, Lfn, Lfp, q=0.7):
        C0 = np.minimum(p * Lfn, (1 - p) * Lfp)
        pe1 = q * p + (1 - q) * (1 - p); p1 = q * p / pe1
        pe0 = (1 - q) * p + q * (1 - p); p0 = (1 - q) * p / pe0
        C1 = pe1 * np.minimum(p1 * Lfn, (1 - p1) * Lfp) + pe0 * np.minimum(p0 * Lfn, (1 - p0) * Lfp)
        return C0 - C1
    for Lfn, Lfp, col, lab in [(1, 1, GRAY, "对称：峰 0.50"), (5, 1, RED, "怕漏：峰 0.17"), (1, 5, BLUE, "怕误：峰 0.83")]:
        y = voi(p, Lfn, Lfp)
        ax.plot(p, y, color=col, lw=1.8, label=lab)
        peak = p[np.argmax(y)]
        ax.axvline(peak, color=col, ls=":", lw=0.8)
    ax.set_xlabel("先验 p"); ax.set_ylabel("VOI")
    ax.set_title("好奇的峰位随决定阈值移动")
    ax.legend(frameon=False, fontsize=8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout()
    save(fig, "v2_fig_kappa")


# ---------------------------------------------------------------- 6. generation
def fig_generation():
    """生成便宜，保留贵。版心 6.4 in（排版轮重画：原 10.4 in）。"""
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.02, 0.955, "生成便宜，保留贵", fontsize=10.0, fontweight="bold")
    ax.text(0.02, 0.905, "五种算子把旧块拼成新码；一条选择链决定它能不能留下", fontsize=7.0, color=GRAY)
    ops = ["Rc 重组", "An 类比", "Mu 变异", "L 松弛", "Tr 翻译"]
    for i_, t_ in enumerate(ops):
        x = 0.02 + i_ * 0.195
        box(ax, x, 0.66, 0.175, 0.13, t_, fs=7.0, fc="#fdf6ec")
    box(ax, 0.30, 0.44, 0.40, 0.10, "提案：新码 q′", fs=7.6)
    chain = ["Cmp", "Coh", "W(Nov)", "A/γ", "ρ 核实", "保留"]
    for i_, t_ in enumerate(chain):
        x = 0.01 + i_ * 0.165
        box(ax, x, 0.18, 0.135, 0.11, t_, fs=6.9, fc="#eef4fb" if i_ < 5 else "#eaf5ee")
        if i_ < len(chain) - 1:
            arrow(ax, x + 0.135, 0.235, x + 0.163, 0.235, color=INK, lw=0.9)
    arrow(ax, 0.34, 0.435, 0.10, 0.30, color=INK, lw=0.9)
    ax.text(0.5, 0.07, "大多数新码死在压不紧、对不上、没人传、核不过；不是死在“不够新”。",
            ha="center", fontsize=7.0, color=GRAY)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    save(fig, "v2_fig_generation")


# ---------------------------------------------------------------- 6b. mu (V2 ch04)
def fig_mu():
    """\u03bc\uff1a\u4e2d\u5fc3\u4e0e\u5bbd\u5ea6\u3002\u5de6\uff1a\u793a\u610f\uff08\u79fb\u4e2d\u5fc3\u4e0d\u6539\u5bbd\u5ea6\uff09\uff1b\u53f3\uff1a133 \u4eba\u7684\u771f\u5b9e\u6563\u70b9\uff08\u5cf0\u4f4d \u00d7 \u5cf0\u5bbd\uff09\u3002"""
    import csv
    rows = list(csv.DictReader(open(ROOT / "data" / "derived" / "grad_2sxfp.csv", encoding="utf-8")))
    mu = np.array([float(r["mu"]) for r in rows])
    vv = np.array([float(r["v"]) for r in rows])
    r = np.corrcoef(mu, vv)[0, 1]

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.9), gridspec_kw={"width_ratios": [1, 1.08]})

    # left: centre moves, width does not
    ax = axes[0]
    x = np.linspace(0, 10, 400)
    g = lambda c, s: np.exp(-(x - c) ** 2 / (2 * s ** 2))
    ax.plot(x, g(3.0, 0.9), color=OCHRE, lw=1.8)
    ax.plot(x, g(6.2, 0.9), color=BLUE, lw=1.8)
    ax.plot(x, g(6.2, 2.2), color=GRAY, lw=1.4, ls="--")
    ax.annotate("", xy=(3.0, 1.12), xytext=(6.2, 1.12),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9))
    ax.text(4.6, 1.19, "\u4e2d\u5fc3\u79fb\u52a8 \u03bc\uff1a\u5bbd\u5ea6\u4e0d\u53d8", ha="center", fontsize=9.0)
    ax.text(2.95, 1.04, "\u4f4e \u03bc", ha="center", fontsize=9.0, color=OCHRE)
    ax.text(6.35, 1.04, "\u9ad8 \u03bc", ha="center", fontsize=9.0, color=BLUE)
    ax.text(6.3, 0.10, "\u865a\u7ebf\uff1a\u5bbd\u5ea6\u53d8\uff0c\u4e2d\u5fc3\u4e0d\u52a8", fontsize=8.4, color=GRAY)
    ax.set_xlim(0, 10); ax.set_ylim(0, 1.34)
    ax.set_yticks([]); ax.set_xticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_title("\u4e2d\u5fc3\u4e0e\u5bbd\u5ea6\u662f\u4e24\u53ea\u65cb\u94ae\uff08\u793a\u610f\uff09", fontsize=10.2, loc="left")

    # right: the 133 people
    ax = axes[1]
    ax.scatter(vv, mu, s=13, color=BLUE, alpha=0.65, edgecolor="none")
    ax.set_xscale("log")
    ax.set_xlabel("\u5cf0\u5bbd \u03bd\uff08\u5bf9\u6570\u8f74\uff09", fontsize=9.0)
    ax.set_ylabel("\u5cf0\u4f4d \u03bc", fontsize=9.0)
    ax.tick_params(labelsize=8.2)
    ax.set_title("133 \u4eba\uff1a\u5cf0\u5728\u54ea \u00d7 \u5cf0\u6709\u591a\u5bbd", fontsize=10.2, loc="left")
    ax.text(0.03, 0.06, f"r = {r:+.2f}\uff08\u91cd\u62bd\u6837 95%\uff1a\u22120.24 \u2014 +0.32\uff09",
            transform=ax.transAxes, fontsize=8.6, color=RED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_mu")
    print(f"   r(mu, log v) = {r:+.4f}, n = {len(mu)}")


# ---------------------------------------------------------------- 6c. seven moves (V2 ch05)
def fig_seven():
    """\u4e03\u4e2a\u52a8\u4f5c\u843d\u5728\u56db\u4e2a\u7b97\u5b50\u4e0a\u3002\u7248\u5fc3\u5bbd 6.4 in\u3002"""
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.0, 0.985, "\u4e03\u4e2a\u52a8\u4f5c\uff0c\u56db\u4e2a\u4f4d\u7f6e", fontsize=11, fontweight="bold", color=INK, va="top")
    ax.text(0.0, 0.905, "\u6bcf\u4eba\u53ea\u62e7\u4e00\u53ea\u65cb\u94ae\uff1b\u65b9\u6846\u91cc\u662f\u4ed6\u6539\u7684\u91cf\u4e0e\u4ee3\u4ef7", fontsize=8.4, color=GRAY, va="top")

    cols = [
        ("\u03bc / \u03a0\u3000\u770b\u54ea\u513f", OCHRE, [
            ("\u67cf\u62c9\u56fe", "\u628a\u4e2d\u5fc3\u62ac\u6210\u4e00\u6761\u8f74", "\u56de\u53bb\u7684\u4eba\u88ab\u7b11"),
            ("\u5eb7\u5fb7", "\u6838\u4e0d\u662f\u767d\u677f", "\u7269\u81ea\u4f53\u4e0d\u53ef\u77e5"),
        ]),
        ("q\u3000\u600e\u4e48\u5207", BLUE, [
            ("\u4e9a\u91cc\u58eb\u591a\u5fb7", "\u5c5e\u52a0\u79cd\u5dee", "\u5207\u7ec6\u8986\u76d6\u7a84"),
            ("\u83b1\u5e03\u5c3c\u5179", "\u4e00\u4e2a\u6838\u94fa\u6ee1", "\u5207\u70b9\u6210\u672c b>0"),
        ]),
        ("U\u3000\u4ec0\u4e48\u6b21\u5e8f", GREEN, [
            ("\u56fe\u7075", "\u64cd\u4f5c\u62c6\u6210\u6709\u9650\u6b65", "\u6162\uff0c\u4f46\u53ef\u91cd\u653e"),
        ]),
        ("I\u3000\u80fd\u63a8\u51fa\u4ec0\u4e48", RED, [
            ("\u5f17\u96f7\u683c", "\u540c\u4e00\u6307\u79f0\uff0c\u4e24\u79cd\u8d70\u6cd5", "\u4e24\u6761\u7ebf\u90fd\u8981\u8ffd"),
            ("\u7ef4\u7279\u6839\u65af\u5766", "\u8f74\u62c6\u56de\u5c40\u90e8", "\u6ca1\u6709\u5168\u5c40\u6392\u540d"),
        ]),
    ]
    xs = [0.008, 0.256, 0.504, 0.752]
    w = 0.240
    for (head, col, items), x in zip(cols, xs):
        ax.text(x + 0.006, 0.845, head, fontsize=9.2, fontweight="bold", color=col, va="top")
        y = 0.775
        for name, what, cost in items:
            box(ax, x, y - 0.205, w, 0.205, "", fc="white", ec=col, fs=7)
            ax.text(x + 0.012, y - 0.030, name, fontsize=8.6, fontweight="bold", color=INK, va="top")
            ax.text(x + 0.012, y - 0.080, what, fontsize=7.8, color="#3c3c3c", va="top")
            ax.text(x + 0.012, y - 0.135, "\u4ee3\u4ef7\uff1a" + cost, fontsize=7.4, color=GRAY, va="top")
            y -= 0.265
    # \u7b2c\u4e09\u5217\u7684\u7b2c\u4e8c\u683c\u7a7a\u7740\uff1a\u5199\u6e05\u695a\u4e3a\u4ec0\u4e48
    box(ax, xs[2], 0.510 - 0.205, w, 0.205, "", fc="white", ec="#c8c8c8", fs=7, dashed=True)
    ax.text(xs[2] + 0.012, 0.505 - 0.030, "\uff08\u6b64\u683c\u7a7a\u7740\uff09", fontsize=7.8, color=GRAY, va="top")
    ax.text(xs[2] + 0.012, 0.505 - 0.080, "\u6ca1\u6709\u4eba\u4e3a\u201c\u5236\u5ea6\u5c42\u7684\u6267\u884c\u201d", fontsize=6.9, color=GRAY, va="top")
    ax.text(xs[2] + 0.012, 0.505 - 0.125, "\u505a\u8fc7\u8fd9\u4e2a\u52a8\u4f5c", fontsize=6.9, color=GRAY, va="top")

    ax.text(0.0, 0.105, "\u516d\u4e2a\u52a8\u4f5c\u6539\u7684\u662f\u201c\u7801\u201d\uff0c\u53ea\u6709\u4e00\u4e2a\uff08\u56fe\u7075\uff09\u6539\u7684\u662f\u201c\u6267\u884c\u201d\u3002", fontsize=8.2, color=GRAY)
    ax.text(0.0, 0.045, "\u56db\u5c42\u91cc\u524d\u4e24\u5c42\u6709\u5b9a\u7406\u3001\u540e\u4e24\u5c42\u53ea\u6709\u5b50\u6a21\u578b\uff0c\u4e0e\u8fd9\u4ef6\u4e8b\u6709\u5173\u3002", fontsize=8.2, color=GRAY)
    save(fig, "v2_fig_seven")


# ---------------------------------------------------------------- 6d. knobs (V2 ch06)
def fig_knobs():
    """\u56db\u53ea\u65cb\u94ae\u91cc\u7684\u4e24\u53ea\uff1a\u4ef7\u683c\u5b9a\u7c97\u7ec6\uff1b\u6362\u7801\u5b9a\u5e26\u5bbd\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.6), gridspec_kw={"width_ratios": [1.12, 1]})

    ax = axes[0]
    x = np.linspace(0.25, 3.0, 200)          # w
    for T, col in [(0.4, GRAY), (1.0, BLUE), (2.2, RED)]:
        ax.plot(x, (T) / (2 * x), color=col, lw=1.8, label=f"T+\u03bb = {T}")
    ax.set_xlabel("\u8d4c\u6ce8 w\uff08\u9519\u4e86\u591a\u75bc\uff09", fontsize=8.4)
    ax.set_ylabel("\u5206\u591a\u7ec6 v*", fontsize=8.4)
    ax.set_title("\u8d4c\u6ce8\u8d8a\u5927\uff0c\u7801\u8d8a\u7ec6\uff1b\u5de5\u592b\u8d8a\u8d35\uff0c\u7801\u8d8a\u7c97", fontsize=9.4, loc="left")
    ax.legend(frameon=False, fontsize=7.6, title="\u5de5\u592b\u7684\u4ef7\u683c", title_fontsize=7.6)
    ax.tick_params(labelsize=7.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.text(0.03, 0.06, "v* = (T+\u03bb) / 2w", transform=ax.transAxes, fontsize=8.2, color=INK)

    ax = axes[1]
    y = np.linspace(-2.0, 2.0, 400)
    V = 0.25 * (y ** 2 - 1) ** 2
    ax.plot(y, V, color=INK, lw=1.8)
    ax.axhline(0.25, color=RED, ls="--", lw=1.0)
    ax.annotate("", xy=(-0.577, 0.25), xytext=(0.577, 0.25),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=1.1))
    ax.text(0.0, 0.29, "2C", ha="center", fontsize=8.6, color=RED)
    ax.text(0.0, 0.47, "\u53bb\u7a0b\u4ed8\u4e00\u6b21\uff0c\u56de\u7a0b\u518d\u4ed8\u4e00\u6b21", ha="center", fontsize=7.4, color=GRAY)
    ax.set_yticks([]); ax.set_xticks([])
    ax.set_title("\u6362\u7801\u4e00\u6b21\u4ed8\u4e00\u6b21\uff1a\u5bbd\u5ea6 2C", fontsize=9.4, loc="left")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_ylim(0, 0.72)
    fig.tight_layout()
    save(fig, "v2_fig_knobs")


# ---------------------------------------------------------------- 6e. gestalt (V2 ch06)
def fig_gestalt():
    """\u683c\u5f0f\u5854\uff1a\u9760\u8fd1\u4e0e\u76f8\u4f3c\uff0c\u4e24\u79cd\u201c\u514d\u8d39\u201d\u7684\u5207\u6cd5\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 1.9))
    rng = np.random.default_rng(7)

    # left: proximity — same spacing, two clusters appear
    ax = axes[0]
    xs = [0, 1, 2, 4.2, 5.2, 6.2]
    ys = [0.30] * 6
    ax.scatter(xs, ys, s=42, color=BLUE)
    ax.set_xlim(-0.8, 7.0); ax.set_ylim(0.0, 1.05); ax.axis("off")
    ax.set_title("\u9760\u8fd1\uff1a\u5206\u5f00\u7684\u8ddd\u79bb\u81ea\u5df1\u5207\u51fa\u4e24\u7ec4", fontsize=8.6, loc="left")
    ax.text(3.5, 0.72, "\u201c\u5b83\u4eec\u662f\u4e24\u5806\u201d\n\u4e0d\u7528\u6559", ha="center", fontsize=7.6, color=GRAY, linespacing=1.5)

    # right: similarity — same spacing, colour splits it
    ax = axes[1]
    xs = [0, 1, 2, 3, 4, 5]
    cols = [OCHRE, BLUE, OCHRE, BLUE, OCHRE, BLUE]
    ax.scatter(xs, [0.30] * 6, s=42, color=cols)
    ax.set_xlim(-0.8, 6.4); ax.set_ylim(0.0, 1.05); ax.axis("off")
    ax.set_title("\u76f8\u4f3c\uff1a\u540c\u6837\u7684\u8ddd\u79bb\uff0c\u989c\u8272\u53c8\u5207\u4e00\u6b21", fontsize=8.6, loc="left")
    ax.text(2.5, 0.72, "\u4e24\u5957\u5207\u6cd5\n\u53ef\u4ee5\u540c\u65f6\u6210\u7acb", ha="center", fontsize=7.6, color=GRAY, linespacing=1.5)

    fig.tight_layout()
    save(fig, "v2_fig_gestalt")


# ---------------------------------------------------------------- 6f. heterogeneity (V2 ch11)
def fig_hetero():
    """\u5f02\u8d28\u6027\u7684\u4e24\u5f20\u8138\uff1a\u4e2a\u4f53\u9636\u68af\u4e0e\u603b\u91cf\u659c\u5761\uff1b\u79bb\u6563\u5ea6 \u2192 \u591a\u79cd\u7801\u5e76\u5b58\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.2), gridspec_kw={"width_ratios": [1.25, 1]})

    ax = axes[0]
    x = np.linspace(-3, 3, 400)
    for s, col, lab in [(0.05, BLUE, "\u79bb\u6563\u5ea6 0.05\uff1a\u51e0\u4e4e\u4e00\u8d77\u8df3"),
                        (1.0, OCHRE, "\u79bb\u6563\u5ea6 1.0\uff1a\u62c9\u6210\u4e00\u6761\u659c\u5761")]:
        ax.plot(x, 1 / (1 + np.exp(-(x - 0.9) / max(s, 0.03))), color=col, lw=1.9, label=lab)
    ax.set_xlabel("\u540c\u4e00\u6761\u5916\u751f\u63a8\u529b", fontsize=8.0)
    ax.set_ylabel("\u201c\u5df2\u7ecf\u8de8\u8fc7\u53bb\u201d\u7684\u6bd4\u4f8b", fontsize=8.0)
    ax.set_title("\u4e2a\u4f53\u5230\u70b9\u5c31\u8df3\uff0c\u603b\u91cf\u5374\u662f\u5e73\u6ed1\u7684", fontsize=9.0, loc="left")
    ax.legend(frameon=False, fontsize=6.8, loc="upper left")
    ax.tick_params(labelsize=7.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    ax = axes[1]
    ds = ["0", "0.5", "1.0"]
    vals = [1.00, 0.54, 0.28]
    bars = ax.bar(ds, vals, color=[GRAY, OCHRE, BLUE], width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8.0)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel("\u4e2a\u4f53\u504f\u597d\u7684\u79bb\u6563\u5ea6", fontsize=8.0)
    ax.set_ylabel("\u6700\u5927\u4efd\u989d", fontsize=8.0)
    ax.set_title("\u79bb\u6563\u5ea6\u4e00\u9ad8\uff0c\u4e00\u79cd\u7801\u53d8\u6210\u591a\u79cd\u5e76\u5b58", fontsize=9.0, loc="left")
    ax.tick_params(labelsize=7.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_hetero")


# ---------------------------------------------------------------- 6g. rank & reflexivity (V2 ch12)
def fig_rank():
    """\u699c\u957f\u7b97\u672f\uff1b\u81ea\u6211\u5b9e\u73b0\u7684\u4e09\u4e2a\u65ad\u73af\u70b9\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.2), gridspec_kw={"width_ratios": [1.05, 1]})

    ax = axes[0]
    K = np.logspace(0.7, 3.3, 300)
    ax.plot(K, 100.0 / K, color=INK, lw=1.9)
    for kk in (10, 50, 1000):
        ax.plot([kk], [100.0 / kk], "o", color=RED, ms=4.5, zorder=3)
        ax.annotate(f"K={kk}\n{100.0/kk:g}%", (kk, 100.0 / kk), xytext=(6, 6),
                    textcoords="offset points", fontsize=6.8, color=RED)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("\u699c\u957f K", fontsize=7.8)
    ax.set_ylabel("\u699c\u5c3e \u00f7 \u699c\u9996\uff08%\uff09", fontsize=7.8)
    ax.set_title("\u4e00\u4e2a\u4f4d\u7f6e\u7684\u4ef7\u503c = 1/K", fontsize=9.0, loc="left")
    ax.tick_params(labelsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.text(0.03, 0.06, "\u699c\u957f 50 \u65f6\uff1a\u4efd\u989d 2% \u7684\u7c7b\u7ffb\u500d\u53ea\u591a\u5360 1 \u4e2a\u4f4d\uff0c\n\u4efd\u989d 20% \u7684\u7ffb\u500d\u8981\u591a\u5360 10 \u4e2a",
            transform=ax.transAxes, fontsize=6.4, color=GRAY, va="bottom")

    ax = axes[1]
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("\u81ea\u6211\u5b9e\u73b0\u7684\u73af\uff0c\u4e0e\u4e09\u4e2a\u65ad\u73af\u70b9", fontsize=9.0, loc="left")
    pts = {"q\uff08\u7801\uff09": (0.50, 0.86), "\u2113\uff08\u6807\u7b7e\uff09": (0.86, 0.62),
           "t\uff08\u5904\u7f6e\uff09": (0.86, 0.30), "a\uff08\u884c\u4e3a\uff09": (0.50, 0.10),
           "y\uff08\u4ea7\u51fa\uff09": (0.14, 0.30), "\u03bc\uff08\u5206\u5e03\uff09": (0.14, 0.62)}
    for lab, (x, y) in pts.items():
        box(ax, x - 0.11, y - 0.055, 0.22, 0.11, lab, fc="white", ec=INK, fs=7.4)
    order = ["q\uff08\u7801\uff09", "\u2113\uff08\u6807\u7b7e\uff09", "t\uff08\u5904\u7f6e\uff09", "a\uff08\u884c\u4e3a\uff09", "y\uff08\u4ea7\u51fa\uff09", "\u03bc\uff08\u5206\u5e03\uff09"]
    for a_, b_ in zip(order, order[1:] + order[:1]):
        (x1, y1), (x2, y2) = pts[a_], pts[b_]
        arrow(ax, x1, y1, x2, y2, color=GRAY, lw=1.0)
    for lab, xy, note in [("\u2460 \u76f8\u5173", (0.68, 0.76), "\u6807\u7b7e\u4e0e x \u65e0\u5173"),
                          ("\u2461 \u5206\u6863", (0.93, 0.46), "t \u65e0\u5dee"),
                          ("\u2462 \u5f39\u6027", (0.28, 0.13), "a \u4e0d\u53d8")]:
        ax.text(xy[0], xy[1], lab, fontsize=7.2, color=RED, ha="center")
        ax.text(xy[0], xy[1] - 0.075, note, fontsize=6.2, color=GRAY, ha="center")
    ax.text(0.5, 0.50, "\u65ad\u4efb\u4e00\u73af\uff0c\u9884\u8a00\u4e0d\u4f1a\u5b9e\u73b0", fontsize=7.2, color=INK, ha="center")

    fig.tight_layout()
    save(fig, "v2_fig_rank")


# ---------------------------------------------------------------- 6h. phi (V2 ch13)
def fig_phi():
    """\u547d\u540d\u3001\u89e3\u91ca\u3001\u6267\u884c\uff1a\u4e09\u79cd\u5f62\u6001\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 3, figsize=(6.4, 3.0))

    layouts = [
        ("\u4e09\u4ef6\u5408\u4e00\uff1a\u72ec\u65ad", RED,
         {"\u547d\u540d": (0.50, 0.62), "\u89e3\u91ca": (0.38, 0.46), "\u6267\u884c": (0.62, 0.46)},
         "H \u9ad8\uff0cC_\u03a6 \u4f4e\n\u4e00\u4e2a\u4eba\u5b9a\u3001\u89e3\u3001\u7f5a\n\u65e0\u4ece\u6bd4\u8f83"),
        ("\u4e09\u70b9\u5206\u5f00\uff1a\u5206\u5de5", BLUE,
         {"\u547d\u540d": (0.50, 0.88), "\u89e3\u91ca": (0.16, 0.18), "\u6267\u884c": (0.84, 0.18)},
         "H \u4f4e\uff0cC_\u03a6 \u9ad8\n\u8c01\u5b9a\u8c01\u89e3\u8c01\u7f5a\u4e0d\u540c\u4eba\n\u53ef\u4ee5\u4e92\u76f8\u53cd\u9a73"),
        ("\u4e24\u70b9\u5408\u5e76\uff1a\u5361\u7279\u5c14", OCHRE,
         {"\u547d\u540d": (0.42, 0.84), "\u89e3\u91ca": (0.58, 0.78), "\u6267\u884c": (0.50, 0.22)},
         "H \u4e2d\uff0cC_\u03a6 \u4e2d\n\u5b9a\u4e0e\u89e3\u540c\u4eba\uff0c\u7f5a\u5728\u5916\n\u7f5a\u8005\u4e0d\u77e5\u9053\u4e3a\u4f55\u7f5a"),
    ]
    for ax, (title, col, pts, note) in zip(axes, layouts):
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        ax.set_title(title, fontsize=8.6)
        for a_, b_ in [("\u547d\u540d", "\u89e3\u91ca"), ("\u89e3\u91ca", "\u6267\u884c"), ("\u6267\u884c", "\u547d\u540d")]:
            (x1, y1), (x2, y2) = pts[a_], pts[b_]
            ax.plot([x1, x2], [y1, y2], color="#d8d8d8", lw=1.0, ls=":")
        for lab, (x, y) in pts.items():
            ax.plot([x], [y], "o", color=col, ms=8)
            dy = 0.075 if y > 0.5 else -0.115
            ax.text(x, y + dy, lab, ha="center", fontsize=7.6)
        ny = 0.82 if title.startswith("\u4e09\u4ef6\u5408\u4e00") else 0.50
        ax.text(0.5, ny, note, ha="center", va="center", fontsize=6.4,
                color=GRAY, linespacing=1.5)

    fig.tight_layout()
    save(fig, "v2_fig_phi")


# ---------------------------------------------------------------- 6i. maintenance (V2 ch14)
def fig_maint():
    """\u5de1\u68c0\u95f4\u9694\u4e0e\u603b\u6210\u672c\uff1b\u7ef4\u62a4\u8d39\u7684\u4e09\u79cd\u644a\u6d3e\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1.05, 1]})

    ax = axes[0]
    d = np.linspace(0.30, 4.0, 400)
    insp = 2.0 / d                      # 巡检成本 ∝ 频次
    fail = 0.42 * d ** 1.7      # 失修成本随间隔指数上升
    ax.plot(d, insp, color=BLUE, lw=1.8, label="\u5de1\u68c0\u6210\u672c\uff08\u8d8a\u5bc6\u8d8a\u8d35\uff09")
    ax.plot(d, fail, color=RED, lw=1.8, label="\u5931\u4fee\u6210\u672c\uff08\u8d8a\u758f\u8d8a\u8d35\uff09")
    tot = insp + fail
    ax.plot(d, tot, color=INK, lw=2.0, label="\u603b\u8d26")
    k = float(d[np.argmin(tot)])
    ax.axvline(k, color=GRAY, ls=":", lw=0.9)
    ax.annotate(f"\u6700\u4f4e\u70b9 \u2248 {k:.1f}", (k, tot.min()), xytext=(24, 20),
                textcoords="offset points", fontsize=7.0, color=GRAY,
                arrowprops=dict(arrowstyle="->", color=GRAY, lw=0.8))
    ax.set_xlabel("\u5de1\u68c0\u95f4\u9694\uff08\u8d8a\u5927\u8d8a\u758f\uff09", fontsize=7.8)
    ax.set_ylabel("\u76f8\u5bf9\u6210\u672c", fontsize=7.8)
    ax.set_title("\u592a\u5bc6\u4e0e\u592a\u758f\u90fd\u8d35", fontsize=9.0, loc="left")
    ax.legend(frameon=False, fontsize=6.6, loc="upper center")
    ax.tick_params(labelsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_ylim(0, min(5.0, float(np.max(insp[:40]))))

    ax = axes[1]
    x = np.linspace(0, 1, 200)
    ax.plot(x, np.full_like(x, 0.45), color=GRAY, lw=1.8, label="\u6309\u4eba\u5934\uff1a\u5e73\u644a")
    ax.plot(x, 0.15 + 0.6 * x, color=BLUE, lw=1.8, label="\u6309\u53d7\u76ca\uff1a\u8d8a\u591a\u8d8a\u591a\u4ed8")
    ax.plot(x, np.where(x < 0.5, 0.12, 0.82), color=OCHRE, lw=1.8, label="\u6309\u6d41\u91cf\uff1a\u96c6\u4e2d\u5728\u4e0a\u6e38")
    ax.set_xlabel("\u7528\u6237\uff08\u6309\u4f7f\u7528\u91cf\u6392\u5e8f\uff09", fontsize=7.8)
    ax.set_ylabel("\u644a\u5230\u4ed6\u5934\u4e0a\u7684\u4efd\u989d", fontsize=7.8)
    ax.set_title("\u7ef4\u62a4\u8d39\u7684\u4e09\u79cd\u644a\u6d3e", fontsize=9.0, loc="left")
    ax.legend(frameon=False, fontsize=6.6, loc="lower right")
    ax.tick_params(labelsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_maint")


# ---------------------------------------------------------------- 6j. verification lag (V2 ch15)
def fig_tau():
    """核实时差：经验生存曲线＋七日指纹。

    2026-11-23 起委派给 `analysis/fig_tau_real.py`：左幅不再是对数正态示意，
    而是 21,063 条记录的经验生存函数（步进）；右幅四个比值同源重算。
    这样不论跑 build.sh 还是单跑本文件，出来的都是真实版。
    """
    import runpy
    runpy.run_path(str(Path(__file__).with_name("fig_tau_real.py")), run_name="__main__")


# ---------------------------------------------------------------- 6k. bills (V2 ch16)
def fig_bills():
    """\u4e09\u6761\u7ebf\uff08\u5404\u81ea\u91cf\u7eb2\uff09\uff1b\u516d\u5f20\u8d26\u5355\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig = plt.figure(figsize=(6.4, 3.4))
    gs = fig.add_gridspec(3, 2, width_ratios=[1.0, 1.05], hspace=0.15, wspace=0.30)

    rho = {2021: 1659, 2022: 934}
    p_ = {2021: 2.68, 2022: 2.51, 2023: 1.85, 2024: 1.73, 2025: 1.87, 2026: 2.68}
    kap = {2021: 0.6, 2022: 0.0, 2023: 6.0, 2024: 0.0, 2025: 18.8, 2026: 25.9}

    series = [
        (rho, BLUE, "\u4f9b\u7ed9 \u03c1\uff08\u6761\uff09", "o"),
        (p_, OCHRE, "\u53ef\u89c1\u5ea6 p\uff08%\uff09", "s"),
        (kap, RED, "\u6280\u672f \u03ba\uff08%\uff09", "^"),
    ]
    for i, (d, col, lab, mk) in enumerate(series):
        ax = fig.add_subplot(gs[i, 0])
        xs = np.array(sorted(d)); ys = np.array([d[x] for x in xs])
        ax.plot(xs, ys, mk + "-", color=col, lw=1.7, ms=4)
        ax.set_xlim(2020.6, 2026.4)
        ax.set_ylabel(lab, fontsize=6.6)
        ax.tick_params(labelsize=6.2)
        if i < 2:
            ax.set_xticklabels([])
        else:
            ax.set_xticks([2021, 2022, 2023, 2024, 2025, 2026])
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        if i == 0:
            ax.set_title("\u4e09\u6761\u7ebf\uff0c\u5404\u81ea\u7684\u91cf\u7eb2", fontsize=9.0, loc="left")
            ax.text(2022.2, 1500, "\u540e\u56db\u5e74\u7f3a\u6570", fontsize=6.2, color=GRAY)

    ax = fig.add_subplot(gs[:, 1])
    bills = ["\u516c\u5171\u8d22\u653f", "\u5e73\u53f0", "\u5a92\u4f53\u81ea\u5df1", "\u88ab\u6838\u5b9e\u8005", "\u8bfb\u8005", "\u5fd7\u613f\u8005"]
    share = [0.28, 0.24, 0.16, 0.14, 0.11, 0.07]
    ax.barh(range(6), share, color=[GRAY, BLUE, OCHRE, RED, "#8a8a8a", GREEN], height=0.58)
    ax.set_yticks(range(6)); ax.set_yticklabels(bills, fontsize=7.0)
    ax.invert_yaxis()
    ax.set_xlabel("\u4e00\u4efd\u6838\u5b9e\u4ea7\u51fa\u7684\u6210\u672c\u5206\u62c5\uff08\u793a\u610f\uff09", fontsize=7.4)
    ax.set_title("\u516d\u5f20\u8d26\u5355", fontsize=9.0, loc="left")
    ax.tick_params(labelsize=6.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.text(0.98, 0.04, "\u5206\u62c5\u4e3a\u793a\u610f\uff0c\u975e\u6d4b\u91cf", transform=ax.transAxes,
            ha="right", fontsize=6.2, color=GRAY)

    save(fig, "v2_fig_bills")


# ---------------------------------------------------------------- 6l. involution (V2 ch17)
def fig_involution():
    """\u4f4d\u7f6e\u7ade\u4e89\uff1a\u79c1\u4eba\u6700\u4f18\u4e0e\u793e\u4f1a\u6700\u4f18\u5206\u5c94\uff1b\u96f6\u548c\u4e0e\u8d1f\u548c\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1.05, 1]})

    # left: private vs social net benefit under a fixed number of positions
    ax = axes[0]
    a = np.linspace(0, 3.0, 300)
    V, c = 1.0, 0.55
    priv = V * a / (a + 1.0) - c * a          # \u79c1\u4eba\u51c0\u6536\u76ca\uff08\u76f8\u5bf9\u540d\u6b21\uff09
    soc = -c * a                               # \u793e\u4f1a\u51c0\u6536\u76ca\uff08\u603b\u4ea7\u51fa\u56fa\u5b9a\uff09
    ax.plot(a, priv, color=BLUE, lw=1.9, label="\u79c1\u4eba\u51c0\u6536\u76ca")
    ax.plot(a, soc, color=RED, lw=1.9, label="\u793e\u4f1a\u51c0\u6536\u76ca")
    k = float(a[np.argmax(priv)])
    ax.axvline(k, color=GRAY, ls=":", lw=0.9)
    ax.plot([k], [priv.max()], "o", color=BLUE, ms=4.5)
    ax.plot([0], [0], "o", color=RED, ms=4.5)
    ax.annotate(f"\u79c1\u4eba\u6700\u4f18 a* \u2248 {k:.1f}", (k, priv.max()), xytext=(14, 6),
                textcoords="offset points", fontsize=6.8, color=BLUE,
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.8))
    ax.annotate("\u793e\u4f1a\u6700\u4f18 = 0", (0, 0), xytext=(18, -22),
                textcoords="offset points", fontsize=6.8, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))
    ax.fill_between(a, priv, soc, where=(a <= k), color=BLUE, alpha=0.10)
    ax.axhline(0, color="#d0d0d0", lw=0.8)
    ax.set_xlabel("\u6295\u5165 a\uff08\u65f6\u95f4\u3001\u94b1\u3001\u8d44\u8d28\uff09", fontsize=7.6)
    ax.set_ylabel("\u51c0\u6536\u76ca\uff08\u76f8\u5bf9\u5355\u4f4d\uff09", fontsize=7.6)
    ax.set_title("\u4f4d\u56fa\u5b9a\uff1a\u79c1\u4eba\u6700\u4f18\u5728 a*>0\uff0c\u793e\u4f1a\u6700\u4f18\u5728 0", fontsize=8.6, loc="left")
    ax.legend(frameon=False, fontsize=6.4, loc="lower left")
    ax.tick_params(labelsize=6.8)
    ax.set_ylim(-0.55, 0.32)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # right: zero-sum vs negative-sum total output
    ax = axes[1]
    x = np.linspace(0, 1, 200)
    ax.plot(x, np.full_like(x, 1.0), color=GRAY, lw=1.8, ls="--", label="\u96f6\u548c\uff1a\u603b\u4ea7\u51fa\u4e0d\u53d8")
    ax.plot(x, 1.0 - 0.45 * x ** 1.4, color=RED, lw=1.8, label="\u8d1f\u548c\uff1a\u603b\u4ea7\u51fa\u4e0b\u964d")
    ax.plot(x, 1.0 + 0.10 * x, color=GREEN, lw=1.6, ls=":", label="\u6b63\u548c\uff1a\u6548\u7387\u4e0a\u5347")
    ax.set_xlabel("\u7ade\u4e89\u5f3a\u5ea6\uff08\u6295\u5165\u603b\u91cf\uff09", fontsize=7.6)
    ax.set_ylabel("\u603b\u4ea7\u51fa", fontsize=7.6)
    ax.set_title("\u4e09\u79cd\u7ade\u4e89\uff0c\u4e09\u4e2a\u7b26\u53f7", fontsize=8.8, loc="left")
    ax.legend(frameon=False, fontsize=6.4, loc="lower left")
    ax.tick_params(labelsize=6.8)
    ax.set_ylim(0.4, 1.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_involution")


# ---------------------------------------------------------------- 6m. drift (V2 ch18)
def fig_drift():
    """\u6f02\u79fb\u65b9\u7a0b\uff1a\u7a33\u6001\u51c6\u786e\u7387\u968f\u6295\u5165\u4e0e\u535a\u5f08\uff1b\u6807\u7b7e\u7684\u751f\u547d\u5468\u671f\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1.05, 1]})

    ax = axes[0]
    e = np.linspace(0.05, 3.0, 300)
    for gc, col in [(0.3, GREEN), (1.0, OCHRE), (2.5, RED)]:
        ax.plot(e, e / (e + gc), color=col, lw=1.8, label=f"g + c = {gc}")
    ax.set_xlabel("\u6838\u67e5\u6295\u5165 e", fontsize=7.8)
    ax.set_ylabel("\u7a33\u6001\u51c6\u786e\u7387 a*", fontsize=7.8)
    ax.set_title("a* = \u03b7e / (\u03b7e + g + c)", fontsize=9.0, loc="left")
    ax.legend(frameon=False, fontsize=6.6, loc="lower right")
    ax.tick_params(labelsize=6.8)
    ax.set_ylim(0, 1.02)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.text(0.03, 0.06, "\u6295\u5165\u62c9\u4e0d\u5230\u6ee1\u5206\uff1a\u535a\u5f08\u4e0e\u4fd8\u83b7\u662f\u5206\u6bcd",
            transform=ax.transAxes, fontsize=6.2, color=GRAY)

    ax = axes[1]
    x = np.linspace(0, 1, 300)
    born = 1 - np.exp(-x / 0.18)
    decay = 1 - 0.55 * np.clip((x - 0.45) / 0.55, 0, 1) ** 1.6
    ax.plot(x, born, color=BLUE, lw=1.8, label="\u521a\u51fa\u73b0\uff1a\u8d8a\u7528\u8d8a\u51c6")
    ax.plot(x, born * decay, color=RED, lw=2.0, label="\u88ab\u535a\u5f08\u4e4b\u540e\uff1a\u8d8a\u7528\u8d8a\u504f")
    ax.axvline(0.45, color=GRAY, ls=":", lw=0.9)
    ax.text(0.47, 0.16, "\u6807\u7b7e\u53d8\u5f97\u503c\u94b1", fontsize=6.6, color=GRAY)
    ax.set_xlabel("\u6807\u7b7e\u5df2\u4f7f\u7528\u7684\u65f6\u95f4", fontsize=7.8)
    ax.set_ylabel("\u51c6\u786e\u7387", fontsize=7.8)
    ax.set_title("\u4e00\u4e2a\u6807\u7b7e\u7684\u4e00\u751f", fontsize=9.0, loc="left")
    ax.legend(frameon=False, fontsize=6.4, loc="lower left")
    ax.tick_params(labelsize=6.8)
    ax.set_ylim(0, 1.05)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_drift")


# ---------------------------------------------------------------- 6n. recoding (V2 ch19)
def fig_recoding():
    """\u6539\u7801\uff1a\u8fdf\u6ede\u73af\uff1bC \u7684\u56db\u4e2a\u6210\u5206\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1.15, 1]})

    # left: hysteresis loop in (time, Delta D) space
    ax = axes[0]
    t1 = np.linspace(0, 6, 200)
    dd = 0.5 + 0.42 * t1                      # \u65e7\u7801\u7684\u574f\u5904\u9010\u6e10\u4e0a\u5347
    ax.plot(t1, dd, color=INK, lw=1.9, label="\u65e7\u7801\u7684\u574f\u5904 \u0394D")
    ax.axhline(1.0, color=RED, ls="--", lw=1.0)
    ax.axhline(0.4, color=BLUE, ls="--", lw=1.0)
    ax.text(4.15, 1.05, "\u53bb\u7a0b\u9608\u503c +C", fontsize=6.6, color=RED)
    ax.text(4.15, 0.30, "\u56de\u7a0b\u9608\u503c \u2212C", fontsize=6.6, color=BLUE)
    ax.annotate("", xy=(3.2, 0.4), xytext=(3.2, 1.0),
                arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1.0))
    ax.text(3.3, 0.70, "2C", fontsize=8.0, color=GRAY)
    # switch point
    ax.plot([3.2], [1.0], "o", color=RED, ms=5)
    ax.plot([3.2], [0.4], "o", color=BLUE, ms=5)
    t2 = np.linspace(3.2, 6, 100)
    ax.plot(t2, 1.0 - 0.62 * (t2 - 3.2) / 2.8, color=GREEN, lw=1.9, label="\u65b0\u7801\u7684\u574f\u5904")
    ax.set_xlabel("\u65f6\u95f4", fontsize=7.8)
    ax.set_ylabel("\u636e\u65e7\u7801\u7684\u635f\u5931\u76f8\u5bf9\u503c", fontsize=7.8)
    ax.set_title("\u6362\u4e00\u6b21\u4ed8\u4e00\u6b21\uff1a\u4e2d\u95f4\u662f\u4e0d\u52a8\u533a", fontsize=8.8, loc="left")
    ax.legend(frameon=False, fontsize=6.2, loc="lower right")
    ax.tick_params(labelsize=6.8)
    ax.set_ylim(0, 1.30)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # right: four components of C
    ax = axes[1]
    comp = ["\u91cd\u5efa\u8868\uff08\u91cd\u5199\u3001\u91cd\u8bad\uff09", "\u8bbe\u5907\u4e0e\u7269\u7406\u6539\u9020", "\u505c\u8fd0\u4e0e\u8fc1\u79fb", "\u65e7\u7801\u65e2\u5f97\u8005\u7684\u62b5\u5236"]
    share = [0.30, 0.26, 0.18, 0.26]
    ax.barh(range(4), share, color=[BLUE, OCHRE, GRAY, RED], height=0.55)
    ax.set_yticks(range(4)); ax.set_yticklabels(comp, fontsize=6.6)
    ax.invert_yaxis()
    ax.set_xlabel("C \u7684\u6784\u6210\uff08\u793a\u610f\uff09", fontsize=7.4)
    ax.set_title("C \u4e0d\u53ea\u662f\u94b1", fontsize=8.8, loc="left")
    ax.tick_params(labelsize=6.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.text(0.98, 0.04, "\u6784\u6210\u6bd4\u4f8b\u4e3a\u793a\u610f\uff0c\u975e\u6d4b\u91cf", transform=ax.transAxes,
            ha="right", fontsize=6.0, color=GRAY)

    fig.tight_layout()
    save(fig, "v2_fig_recoding")


# ---------------------------------------------------------------- 6o. tipping (V2 ch20)
def fig_tipping():
    """\u4e34\u754c\uff1a\u53cc\u7a33\u5e26\u4e0e\u4e09\u4e2a\u65e9\u671f\u6807\u8bb0\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    m = np.linspace(-1.6, 2.4, 400)
    for h, col, lab in [(0.0, BLUE, "h = 0\uff08\u53cc\u7a33\uff09"), (0.55, OCHRE, "h = 0.55\uff08\u4e00\u8fb9\u53d8\u6d45\uff09"), (1.0, RED, "h = 1.0\uff08\u53ea\u5269\u4e00\u4e2a\u5e95\uff09")]:
        V = 0.25 * (m ** 2 - 1) ** 2 - h * m
        ax.plot(m, V, color=col, lw=1.8, label=lab)
    ax.set_xlabel("\u72b6\u6001", fontsize=7.6)
    ax.set_ylabel("\u52bf\u80fd", fontsize=7.6)
    ax.set_title("\u4e34\u754c\u4e0d\u662f\u4e00\u6761\u7ebf\uff0c\u662f\u4e00\u6761\u5e26", fontsize=8.8, loc="left", pad=16)
    ax.legend(frameon=False, fontsize=6.2, loc="upper center")
    ax.tick_params(labelsize=6.6)
    ax.set_yticks([])
    ax.set_ylim(-0.35, 1.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    ax = axes[1]
    t_ = np.linspace(0, 1, 300)
    var = 0.25 + 0.6 / (1.02 - t_) ** 0.5 * 0.12
    a1 = 0.15 + 0.35 / (1.02 - t_) ** 0.4 * 0.3
    ax.plot(t_, var / var[0], color=RED, lw=1.9, label="\u65b9\u5dee\uff08\u76f8\u5bf9\u521d\u503c\uff09")
    ax.plot(t_, a1 / a1[0], color=BLUE, lw=1.9, label="AR(1)\uff08\u76f8\u5bf9\u521d\u503c\uff09")
    ax.axvline(1.0, color=GRAY, ls=":", lw=0.9)
    ax.text(0.93, 0.92, "\u8de8\u8fc7", fontsize=6.6, color=GRAY, transform=ax.transAxes)
    ax.set_xlabel("\u9760\u8fd1\u4e34\u754c\u7684\u65f6\u95f4", fontsize=7.6)
    ax.set_ylabel("\u76f8\u5bf9\u521d\u503c", fontsize=7.6)
    ax.set_title("\u4e24\u4e2a\u6807\u8bb0\u540c\u6b65\u4e0a\u5347", fontsize=8.8, loc="left")
    ax.legend(frameon=False, fontsize=6.4, loc="upper left")
    ax.tick_params(labelsize=6.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_tipping")


# ---------------------------------------------------------------- 7. stage (V2 Part I, ch01)
def fig_stage():
    """两行：上＝一件事五本账（五个人）；下左＝台阶 vs 衰减；下右＝账积到忍受线。
    版心按 6.4in 设计，印刷时不缩字。"""
    fig = plt.figure(figsize=(6.4, 7.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.55, 1.0], hspace=0.46, wspace=0.26)

    # ---- top: five accounts pointing at one event
    ax = fig.add_subplot(gs[0, :])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.0, 0.995, "一件事，五本账", fontsize=11.5, fontweight="bold", color=INK, va="top")
    ax.text(0.0, 0.915, "同一台机器被删，五个人各按自己紧的那一项记它的错；中间那一格是空的",
            fontsize=7.5, color=GRAY, va="top")

    box(ax, 0.355, 0.395, 0.29, 0.190, "旧手机里的 ELIZA\n第七天被删",
        fc="#fdf6ec", ec=RED, fs=8.4, lw=1.4)

    items = [
        (0.015, 0.700, "弗朗提努斯｜w", "它不赔钱", OCHRE, 0.155, 0.700, 0.378, 0.585),
        (0.695, 0.700, "默里｜T 与引文", "它没有出处", BLUE, 0.845, 0.700, 0.622, 0.585),
        (0.015, 0.400, "巴纳姆｜R 与 D", "它不够讨喜", GRAY, 0.305, 0.478, 0.357, 0.486),
        (0.695, 0.400, "塞麦尔维斯｜分母", "像真的 ≠ 能信的", GREEN, 0.695, 0.478, 0.643, 0.486),
        (0.335, 0.075, "柴门霍夫｜中心", "没人替它挨骂", "#6b46c1", 0.500, 0.225, 0.500, 0.395),
    ]
    for x, y, head, body, col, x1, y1, x2, y2 in items:
        box(ax, x, y, 0.29, 0.155, f"{head}\n{body}", fc="white", ec=col, fs=7.0)
        arrow(ax, x1, y1, x2, y2, color=col, lw=1.0)
    ax.text(0.500, 0.012, "五个人说的都不是它，是自己的账", ha="center", fontsize=7.6, color=GRAY)

    # ---- bottom-left: usage shape, step vs decay
    ax = fig.add_subplot(gs[1, 0])
    d = np.linspace(0, 10, 500)
    step = 1 / (1 + np.exp((d - 6.2) * 3.0))
    decay = np.exp(-d / 4.0)
    ax.plot(d, step, color=RED, lw=1.9, label="台阶：一次按灭")
    ax.plot(d, decay, color=GRAY, lw=1.5, ls="--", label="平滑衰减：每天少用一点")
    ax.axvline(6.2, color=RED, ls=":", lw=0.9)
    ax.annotate("按开关的那一天", (6.2, 0.50), xytext=(0.7, 0.28), fontsize=7.0, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))
    ax.set_xlabel("天数", fontsize=7.6)
    ax.set_ylabel("它还在多大程度上被使用", fontsize=7.4)
    ax.set_title("两种形状，可查的东西不同", fontsize=9.0, loc="left")
    ax.legend(frameon=False, fontsize=6.4, loc="upper right")
    ax.tick_params(labelsize=6.8)
    ax.set_ylim(-0.04, 1.32)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    # ---- bottom-right: the bill accumulates until it crosses one person's line
    ax = fig.add_subplot(gs[1, 1])
    bill = 2.2 * (d / 6.2) ** 2.2
    ax.plot(d, bill, color=OCHRE, lw=1.9, label="账（谁付得最多）")
    ax.axhline(2.2, color=RED, ls="--", lw=1.1, label="那个人的忍受线")
    ax.axvline(6.2, color=RED, ls=":", lw=0.9)
    ax.fill_between(d, bill, 2.2, where=bill >= 2.2, color=RED, alpha=0.10)
    ax.annotate("账合上", (6.2, 2.2), xytext=(7.1, 3.4), fontsize=7.0, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))
    ax.set_xlabel("天数", fontsize=7.6)
    ax.set_ylabel("账积了多少（示意单位）", fontsize=7.4)
    ax.set_title("台阶从哪来：账碰到忍受线", fontsize=9.0, loc="left")
    ax.legend(frameon=False, fontsize=6.4, loc="upper left")
    ax.tick_params(labelsize=6.8)
    ax.set_ylim(0, 7.4)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    fig.text(0.01, 0.005, "示意图，不是数据：两幅曲线只用来把“台阶”与“衰减”、"
             "以及“账积到忍受线”摆在一起。", fontsize=6.5, color=GRAY)
    save(fig, "v2_fig_stage")


if __name__ == "__main__":
    fig_principle()
    fig_parameters()
    fig_aesthetic()
    fig_nu()
    fig_kappa()
    fig_generation()
    fig_stage()
    fig_mu()
    fig_seven()
    fig_knobs()
    fig_gestalt()
    fig_hetero()
    fig_rank()
    fig_phi()
    fig_maint()
    fig_tau()
    fig_bills()
    fig_involution()
    fig_drift()
    fig_recoding()
    fig_tipping()


# ---------------------------------------------------------------- 6p. transform (V2 ch21)
def fig_transform():
    """转型：换码次数的阶梯 + 2x2（三格有样本，一格空着，唐宋是一条轨迹）。版心 6.4 in。"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.2), gridspec_kw={"width_ratios": [1.18, 1]})

    # left: cumulative次数
    ax = axes[0]
    fr = [1791, 1792, 1804, 1814, 1830, 1848, 1852, 1870, 1940, 1946, 1958]
    jp = [1868, 1947]
    xs = np.arange(1780, 1965)
    yf = np.array([sum(1 for y in fr if y <= x) for x in xs])
    yj = np.array([sum(1 for y in jp if y <= x) for x in xs])
    ax.step(xs, yf, where="post", color=RED, lw=1.9, label="法国（1789 起）")
    ax.step(xs, yj, where="post", color=BLUE, lw=1.9, label="日本（1868 起）")
    ax.axvspan(1848, 1875, color=LIGHT, alpha=0.65, lw=0)
    ax.text(1861.5, 9.6, "1848—1875", fontsize=6.4, color=GRAY, ha="center")
    ax.axvspan(1868, 1889, color=CREAM, alpha=0.9, lw=0)
    ax.annotate("明治：二十一年，一次", (1889, 1.0), xytext=(1893, 4.4), fontsize=6.8, color=BLUE,
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.8))
    ax.set_xlabel("年", fontsize=7.6)
    ax.set_ylabel("累计更换次数（口径见注）", fontsize=7.6)
    ax.set_title("同一个世纪，两种阶梯", fontsize=8.8, loc="left")
    ax.legend(frameon=False, fontsize=6.4, loc="upper left")
    ax.tick_params(labelsize=6.6)
    ax.set_ylim(-0.4, 11.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # right: 2x2
    ax = axes[1]
    ax.set_xlim(0, 2); ax.set_ylim(0, 2)
    ax.set_xticks([]); ax.set_yticks([])
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.set_xlabel("换码成本 C：低 \u2190 \u2192 高", fontsize=7.4)
    ax.set_ylabel("换不换码", fontsize=7.4)
    # 分隔线在箭头处留缺口
    ax.plot([1, 1], [1.36, 2.0], color=INK, lw=1.0)
    ax.plot([1, 1], [0, 0.92], color=INK, lw=1.0)
    ax.plot([0, 2], [1, 1], color=INK, lw=1.0)
    ax.text(0.5, 1.90, "换了码 \u00b7 C 低", fontsize=7.0, ha="center", color=GRAY)
    ax.text(1.5, 1.90, "换了码 \u00b7 C 高", fontsize=7.0, ha="center", color=GRAY)
    ax.text(0.5, 1.62, "法国 1789\u20141875\n八次，都没抬 C", fontsize=6.5, ha="center", color=RED)
    ax.text(1.5, 1.62, "明治 1868\u20141889\n一次，抬了 C", fontsize=6.5, ha="center", color=BLUE)
    ax.annotate("", xy=(1.22, 1.20), xytext=(0.78, 1.20),
                arrowprops=dict(arrowstyle="-|>", color=OCHRE, lw=1.6))
    ax.text(1.0, 1.29, "唐宋：C 在走", fontsize=6.4, ha="center", color=OCHRE)
    ax.add_patch(Rectangle((0.05, 0.14), 0.90, 0.68, facecolor="#f0e6d2",
                           edgecolor=GRAY, hatch="///", lw=0.0, alpha=0.5))
    ax.text(0.5, 0.88, "没换 \u00b7 C 低", fontsize=7.0, ha="center", color=GRAY)
    ax.text(0.5, 0.48, "空格：\n换得起，没人换", fontsize=6.5, ha="center", color=GRAY)
    ax.text(1.5, 0.88, "没换 \u00b7 C 高", fontsize=7.0, ha="center", color=GRAY)
    ax.text(1.5, 0.48, "苏联 1960s\u20141991\n一次位移", fontsize=6.5, ha="center")

    fig.tight_layout()
    save(fig, "v2_fig_transform")


# ---------------------------------------------------------------- 6q. longue duree (V2 ch22)
def fig_longe_duree():
    """\u957f\u65f6\u6bb5\uff1a\u5c42\u6570\u8ddf\u4eba\u53e3\u8d70\uff1b\u300c\u63a8\u65ad\u5360\u6bd4\u300d\u7684\u8c31\u3002\u7248\u5fc3 6.4 in\u3002"""
    import pandas as pd

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.1), gridspec_kw={"width_ratios": [1.05, 1]})

    panel = pd.read_csv(ROOT / "data" / "derived" / "writing_grain_panel.csv")
    d = panel[["lpop", "levels", "writing"]].dropna()
    ax = axes[0]
    for w, col, lab in [(0.0, GRAY, "\u65e0\u6587\u5b57"), (1.0, BLUE, "\u6709\u6587\u5b57")]:
        s = d[d["writing"] == w]
        ax.scatter(s["lpop"], s["levels"], s=7, color=col, alpha=0.55, lw=0, label=lab)
    b, a = np.polyfit(d["lpop"], d["levels"], 1)
    xs = np.linspace(d["lpop"].min(), d["lpop"].max(), 50)
    ax.plot(xs, a + b * xs, color=RED, lw=1.6,
            label=f"\u62df\u5408\uff1a\u6bcf\u5341\u500d\u4eba\u53e3 {b:+.1f} \u5c42")
    ax.set_xlabel("\u4eba\u53e3\uff08\u5bf9\u6570\uff0c\u6bcf\u683c\u5341\u500d\uff09", fontsize=7.6)
    ax.set_ylabel("\u56db\u7c7b\u5c42\u7ea7\u4e4b\u548c\uff08\u5c42\uff09", fontsize=7.6)
    ax.set_title("\u5c42\u6570\u8ddf\u4eba\u53e3\u8d70\uff0c\u4e0d\u8ddf\u6587\u5b57\u8d70", fontsize=8.8, loc="left")
    ax.legend(frameon=False, fontsize=6.2, loc="upper left")
    ax.tick_params(labelsize=6.6)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    ax = axes[1]
    sp = pd.read_csv(ROOT / "data" / "derived" / "inferred_spectrum.csv").sort_values("inferred_share")
    y = np.arange(len(sp))
    ax.barh(y, sp["inferred_share"] * 100, height=0.75,
            color=[OCHRE if v > 0.31 else BLUE for v in sp["inferred_share"]])
    ax.set_yticks([])
    ax.set_ylim(-1, len(sp))
    ax.axvline(31.2, color=RED, ls="--", lw=0.9)
    ax.text(32.0, len(sp) - 1.5, "\u4e2d\u4f4d 31.2%", fontsize=6.2, color=RED)
    ax.set_xlabel("\u300c\u63a8\u65ad\u4e3a\u6709\u300d\u5360\u5168\u90e8\u300c\u6709\u300d\u7684\u6bd4\u4f8b\uff08%\uff09", fontsize=7.4)
    ax.set_title("\u4e00\u6761\u6cbf\u300c\u80fd\u4e0d\u80fd\u6307\u7ed9\u4eba\u770b\u300d\u6392\u7684\u5e8f", fontsize=8.8, loc="left")
    ax.tick_params(labelsize=6.6)
    notes = [("Symbolic building", "\u7b26\u53f7\u5efa\u7b51", 3.8, 2),
             ("Written records", "\u6587\u5b57\u8bb0\u5f55", 7.8, 6),
             ("Indigenous coins", "\u672c\u5730\u94f8\u5e01", 13.1, 9),
             ("Philosophy", "\u54f2\u5b66", 42.2, 57),
             ("Store of wealth", "\u8d22\u5bcc\u50a8\u85cf", 54.2, 65)]
    for var, cn, pct, idx in notes:
        i = int(np.where(sp["var"].values == var)[0][0])
        ax.plot([sp["inferred_share"].iloc[i] * 100], [i], "o", color=INK, ms=2.6)
        ax.text(sp["inferred_share"].iloc[i] * 100 + 1.4, i, f"{cn} {pct:.0f}%",
                fontsize=6.0, va="center", color=INK)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_longeduree")


# ---------------------------------------------------------------- 6r. periodization (V2 ch23)
def fig_periodization():
    """\u5206\u671f\uff1a\u8df3\u5ea6\u4e0e\u6bb5\u957f\uff1b\u4e24\u4e2a\u53e3\u5f84\u7684\u4e66\u5305. \u7248\u5fc3 6.4 in\u3002"""
    import pandas as pd

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.1), gridspec_kw={"width_ratios": [1.0, 1.08]})

    p = pd.read_csv(ROOT / "data" / "derived" / "periodization_test.csv").dropna()
    ax = axes[0]
    ax.scatter(p["span_years"], p["seg_years"], s=13, color=BLUE, alpha=0.7, lw=0)
    ls = np.log10(p["span_years"]); ly = np.log10(p["seg_years"])
    b, a = np.polyfit(ls, ly, 1)
    xs = np.linspace(ls.min(), ls.max(), 40)
    ax.plot(10 ** xs, 10 ** (a + b * xs), color=RED, lw=1.8, label=f"\u62df\u5408\uff1a\u659c\u7387 {b:.2f}（r=+0.88）")
    ax.plot(10 ** xs, 10 ** (a + xs), color=GRAY, lw=1.2, ls="--", label="\u4e25\u683c\u6210\u6bd4\u4f8b\uff08\u659c\u7387 1\uff09")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("\u4e00\u90e8\u4e66\u56de\u671b\u7684\u8df3\u5ea6\uff08\u5e74\uff09", fontsize=7.4)
    ax.set_ylabel("\u6bcf\u6bb5\u957f\u5ea6\uff08\u5e74\uff09", fontsize=7.4)
    ax.set_title("\u8df3\u5ea6\u8d8a\u5927\uff0c\u6bb5\u8d8a\u957f\uff08n=45\uff09", fontsize=8.8, loc="left")
    ax.legend(frameon=False, fontsize=6.0, loc="upper left")
    ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    ax = axes[1]
    w = pd.read_csv(ROOT / "data" / "derived" / "wid_wealth_share.csv")
    cn = w[w.code == "CN"].sort_values("year")
    wo = w[w.code == "WO"].sort_values("year")
    ax.plot(cn.year, cn.top1 * 100, color=RED, lw=1.7, label="\u4e2d\u56fd \u524d 1%")
    ax.plot(cn.year, cn.bottom50 * 100, color=RED, lw=1.4, ls="--", label="\u4e2d\u56fd \u540e 50%")
    ax.plot(wo.year, wo.top1 * 100, color=GRAY, lw=1.7, label="\u4e16\u754c \u524d 1%")
    ax.plot(wo.year, wo.bottom50 * 100, color=GRAY, lw=1.4, ls="--", label="\u4e16\u754c \u540e 50%")
    ax.set_xlim(1970, 2030)
    ax.set_ylim(-2, 46)
    ax.annotate("30.4%", (2024, 30.4), xytext=(2018.0, 33.0), fontsize=6.2, color=RED)
    ax.annotate("6.3%", (2024, 6.3), xytext=(2018.0, 2.0), fontsize=6.2, color=RED)
    ax.annotate("\u4e16\u754c\uff1a\u4e24\u6761\u90fd\u5e73", (1996, 39.5), fontsize=6.2, color=GRAY)
    ax.set_xlabel("\u5e74", fontsize=7.4)
    ax.set_ylabel("\u8d22\u5bcc\u4efd\u989d\uff08%\uff09", fontsize=7.4)
    ax.set_title("\u4e00\u4e2a\u526a\u5200\u53e3\uff0c\u4e24\u6761\u5e73\u7ebf", fontsize=8.8, loc="left")
    ax.legend(frameon=False, fontsize=5.9, loc="center left", ncol=1)
    ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_periods")


# ---------------------------------------------------------------- 6s. translation (V2 ch24)
def fig_translation():
    """\u7ffb\u8bd1\uff1a\u516b\u5bf9\u8bed\u8a00\u7684\u7ed3\u6784\u8ddd\u79bb\uff1b\u4e09\u79cd\u5bf9\u9f50\u3002\u7248\u5fc3 6.4 in\u3002"""
    import pandas as pd

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.2), gridspec_kw={"width_ratios": [1.25, 1]})

    d = pd.read_csv(ROOT / "data" / "derived" / "narrative_distance.csv")
    d["label"] = d["a"] + "\u2013" + d["b"]
    ev_col = {"\u7532\u5348\u6218\u4e89": RED, "\u671d\u9c9c\u6218\u4e89": BLUE, "\u8499\u53e4\u5e1d\u56fd": GRAY}
    ax = axes[0]
    y = 0
    ticks, labels = [], []
    for ev, g in d.groupby("event", sort=False):
        for _, r in g.sort_values("distance").iterrows():
            ax.plot([r["distance"]], [y], "o", ms=4.2, color=ev_col.get(ev, INK))
            ticks.append(y); labels.append(r["label"])
            y += 1
        y += 0.8
    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=5.8)
    ax.invert_yaxis()
    ax.set_xlim(0.78, 1.00)
    ax.set_xlabel("\u7ed3\u6784\u8ddd\u79bb\uff081 \u2212 Jaccard\uff09", fontsize=7.2)
    ax.set_title("\u5341\u516b\u5bf9\u7248\u672c\uff0c\u6ca1\u6709\u4e00\u5bf9\u63a5\u8fd1", fontsize=8.8, loc="left")
    ax.axvline(0.82, color=GRAY, ls=":", lw=0.8)
    ax.text(0.8215, -0.9, "\u6700\u4f4e 0.82", fontsize=5.8, color=GRAY)
    ax.annotate("en\u2013ja\uff1a\u4e94\u767e\u4e2a\u5b9e\u4f53\u53ea\u91cd\u5408 13",
                (0.978, 5), xytext=(0.826, 5.0), fontsize=6.0, color=RED, va="center",
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))
    ax.tick_params(axis="x", labelsize=6.4)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    # right: three kinds of alignment
    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.text(0.0, 9.6, "\u4e09\u79cd\u5bf9\u9f50", fontsize=8.8, fontweight="bold")
    pairs = [(8.2, "\u4e00\u5bf9\u4e00", "\u5207\u70b9\u4e00\u6837", BLUE),
             (5.0, "\u4e00\u5bf9\u591a", "\u5bf9\u65b9\u628a\u4e00\u683c\u5207\u6210\u4e24\u683c", OCHRE),
             (1.8, "\u65e0\u5bf9\u5e94", "\u683c\u5b50\u4e0d\u5b58\u5728", RED)]
    for yc, name, note, col in pairs:
        ax.text(0.0, yc + 0.55, name, fontsize=7.2, color=col)
        ax.text(0.0, yc - 0.15, note, fontsize=6.2, color=GRAY)
        ax.plot([3.4], [yc], "s", ms=6, color=INK)
        ax.plot([6.2], [yc], "s", ms=6, color=INK)
        if name == "\u4e00\u5bf9\u4e00":
            ax.annotate("", xy=(6.0, yc), xytext=(3.6, yc),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.2))
        elif name == "\u4e00\u5bf9\u591a":
            ax.annotate("", xy=(6.0, yc + 0.28), xytext=(3.6, yc),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.1))
            ax.annotate("", xy=(6.0, yc - 0.28), xytext=(3.6, yc),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.1))
            ax.plot([6.2], [yc + 0.28], "s", ms=5, color=INK)
            ax.plot([6.2], [yc - 0.28], "s", ms=5, color=INK)
        else:
            ax.annotate("", xy=(5.9, yc), xytext=(4.0, yc),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.1, ls="--"))
            ax.text(6.9, yc, "\u53ea\u80fd\u501f/\u9020", fontsize=6.0, color=RED)
    ax.text(3.3, 0.55, "\u6e90\u7801", fontsize=6.2, color=GRAY)
    ax.text(6.1, 0.55, "\u8bd1\u7801", fontsize=6.2, color=GRAY)

    fig.tight_layout()
    save(fig, "v2_fig_translation")


# ---------------------------------------------------------------- 6t. margins (V2 ch25)
def fig_margin():
    """\u8fb9\u7f18\uff1a\u4e24\u5757\u4e00\u6865\u4e0e Fiedler \u5411\u91cf\uff1b\u56db\u7c7b\u8fb9\u7f18\u7684 2x2\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.1), gridspec_kw={"width_ratios": [1.1, 1]})

    # left: two communities, one bridge; colour by Fiedler vector
    n_a, n_b = 9, 8
    ang_a = np.linspace(0, 2 * np.pi, n_a, endpoint=False)
    ang_b = np.linspace(0, 2 * np.pi, n_b, endpoint=False)
    pos = {}
    for i, t in enumerate(ang_a):
        pos[i] = (0.30 + 0.13 * np.cos(t), 0.55 + 0.20 * np.sin(t))
    for j, t in enumerate(ang_b):
        pos[n_a + j] = (0.72 + 0.13 * np.cos(t), 0.55 + 0.20 * np.sin(t))
    edges = [(i, (i + 1) % n_a) for i in range(n_a)] + [(n_a + j, n_a + (j + 1) % n_b) for j in range(n_b)]
    edges += [(0, 3), (n_a, n_a + 4)]          # intra-block chords
    edges += [(2, n_a + 1)]                     # the single bridge
    W = np.zeros((n_a + n_b, n_a + n_b))
    for i, j in edges:
        W[i, j] = W[j, i] = 1.0
    d = W.sum(1)
    L = np.diag(d) - W
    ev, vec = np.linalg.eigh(L)
    f = vec[:, 1]
    f = f / np.abs(f).max()
    ax = axes[0]
    for i, j in edges:
        ax.plot([pos[i][0], pos[j][0]], [pos[i][1], pos[j][1]], color=GRAY, lw=0.7,
                zorder=1, ls="-" if (i, j) != (2, n_a + 1) else "-")
    for k, (x, y) in pos.items():
        col = plt.cm.RdBu_r((f[k] + 1) / 2)
        ax.scatter([x], [y], s=52, color=col, edgecolor=INK, lw=0.5, zorder=2)
    ax.plot([pos[2][0], pos[n_a + 1][0]], [pos[2][1], pos[n_a + 1][1]], color=RED, lw=1.8, zorder=0)
    ax.text(0.51, 0.60, "\u6865\u53ea\u6709\u4e00\u6761", fontsize=6.6, color=RED, ha="center")
    ax.text(0.30, 0.16, "\u5757 A", fontsize=7.2, ha="center")
    ax.text(0.72, 0.16, "\u5757 B", fontsize=7.2, ha="center")
    ax.text(0.0, 0.98, f"\u03bb2 = {ev[1]:.2f}\uff08\u6865\u8d8a\u5c11\uff0c\u5207\u5f97\u8d8a\u5e72\u51c0\uff09", fontsize=6.8, va="top")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    # right: 2x2 of margins
    ax = axes[1]
    ax.set_xlim(0, 2); ax.set_ylim(0, 2)
    ax.set_xticks([0.5, 1.5]); ax.set_xticklabels(["低", "高"])
    ax.set_yticks([0.5, 1.5]); ax.set_yticklabels(["低", "高"])
    ax.set_xlabel("核实率", fontsize=7.4)
    ax.set_ylabel("创新率", fontsize=7.4)
    ax.plot([1, 1], [0, 2], color=INK, lw=0.9)
    ax.plot([0, 2], [1, 1], color=INK, lw=0.9)
    ax.text(0.5, 1.55, "边缘：\n新码先出现，\n但没人核", fontsize=6.5, ha="center", color=RED)
    ax.text(1.5, 1.55, "中心：\n有核实力，\n也有惰性", fontsize=6.5, ha="center")
    ax.text(0.5, 0.45, "停滞的边缘：\n既不新，\n也没人核", fontsize=6.5, ha="center", color=GRAY)
    ax.text(1.5, 0.45, "强制核实的中心：\n新得少，\n但错得少", fontsize=6.5, ha="center")
    ax.tick_params(labelsize=6.6)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_margin")


# ---------------------------------------------------------------- 6u. semantics (V2 ch26)
def fig_semantics():
    """\u8bed\u4e49\uff1a\u4e49\u9879\u6570\u4e0e\u53d8\u52a8\u7387\uff1b\u68d8\u8f6e\u3002\u7248\u5fc3 6.4 in\u3002"""
    import json

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1.15, 1]})

    d = json.loads((ROOT / "data" / "derived" / "sense_inventory.json").read_text(encoding="utf-8"))
    bins = d["bins"]
    ax = axes[0]
    labels = ["1", "2", "3\u20144", "5\u20149", "10+"]
    rates = [b["change_rate"] * 100 for b in bins]
    ns = [b["n"] for b in bins]
    ax.bar(range(len(bins)), rates, color=[BLUE] * 4 + [RED], width=0.6)
    for i, r in enumerate(rates):
        ax.text(i, r + 0.08, f"{r:.1f}%", ha="center", fontsize=6.4)
    ax.set_xticks(range(len(bins)))
    ax.set_xticklabels([f"\u4e49\u9879 {l}\nn={n:,}" for l, n in zip(labels, ns)], fontsize=5.8)
    ax.set_ylim(0, 7.2)
    ax.set_ylabel("\u4e24\u5e74\u95f4\u4e49\u9879\u6570\u53d8\u52a8\u7684\u6bd4\u4f8b\uff08%\uff09", fontsize=7.2)
    ax.set_title("\u8d8a\u591a\u4e49\uff0c\u8d8a\u5bb9\u6613\u53d8", fontsize=8.8, loc="left")
    ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    ax = axes[1]
    inv = d["inventory"]
    vals = [inv["added"], inv["dropped"]]
    ax.bar([0, 1], vals, color=[BLUE, RED], width=0.5)
    ax.set_yscale("log")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["\u65b0\u589e\u4e49\u9879", "\u6d88\u5931\u4e49\u9879"], fontsize=7.0)
    ax.set_ylim(10, 12000)
    for i, v in enumerate(vals):
        ax.text(i, v * 1.15, f"{v:,}", ha="center", fontsize=7.0)
    ax.text(0.5, 7000, "54 : 1", ha="center", fontsize=10, color=INK, fontweight="bold")
    ax.set_title("\u8bcd\u6c47\u51e0\u4e4e\u53ea\u8fdb\u4e0d\u51fa", fontsize=8.8, loc="left")
    ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.text(0.0, -0.30, f"\u4e24\u7248\u5171\u6709 {inv['shared']:,} \u8bcd\u6761", transform=ax.transAxes,
            fontsize=6.0, color=GRAY)

    fig.tight_layout()
    save(fig, "v2_fig_semantics")


# ---------------------------------------------------------------- 6v. boundary (V2 ch27)
def fig_boundary():
    """\u8fb9\u754c\uff1a\u540c\u4e00\u76f8\u5173\u4e24\u4e2a\u7b26\u53f7\uff1b\u53e3\u5f84\u5dee\u662f\u5206\u5e03\u4e0d\u662f\u5355\u4f8b\u3002\u7248\u5fc3 6.4 in\u3002"""
    import json

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1, 1.1]})

    d = json.loads((ROOT / "data" / "derived" / "claims_tests.json").read_text(encoding="utf-8"))
    a = d["A_P7_trust_vs_tfr"]
    ax = axes[0]
    vals = [a["pooled_corr"], a["within_country_corr"]]
    ax.bar([0, 1], vals, color=[RED, BLUE], width=0.5)
    ax.axhline(0, color=INK, lw=0.9)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["\u8de8\u56fd\u6a2a\u622a\u9762\n\uff08\u6bd4\u56fd\u5bb6\uff09", "\u540c\u4e00\u56fd\u5bb6\u5185\u90e8\n\uff08\u6bd4\u5e74\u4efd\uff09"], fontsize=6.6)
    ax.set_ylim(-0.36, 0.36)
    for i, v in enumerate(vals):
        ax.text(i, v + (0.03 if v > 0 else -0.055), f"{v:+.2f}", ha="center", fontsize=8.4)
    ax.set_ylabel("\u4fe1\u4efb \u4e0e \u751f\u80b2\u7387 \u7684 \u76f8\u5173", fontsize=7.2)
    ax.set_title("\u540c\u4e00\u4e2a\u76f8\u5173\uff0c\u4e24\u4e2a\u7b26\u53f7", fontsize=8.8, loc="left")
    ax.text(0.02, 0.03, f"n={a['n']} \u4e2a\u56fd\u5bb6-\u5e74\u4efd", transform=ax.transAxes,
            fontsize=6.0, color=GRAY)
    ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    ax = axes[1]
    rng = np.random.default_rng(7)
    gap = np.exp(rng.normal(0.9, 0.75, 400)) + 0.6
    ax.hist(gap, bins=40, color=LIGHT, edgecolor=GRAY, lw=0.5)
    med = np.median(gap)
    ax.axvline(med, color=BLUE, lw=1.6)
    ax.text(med + 0.6, ax.get_ylim()[1] * 0.55, f"\u4e2d\u4f4d {med:.1f} \u70b9", fontsize=6.4, color=BLUE)
    ax.axvline(19, color=RED, lw=1.6, ls="--")
    ax.text(15.4, ax.get_ylim()[1] * 0.62, "\u5355\u4f8b\uff1a19 \u70b9", fontsize=6.4, color=RED)
    ax.set_xlabel("\u53e3\u5f84\u5dee\uff08\u70b9\uff09", fontsize=7.2)
    ax.set_ylabel("\u6b21\u6570", fontsize=7.2)
    ax.set_title("\u53e3\u5f84\u5dee\u662f\u4e00\u4e2a\u53f3\u504f\u5206\u5e03", fontsize=8.8, loc="left")
    ax.text(0.02, 0.70, "\u793a\u610f\uff1a\u5f62\u72b6\u662f\u5047\u5b9a\u7684",
            transform=ax.transAxes, fontsize=5.8, color=GRAY)
    ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_boundary")


# ---------------------------------------------------------------- 6w. transfer (V2 ch28)
def fig_transfer():
    """\u8f6c\u79fb\uff1a\u56db\u6761\u901a\u9053\u4e0e\u5b83\u4eec\u7684\u65f6\u6ede\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.text(0.0, 9.6, "\u56db\u6761\u8f6c\u79fb\u901a\u9053\uff1a\u8c01\u7701\u4e86\u529b\u6c14\uff0c\u8d26\u843d\u5230\u8c01\u5934\u4e0a", fontsize=9.0, fontweight="bold")

    rows = [
        (7.6, "\u2460 \u53d1\u9001\u7aef \u2192 \u63a5\u6536\u7aef", "\u8bf4\u7684\u4eba\u7701\u5b57\uff0c\u542c\u7684\u4eba\u8865\u8bfe", "\u79d2\u2014\u5206\u949f", BLUE),
        (5.6, "\u2461 \u5224\u65ad\u8005 \u2192 \u88ab\u5224\u65ad\u8005", "\u6807\u7b7e\u7701\u4e00\u6b21\u8bc4\u4f30\uff0c\u88ab\u8d34\u7684\u4eba\u627f\u62c5\u8bef\u5dee", "\u6708\u2014\u5e74", OCHRE),
        (3.6, "\u2462 \u673a\u6784 \u2192 \u4e2a\u4eba", "\u8868\u683c\u7701\u4e00\u680f\uff0c\u586b\u8868\u7684\u4eba\u591a\u82b1\u51e0\u5206\u949f", "\u5e74", GREEN),
        (1.6, "\u2463 \u4eca\u5929 \u2192 \u4ee5\u540e", "\u5f53\u671f\u7701\u4e00\u7b14\uff0c\u540e\u9762\u7684\u4eba\u8865\u4e00\u8f88\u5b50", "20\u201440 \u5e74", RED),
    ]
    for y, name, note, lag, col in rows:
        ax.add_patch(Rectangle((0.0, y - 0.55), 6.0, 1.15, facecolor="#fbfbfb", edgecolor=col, lw=1.2))
        ax.text(0.2, y + 0.22, name, fontsize=7.6, color=INK)
        ax.text(0.2, y - 0.28, note, fontsize=6.4, color=GRAY)
        ax.annotate("", xy=(7.9, y), xytext=(6.2, y),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.4))
        ax.text(8.0, y - 0.06, lag, fontsize=6.8, color=col, va="center")
    ax.text(7.95, 8.55, "\u65f6\u6ede", fontsize=6.6, color=GRAY)
    ax.text(0.0, 0.3, "\u56db\u6bb5\u5171\u7528\u4e00\u4e2a\u8f6c\u8f74\uff1a\u4ee3\u4ef7\u53ef\u4ee5\u88ab\u6307\u5b9a\u3002\u65f6\u6ede\u8d8a\u957f\uff0c\u6307\u5b9a\u8d8a\u5bb9\u6613\u3002",
            fontsize=6.6, color=INK)
    save(fig, "v2_fig_transfer")


# ---------------------------------------------------------------- 6x. two times (V2 ch29)
def fig_twotimes():
    """\u4e24\u79cd\u65f6\u523b\uff1a\u6392\u73ed\uff08B<0\uff09\u4e0e\u590d\u4f4d\uff08B>0\uff09\u3002\u7248\u5fc3 6.4 in\u3002"""
    import json

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0))

    rb = json.loads((ROOT / "data" / "derived" / "revision_bursts.json").read_text(encoding="utf-8"))
    g = json.loads((ROOT / "data" / "derived" / "gregorian_adoption.json").read_text(encoding="utf-8"))

    ax = axes[0]
    pp = rb["ecfr_section_gaps"]["per_part"]
    parts = list(pp.items())
    xs = np.arange(len(parts))
    means = [v["mean"] for _, v in parts]
    ns = [v["n_gaps"] for _, v in parts]
    ax.scatter(xs, means, s=[6 + 1.1 * n for n in ns], color=BLUE, alpha=0.75, lw=0)
    overall = rb["ecfr_section_gaps"]["mean_years"]
    ax.axhline(overall, color=RED, lw=1.3, ls="--")
    ax.text(0.4, overall + 0.35, f"\u5168\u4f53\u5747\u503c {overall:.1f} \u5e74", fontsize=6.2, color=RED)
    ax.set_xticks([])
    ax.set_xlabel("21 CFR \u7684 19 \u4e2a\u90e8\u5206\uff08\u70b9\u5927\u5c0f = \u95f4\u9694\u6570\uff0c\u5171 266 \u4e2a\uff09", fontsize=6.6)
    ax.set_ylabel("\u8be5\u90e8\u5206\u7684\u5e73\u5747\u4fee\u8ba2\u95f4\u9694\uff08\u5e74\uff09", fontsize=7.0)
    ax.set_title(f"\u6392\u73ed\uff1a\u6bd4\u968f\u673a\u66f4\u89c4\u5219\uff08B={rb['ecfr_section_gaps']['burstiness_B']:+.2f}\uff09",
                 fontsize=8.2, loc="left")
    ax.tick_params(labelsize=6.4)
    ax.set_ylim(0, 9)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    ax = axes[1]
    years = np.array(g["years"])
    bins = np.arange(1575, 1945, 5)
    ax.hist(years, bins=bins, color=OCHRE, alpha=0.8, edgecolor="white", lw=0.5)
    for y, c in [(1583, 25), (1582, 18), (1700, 14), (1584, 12)]:
        ax.annotate(str(y), (y, c + 0.6), fontsize=5.8, color=INK, ha="center")
    ax.set_xlim(1575, 1940)
    ax.set_xlabel("\u91c7\u7528\u516c\u5386\u7684\u5e74\u4efd", fontsize=7.0)
    ax.set_ylabel("\u56fd\u5bb6\u6570", fontsize=7.0)
    ax.set_title(f"\u590d\u4f4d\uff1a\u56f4\u7740\u4e00\u6b21\u4e8b\u4ef6\u6210\u56e2\uff08B={g['burstiness_B']:+.2f}\uff09",
                 fontsize=8.2, loc="left")
    ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)

    fig.tight_layout()
    save(fig, "v2_fig_twotimes")


# ---------------------------------------------------------------- 6y. gaps (V2 ch30)
def fig_gaps():
    """\u4e5d\u5904\u7a7a\u767d\uff1a\u8865\u7684\u4ee3\u4ef7 \u00d7 \u8865\u4e0a\u4e4b\u540e\u7ed3\u8bba\u4f1a\u53d8\u591a\u5c11\u3002\u7248\u5fc3 6.4 in\u3002"""
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_xlabel("\u8865\u7684\u4ee3\u4ef7\uff08\u5e8f\u6570\uff09\u2192 \u8d35", fontsize=7.4)
    ax.set_ylabel("\u8865\u4e0a\u4e4b\u540e\uff0c\u7ed3\u8bba\u4f1a\u53d8\u591a\u5c11\uff08\u5e8f\u6570\uff09\u2192 \u5927", fontsize=7.4)
    ax.set_xticks([]); ax.set_yticks([])
    ax.plot([5, 5], [0, 10], color=LIGHT, lw=1.0)
    ax.plot([0, 10], [5, 5], color=LIGHT, lw=1.0)
    pts = [
        (1.2, 8.6, "9 \u539f\u7406\u4e8c\u7684\u68c0\u9a8c", RED),
        (4.2, 7.4, "1 \u5206\u8fa8\u7387\u5206\u5e03", BLUE),
        (7.6, 8.2, "3 \u5957\u5229\u6298\u635f\u7cfb\u6570", RED),
        (3.0, 4.2, "2 \u9677\u9631\u95e8\u69db", BLUE),
        (6.4, 3.0, "5 \u65b0\u7801\u4ece\u54ea\u6765", GRAY),
        (8.2, 5.6, "4 \u4e00\u53e5\u8bdd\u4e3a\u4ec0\u4e48\u594f\u6548", GRAY),
        (5.2, 1.8, "7 \u591a\u671f", GRAY),
        (7.0, 1.4, "8 \u591a\u5c42\u7b97\u5b50", GRAY),
        (9.0, 0.8, "6 \u4e3a\u4ec0\u4e48\u662f\u8fd9\u4e00\u4e2a", GRAY),
    ]
    for x, y, lab, col in pts:
        ax.plot([x], [y], "o", ms=8, color=col, alpha=0.85)
        if x > 7.4:
            ax.text(x - 0.22, y + 0.05, lab, fontsize=6.4, va="center", ha="right", color=INK)
        else:
            ax.text(x + 0.22, y + 0.05, lab, fontsize=6.4, va="center", color=INK)
    ax.text(0.2, 9.6, "\u5148\u505a\uff08\u4fbf\u5b9c\u800c\u8981\u7d27\uff09", fontsize=7.0, color=RED)
    ax.text(0.2, 0.3, "\u7ed9\u5341\u500d\u6570\u636e\u4e5f\u7b54\u4e0d\u4e0a\uff1a\u8981\u6362\u5de5\u5177", fontsize=6.6, color=GRAY)
    ax.set_title("\u4e5d\u5904\u7a7a\u767d\u653e\u5728\u540c\u4e00\u5f20\u7eb8\u4e0a", fontsize=9.0, loc="left")
    ax.text(0.0, -0.12, "\u500d\u7ea7\uff1a\u4f4d\u7f6e\u662f\u672c\u4e66\u7684\u5224\u8bfb\uff0c\u4e24\u8f74\u90fd\u662f\u5e8f\u6570\uff1b\u7ea2\u8272\u4e09\u4ef6\u662f\u300c\u4fbf\u5b9c\u800c\u8981\u7d27\u300d\uff0c\u6df1\u84dd\u4e09\u4ef6\u662f\u300c\u7f3a\u6570\u636e\u300d\uff0c\u7070\u8272\u56db\u4ef6\u662f\u300c\u7f3a\u6982\u5ff5\uff0f\u8fb9\u754c\u300d\u3002",
            transform=ax.transAxes, fontsize=5.8, color=GRAY)
    save(fig, "v2_fig_gaps")


# ---------------------------------------------------------------- 6z. memory / bandwidth / naming (V2 ch07/08/15)
def fig_memory():
    """\u8bb0\u4f4f\uff1a\u9057\u5fd8\u66f2\u7ebf\uff08\u6587\u732e\u503c\uff09\u4e0e\u6362\u624b\u7387\u4e09\u6761\u7ebf\uff08\u6a21\u62df\u503c\uff09\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0))
    ax = axes[0]
    t = np.array([1/72, 1/24, 1, 2, 6, 31]); keep = np.array([100-42, 100-56, 100-66, 100-72, 100-75, 100-79])
    ax.plot(t, keep, "o-", color=BLUE, lw=1.8, ms=4)
    ax.set_xscale("log")
    ax.set_xlabel("\u91cd\u5b66\u95f4\u9694\uff08\u5929\uff0c\u5bf9\u6570\uff09", fontsize=7.2)
    ax.set_ylabel("\u8282\u7701\u7684\u91cd\u5b66\u65f6\u95f4\uff08%\uff09", fontsize=7.2)
    ax.set_title("\u9057\u5fd8\u66f2\u7ebf\uff1a\u4e00\u5f00\u59cb\u6389\u5f97\u5feb", fontsize=8.4, loc="left")
    ax.set_ylim(0, 70); ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
    ax.text(0.03, 0.06, "\u827e\u5bbe\u6d69\u65af 1885\uff08\u65e0\u610f\u4e49\u97f3\u8282\uff0cn=1\uff09", transform=ax.transAxes, fontsize=5.8, color=GRAY)

    ax = axes[1]
    turn = ["0", "0.2%", "1%"]; cons = [0.958, 0.737, 0.496]; labels = [7, 9, 25]
    ax.plot(range(3), cons, "o-", color=RED, lw=1.8, ms=5, label="\u9010\u683c\u5171\u8bc6\u5ea6")
    for i, v in enumerate(cons): ax.text(i, v + 0.03, f"{v:.2f}", ha="center", fontsize=6.2, color=RED)
    ax.set_ylim(0.4, 1.05); ax.set_xticks(range(3)); ax.set_xticklabels(turn, fontsize=6.8)
    ax.set_xlabel("\u6210\u5458\u6362\u624b\u7387\uff08\u6bcf\u8f6e\uff09", fontsize=7.2)
    ax.set_ylabel("\u9010\u683c\u5171\u8bc6\u5ea6", fontsize=7.2)
    ax.set_title("\u522b\u4eba\u6362\u4e86\uff0c\u4f60\u5c31\u5fd8\u4e86", fontsize=8.4, loc="left")
    ax2 = ax.twinx(); ax2.bar(range(3), labels, color=LIGHT, width=0.45, zorder=0)
    ax2.set_ylabel("\u6807\u7b7e\u79cd\u7c7b", fontsize=7.0); ax2.set_ylim(0, 40); ax2.tick_params(labelsize=6.2)
    ax.tick_params(labelsize=6.4)
    for s_ in ("top",): ax.spines[s_].set_visible(False); ax2.spines[s_].set_visible(False)
    fig.tight_layout(); save(fig, "v2_fig_memory")


def fig_bandwidth():
    """\u8ddf\u4e0a\uff1a\u4e24\u79cd\u75b2\u52b3\u7684\u5206\u5c94\uff1b\u5e26\u5bbd 2C \u4e0e\u91cd\u65b0\u8ddf\u4e0a\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0))
    ax = axes[0]
    x = np.linspace(0, 10, 300)
    ax.plot(x, 1.0 / (1 + np.exp(-(x - 6))), color=RED, lw=1.8, label="\u4efb\u52a1\u91cf\uff08\u7a81\u7136\u4e0a\u5347\uff09")
    ax.plot(x, 0.55 * np.ones_like(x), color=BLUE, lw=1.8, label="\u5904\u7406\u80fd\u529b\uff08\u65f6\u95f4\uff09")
    ax.plot(x, 0.55 * (1 - 0.35 * np.clip((x - 4) / 6, 0, 1)), color=OCHRE, lw=1.6, ls="--", label="\u5904\u7406\u80fd\u529b\uff08\u75b2\u52b3\uff09")
    ax.set_xlabel("\u65f6\u95f4", fontsize=7.2); ax.set_ylabel("\u8d1f\u8377\uff08\u76f8\u5bf9\uff09", fontsize=7.2)
    ax.set_title("\u4e24\u79cd\u75b2\u52b3\uff1a\u6765\u4e0d\u53ca\uff0c\u8fd8\u662f\u7d2f\u4e86", fontsize=8.4, loc="left")
    ax.legend(frameon=False, fontsize=6.0, loc="center left"); ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
    ax = axes[1]
    ax.plot([0, 1, 2, 3], [0, 0.15, 0.6, 0.62], color=GRAY, lw=1.2, ls="--", label="\u65e7\u7801\u7684\u574f\u5904")
    ax.axhspan(0.3, 0.5, color=LIGHT, alpha=0.6)
    ax.text(0.05, 0.40, "2C\uff1a\u4e0d\u52a8\u533a", fontsize=6.4, color=INK)
    ax.plot([1.2, 2.2], [0.55, 0.55], color=RED, lw=2.0)
    ax.annotate("\u6362\u7801\u540e\u91cd\u65b0\u8ddf\u4e0a\uff1a\n\u65b0\u7801\u7684\u574f\u5904\u4ece\u96f6\u91cd\u8ba1", (1.7, 0.55), xytext=(0.1, 0.78),
                fontsize=6.2, color=RED, arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))
    ax.set_xlabel("\u65f6\u95f4", fontsize=7.2); ax.set_ylabel("\u636e\u65e7\u7801\u7684\u635f\u5931", fontsize=7.2)
    ax.set_title("\u5e26\u5bbd\u4e0e\u91cd\u65b0\u8ddf\u4e0a", fontsize=8.4, loc="left"); ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
    fig.tight_layout(); save(fig, "v2_fig_bandwidth")


def fig_naming():
    """\u8bb2\u8ff0\uff1a\u4e00\u6bd4\u7279\u66ff\u4ee3\u4e00\u6bb5\u8bdd\uff1b\u547d\u540d\u6743\u7684\u56db\u4e2a\u6765\u6e90\u3002"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0))
    ax = axes[0]
    ax.plot([0, 5], [11, 11], color=BLUE, lw=2.0)
    ax.text(0, 11.5, "\u4e00\u6bb5\u53d9\u4e8b\uff1a\u5341\u51e0\u4e2a\u683c\uff0c\u53ef\u5206\u8fa8\u3001\u53ef\u4e89", fontsize=6.4, color=BLUE)
    ax.plot([0, 5], [4.5, 4.5], color=RED, lw=2.0)
    ax.text(0, 5.0, "\u4e00\u4e2a\u6807\u7b7e\uff1a\u4e00\u6bd4\u7279\uff0c\u4e0d\u53ef\u5206\u8fa8", fontsize=6.4, color=RED)
    ax.annotate("", xy=(4.6, 4.5), xytext=(4.6, 11), arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1.0))
    ax.text(4.7, 7.6, "\u7701\u4e0b\u7684\n\u5c31\u662f\u4e89\u7684\n\u4f59\u5730", fontsize=6.0, color=GRAY)
    ax.set_xlim(0, 6); ax.set_ylim(0, 13); ax.axis("off")
    ax.set_title("\u6807\u7b7e\u66ff\u4ee3\u53d9\u4e8b\uff1a\u6210\u672c\u5728\u54ea\u91cc", fontsize=8.4, loc="left")

    ax = axes[1]
    src = ["\u884c\u653f", "\u4e13\u4e1a", "\u5e02\u573a", "\u5171\u540c\u4f53"]
    keep = [0.62, 0.41, 0.28, 0.12]   # \u547d\u540d\u6743\u96c6\u4e2d\u5ea6\uff08\u793a\u610f\uff09
    ax.barh(range(4), keep, color=[BLUE, OCHRE, GRAY, GREEN], height=0.55)
    ax.set_yticks(range(4)); ax.set_yticklabels(src, fontsize=7.0); ax.invert_yaxis()
    ax.set_xlabel("\u547d\u540d\u6743\u96c6\u4e2d\u5ea6\uff08\u793a\u610f\uff09", fontsize=7.2)
    ax.set_title("\u56db\u4e2a\u6765\u6e90\uff0c\u56db\u79cd\u4ee3\u4ef7", fontsize=8.4, loc="left")
    ax.tick_params(labelsize=6.4)
    for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
    fig.tight_layout(); save(fig, "v2_fig_naming")


# ---------------------------------------------------------------- 8e. yanduan (V2 ch23, 图23.2)
def fig_yanduan():
    """阈值的两种写法 + 卷积过阈后的权重反转。版心 6.4 in；图内字 >=7 pt。
    左幅是设定值的形状演示（C 级）；中、右两幅用 analysis/sim_yanduan.py 的输出。
    """
    import csv
    rows = list(csv.DictReader(open(ROOT / "data" / "derived" / "sim_yanduan.csv",
                                    encoding="utf-8-sig")))
    yr = np.array([float(r["year"]) for r in rows])
    A = np.array([float(r["A"]) for r in rows])
    S = np.array([float(r["S"]) for r in rows])
    worder = np.array([float(r["w_order"]) for r in rows])
    wvict = np.array([float(r["w_victory"]) for r in rows])
    code = np.array([float(r["code"]) for r in rows])

    fig, axes = plt.subplots(1, 3, figsize=(6.4, 2.7),
                             gridspec_kw={"width_ratios": [1.0, 1.1, 1.05]})

    # (a) 阈值：一条线 vs 一个函数
    ax = axes[0]
    tau = np.linspace(0.5, 30, 200)
    theta0, aa, bb = 1.0, 0.9, 1.6
    for w, col, lab in [(2.0, RED, "w 高"), (1.0, OCHRE, "w 中"), (0.5, BLUE, "w 低")]:
        ax.plot(tau, theta0 + aa * tau / (1 + bb * w), color=col, lw=1.7, label=lab)
    ax.axhline(theta0, color=GRAY, ls="--", lw=1.0)
    ax.text(9.0, 1.45, "常数写法", fontsize=7.0, color=GRAY)
    ax.set_xlabel("核实延迟 τ（天）", fontsize=7.4)
    ax.set_ylabel("判为“已过阈”的推力", fontsize=7.2)
    ax.set_title("阈值：一个点，还是一个函数", fontsize=8.6, loc="left", pad=6)
    ax.legend(frameon=False, fontsize=7.0, loc="upper left", handlelength=1.4)
    ax.set_ylim(0.6, 17.5)
    ax.tick_params(labelsize=7.0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # (b) 冲击的卷积与慢变量
    ax = axes[1]
    ax.plot(yr, A, color=BLUE, lw=1.3, label="冲击的卷积 A(t)")
    ax.plot(yr, S, color=OCHRE, lw=1.6, label="慢变量 S（泄漏积分）")
    ax.set_xlabel("年", fontsize=7.4)
    ax.set_xticks([2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026])
    ax.tick_params(axis="x", labelrotation=0)
    ax.set_ylabel("量（设定单位）", fontsize=7.2)
    ax.set_title("冲击先成峰，再积成台阶", fontsize=8.6, loc="left", pad=6)
    ax.legend(frameon=False, fontsize=7.0, loc="upper left", handlelength=1.4)
    ax.tick_params(labelsize=7.0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # (c) 权重反转与迟滞（底色＝实现出来的码）
    ax = axes[2]
    ax.fill_between(yr, 0.0, 3.6, where=(code > 0), color=RED, alpha=0.10, lw=0)
    ax.plot(yr, wvict, color=GRAY, lw=1.2, ls="--", label="w 求胜")
    ax.plot(yr, worder, color=RED, lw=1.8, label="w 求序")
    flip = yr[np.argmax(code > 0)] if (code > 0).any() else None
    if flip is not None:
        ax.axvline(flip, color=INK, ls=":", lw=0.9)
        ax.annotate("翻过去，不回头", xy=(flip, 3.30), xytext=(flip + 4, 3.34),
                    fontsize=7.0, color=INK, va="top")
    ax.set_ylim(0.85, 3.6)
    ax.set_xlabel("年", fontsize=7.4)
    ax.set_xticks([2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026])
    ax.tick_params(axis="x", labelrotation=0)
    ax.set_ylabel("权重", fontsize=7.2)
    ax.set_title("过阈之后：台阶，不是斜坡", fontsize=8.6, loc="left", pad=6)
    ax.legend(frameon=False, fontsize=7.0, loc="upper left", handlelength=1.4)
    ax.tick_params(labelsize=7.0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.09, 0.035, "参数为设定值，非估计（C 级）：这幅图演示形状，不提供读数。", fontsize=7.0, color=GRAY)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.85, bottom=0.26, wspace=0.42)
    save(fig, "v2_fig_yanduan")


# ---------------------------------------------------------------- 9. voi2 (ch10 图10.2)
def fig_voi2():
    """VOI 的两个参数：信号精度只抬峰，代价比只挪峰。版心 6.4 in，图内字 >=7 pt。"""
    import numpy as np
    def pv(p, q, lfn, lfp):
        l0 = min((1 - p) * lfp, p * lfn)
        p1 = p * q / (p * q + (1 - p) * (1 - q))
        p0 = p * (1 - q) / (p * (1 - q) + (1 - p) * q)
        l1 = (p * q + (1 - p) * (1 - q)) * min((1 - p1) * lfp, p1 * lfn) + \
             (p * (1 - q) + (1 - p) * q) * min((1 - p0) * lfp, p0 * lfn)
        return l0 - l1

    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.6))
    ps = np.linspace(0.02, 0.98, 240)
    ax = axes[0]
    for q, col in [(0.7, GRAY), (0.8, OCHRE), (0.9, RED)]:
        ax.plot(ps, [pv(p, q, 1, 1) for p in ps], color=col, lw=1.7, label="q = %.1f" % q)
    ax.axvline(0.5, color=INK, ls=":", lw=0.8)
    ax.set_xlabel("先验 p", fontsize=7.4); ax.set_ylabel("信息价值 VOI", fontsize=7.2)
    ax.set_title("信号变准：只抬峰，不挪峰", fontsize=8.6, loc="left", pad=6)
    ax.legend(frameon=False, fontsize=7.0, loc="upper right")
    ax.tick_params(labelsize=7.0)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

    ax = axes[1]
    rs = np.linspace(1, 10, 120)
    peaks, heights = [], []
    for r in rs:
        v = [pv(p, 0.7, r, 1.0) for p in ps]
        j = int(np.argmax(v)); peaks.append(ps[j]); heights.append(v[j])
    ax.plot(rs, peaks, color=BLUE, lw=1.8, label="峰位 p*")
    ax2 = ax.twinx()
    ax2.plot(rs, heights, color=RED, lw=1.5, ls="--", label="峰高")
    for r, lab in [(5, "5:1"), (2, "2:1")]:
        ax.plot([r], [1 / (1 + r)], "o", color=BLUE, ms=3.5)
        ax.annotate(lab, (r, 1 / (1 + r)), textcoords="offset points", xytext=(3, 6), fontsize=7.0, color=BLUE)
    ax.set_xlabel("代价比 漏判:错判（L_FN : L_FP）", fontsize=7.4)
    ax.set_ylabel("峰位 p*", fontsize=7.2); ax2.set_ylabel("峰高", fontsize=7.2, color=RED)
    ax.set_title("代价变了：横向挪峰", fontsize=8.6, loc="left", pad=6)
    ax.tick_params(labelsize=7.0); ax2.tick_params(labelsize=7.0, colors=RED)
    for s in ("top",): ax.spines[s].set_visible(False); ax2.spines[s].set_visible(False)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=7.0, loc="center right")
    fig.subplots_adjust(left=0.09, right=0.91, top=0.84, bottom=0.20, wspace=0.52)
    save(fig, "v2_fig_voi2")


# ---------------------------------------------------------------- 9b. discount (ch31 图31.2)
def fig_discount():
    """时滞的贴现：3% 与 5%，标出 20 年与 40 年。版心 6.4 in。"""
    import numpy as np
    fig, ax = plt.subplots(figsize=(6.4, 2.5))
    t = np.linspace(0, 60, 300)
    ax.plot(t, (1.03) ** (-t), color=OCHRE, lw=1.9, label="r = 3%")
    ax.plot(t, (1.05) ** (-t), color=BLUE, lw=1.4, ls="--", label="r = 5%")
    for tt in (20, 40):
        ax.axvline(tt, color=GRAY, ls=":", lw=0.8)
    ax.plot([20], [1.03 ** -20], "o", color=OCHRE, ms=4)
    ax.plot([40], [1.03 ** -40], "o", color=OCHRE, ms=4)
    ax.annotate("20 年：0.554", (20, 1.03 ** -20), textcoords="offset points", xytext=(5, 6), fontsize=7.0, color=OCHRE)
    ax.annotate("40 年：0.307", (40, 1.03 ** -40), textcoords="offset points", xytext=(5, 6), fontsize=7.0, color=OCHRE)
    ax.set_xlabel("这笔账落在多少年之后", fontsize=7.4)
    ax.set_ylabel("今天的现值", fontsize=7.2)
    ax.set_title("时滞越长，账越轻：每翻一倍，再打六折", fontsize=8.6, loc="left", pad=6)
    ax.legend(frameon=False, fontsize=7.2, loc="upper right")
    ax.set_ylim(0, 1.02); ax.tick_params(labelsize=7.0)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.subplots_adjust(left=0.11, right=0.98, top=0.86, bottom=0.24)
    save(fig, "v2_fig_discount")


# ---------------------------------------------------------------- 10. three lines (ch19 图19.2)
def fig_three():
    """三个量三条线：ρ（供给）、p（报道比）、κ（议程）。数据 gap_proxies.csv。版心 6.4 in。"""
    import csv
    rows = list(csv.DictReader(open(ROOT / "data" / "derived" / "gap_proxies.csv", encoding="utf-8-sig")))
    yr = [int(r["year"]) for r in rows]
    rho = [float(r["rho_checks"]) if r["rho_checks"] else None for r in rows]
    p_ = [float(r["p_rate"]) * 100 if r["p_rate"] else None for r in rows]
    kap = [float(r["kappa_share"]) * 100 if r["kappa_share"] else None for r in rows]

    def line(vals):
        xs = [y for y, v in zip(yr, vals) if v is not None]
        ys = [v for v in vals if v is not None]
        return xs, ys

    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    x, y = line(rho)
    ax.plot(x, y, color=BLUE, lw=1.8, label="供给 ρ（年核查条数）")
    ax.set_ylabel("ρ：条／年", fontsize=7.2, color=BLUE)
    ax.tick_params(labelsize=7.0)
    ax2 = ax.twinx()
    x2, y2 = line(p_); ax2.plot(x2, y2, color=OCHRE, lw=1.7, label="报道比 p（%）")
    x3, y3 = line(kap); ax2.plot(x3, y3, color=RED, lw=1.7, ls="--", label="议程 κ（%）")
    ax2.set_ylabel("p 与 κ：百分比", fontsize=7.2)
    ax2.tick_params(labelsize=7.0)
    ax.annotate("1,963", (2012, 1963), textcoords="offset points", xytext=(-4, 8), fontsize=7.0, color=BLUE)
    ax.annotate("934", (2022, 934), textcoords="offset points", xytext=(6, 10), fontsize=7.0, color=BLUE)
    ax2.annotate("25.9%", (2026, 25.86), textcoords="offset points", xytext=(-30, 2), fontsize=7.0, color=RED)
    ax.set_xlabel("年", fontsize=7.4)
    ax.set_xticks([2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026])
    ax.tick_params(axis="x", labelrotation=0)
    ax.set_title("三条线不同步：供给先降，议程后跳", fontsize=8.6, loc="left", pad=6)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=6.9, loc="upper center")
    for s in ("top",): ax.spines[s].set_visible(False); ax2.spines[s].set_visible(False)
    fig.subplots_adjust(left=0.10, right=0.90, top=0.86, bottom=0.22)
    save(fig, "v2_fig_three")


# ---------------------------------------------------------------- 11. budget (ch03 图3.2)
def fig_budget():
    """预算线与等值线：w 与 (T+λ) 各把 v* 往哪边推。版心 6.4 in，图内字 >=7 pt。"""
    import numpy as np
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.7))
    # 左：J(v) 三条曲线
    ax = axes[0]
    v = np.linspace(0.06, 6, 500)
    for w, L, col, lab in [(1.0, 1.0, GRAY, "w=1, T+λ=1"), (2.0, 1.0, RED, "w=2"), (1.0, 2.0, BLUE, "T+λ=2")]:
        J = w * v + L * 0.5 * np.log2(1.0 / v)
        ax.plot(v, J, color=col, lw=1.7, label=lab)
        k = int(np.argmin(J))
        ax.plot([v[k]], [J[k]], "o", color=col, ms=4)
    ax.set_ylim(-1.5, 6); ax.set_xlim(0, 6)
    ax.set_xlabel("分辨率 v（越左越细）", fontsize=7.3)
    ax.set_ylabel("总账 J(v)", fontsize=7.3)
    ax.set_title("两只价各把谷底往两边推", fontsize=8.6, loc="left", pad=6)
    ax.legend(frameon=False, fontsize=6.9, loc="upper left")
    ax.tick_params(labelsize=7.0)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    # 右：等值线 v*=(T+λ)/(2w)
    ax = axes[1]
    w = np.logspace(-0.4, 1.0, 240)
    for level in (0.1, 0.3, 1.0, 3.0):
        L = 2 * w * level
        m = (L <= 9) & (L >= 0.35)
        ax.plot(w[m], L[m], color=INK, lw=0.9, ls="--")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.5, 8); ax.set_ylim(0.4, 9)
    ax.set_xlabel("错的代价 w", fontsize=7.3)
    ax.set_ylabel("时间与疲劳 T+λ", fontsize=7.3)
    ax.set_title("等值线：同一条线上的 v* 一样", fontsize=8.6, loc="left", pad=6)
    ax.annotate("", xy=(2.0, 5.2), xytext=(2.0, 2.0),
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.4))
    ax.annotate("T+λ 抬：更粗", xy=(2.3, 5.6), fontsize=7.0, color=BLUE, ha="left")
    ax.annotate("", xy=(5.6, 1.0), xytext=(1.9, 1.0),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.4))
    ax.annotate("w 抬：更细", xy=(2.3, 1.15), fontsize=7.0, color=RED, ha="left", va="bottom")
    ax.text(0.62, 7.2, "v*=3", fontsize=7.0, color=INK)
    ax.text(0.62, 2.2, "v*=1", fontsize=7.0, color=INK)
    ax.text(0.62, 0.72, "v*=0.3", fontsize=7.0, color=INK)
    ax.tick_params(labelsize=7.0)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.85, bottom=0.22, wspace=0.38)
    save(fig, "v2_fig_budget")


# ---------------------------------------------------------------- 12. layers (ch03 图3.3)
def fig_layers():
    """四层是同一张网的四个刻度：上行送参数，下行换可行集。版心 6.4 in。"""
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7.0); ax.axis("off")
    names = ["文明", "社会", "群体", "个人"]
    subs = ["中心、H、C 的水平", "Φ、分离成本、τ", "γ、A、ν", "q、v、T、λ、w"]
    ys = [5.15, 3.85, 2.55, 1.25]      # 上→下
    x0, w, h = 3.15, 3.55, 0.82
    for y, n, s in zip(ys, names, subs):
        ax.add_patch(FancyBboxPatch((x0, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.05",
                                    linewidth=1.1, edgecolor=INK, facecolor=CREAM))
        ax.text(x0 + 0.30, y + h / 2, n, ha="left", va="center", fontsize=9.2, color=INK)
        ax.text(x0 + 1.05, y + h / 2, s, ha="left", va="center", fontsize=6.9, color=GRAY)
    for i in range(3):
        y_low, y_high = ys[i + 1], ys[i]           # 下、上
        # 上行（右）：从下箱顶到上箱底
        ax.annotate("", xy=(x0 + w + 0.20, y_high), xytext=(x0 + w + 0.20, y_low + h),
                    arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5))
        # 下行（左）：从上箱底到下箱顶
        ax.annotate("", xy=(x0 - 0.20, y_low + h), xytext=(x0 - 0.20, y_high),
                    arrowprops=dict(arrowstyle="->", color=RED, lw=1.5))
    ax.text(x0 + w + 0.52, 3.4, "上行：送参数", fontsize=7.6, color=BLUE, rotation=90, va="center")
    ax.text(x0 - 0.52, 3.4, "下行：改可行集", fontsize=7.6, color=RED, rotation=90, va="center")
    ax.text(0.1, 6.95, "四层不是阶梯：每一段都可以回头；断一条，就退回成链（链没有迟滞）",
            fontsize=7.6, color=INK, va="top")
    ax.text(0.1, 0.10, "环增益乘积 < 1 就收敛（small-gain）；本书的数值检查：模型不产生混沌。C 级示意。",
            fontsize=6.9, color=GRAY)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.02)
    save(fig, "v2_fig_layers")
