#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""代际 vs 表征（教育）的初步对照：ESS 第 8 轮。

要回答的问题（来自模型"伪代际"命题）：
    年龄的效应，在控制教育（μ 的粗代理）后，是否显著缩小？

做法
  y1 = ppltrst（0—10 人际信任，E_t 的个体侧代理）
  y2 = mnrgtjb（男性优先就业，1—5，反向计分后越高=越平等）
  x  = agea（年龄）、eduyrs（受教育年限）、country（固定效应）
  比较：只放年龄 vs 年龄+教育，年龄系数缩小多少；以及两者的偏 R²。

输出 data/derived/ess8_age_vs_edu.json
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "data" / "raw" / "datasets" / "kg_ess8.zip"
OUT = ROOT / "data" / "derived" / "ess8_age_vs_edu.json"
COLS = ["cntry", "agea", "eduyrs", "ppltrst", "mnrgtjb", "gndr", "essround"]


def load() -> pd.DataFrame:
    z = zipfile.ZipFile(ZIP)
    name = [n for n in z.namelist() if n.endswith("_F1.csv")][0]
    with z.open(name) as f:
        df = pd.read_csv(f, usecols=lambda c: c in COLS, low_memory=False)
    for c in ("agea", "eduyrs", "ppltrst", "mnrgtjb", "gndr", "essround"):
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # ESS 缺失码：6/7/8/9, 66/77/88/99, -1/-2/-3
    for c in ("ppltrst", "agea", "eduyrs", "mnrgtjb"):
        if c in df:
            df.loc[df[c] < 0, c] = np.nan
    df.loc[df["ppltrst"] > 10, "ppltrst"] = np.nan
    df.loc[df["mnrgtjb"] > 5, "mnrgtjb"] = np.nan
    df.loc[df["eduyrs"] > 40, "eduyrs"] = np.nan
    df["gender_egal"] = df["mnrgtjb"]              # ESS8: 1=同意男性优先, 5=强烈反对 → 越高越平等
    return df.dropna(subset=["agea", "eduyrs", "cntry"])


def ols_r2(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    return 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean())), beta


def compare(df: pd.DataFrame, ycol: str) -> dict:
    d = df.dropna(subset=[ycol]).copy()
    d[ycol] = (d[ycol] - d[ycol].mean()) / d[ycol].std()
    d["age_z"] = (d["agea"] - d["agea"].mean()) / d["agea"].std()
    d["edu_z"] = (d["eduyrs"] - d["eduyrs"].mean()) / d["eduyrs"].std()
    dummies = pd.get_dummies(d["cntry"], drop_first=True).astype(float)
    base = np.column_stack([np.ones(len(d)), dummies.values])
    X1 = np.column_stack([base, d["age_z"].values])
    X2 = np.column_stack([base, d["age_z"].values, d["edu_z"].values])
    r2_0, _ = ols_r2(d[ycol].values, base)
    r2_1, b1 = ols_r2(d[ycol].values, X1)
    r2_2, b2 = ols_r2(d[ycol].values, X2)
    age_alone = float(b1[-1])
    age_ctrl = float(b2[-2])
    edu_ctrl = float(b2[-1])
    return {
        "n": int(len(d)),
        "r2_country_only": round(float(r2_0), 4),
        "r2_plus_age": round(float(r2_1), 4),
        "r2_plus_edu": round(float(r2_2), 4),
        "age_coef_std_alone": round(age_alone, 4),
        "age_coef_std_with_edu": round(age_ctrl, 4),
        "edu_coef_std_with_age": round(edu_ctrl, 4),
        "delta_r2_age": round(float(r2_1 - r2_0), 5),
        "delta_r2_edu": round(float(r2_2 - r2_1), 5),
        "age_shrink_pct_when_edu_added": round(100 * (1 - age_ctrl / age_alone), 1) if abs(age_alone) > 0.01 else None,
    }


def main() -> None:
    df = load()
    res = {"source": "ESS round 8 (kg_ess8.zip)", "n_rows": int(len(df)),
           "trust": compare(df, "ppltrst"),
           "gender_egal": compare(df, "gender_egal"),
           "note": "教育是 μ 的粗代理；单轮数据无法区分队列效应与年龄效应；"
                   "系数为全样本标准化后的 OLS，含国家固定效应。"}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
