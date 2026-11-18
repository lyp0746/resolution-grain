#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""跨书检验：分期的粒度是不是 `f(w, T)`？

假设（来自 `v_t*=(T+λ)/(2w)`）
  P1  `T`（回望带宽的价格）↑ ⇒ 段变粗。
      代理：方案覆盖的时间跨度。跨度越大，一部书读不完，`T` 越大 ⇒ 段长更长。
      → log(平均段长) 对 log(跨度) 回归，斜率应显著为正。
  P2  `w`（这份分期要被用来做什么）↑ ⇒ 段变细。
      代理：体裁。政治/事件取向（survey 编年、curriculum 教程、chronicle 编年史）
      比"长时段"取向（argument 论辩、treatise 专著）更需要在"现在谁在位"上精确。
      → 政治/教学类的平均段长，应短于论辩/专著类。

数据：《谁在切时间轴》`data/schemes.csv`，60 部方案、252 个分期边界。

输出
  analysis/results/periodization_test.csv   每个方案的跨度/段数/段长/体裁
  stdout 两组检验；任一不成立都照实报。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

SRC = Path("D:/0_Article/WorldPeriodization/data/schemes.csv")
OUT = Path(__file__).resolve().parents[1] / "analysis" / "results" / "periodization_test.csv"

POLITICAL = {"survey", "curriculum", "chronicle"}


def main() -> None:
    d = pd.read_csv(SRC)
    d = d.dropna(subset=["boundary_year", "source"])
    rows = []
    for src, g in d.groupby("source"):
        y = np.sort(g["boundary_year"].astype(float).values)
        if len(y) < 3:
            continue
        span = y.max() - y.min()
        if span <= 0:
            continue
        rows.append({"source": src, "genre": g["genre"].iloc[0], "scope": g["scope"].iloc[0],
                     "tradition": g["tradition"].iloc[0], "n_boundaries": len(y),
                     "span_years": span, "seg_years": span / (len(y) - 1)})
    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"方案 {len(out)} 部；跨度中位 {out.span_years.median():.0f} 年；"
          f"平均段长中位 {out.seg_years.median():.0f} 年")

    # P1: 跨度 ↑ ⇒ 段长 ↑
    x = np.log(out.span_years.values)
    y = np.log(out.seg_years.values)
    b, a = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    n = len(out)
    t = r * np.sqrt((n - 2) / max(1 - r * r, 1e-12))
    print(f"\nT1  log(段长) = {a:+.2f} {b:+.2f}·log(跨度)   r={r:+.3f}  n={n}")
    print(f"    {'成立' if r > 0.4 else '不成立/弱'}：跨度每增 10 倍，段长增 {10 ** b:.1f} 倍（斜率 {b:.2f}，比例缩放的理想值是 1.0）")

    # P2: 政治/教学取向 ⇒ 段更细
    out["polit"] = out.genre.isin(POLITICAL)
    A = out[out.polit]["seg_years"]
    B = out[~out.polit]["seg_years"]
    print(f"\nT2  政治/教学类 n={len(A)} 段长中位 {A.median():.0f} 年 | "
          f"论辩/专著类 n={len(B)} 段长中位 {B.median():.0f} 年")
    from scipy.stats import mannwhitneyu
    if len(A) and len(B):
        u, p = mannwhitneyu(A, B, alternative="less")
        print(f"    单侧 Mann–Whitney p={p:.4f}  → {'成立' if p < 0.05 else '不成立（无显著差异）'}")

    # 附加：控制跨度后的体裁差（用完整的一元回归残差）
    out["log_span"] = np.log(out.span_years)
    out["log_seg"] = np.log(out.seg_years)
    fit = np.polyfit(out.log_span, out.log_seg, 1)
    out["resid"] = out.log_seg - np.polyval(fit, out.log_span)
    gg = out.groupby("polit")["resid"].agg(["mean", "count"])
    a_, b_ = gg.loc[True, "mean"], gg.loc[False, "mean"]
    from scipy.stats import ttest_ind
    tp = ttest_ind(out[out.polit].resid, out[~out.polit].resid).pvalue
    print(f"\n控制跨度后的体裁残差：政治/教学 {a_:+.2f}（n={int(gg.loc[True,'count'])}），"
          f"其他 {b_:+.2f}（n={int(gg.loc[False,'count'])}）；t 检验 p={tp:.3f}（负值 = 更细）")
    print("→", OUT)


if __name__ == "__main__":
    main()
