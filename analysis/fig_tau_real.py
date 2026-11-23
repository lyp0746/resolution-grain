#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图 23.1（真实版）：核实时差的经验生存曲线 + 七日倍数的排班指纹。

与旧图的区别只有一处，但那一处要紧：**左幅不再是"对数正态示意"，而是 21,063 条
记录的经验生存函数（步进）**；右幅的四个比值也由同一批数据算出，与表 23.2 同源。

数据：data/derived/tau_politifact.csv（字段 lag_days）
输出：assets/charts/v2_fig_tau.png（覆盖旧图）
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "assets" / "charts"
DATA = ROOT / "data" / "derived" / "tau_politifact.csv"

INK, OCHRE, BLUE, RED, GRAY = "#2b2b2b", "#b7791f", "#2b6cb0", "#b03a2e", "#718096"

mpl.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "SimHei"],
    "axes.unicode_minus": False,
    "figure.facecolor": "white",
    "text.color": INK,
    "font.size": 9,
})

rows = list(csv.DictReader(DATA.open(encoding="utf-8")))
lags = np.array([int(r["lag_days"]) for r in rows if r["lag_days"].strip().isdigit()])
n = len(lags)
counts = {d: int((lags == d).sum()) for d in range(0, 60)}
med = int(np.median(lags))
p90 = int(np.quantile(lags, 0.90))

fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1.2, 1]})

ax = axes[0]
xs = np.arange(0, 61)
surv = np.array([(lags > k).mean() for k in xs])
ax.step(xs, surv, where="post", color=INK, lw=2.0)
for v, lab, yv in [(med, f"中位 {med} 天：一半", 0.5), (p90, f"P90 {p90} 天：一成", 0.10)]:
    ax.axvline(v, color=RED, ls=":", lw=1.0)
    ax.plot([v], [yv], "o", color=RED, ms=4.5)
    ax.text(v * 1.12, yv + 0.035, lab, fontsize=7.0, color=RED)
ax.fill_between(xs, surv, where=(xs <= med), step="post", color=BLUE, alpha=0.12)
ax.set_xscale("log")
ax.set_xlim(0.9, 60)
ax.set_xticks([1, 2, 5, 10, 20, 30, 60])
ax.set_xticklabels(["1", "2", "5", "10", "20", "30", "60"])
ax.set_ylim(0, 1.02)
ax.set_xlabel("从出错到更正的间隔（天，对数轴）", fontsize=7.8)
ax.set_ylabel("还没更正的比例", fontsize=7.8)
ax.set_title("一半一周内，一成超过二十六天", fontsize=9.0, loc="left")
ax.tick_params(labelsize=7)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.text(0.03, 0.13, f"经验曲线：{n:,} 条记录，步进\n（每格一点，不拟合）",
        transform=ax.transAxes, fontsize=6.4, color=GRAY, linespacing=1.4)

ax = axes[1]
days = [7, 14, 21, 28]
vals = [counts[d] / ((counts[d - 1] + counts[d + 1]) / 2) for d in days]
bars = ax.bar([str(d) for d in days], vals, color=OCHRE, width=0.55)
ax.axhline(1.0, color=GRAY, ls="--", lw=1.0)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.012, f"{v:.2f}", ha="center", fontsize=7.6)
ax.set_ylim(0.9, 1.40)
ax.set_xlabel("间隔天数（均为 7 的倍数）", fontsize=7.8)
ax.set_ylabel("条数 ÷ 左右邻格均值", fontsize=7.8)
ax.set_title("排班指纹：7 的倍数偏高", fontsize=9.0, loc="left")
ax.tick_params(labelsize=7)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)

fig.tight_layout()
fig.savefig(CH / "v2_fig_tau.png", dpi=300, bbox_inches="tight")
print("n=", n, "median", med, "p90", p90, "ratios", [round(v, 2) for v in vals])
