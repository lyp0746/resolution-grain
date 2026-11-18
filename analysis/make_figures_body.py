#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""正文各章的图（一章一张）。

为什么要和 `make_figures.py` 分开
  `make_figures.py` 出的是全书统共十张"数据图"，由 `data/derived/` 直接画。
  正文每章还差一张图，其中一半是**由推导或判据决定的示意**，不来自数据文件。
  两类混在一个脚本里跑，重跑时会把已发布的数据图静默改掉（AGENTS §9 第 6 条）。

视觉语言与 `make_figures.py` 一致：300 dpi + SVG，C_MAIN=#1f3b57 / C_ALT=#b5651d / C_GREY=#8c8c8c。

纪律
  每张图的图注必须能回答"这是测量还是判决条件的画法"。示意图标 C 级；
  凡坐标轴上的数是构造出来的，轴标签里就写"示意"。
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
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


# ---------------------------------------------------------------- 第 11 章
def fig_c11_iso_cost() -> None:
    """同一份成本，两种拆法：加性预测"平"，分渠道预测"升"。

    设定（全部为示意，不是测量）：
      总成本 c = T + λ 固定为 2；
      横轴取 x = T / c ∈ (0.05, 0.95)，即"这份成本里有多少是时间付的"。
      加性：v = c / (2w)，w = 1 → v 恒为 1，与 x 无关。
      分渠道：时间定价决定可用采样次数（m ∝ 1/T），疲劳决定每次采样的噪声
              （σ² ∝ 1 + bλ），于是 v ∝ T·(1 + bλ)。取 c = 2、b = 1、w = 1。
    两条线只在 T = 1/b 处相交，交点右侧（时间很贵）分歧最大——那就是判决区。
    """
    c, b, w = 2.0, 1.0, 1.0
    x = np.linspace(0.05, 0.95, 400)
    T = x * c
    lam = c - T

    v_add = (T + lam) / (2 * w)          # 与 x 无关
    v_sep = 0.5 * T * (1 + b * lam)      # v ∝ T·(1+bλ)，常数取 0.5 使 x=c/2 处对齐

    fig, ax = plt.subplots(figsize=(5.0, 2.7))
    ax.plot(x, v_add, color=C_MAIN, lw=2.0, label="加性：T 与 λ 只以和出现")
    ax.plot(x, v_sep, color=C_ALT, lw=2.0, label="分渠道：时间买采样、疲劳买噪声")
    ax.axvline(0.5, color=C_GREY, lw=0.9, ls=":")
    ax.text(0.505, 0.06, "交点 T = 1/b", color=C_GREY, fontsize=7, va="bottom")

    # 判决区：两线之上与之下各一块
    ax.fill_between(x, v_add, v_sep, where=v_sep > v_add, color=C_ALT, alpha=0.10, lw=0)
    ax.fill_between(x, v_add, v_sep, where=v_sep < v_add, color=C_MAIN, alpha=0.10, lw=0)

    ax.set_xlabel("这份成本里，时间付的那一份（示意，总成本固定）")
    ax.set_ylabel("分辨率 v（示意）")
    ax.set_ylim(0, 1.6)
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    ax.set_title("同一份成本，两种拆法：一条线说不动，一条线说会动", fontsize=9, loc="left")
    save(fig, "c11_iso_cost")




# ---------------------------------------------------------------- 第 12 章
def fig_c12_arrows() -> None:
    """三个箭头换得到分辨率，一个箭头换不到。

    v* = (T+λ)/(2w) ⇒ 在 (成本, 利害) 平面上，等分辨率线是过原点的直线 w = (T+λ)/(2v)。
    往上（w↑）与往左（T+λ↓）都跨过等值线；沿等值线走（"下决心"）什么也不变。
    """
    c = np.linspace(0, 10, 200)
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    for v, lab in [(0.5, "v=0.5 粗"), (1.0, "v=1"), (2.0, "v=2 细")]:
        ax.plot(c, c / (2 * v), color=C_GREY, lw=0.9, ls="--")
        ax.text(9.4, 9.4 / (2 * v), lab, fontsize=6.5, color=C_GREY, va="bottom", ha="right")

    arrow = dict(arrowstyle="-|>", lw=1.6, shrinkA=0, shrinkB=0)
    # w↑：从 (3,2) 到 (3,6.5)，跨过 v=1 与 v=0.5 两条线
    ax.annotate("", xy=(3, 6.6), xytext=(3, 2.0), arrowprops=dict(color=C_MAIN, **arrow))
    ax.text(2.8, 4.6, "抬高利害 w↑\n（设后果、找见证、改用途）", fontsize=7, color=C_MAIN,
            va="center", ha="right")
    # 成本↓：从 (7,3) 到 (3.2,3)
    ax.annotate("", xy=(3.1, 3), xytext=(7.0, 3), arrowprops=dict(color=C_ALT, **arrow))
    ax.text(5.1, 3.35, "压低成本 T+λ↓（给时间、先睡）", fontsize=7, color=C_ALT, ha="center")
    # 沿等值线：从 (2,2) 到 (6.4,6.4)（正好在 v=0.5 那条线上）
    ax.annotate("", xy=(8.2, 8.2), xytext=(4.6, 4.6), arrowprops=dict(color="#b03a2e", **arrow))
    ax.text(5.4, 6.9, "“更仔细”这个决心：\n沿等值线走，v 不变", fontsize=7, color="#b03a2e",
            ha="left", va="bottom")

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel("成本：T + λ（示意）")
    ax.set_ylabel("利害：w（示意）")
    ax.set_title("三条路跨过等分辨率线，一条路走在线上", fontsize=9, loc="left")
    save(fig, "c12_arrows")


# ---------------------------------------------------------------- 第 9 章
def fig_c09_axes() -> None:
    """峰位与峰宽在同一样本里几乎不相关——两根轴不是一个轴。

    数据：data/derived/grad_2sxfp.csv（他人公开数据，133 人，我们只做拟合）。
    注意两处删失：v 上限 100、mu 边界 0.5/7.5。图上用空心点标出，不计入相关系数之外的任何主张。
    """
    import pandas as pd

    d = pd.read_csv(ROOT / "data" / "derived" / "grad_2sxfp.csv", encoding="utf-8-sig").dropna(subset=["mu", "v"])
    d = d[(d.v > 0)]
    r = d[["mu", "v"]].corr().iloc[0, 1]
    cen = (d.v >= 99) | (d.mu <= 0.51) | (d.mu >= 7.49)
    fig, ax = plt.subplots(figsize=(4.8, 2.9))
    ax.scatter(d.mu[~cen], np.log10(d.v[~cen]), s=16, color=C_MAIN, alpha=0.7, lw=0, label="个体拟合值")
    ax.scatter(d.mu[cen], np.log10(d.v[cen]), s=22, facecolor="none", edgecolor=C_ALT, lw=0.9,
               label="触到拟合边界（删失）")
    b, a = np.polyfit(d.mu, np.log10(d.v), 1)
    xs = np.linspace(d.mu.min(), d.mu.max(), 50)
    ax.plot(xs, a + b * xs, color=C_ALT, lw=1.4, ls="--", label=f"拟合线（斜率 {b:+.2f}）")
    ax.set_xlabel("峰位 μ（刺激刻度）")
    ax.set_ylabel("峰宽 v（对数轴）")
    ax.set_title(f"峰位与峰宽：r = {r:+.2f}，n = {len(d)}", fontsize=9, loc="left")
    ax.set_ylim(-1.3, 2.3)
    ax.legend(frameon=False, fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.24))
    save(fig, "c09_axes")


