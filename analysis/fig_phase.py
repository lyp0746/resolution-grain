#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""相图：v* = (T+λ)/(2w)。x=w，y=码率总价格 T+λ。"""
from pathlib import Path
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np

mpl.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
mpl.rcParams["axes.unicode_minus"] = False
OUT = Path(__file__).resolve().parents[1] / "analysis" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

w = np.linspace(0.2, 3.0, 400); c = np.linspace(0.2, 3.0, 400)
W, C = np.meshgrid(w, c)
V = C / (2 * W)

fig, ax = plt.subplots(figsize=(7.4, 5.6), dpi=200)
cs = ax.contour(W, C, V, levels=[0.1, 0.2, 0.4, 0.8, 1.6], colors="#1f3be0", linewidths=1.1)
ax.clabel(cs, fmt="v=%.1f", fontsize=7)
ax.contourf(W, C, V, levels=[0, 0.2, 0.4, 0.8, 10],
            colors=["#dfe6fb", "#eef0f8", "#f7efe6", "#f3e2dc"], alpha=0.7)

pts = {"精编：高 w、低码价": (2.6, 0.4), "粗码：低 w、高码价": (0.4, 2.6)}
for lab, (x, y) in pts.items():
    ax.plot(x, y, "o", ms=9, mfc="#b03a2e", mec="white", mew=1.2)
    ax.annotate(lab, (x, y), textcoords="offset points", xytext=(8, -14), fontsize=8)

ax.set_xlabel("w：对准确度的加权（利害、在意程度）")
ax.set_ylabel("T + λ：码率的总价格（带宽价格 + 认知成本）")
ax.set_title("分辨率相图  v* = (T + λ) / (2w)", fontsize=10)
ax.text(0.98, 0.03, "左下 = 细码（失真小、成本高）；右上 = 粗码（便宜、失真大）",
        transform=ax.transAxes, ha="right", fontsize=7, color="#666")
ax.set_xlim(0.2, 3.0); ax.set_ylim(0.2, 3.0)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(OUT / "phase_w_T.png")
print("saved")
