#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""泛化梯度拟合器：从「被试 × 刺激水平 × 响应」数据里估出核宽 v。

这是模型里 v（分辨率/核宽）的**通用测量脚本**，不绑定任何一份数据。

输入 CSV 需三列：subject, stim, response
  stim     刺激水平（数值，等距）
  response 响应概率/强度（0—1 或任意单调量）

做法
  对每个被试拟合   y = base + A·exp(−(s−μ)²/(2v))
  v 即核宽；μ 即峰位；R² 用于剔除拟合失败者。

用法
  python analysis/fit_gradients.py --csv "data/raw/osf/2sxfp/perceptual gradient LF.csv" \
      --sep ";" --decimal "," --subj EMS_nr --stim stim --resp CSP_cat --out data/derived/grad_2sxfp.csv

输出
  每行一个被试：subject, mu, v, amp, base, r2
  并在 stdout 打印 v 的分布。
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def gauss(s, A, mu, v, base):
    return base + A * np.exp(-(s - mu) ** 2 / (2 * v))


def fit_one(s: np.ndarray, y: np.ndarray):
    p0 = [max(y) - min(y) + 1e-3, float(np.median(s)), float(np.var(s)), float(np.min(y))]
    lo = [0, s.min() - 0.5, 1e-3, 0]
    hi = [max(1.0, y.max()) * 2, s.max() + 0.5, 100.0, 1.0]
    popt, _ = curve_fit(gauss, s, y, p0=p0, maxfev=20000, bounds=(lo, hi))
    resid = y - gauss(s, *popt)
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean())) if np.var(y) > 0 else np.nan
    return popt, r2


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--sep", default=",")
    ap.add_argument("--decimal", default=".")
    ap.add_argument("--subj", default="subject")
    ap.add_argument("--stim", default="stim")
    ap.add_argument("--resp", default="response")
    ap.add_argument("--min-levels", type=int, default=5)
    ap.add_argument("--out", default="data/derived/gradients.csv")
    a = ap.parse_args()

    df = pd.read_csv(a.csv, sep=a.sep, decimal=a.decimal, dtype=str)
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    for c in (a.stim, a.resp):
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    d = df.dropna(subset=[a.stim, a.resp])

    rows = []
    for sid, g in d.groupby(a.subj):
        g = g.drop_duplicates(subset=[a.stim])
        if len(g) < a.min_levels:
            continue
        s, y = g[a.stim].values.astype(float), g[a.resp].values.astype(float)
        try:
            popt, r2 = fit_one(s, y)
        except Exception:  # noqa: BLE001
            continue
        rows.append({"subject": sid, "mu": popt[1], "v": popt[2],
                     "amp": popt[0], "base": popt[3], "r2": r2})

    out = pd.DataFrame(rows)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.out, index=False, encoding="utf-8")
    good = out[out.r2 > 0.3]
    print(f"subjects fitted: {len(out)}  (r2>0.3: {len(good)})")
    if len(good):
        print(good["v"].describe(percentiles=[.25, .5, .75]).round(3).to_string())
    print(f"→ {a.out}")


if __name__ == "__main__":
    main()
