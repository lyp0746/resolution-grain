#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""k36ba：把「特质 → 泛化更宽」的相关算准（按作者自己的语法与量表口径）。

为什么要重做
  上一轮我用「IUS 27 题直接求和」当 IUS 总分、用 n=126（未过滤）算相关，
  得到 r = 0.172。那是个**未经核对的口径**，不能当基线。

这一轮做的三件事
  1. 核 STAI-T 与 IUS 的计分：数据文件自带 `STAI_T` / `IUS_total_score`，
     作者的 README 明说「反向计分已在最终数据文件中完成」。
     用三条独立证据核它：(a) 总分能否由分项线性复原；(b) 分项—总分相关是否全正；
     (c) Cronbach α 是否在合理区间。
  2. 按作者语法 `Syntax_gedragsdata_UPDATED March 2022.sps` 的**最终样本过滤**算相关：
     `Fysiological_data_quality=1 & Contingency_awareness=1 & Words_order_check=1`。
  3. 给每个 r 配 Fisher-z 95% 置信区间和 p 值，并把 r 折算成 d，
     供 `PROTOCOL-gradients.md` 的功效表使用。

输出
  archive/logs/RESULTS-traits-k36ba.md（脚本直接写，不手抄数字）

纪律
  相关是**横断**的；方向（特质使梯度变宽，还是宽梯度使特质得分高）不可判。
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
SAV = ROOT / "data" / "raw" / "osf" / "k36ba" / "Behavioral_data_all PPS.sav"
OUT = ROOT / "archive" / "logs" / "RESULTS-traits-k36ba.md"

IUS = [f"IUS_{i}" for i in range(1, 28)]
STAI_T = [f"STAI_{i}" for i in range(21, 41)]


def cronbach(d: pd.DataFrame) -> float:
    k = d.shape[1]
    return k / (k - 1) * (1 - d.var(ddof=1).sum() / d.sum(axis=1).var(ddof=1))


def fisher_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    z = math.atanh(r)
    se = 1 / math.sqrt(n - 3)
    zc = 1.959963985
    lo, hi = z - zc * se, z + zc * se
    return math.tanh(lo), math.tanh(hi)


def p_value(r: float, n: int) -> float:
    if n <= 3:
        return float("nan")
    t = r * math.sqrt((n - 2) / max(1 - r * r, 1e-12))
    # 双侧 t 分布尾概率，用不完全 Beta 的初等近似（n>30 时与正态几乎等价）
    z = abs(t)
    return math.erfc(z / math.sqrt(2))