# ---------------------------------------------------------------- 第 10 章
def fig_c10_age_edu() -> None:
    """年龄效应在教育（μ 的粗代理）进来之后缩水多少。"""
    p = ROOT / "data" / "derived" / "ess8_age_vs_edu.json"
    if not p.exists():
        return
    j = json.loads(p.read_text(encoding="utf-8"))
    keys = [("trust", "人际信任"), ("gender_egal", "性别平等观")]
    fig, ax = plt.subplots(figsize=(5.2, 2.7))
    x = np.arange(len(keys))
    w = 0.26
    alone = [j[k]["age_coef_std_alone"] for k, _ in keys]
    with_edu = [j[k]["age_coef_std_with_edu"] for k, _ in keys]
    edu = [j[k]["edu_coef_std_with_age"] for k, _ in keys]
    ax.bar(x - w, alone, w, color=C_GREY, label="只放年龄")
    ax.bar(x, with_edu, w, color=C_MAIN, label="年龄 + 受教育年限")
    ax.bar(x + w, edu, w, color=C_ALT, label="受教育年限本身")
    ax.axhline(0, color="black", lw=0.8)
    for xi, (a_, b_, c_) in enumerate(zip(alone, with_edu, edu)):
        ax.text(xi - w, a_ + (0.006 if a_ >= 0 else -0.006), f"{a_:+.3f}", ha="center",
                fontsize=6.5, va="bottom" if a_ >= 0 else "top")
        if b_ >= 0.01:
            ax.text(xi, b_ + 0.006, f"{b_:+.3f}", ha="center", fontsize=6.5, va="bottom")
        ax.text(xi + w, c_ + 0.006, f"{c_:+.3f}", ha="center", fontsize=6.5, va="bottom")
    ax.annotate("年龄 −0.044 → −0.028：缩 36%", xy=(1, -0.028), xytext=(1, -0.09), ha="center",
                fontsize=7, color=C_MAIN, arrowprops=dict(arrowstyle="->", lw=0.8, color=C_MAIN))
    ax.set_xticks(x)
    ax.set_xticklabels([n for _, n in keys])
    ax.set_ylabel("标准化系数")
    ax.set_ylim(-0.105, 0.26)
    ax.legend(frameon=False, fontsize=7, ncol=3, loc="upper left")
    ax.set_title("ESS 第 8 轮（n≈4.4 万）：年龄的效应里，有一块是教育", fontsize=9, loc="left")
    save(fig, "c10_age_edu")


# ---------------------------------------------------------------- 第 13 章
def fig_c13_labels() -> None:
    """标签不是慢慢变多，是成批进来的：三个词在六年里的密度（每万字）。

    数据：data/derived/rmrb_daily.csv（1940 个出版日，2021-01 至 2026-04）。
    只是一个字段、一家报纸——它测的是编辑议程，不是社会现象（见第 14 章的反例段）。
    """
    import pandas as pd

    d = pd.read_csv(ROOT / "data" / "derived" / "rmrb_daily.csv", dtype={"date": str})
    d["year"] = d["date"].str[:4].astype(int)
    g = d.groupby("year").agg(chars=("chars", "sum"), 摆拍=("摆拍", "sum"),
                              剧本=("剧本", "sum"), 谣言=("谣言", "sum"))
    fig, ax = plt.subplots(figsize=(5.0, 2.6))
    for col, c, lab in [("剧本", C_MAIN, "剧本"), ("谣言", C_GREY, "谣言"), ("摆拍", C_ALT, "摆拍")]:
        y = g[col] / g["chars"] * 10000
        ax.plot(g.index, y, "o-", color=c, lw=1.6, ms=4, label=lab)
    ax.set_xticks(list(g.index))
    ax.set_xlabel("年（《人民日报》正文，2026 年只到 4 月）")
    ax.set_ylabel("每万字出现次数")
    ax.legend(frameon=False, fontsize=7)
    ax.set_title("一个词可以一年翻倍：标签是成批进来的", fontsize=9, loc="left")
    save(fig, "c13_labels")


# ---------------------------------------------------------------- 第 14 章
def fig_c14_field() -> None:
    """同一个词，换一个字段就换一个世界：密度差 27 倍，精度差 8 倍。

    数据：data/derived/label_density.csv（三份语料，"摆拍"的原始命中与锚定命中）。
    左：密度（每万条 / 每万字，对数轴）；右：精度代理＝锚定命中 / 原始命中。
    """
    import pandas as pd

    d = pd.read_csv(ROOT / "data" / "derived" / "label_density.csv", encoding="utf-8-sig")
    d = d[d.corpus != "人民日报正文 2024"]
    order = ["微博热搜标题 2020—21", "人民日报正文 2022—2025", "微博正文（热搜话题，2026-11 抽样）"]
    lab = ["热搜标题\n(7.6 万条)", "报纸正文\n(9.8 万篇)", "微博正文\n(1.2 万条)"]
    d = d.set_index("corpus").loc[order]
    dens = d["raw_摆拍"] / d["n"] * 100
    prec = d["anch_摆拍"] / d["raw_摆拍"] * 100

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.6))
    ax = axes[0]
    bars = ax.bar(lab, dens, color=[C_GREY, C_MAIN, C_ALT], width=0.55)
    ax.set_yscale("log")
    ax.set_ylabel("密度（%，对数轴）")
    for b, v in zip(bars, dens):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.15, f"{v:.3f}%", ha="center", fontsize=7)
    ax.set_ylim(dens.min() * 0.4, dens.max() * 6)
    ax.set_title("密度：差 27 倍", fontsize=8.5, loc="left")

    ax = axes[1]
    bars = ax.bar(lab, prec, color=[C_GREY, C_MAIN, C_ALT], width=0.55)
    ax.set_ylabel("精度代理（%）")
    ax.set_ylim(0, 118)
    for b, v in zip(bars, prec):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f}%", ha="center", fontsize=7)
    ax.set_title("精度：差 8 倍", fontsize=8.5, loc="left")
    fig.suptitle("同一个词“摆拍”，换一个字段就换一个世界", fontsize=9, x=0.01, ha="left")
    save(fig, "c14_field")


