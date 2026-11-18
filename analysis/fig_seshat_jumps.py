#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""图：Seshat 两组指标的跳变时间轴（|Δ|≥1 才算跳变）。"""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "seshat" / "axial_dataset.05.2018.csv"
OUT = ROOT / "analysis" / "figures"

A = ["8. Formal legal code", "9. General applicability of law",
     "10. Constraint on executive", "11. Full-time bureaucrats", "12. Impeachment"]
B = ["1. Moralistic punishment", "2. Moralizing norms", "3. Promotion of prosociality",
     "4. Omniscient supernatural beings", "5. Rulers not gods",
     "6. Equating elites and commoners", "7. Equating rulers and commoners"]

mpl.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
mpl.rcParams["axes.unicode_minus"] = False


def main() -> None:
    df = pd.read_csv(SRC, encoding="utf-8-sig").rename(columns={"Date.From": "year"})
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"]).sort_values(["NGA", "year"])
    df["A"] = df[A].sum(axis=1, min_count=1)
    df["B"] = df[B].sum(axis=1, min_count=1)

    ngas = sorted(df["NGA"].unique())
    ypos = {n: i for i, n in enumerate(ngas)}

    jumps = []
    for nga, g in df.groupby("NGA"):
        g = g.sort_values("year").reset_index(drop=True)
        for i in range(1, len(g)):
            dA = g["A"][i] - g["A"][i - 1]
            dB = g["B"][i] - g["B"][i - 1]
            mid = (g["year"][i] + g["year"][i - 1]) / 2
            if abs(dA) >= 1:
                jumps.append((nga, mid, "A", dA))
            if abs(dB) >= 1:
                jumps.append((nga, mid, "B", dB))
    j = pd.DataFrame(jumps, columns=["NGA", "year", "grp", "delta"])

    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=200)
    for band in (-2000, -1000, 200, 500):
        ax.axvspan(band - 50, band + 50, color="#f0ede6", zorder=0, lw=0)

    for nga in ngas:
        y = ypos[nga]
        ax.axhline(y, color="#d8d4cc", lw=0.6, zorder=1)

    ca, cb = "#b03a2e", "#1f3be0"
    for grp, color, dy, va in (("A", ca, 0.26, "bottom"), ("B", cb, -0.26, "top")):
        s = j[j.grp == grp]
        ax.scatter(s["year"], s["NGA"].map(ypos) + dy,
                   s=18 + 26 * s["delta"].abs(), c=color, alpha=0.75,
                   edgecolors="white", linewidths=0.5, zorder=3, label=f"{grp} 组跳变")

    ax.set_yticks(range(len(ngas)))
    ax.set_yticklabels(ngas, fontsize=8)
    ax.set_xlim(-5500, 2000)
    ax.set_ylim(-0.8, len(ngas) - 0.2)
    ax.set_xlabel("年份（负 = 公元前）")
    ax.set_title("规则形式化（A，上）与道德化规范（B，下）的跳变时刻\n"
                 "Seshat axial 数据集 · 10 个自然地理区 · 仅标记 |Δ|≥1 的世纪步长", fontsize=10)
    ax.legend(loc="upper left", ncol=2, fontsize=8, frameon=False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.text(0.01, 0.01, "灰带：变化最大的四个世纪（−2000、−1000、200、500）",
             fontsize=7, color="#666")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "seshat_jumps.png")
    print(f"saved {OUT / 'seshat_jumps.png'}  jumps A={len(j[j.grp=='A'])} B={len(j[j.grp=='B'])}")


if __name__ == "__main__":
    main()