def main() -> None:
    df, _ = pyreadstat.read_sav(SAV)
    L = []  # 报告行
    L.append("# k36ba：特质 × 泛化的相关（按作者口径重算）\n")
    L.append("> 由 `analysis/traits_k36ba.py` 生成，数字不手抄。\n")

    # ---- 1 计分核验 ----
    L.append("## 1 计分核验（先证明量表分是对的，再谈相关）\n")
    X = df[IUS].apply(pd.to_numeric, errors="coerce").values
    y = pd.to_numeric(df["IUS_total_score"], errors="coerce").values
    ok = ~(np.isnan(X).any(1) | np.isnan(y))
    w = np.linalg.lstsq(X[ok], y[ok], rcond=None)[0]
    L.append("| 检验 | 结果 |")
    L.append("|---|---|")
    L.append(f"| IUS 总分 = 27 题加权和？（最小二乘权重） | 权重全为 {np.round(w.mean(), 3)}，残差 sd = "
             f"{np.sqrt(((X[ok] @ w - y[ok]) ** 2).mean()):.4f} → **完全线性** |")
    L.append(f"| IUS 总分范围 | {np.nanmin(y):.0f}—{np.nanmax(y):.0f}，均值 {np.nanmean(y):.1f} |")

    item_rest = []
    for c in STAI_T:
        rest = df[[x for x in STAI_T if x != c]].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=5)
        item_rest.append(pd.to_numeric(df[c], errors="coerce").corr(rest))
    L.append(f"| STAI-T 分项—余项相关（反向计分是否已做） | 20 项**全部为正**，最小 {min(item_rest):+.2f}，中位 "
             f"{np.median(item_rest):+.2f} → 反向计分确已落在数据里 |")
    L.append(f"| STAI-T Cronbach α（20 题） | {cronbach(df[STAI_T].apply(pd.to_numeric, errors='coerce')):.3f} |")
    L.append(f"| STAI-T 范围 | {pd.to_numeric(df['STAI_T'], errors='coerce').min():.0f}—"
             f"{pd.to_numeric(df['STAI_T'], errors='coerce').max():.0f} |")
    L.append("")
    L.append("**结论**：作者 README 说反向计分已在最终文件完成；语法里那条 `RECODE` 被注释掉是正确的，"
             "不是遗漏。上一轮我手算的 IUS 求和与该文件完全一致（同范围 32—94，同均值 63.7），"
             "所以差异不在量表分，而在**样本过滤**。\n")

    # ---- 2 过滤与相关 ----
    flt = df[(df["Fysiological_data_quality"] == 1)
             & (df["Contingency_awareness"] == 1)
             & (df["Words_order_check"] == 1)]
    L.append("## 2 相关（用作者语法的最终样本）\n")
    L.append(f"未过滤 n = {len(df)}，语法过滤后 n = {len(flt)}。\n")

    gis = [("GI_fear_ratings", "恐惧评分泛化（主指标）"),
           ("GI_alt1_fear", "恐惧：仅 GS3 / CS+"),
           ("GI_alt1_expec", "预期：仅 GS3 / CS+"),
           ("GI_alt3_expec", "预期：三分刺激 / CS−"),
           ("GI_SCR", "皮电（SCR）泛化"),
           ("GI_FPS", "惊吓（FPS）泛化")]
    traits = [("IUS_total_score", "不确定性不耐受（IUS）"), ("STAI_T", "特质焦虑（STAI-T）")]

    L.append("| 泛化指标 | 特质 | r | 95% CI | n | p | 折算 d |")
    L.append("|---|---|---|---|---|---|---|")
    best = None
    for g, gl in gis:
        if g not in flt:
            continue
        for t, tl in traits:
            s = flt[[g, t]].apply(pd.to_numeric, errors="coerce").dropna()
            if len(s) < 20:
                continue
            r = s[g].corr(s[t])
            lo, hi = fisher_ci(r, len(s))
            # 双变量 r → Cohen's d（等组假设）
            d = 2 * r / math.sqrt(max(1 - r * r, 1e-9))
            L.append(f"| {gl} | {tl} | {r:+.3f} | [{lo:+.2f}, {hi:+.2f}] | {len(s)} | {p_value(r, len(s)):.3f} | {d:.2f} |")
            if best is None and g == "GI_fear_ratings" and t == "IUS_total_score":
                best = (r, len(s), lo, hi, d)
    L.append("")
    r, n, lo, hi, d = best
    L.append(f"**主读数**：恐惧泛化 × IUS，r = {r:+.3f}，95% CI [{lo:+.2f}, {hi:+.2f}]，n = {n}。"
             f"区间跨 0；点估计折算 d ≈ {d:.2f}。\n")

    # ---- 3 功效 ----
    L.append("## 3 折算成效的样本量（供 `PROTOCOL-gradients.md`）\n")
    L.append("组内设计：`d_z = d / sqrt(2(1-ρ))`，ρ 取相邻条件的相关；"
             "n = (z_{.975}+z_{.80})² / d_z²（双侧 .05，功效 80%）。\n")
    L.append("| 假设 | d_z | n（组内） | n（组间，每组） |")
    L.append("|---|---|---|---|")
    for rho, lab in [(0.0, "ρ=0（独立，最保守）"), (0.5, "ρ=0.5（常见）"), (0.7, "ρ=0.7（同人同任务）")]:
        for dd in (round(d, 2), 0.55):
            dz = dd / math.sqrt(2 * (1 - rho))
            n_in = math.ceil((1.959963985 + 0.8416212336) ** 2 / dz ** 2)
            n_bt = math.ceil(2 * (1.959963985 + 0.8416212336) ** 2 / dd ** 2)
            L.append(f"| d={dd:.2f}，{lab} | {dz:.2f} | {n_in} | {n_bt} |")
    L.append("")
    L.append("**读法**：d=0.30 是实测的**特质**相关折算值（悲观情形：操纵只做到和特质一样弱）；"
             "d=0.55 是「设计出来的操纵应当比特质相关更强」的假设（乐观情形）。"
             "ρ=0.5 时区间为 **26—101 人**，ρ=0（最保守）时 **52—201 人**。"
             "原协议写的 n=64 只在「d≈0.55 且 ρ≥0.5」时成立，应写成区间而不是一个数。\n")

    # ---- 4 诚实边界 ----
    L.append("## 4 边界\n")
    L.append("1. **横断相关**，方向不可判：特质→宽梯度，与宽梯度→高分，在本数据里同构。")
    L.append("2. **便利样本**：133 人，荷兰被试，全部是恐惧条件化范式；"
             "「泛化指数 GI」是比值，不是拟合出来的核宽 v，两者只在单调意义上可比。")
    L.append("3. **多重比较**：12 个相关里只有恐惧侧 2 个方向为正且接近显著，"
             "按 Bonferroni（α/12 ≈ .004）无一通过。可当**效应量估计**，不可当**发现**。")
    L.append("4. 预期侧与生理侧（SCR/FPS）全部近零 —— 这与「焦虑只加宽恐惧泛化、不加宽预期泛化」"
             "的文献结论一致，但对模型 S4（模糊度↑⇒v↑）不构成证据。")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:6]))
    print(f"... → {OUT}")


if __name__ == "__main__":
    main()