# ---------------------------------------------------------------- 第 27 章
def fig_c27_chain() -> None:
    """七环链：评价权 → 代价外置 → 手里的 w → 分辨率 → 档内尺度 → 选拔质量 → 信任，回到评价权。

    不是测量，是一条推导链的画法。第六环回到第一环的虚线，是这条链之所以是"螺旋"而不是"斜坡"的原因。
    """
    from matplotlib.patches import FancyBboxPatch

    nodes = ["评价权\nΦ 上升", "代价外置\nτ 下降", "手里的 w\nw 下降", "分辨率\nv 变大",
             "档内尺度\nδ 变大", "选拔质量\nq 下降", "制度信任\nθ 下降"]
    n, step, w, h = len(nodes), 1.32, 1.04, 0.58
    fig, ax = plt.subplots(figsize=(7.6, 2.1))
    ax.set_xlim(0.0, n * step)
    ax.set_ylim(0.0, 1.55)
    ax.axis("off")
    cx = []
    for i, label in enumerate(nodes):
        x = 0.10 + i * step
        cx.append(x + w / 2)
        hl = (i == 1)
        ax.add_patch(FancyBboxPatch((x, 0.32), w, h, boxstyle="round,pad=0.01,rounding_size=0.07",
                                    fc="#f7e8da" if hl else "#eef1f5",
                                    ec=C_ALT if hl else C_MAIN, lw=1.3))
        ax.text(x + w / 2, 0.60, label, ha="center", va="center", fontsize=8,
                color=C_ALT if hl else C_MAIN)
        if i:
            ax.annotate("", xy=(x - 0.06, 0.60), xytext=(x - step + w + 0.06, 0.60),
                        arrowprops=dict(arrowstyle="-|>", lw=1.5, color=C_MAIN,
                                        shrinkA=0, shrinkB=0))
    ax.text(cx[1], 0.16, "第六条（P6）只在这一环上场", ha="center", fontsize=7, color=C_ALT)
    # 回环
    ax.plot([cx[-1], cx[-1]], [0.88, 1.12], ls="--", lw=1.1, color=C_GREY)
    ax.plot([cx[0], cx[-1]], [1.12, 1.12], ls="--", lw=1.1, color=C_GREY)
    ax.annotate("", xy=(cx[0], 0.90), xytext=(cx[0], 1.12),
                arrowprops=dict(arrowstyle="-|>", lw=1.1, color=C_GREY, ls="--"))
    ax.text((cx[0] + cx[-1]) / 2, 1.22, "信任下降 → 更依赖粗判 → 评价权更集中（闭环）",
            ha="center", fontsize=7, color=C_GREY)
    ax.set_title("七环链：一个文明怎么变糙的最小写法", fontsize=9, loc="left")
    save(fig, "c27_chain")


# ---------------------------------------------------------------- 第 15 章
def fig_c15_capacity() -> None:
    """固定容量的算术：份额越小，"翻倍"需要的绝对增量越少——所以"翻倍"根本不是新闻。

    左：榜长 K=50，各类份额 s 翻倍需要多占几个位置（Δk = s·K）。
    右：榜内份额恒和为 100%（只能重分配）与平台总量可以扩张（可以重分配，也可以都涨）。
    两幅都是算术示意，不含任何实测数据。
    """
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.5))
    K = 50
    ax = axes[0]
    shares = np.array([0.5, 1, 2, 5, 10, 20])
    dk = shares / 100 * K
    bars = ax.bar([f"{s:g}%" for s in shares], dk, color=C_MAIN, width=0.6)
    ax.set_ylabel("翻倍需要多占的位置数")
    for b, v in zip(bars, dk):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.15, f"{v:g}", ha="center", fontsize=7.5)
    ax.set_ylim(0, max(dk) + 2)
    ax.set_xlabel("这类内容在榜上的份额（榜长 50）")
    ax.set_title("份额越小，“翻倍”越不算事", fontsize=8.5, loc="left")

    ax = axes[1]
    ax.set_xlim(0, 3.2)
    ax.set_ylim(0, 1.35)
    ax.axis("off")
    # 榜内：固定高度
    ax.add_patch(plt.Rectangle((0.15, 0.1), 0.7, 0.9, fc="#eef1f5", ec=C_MAIN, lw=1.2))
    ax.add_patch(plt.Rectangle((0.15, 0.62), 0.7, 0.38, fc=C_ALT, alpha=0.35, ec="none"))
    ax.add_patch(plt.Rectangle((0.15, 0.1), 0.7, 0.52, fc=C_MAIN, alpha=0.15, ec="none"))
    ax.text(0.5, 0.81, "某类", ha="center", fontsize=7, color=C_ALT)
    ax.text(0.5, 0.3, "其他", ha="center", fontsize=7, color=C_MAIN)
    ax.text(0.5, 1.02, "榜内：高度固定", ha="center", fontsize=7.5, color=C_MAIN)
    ax.text(0.5, 0.02, "高度固定 → 只能重新分配", ha="center", fontsize=7, color=C_GREY)
    # 平台间：高度可变
    ax.add_patch(plt.Rectangle((1.8, 0.1), 0.5, 0.55, fc=C_MAIN, alpha=0.25, ec=C_MAIN, lw=1.2))
    ax.add_patch(plt.Rectangle((2.4, 0.1), 0.5, 0.95, fc=C_MAIN, alpha=0.25, ec=C_MAIN, lw=1.2))
    ax.text(2.05, 0.02, "之前", ha="center", fontsize=7, color=C_MAIN)
    ax.text(2.65, 0.02, "之后", ha="center", fontsize=7, color=C_MAIN)
    ax.text(2.35, 1.02, "平台间：高度可变 → 可以都涨", ha="center", fontsize=7.5, color=C_MAIN)
    ax.set_title("两种“零和”，不是一件事", fontsize=8.5, loc="left")
    fig.suptitle("固定容量的算术：榜内是除法，榜外不是", fontsize=9, x=0.01, ha="left")
    save(fig, "c15_capacity")


# ---------------------------------------------------------------- 第 16 章
def fig_c16_phase() -> None:
    """γ–δ 相图：更不准的码只有在 γ > δ 时才活得下来。

    左：分界线 γ=δ。线上方是双稳（差的码可以被维持），下方是单稳（好的码全局胜出）。
    右：从众率随准确度差 δ 下降，而斜率取决于 γ——两条线不平行，这是可查的差别。
    两个面板都是推理性示意，不含实测数据。
    """
    d = np.linspace(0, 3, 200)
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.7))

    ax = axes[0]
    ax.fill_between(d, d, 3.0, color=C_ALT, alpha=0.14, lw=0)
    ax.fill_between(d, 0.0, d, color=C_MAIN, alpha=0.10, lw=0)
    ax.plot(d, d, color=C_MAIN, lw=1.6)
    ax.text(2.35, 2.55, "双稳：更不准的码\n可以被维持", fontsize=7.5, color=C_ALT, ha="center")
    ax.text(2.05, 0.45, "单稳：准的那个码\n全局胜出", fontsize=7.5, color=C_MAIN, ha="center")
    ax.text(1.0, 1.06, "γ = δ", fontsize=7, color=C_MAIN)
    ax.set_xlabel("准确度差 δ")
    ax.set_ylabel("一致性代价 γ")
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3)
    ax.set_title("分界线：γ = δ", fontsize=8.5, loc="left")

    ax = axes[1]
    for g, c, lab in [(2.0, C_ALT, "γ 高（偏离很贵）"), (0.9, C_MAIN, "γ 低")]:
        ax.plot(d, 1 / (1 + np.exp((d - g) * 3.2)), color=c, lw=1.6, label=lab)
    ax.set_xlabel("准确度差 δ（正确答案与错误答案差多远）")
    ax.set_ylabel("从众率（示意）")
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=False, fontsize=7)
    ax.set_title("两条线的斜率不同——这可查", fontsize=8.5, loc="left")
    fig.suptitle("更差的码为什么能活：γ > δ 那一侧", fontsize=9, x=0.01, ha="left")
    save(fig, "c16_phase")


# ---------------------------------------------------------------- 第 17 章
def fig_c17_theta_tau() -> None:
    """θ 与 τ 的等值线：什么时候“信”比“核实”便宜。

    判据：信 的期望损失 = θ·D；核实的成本 = c·τ。
    于是 θ* = c·τ / D 是一条过原点的直线：线**之上**核实（θ 高 ⇒ 错得疼 ⇒ 去查），
    线**之下**信（θ 低 ⇒ 赌得起）。两条实线对应两个 D。
    虚线是同一判据在“核实变便宜／变贵”之后的界线：c 小 ⇒ 界线变平 ⇒ 核实区扩大。
    """
    tau = np.linspace(0, 10, 200)
    fig, ax = plt.subplots(figsize=(5.2, 2.9))
    for D, c, lab in [(2.0, C_MAIN, "D 大（错得疼）"), (1.0, C_ALT, "D 小")]:
        ax.plot(tau, tau / D, color=c, lw=1.6, label=lab)
    ax.plot(tau, tau / 6.0, color=C_GREY, lw=1.0, ls="--")
    ax.plot(tau, np.clip(tau / 0.55, 0, 10), color=C_GREY, lw=1.0, ls=":")
    ax.fill_between(tau, tau / 1.0, 10, color=C_MAIN, alpha=0.07, lw=0)
    ax.text(1.0, 8.6, "线之上：核实\nθ 高，错得疼，去查", fontsize=7.5, color=C_MAIN)
    ax.text(6.6, 1.0, "线之下：信\nθ 低，赌得起", fontsize=7.5, color=C_ALT)
    ax.text(8.4, 3.0, "核实更便宜\n（界线变平）", fontsize=6.8, color=C_GREY, ha="center")
    ax.text(8.4, 8.2, "核实更贵\n（界线变陡）", fontsize=6.8, color=C_GREY, ha="center")
    ax.set_xlabel("核实延迟 τ（要多久才知道真假）")
    ax.set_ylabel("θ（愿意把别人的错算进自己的账）")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.legend(frameon=False, fontsize=7, loc="center left")
    ax.set_title("信还是查：θ 与 τ 的等值线", fontsize=9, loc="left")
    save(fig, "c17_theta_tau")


# ---------------------------------------------------------------- 第 20 章
def fig_c20_hysteresis() -> None:
    """迟滞：进去与出来的临界不是同一个数。

    左：两条稳定分支。旧码那一支一直撑到 D=6.0 才断；新码那一支要 D 掉到 3.6 才断。
        中间 3.6—6.0 是双稳带（两个状态都稳），带宽＝换码成本。
    右：双稳的景观——两个坑一道坎；坎的高度就是换码成本。
    两幅都是推理性示意，不含实测数据。
    """
    enter, exit_ = 6.0, 3.6
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.7))

    ax = axes[0]
    ax.plot([0, enter], [0, 0], color=C_MAIN, lw=2.0)          # 旧码分支
    ax.plot([enter, enter], [0, 1], color=C_MAIN, lw=1.4, ls=":")
    ax.plot([exit_, 10], [1, 1], color=C_ALT, lw=2.0)          # 新码分支
    ax.plot([exit_, exit_], [1, 0], color=C_ALT, lw=1.4, ls=":")
    ax.axvspan(exit_, enter, color=C_GREY, alpha=0.13, lw=0)
    ax.annotate("", xy=(enter - 0.15, 0.12), xytext=(3.9, 0.12),
                arrowprops=dict(arrowstyle="-|>", lw=1.2, color=C_MAIN))
    ax.text(4.9, 0.26, "去程：撑到 D=6 才换", fontsize=6.8, color=C_MAIN, ha="center")
    ax.annotate("", xy=(exit_ + 0.15, 0.88), xytext=(5.9, 0.88),
                arrowprops=dict(arrowstyle="-|>", lw=1.2, color=C_ALT))
    ax.text(4.9, 0.72, "回程：跌到 D=3.6 才换回来", fontsize=6.8, color=C_ALT, ha="center")
    ax.text(4.8, -0.18, "带内两个状态都稳（双稳区）", fontsize=6.8, color=C_GREY, ha="center")
    ax.set_xlabel("累积失真 D")
    ax.set_ylabel("采用新码的比例")
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.28, 1.15)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["旧码", "新码"])
    ax.set_title("同一个系统，两条临界", fontsize=8.5, loc="left")

    ax = axes[1]
    x = np.linspace(-2.8, 2.8, 400)
    V = 0.5 * (x ** 2 - 1) ** 2 + 0.55 * np.exp(-x ** 2 * 2.2)
    ax.plot(x, V, color=C_MAIN, lw=1.6)
    ax.fill_between(x, 0, V, color=C_MAIN, alpha=0.07, lw=0)
    ax.text(-1.0, -0.20, "旧码", ha="center", fontsize=8, color=C_MAIN)
    ax.text(1.0, -0.20, "新码", ha="center", fontsize=8, color=C_MAIN)
    ax.annotate("坎的高度\n＝换码成本", xy=(0, 0.56), xytext=(-2.4, 1.55),
                fontsize=7, color=C_ALT, ha="left",
                arrowprops=dict(arrowstyle="->", lw=0.9, color=C_ALT))
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-0.3, 2.1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_xlabel("码的状态（示意）")
    ax.set_ylabel("代价")
    ax.set_title("双稳：两个坑，一道坎", fontsize=8.5, loc="left")
    fig.suptitle("临界不是一条线，是一段带", fontsize=9, x=0.01, ha="left")
    save(fig, "c20_hysteresis")


# ---------------------------------------------------------------- 第 21 章
def fig_c21_periodization() -> None:
    """45 部分期方案：跨度越大，段越长（r=+0.88），而斜率小于 1。

    数据：data/derived/periodization_test.csv（45 部可算段长的方案，他人整理）。
    双对数轴：斜率 0.72 = 次比例；若严格成比例，斜率应当为 1（虚线）。
    """
    import pandas as pd

    d = pd.read_csv(ROOT / "data" / "derived" / "periodization_test.csv", encoding="utf-8-sig").dropna()
    x, y = d.span_years.values, d.seg_years.values
    r = np.corrcoef(np.log10(x), np.log10(y))[0, 1]
    b, a = np.polyfit(np.log10(x), np.log10(y), 1)

    fig, ax = plt.subplots(figsize=(4.9, 2.9))
    mark = {"survey": ("o", C_MAIN, "通史"), "reference": ("s", C_ALT, "工具书／条目"),
            "curriculum": ("^", C_GREY, "课程框架"), "chronicle": ("D", "#7a8b99", "编年"),
            "argument": ("*", "#b03a2e", "论辩")}
    for g, (m, c, lab) in mark.items():
        sub = d[d.genre == g]
        if len(sub):
            ax.scatter(sub.span_years, sub.seg_years, marker=m, s=26, color=c, alpha=0.85,
                       lw=0, label=f"{lab}（n={len(sub)}）")
    xs = np.logspace(np.log10(x.min()), np.log10(x.max()), 50)
    ax.plot(xs, 10 ** a * xs ** 1.0, color=C_GREY, lw=0.9, ls=":", label="严格成比例（斜率 1）")
    ax.plot(xs, 10 ** a * xs ** b, color="#b03a2e", lw=1.6, label=f"拟合（斜率 {b:.2f}）")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("回望跨度（年，对数轴）")
    ax.set_ylabel("段长（年，对数轴）")
    ax.set_title(f"跨度越大，段越长：r = {r:+.2f}，n = {len(d)}", fontsize=9, loc="left")
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    save(fig, "c21_periodization")


# ---------------------------------------------------------------- 第 23 章
def fig_c23_distance() -> None:
    """同一批事件，不同语言版本的结构距离（Jaccard 距离，越高越远）。

    数据：data/derived/narrative_distance.csv（3 个事件 × 6 对语言，共 18 对）。
    三件事一眼可见：甲午那一组跨度极大（0.82—0.98）；朝鲜战争与蒙古帝国挤在 0.91—0.95；
    而"争议不是均匀的"这句话，就是这两点的差。
    """
    import pandas as pd

    d = pd.read_csv(ROOT / "data" / "derived" / "narrative_distance.csv", encoding="utf-8-sig")
    d = d.sort_values("distance", ascending=True).reset_index(drop=True)
    color = {"甲午战争": C_ALT, "朝鲜战争": C_MAIN, "蒙古帝国": C_GREY}
    fig, ax = plt.subplots(figsize=(5.4, 3.4))
    labels = [f"{r.event[:2]} {r.a}–{r.b}" for r in d.itertuples()]
    bars = ax.barh(labels, d.distance, color=[color[e] for e in d.event], height=0.72)
    for b, v in zip(bars, d.distance):
        ax.text(v + 0.006, b.get_y() + b.get_height() / 2, f"{v:.2f}", va="center", fontsize=6.5)
    ax.set_xlim(0.75, 1.02)
    ax.set_xlabel("结构距离（1 − Jaccard 重合）")
    ax.tick_params(axis="y", labelsize=7)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (C_ALT, C_MAIN, C_GREY)]
    ax.legend(handles, ["甲午战争", "朝鲜战争", "蒙古帝国"], frameon=False, fontsize=7,
              loc="lower right")
    ax.set_title("争议不是均匀的：一个事件拉出大跨度，另两个挤成窄带", fontsize=9, loc="left")
    save(fig, "c23_distance")


# ---------------------------------------------------------------- 第 24 章
def fig_c24_tree() -> None:
    """六型的判别顺序：先问"哪一只价格动了"，再一路问下去。

    判据图，不是软件流程图。顺序本身是主张：**必须先填触发条件，再填型**。
    "是"向左给出一个型；"否"向下进下一问。
    """
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#eef1f5", ec=C_MAIN, fs=7.4):
        ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.1))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)

    gates = [
        ("① 触发条件是什么？哪一只价格动了", "（先填这一格，填不出就不是分析）", None),
        ("② 分辨率是否趋零？", "划分退化成 顺我／逆我", "崩塌"),
        ("③ 覆盖域缩了吗？", "只顾一件事，那件事仍看得细", "收窄"),
        ("④ 中心移了吗？", "同一种精细，围着新东西建", "重锚"),
        ("⑤ 码率与程序变多了吗？", "术语、分类、程序增厚", "加细"),
        ("⑥ 抬的是谁的换码成本？", "抬别人的＝换码；抬自己的＝自设成本", "换码／自设成本"),
    ]
    y = 9.0
    for i, (q, sub, ans) in enumerate(gates):
        box(4.2, y - 0.55, 5.4, 0.95, f"{q}\n{sub}", fs=6.8 if i == 0 else 7.2)
        if ans:
            box(0.4, y - 0.55, 3.2, 0.95, ans, fc="#f6e6d8", ec=C_ALT, fs=8)
            ax.annotate("", xy=(3.6, y - 0.08), xytext=(4.2, y - 0.08),
                        arrowprops=dict(arrowstyle="-|>", lw=1.0, color=C_GREY))
            ax.text(3.9, y + 0.02, "是", fontsize=6.2, color=C_GREY, ha="center")
        if i < len(gates) - 1:
            ax.annotate("", xy=(6.9, y - 1.35), xytext=(6.9, y - 0.62),
                        arrowprops=dict(arrowstyle="-|>", lw=1.0, color=C_GREY))
            ax.text(7.05, y - 0.98, "否", fontsize=6.2, color=C_GREY, va="center")
        y -= 1.55
    ax.set_title("先填触发条件，再填型（第①格不可跳过）", fontsize=8.5, loc="left")
    save(fig, "c24_tree")


# ---------------------------------------------------------------- 第 7 章
def fig_c07_ratedistortion() -> None:
    """同一条率—失真曲线，两种读法。

    左：R(D)=½log2(σ²/D)（高斯信源），等成本线 w·D+c·R，切点 D*=c/(2w)。
    右：把同一次最优换成"规则的读法"——D* 对应一个可数的块数 k*=2^{R*}。
    这条曲线是教科书内容（Shannon 1948）；本图只是把它与本书的读法并置。
    """
    sig2, c, w = 1.0, 2.0, 4.0
    D = np.logspace(-2.2, np.log10(sig2) - 0.02, 400)
    R = 0.5 * np.log2(sig2 / D)
    Dstar = c / (2 * w)
    Rstar = 0.5 * np.log2(sig2 / Dstar)

    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.7))
    ax = axes[0]
    ax.plot(R, D, color=C_MAIN, lw=1.8)
    for cost, ls in [(2.6, ":"), (3.4, "--")]:
        ax.plot(R, (cost - c * R) / w, color=C_GREY, lw=0.9, ls=ls)
    ax.plot([Rstar], [Dstar], "o", color=C_ALT, ms=6, zorder=5)
    ax.annotate(f"最优：D* = c/(2w)\n= {Dstar:.2f}", xy=(Rstar, Dstar), xytext=(Rstar + 1.1, Dstar * 2.2),
                fontsize=7, color=C_ALT,
                arrowprops=dict(arrowstyle="->", lw=0.9, color=C_ALT))
    ax.set_xlabel("码率 R（比特）")
    ax.set_ylabel("失真 D")
    ax.set_xlim(0, max(R) * 1.02)
    ax.set_ylim(0, sig2)
    ax.set_title("原读法：信号要多少比特", fontsize=8.5, loc="left")

    ax = axes[1]
    ax.plot(R, 2 ** R, color=C_ALT, lw=1.8)
    ax.plot([Rstar], [2 ** Rstar], "o", color=C_MAIN, ms=6, zorder=5)
    ax.annotate(f"同一个最优，换成一个可数的数\nk* = 2^{{R*}} = {2 ** Rstar:.1f} 块",
                xy=(Rstar, 2 ** Rstar), xytext=(Rstar + 0.9, 2 ** Rstar * 0.42),
                fontsize=7, color=C_MAIN,
                arrowprops=dict(arrowstyle="->", lw=0.9, color=C_MAIN))
    ax.set_yscale("log")
    ax.set_xlabel("码率 R（比特）")
    ax.set_ylabel("块数 k = 2^R（对数轴）")
    ax.set_xlim(0, max(R) * 1.02)
    ax.set_title("本书的读法：规则有几块", fontsize=8.5, loc="left")
    fig.suptitle("同一条曲线，两种读法：一个连续的量，一个可数的量", fontsize=9, x=0.01, ha="left")
    save(fig, "c07_ratedistortion")


# ---------------------------------------------------------------- 第 8 章
def fig_c08_checks() -> None:
    """两次认真检验，两个面板：它们到底支持了什么。

    左：Shepard 一系的复算（data/derived/shepard_check.csv）——个体码宽异质性 k 越大，
        群体泛化梯度的尾指数 b 越接近指数尾（b→1 是指数尾，b=2 是高斯尾）。
    右：分期粒度（data/derived/periodization_test.csv）——回望跨度越大段越长，r≈+0.88。
    两幅都是"观测到的方向"与"预测的方向"并置，不是拟合优度的展示。
    """
    import pandas as pd

    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.8))

    d = pd.read_csv(ROOT / "data" / "derived" / "shepard_check.csv", encoding="utf-8-sig")
    ax = axes[0]
    ax.plot(d.k_gamma, d.b_shape, "o-", color=C_MAIN, lw=1.5, ms=5)
    ax.axhline(1.0, color=C_ALT, lw=1.0, ls="--")
    ax.axhline(2.0, color=C_GREY, lw=1.0, ls=":")
    ax.text(d.k_gamma.min(), 1.03, "指数尾（预测方向）", fontsize=6.5, color=C_ALT, va="bottom")
    ax.text(d.k_gamma.min(), 1.94, "高斯尾（单码预测）", fontsize=6.5, color=C_GREY, va="bottom")
    ax.set_xlabel("核宽分布的异质性 k（越大＝越同质）")
    ax.set_ylabel("泛化梯度的尾指数 b")
    ax.set_ylim(0.9, 2.1)
    ax.set_title(f"检验一：方向对，斜率不足（n={int(d.n.iloc[0])} 起）", fontsize=8.5, loc="left")

    p2 = pd.read_csv(ROOT / "data" / "derived" / "periodization_test.csv", encoding="utf-8-sig").dropna()
    ax = axes[1]
    ax.scatter(p2.span_years, p2.seg_years, s=18, color=C_MAIN, alpha=0.75, lw=0, label="45 部方案")
    b, a = np.polyfit(np.log10(p2.span_years), np.log10(p2.seg_years), 1)
    r = np.corrcoef(np.log10(p2.span_years), np.log10(p2.seg_years))[0, 1]
    xs = np.logspace(np.log10(p2.span_years.min()), np.log10(p2.span_years.max()), 40)
    ax.plot(xs, 10 ** a * xs ** b, color=C_ALT, lw=1.4, label=f"拟合（斜率 {b:.2f}）")
    ax.plot(xs, 10 ** a * xs, color=C_GREY, lw=1.0, ls=":", label="严格成比例")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("回望跨度（年，对数轴）")
    ax.set_ylabel("段长（年，对数轴）")
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    ax.set_title(f"检验二：成立且强（r={r:+.2f}）", fontsize=8.5, loc="left")

    fig.suptitle("两次认真检验：一次弱支持，一次强支持", fontsize=9, x=0.01, ha="left")
    save(fig, "c08_checks")


# ---------------------------------------------------------------- 第 5 章
def fig_c05_levels() -> None:
    """一条泛函，三层读法；四个尺度，各有一条式子。

    左：同一个 F[P]，三种最小化——固定 P 求 q 得 v*；对 P 求极小得群体动力学；势垒被跨过得相变。
    右：个人→群体→社会→文明四级，各写它现在的式子；第三到第四级之间那一刀（Φ 与规则谱没有方程）画成缺口。
    两幅都是结构示意图，不含数据。
    """
    from matplotlib.patches import FancyBboxPatch

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))

    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.6, 8.1), 8.4, 1.2, boxstyle="round,pad=0.03,rounding_size=0.15",
                                fc="#eef1f5", ec=C_MAIN, lw=1.3))
    ax.text(4.8, 8.7, "一条泛函  F[P]（分辨率的分布）", ha="center", va="center", fontsize=8, color=C_MAIN)
    rows = [("固定 P，对 q 求极小", "→ 个体：v* 出现（第 3 章）"),
            ("对 P 求极小", "→ 群体：复制子（第 8 章、附录 A.3）"),
            ("势垒被跨过", "→ 相变：统一或分裂（第 20 章）")]
    for i, (op, res) in enumerate(rows):
        y = 6.0 - i * 2.0
        ax.annotate("", xy=(1.4, y + 0.45), xytext=(4.8, 7.95),
                    arrowprops=dict(arrowstyle="-|>", lw=0.9, color=C_GREY))
        ax.text(1.6, y, op, ha="left", va="center", fontsize=7.4, color=C_ALT)
        ax.text(5.0, y, res, ha="left", va="center", fontsize=7.2, color=C_MAIN)
    ax.text(4.8, 0.8, "三次最小化，不是三套理论", ha="center", fontsize=7.5, color=C_GREY)
    ax.set_title("① 三层读法", fontsize=8.5, loc="left")

    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    rows = [("文明", "规则谱漂移 ＋ 评价权 Φ", 8.2), ("社会", "平均在意 ／ 信任 θ ／ 标签读数", 6.1),
            ("群体", "泛函 ＋ 复制子 ＋ γ* = δ", 4.0), ("个人", "v* = (T+λ)/(2w)；D > C 才换码", 1.9)]
    for name, eq, y in rows:
        ax.add_patch(FancyBboxPatch((0.2, y - 0.7), 2.6, 1.4, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    fc="#eef1f5", ec=C_MAIN, lw=1.1))
        ax.text(1.5, y, name, ha="center", va="center", fontsize=8)
        ax.text(3.1, y, eq, ha="left", va="center", fontsize=6.8, color=C_MAIN)
    ax.plot([1.5, 1.5], [7.15, 7.55], color="#b03a2e", lw=2.0, ls=(0, (2, 2)))
    ax.text(3.1, 7.35, "缺口：Φ 与规则谱之间没有方程", fontsize=6.4, color="#b03a2e", va="center")
    ax.annotate("", xy=(1.5, 5.3), xytext=(1.5, 4.7),
                arrowprops=dict(arrowstyle="-|>", lw=0.9, color=C_GREY))
    ax.annotate("", xy=(1.5, 3.2), xytext=(1.5, 2.6),
                arrowprops=dict(arrowstyle="-|>", lw=0.9, color=C_GREY))
    ax.set_title("② 四个尺度：两层通，第三层一半，第四层断", fontsize=8.5, loc="left")

    fig.suptitle("一条泛函，四种场地", fontsize=9, x=0.01, ha="left")
    save(fig, "c05_levels")


# ---------------------------------------------------------------- 第 6 章
def fig_c06_two_outlets() -> None:
    """一份预算，两个出口：δ = Δ / 2^R 的几何。

    双对数平面上，等码率线是斜率 1 的直线：δ = Δ / 2^R。
    同一条线上，铺开（Δ 大）与加密（δ 小）只能此消彼长；换一条线才换得起预算。
    七个例子按"相对位置"摆放——**坐标是示意，只有相对位置有意义**。
    """
    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    D = np.logspace(-1, 2.2, 300)
    handles = []
    for R, lab in [(1, "R = 1 比特（两块）"), (4, "R = 4（十六块）"), (8, "R = 8（256 块）")]:
        h, = ax.plot(D, D / 2 ** R, color=C_GREY, lw=1.0, ls="--")
        handles.append((h, lab))
    ax.legend([h for h, _ in handles], [l for _, l in handles], frameon=False,
              fontsize=6.4, loc="lower right", handlelength=2.4)

    pts = [("概念拉伸", 60, 60 / 2 ** 2, C_ALT), ("标签", 0.8, 0.8 / 2 ** 0.6, C_ALT),
           ("分诊三级", 40, 40 / 2 ** 1.6, C_MAIN), ("十二平均律", 12, 12 / 2 ** 3.6, C_MAIN),
           ("规则（限速六十）", 3, 3 / 2 ** 6, C_MAIN), ("标准（合理注意）", 8, 8 / 2 ** 2, C_MAIN),
           ("词片", 1.6, 1.6 / 2 ** 5.2, C_ALT)]
    off = {"概念拉伸": (-8, -13), "分诊三级": (7, 4)}
    for name, d, dd, c in pts:
        ax.plot([d], [dd], "o", ms=6, color=c, zorder=5)
        dx, dy = off.get(name, (6, 5))
        ax.annotate(name, (d, dd), textcoords="offset points", xytext=(dx, dy), fontsize=6.6,
                    color=c, ha="right" if dx < 0 else "left")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("覆盖 Δ（能管多宽，示意）")
    ax.set_ylabel("档内刻度 δ（分多细，示意）")
    ax.set_xlim(0.5, 200)
    ax.set_ylim(1e-3, 60)
    ax.set_title("一份预算，两个出口：沿虚线只能此消彼长", fontsize=9, loc="left")
    save(fig, "c06_two_outlets")


# ---------------------------------------------------------------- 第 1 章
def fig_c01_age_vs_edu() -> None:
    """左：真的数（ESS8，年龄与教育各解释多少方差）；右：错的位置（把一列读成两列）。

    左：ΔR²，对数轴——0.00008 与 0.018 差 225 倍，线性轴上年龄那一根会消失。
    右：判据示意，不是数据。同一群点，按年龄切（竖线）时两团几乎重合；按处境切（斜线）才分开。
    """
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.7))

    ax = axes[0]
    vals = [8e-5, 1.82e-2]
    bars = ax.bar(["年龄", "受教育年限"], vals, color=[C_GREY, C_MAIN], width=0.5)
    ax.set_yscale("log")
    ax.set_ylim(2e-5, 8e-2)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.25, f"{v:.5f}".rstrip("0"), ha="center", fontsize=7.5)
    ax.set_ylabel("ΔR²（对数轴）")
    ax.set_title("真的数：差 225 倍（ESS8，n=43,852）", fontsize=8.5, loc="left")
    ax.text(1.0, 4.5e-5, "年龄那一根\n几乎贴着零", ha="center", fontsize=6.8, color=C_GREY)

    ax = axes[1]
    rs = np.random.RandomState(3)
    x = rs.normal(0, 1.0, 120)
    y = 0.55 * x + rs.normal(0, 0.85, 120)
    age = (x + rs.normal(0, 2.4, 120) > 0)
    ax.scatter(x[age], y[age], s=14, color=C_ALT, alpha=0.75, lw=0, label="按“年轻”划的一半")
    ax.scatter(x[~age], y[~age], s=14, color=C_MAIN, alpha=0.55, lw=0, label="按“年长”划的一半")
    ax.axvline(0, color=C_GREY, lw=0.9, ls=":")
    ax.plot([-2.4, 2.4], [-1.3, 1.3], color="#b03a2e", lw=1.3, ls="--")
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-2.6, 2.6)
    ax.set_xlabel("处境之一（示意）")
    ax.set_ylabel("处境之二（示意）")
    ax.legend(frameon=False, fontsize=6.4, loc="lower right")
    ax.set_title("错的位置：竖线切不开，斜线才切得开", fontsize=8.5, loc="left")

    fig.suptitle("年龄解释不了它——因为切的方向错了", fontsize=9, x=0.01, ha="left")
    save(fig, "c01_age_vs_edu")


# ---------------------------------------------------------------- 第 2 章
def fig_c02_four_cells() -> None:
    """四个格：环境宽度 × 预算松紧。不是四个抽屉，是两条轴上的四个位置。

    左：2×2，两条轴都是连续量，"四个格"只是四个区域；"预算紧"那一行被标出，
        因为原来说法的两个类型正是这一行的两个格。
    右：同一个人在两种处境之间的移动——两个月里看不出（像特质），五年里看得出来（是处境）。
    """
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))

    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.add_patch(plt.Rectangle((1.2, 1.0), 7.6, 8.0, fc="#f4f6f8", ec=C_GREY, lw=0.8))
    ax.plot([1.2, 8.8], [5.0, 5.0], color=C_GREY, lw=0.8)
    ax.plot([5.0, 5.0], [1.0, 9.0], color=C_GREY, lw=0.8)
    cells = [("通才", 6.9, 7.0, C_MAIN), ("专家", 3.1, 7.0, C_MAIN),
             ("隧道", 6.9, 3.0, C_ALT), ("糊", 3.1, 3.0, C_ALT)]
    for name, x, y, c in cells:
        ax.text(x, y + 0.35, name, ha="center", va="center", fontsize=10, color=c)
    sub = {"通才": "铺得开，分得细", "专家": "守得窄，分得细", "隧道": "守得窄，但守得细", "糊": "铺得开，但分不清"}
    for name, x, y, c in cells:
        ax.text(x, y - 0.7, sub[name], ha="center", va="center", fontsize=6.6, color=C_GREY)
    ax.add_patch(plt.Rectangle((1.2, 1.0), 7.6, 4.0, fc=C_ALT, alpha=0.07, lw=0))
    ax.annotate("", xy=(8.4, 1.95), xytext=(5.9, 1.95),
                arrowprops=dict(arrowstyle="-|>", lw=1.1, color=C_ALT))
    ax.text(7.15, 1.5, "同一次省力，两种长相", fontsize=6.4, color=C_ALT, ha="center")
    ax.text(5.0, 0.55, "环境宽度（窄 → 宽）", ha="center", fontsize=7.2)
    ax.text(0.55, 5.0, "预算（紧 → 松）", va="center", fontsize=7.2, rotation=90)
    ax.set_title("四个格：预算紧那一行，正是原来说法的两个“类型”", fontsize=8.5, loc="left")

    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.annotate("", xy=(9.4, 2.0), xytext=(0.8, 2.0),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, color=C_GREY))
    ax.text(9.4, 1.5, "时间（年）", ha="right", fontsize=7.2)
    ax.plot([1.2, 8.8], [3.2, 6.4], color=C_MAIN, lw=1.6, ls="--")
    ax.text(5.0, 7.3, "格的慢漂移（以年计）", fontsize=6.8, color=C_MAIN, ha="center")
    for x, y, lab in [(2.6, 3.55, "门诊里：四十秒一个"), (7.4, 5.95, "读片会上：半小时一张")]:
        ax.plot([x], [y], "o", ms=7, color=C_ALT, zorder=5)
        ax.text(x, y + 0.75, lab, ha="center", fontsize=6.6, color=C_ALT)
    ax.annotate("", xy=(3.4, 2.0), xytext=(2.9, 2.0),
                arrowprops=dict(arrowstyle="-", lw=0.8, color=C_LN if False else C_GREY))
    ax.text(3.15, 2.25, "两个月：看不出差别", fontsize=6.2, color=C_GREY, ha="center")
    ax.set_title("同一个人，两个处境：慢变量不是不变的量", fontsize=8.5, loc="left")

    fig.suptitle("不是四个抽屉，是两条轴上的四个位置", fontsize=9, x=0.01, ha="left")
    save(fig, "c02_four_cells")


if __name__ == "__main__":
    print("chapter figures:")
    fig_c11_iso_cost()
    fig_c12_arrows()
    fig_c09_axes()
    fig_c10_age_edu()
    fig_c13_labels()
    fig_c14_field()
    fig_c27_chain()
    fig_c15_capacity()
    fig_c16_phase()
    fig_c17_theta_tau()
    fig_c20_hysteresis()
    fig_c21_periodization()
    fig_c23_distance()
    fig_c24_tree()
    fig_c07_ratedistortion()
    fig_c08_checks()
    fig_c05_levels()
    fig_c06_two_outlets()
    fig_c01_age_vs_edu()
    fig_c02_four_cells()

# ---------------------------------------------------------------- 第 19 章（2026-11-18 补）
def fig_c19_pi() -> None:
    """(a) 跳／赛跑的构造形状；(b) 核实时滞逐年（实测）；(c) 同期信任（ESS，实测）。"""
    import csv
    import statistics as st
    from collections import defaultdict

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(7.4, 2.7))

    t = np.linspace(0, 10, 400)
    jump = 0.95 + 0.65 / (1 + np.exp(-(t - 4.2) * 3.0))
    race = 1.02 + 0.05 * np.sin(t * 2.0) - 0.12 * np.exp(-t / 2.2)
    ax1.axhline(1.0, color=C_GREY, lw=0.9, ls=":")
    ax1.plot(t, jump, color=C_ALT, lw=1.8, label="跳：过 1 不回落")
    ax1.plot(t, race, color=C_MAIN, lw=1.8, label="赛跑：贴着 1 走")
    ax1.set_xlabel("时间（示意）")
    ax1.set_ylabel("套利净收益 Π（示意）")
    ax1.set_ylim(0.5, 1.9)
    ax1.legend(fontsize=6.2, frameon=False, loc="upper left")
    ax1.set_title("（a）判据的形状", fontsize=8.2, color=C_MAIN, loc="left")

    by = defaultdict(list)
    with open(ROOT / "data" / "derived" / "tau_politifact.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                y, lag = int(r["year"]), float(r["lag_days"])
            except Exception:
                continue
            if 0 < lag <= 365:
                by[y].append(lag)
    years = sorted(y for y in by if len(by[y]) >= 300)
    med = [st.median(by[y]) for y in years]
    ax2.plot(years, med, color=C_MAIN, lw=1.8, marker="o", ms=3)
    ax2.set_ylabel("核实时滞的中位（天）")
    ax2.set_xlabel("年份")
    ax2.set_ylim(0, max(med) * 1.4)
    ax2.set_xticks(years[::3])
    ax2.set_xticklabels([str(y) for y in years[::3]])
    ax2.set_title("（b）实测：核查端变快了", fontsize=8.2, color=C_MAIN, loc="left")

    th = defaultdict(list)
    with open(ROOT / "data" / "derived" / "ess_country_round.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                th[int(r["year"])].append(float(r["E"]))
            except Exception:
                continue
    ys = sorted(th)
    mv = [st.mean(th[y]) for y in ys]
    ax3.plot(ys, mv, color=C_ALT, lw=1.8, marker="s", ms=3)
    ax3.set_ylabel("人际信任（ESS 年均）")
    ax3.set_xlabel("年份")
    ax3.set_ylim(0.3, 0.7)
    ax3.set_xticks(ys[::3])
    ax3.set_xticklabels([str(y) for y in ys[::3]])
    ax3.set_title("（c）同期：信任没有跟着升", fontsize=8.2, color=C_ALT, loc="left")

    fig.tight_layout()
    save(fig, "c19_pi_race")
