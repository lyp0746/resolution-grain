#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把窗口改成 1978—2026，用年度数据重估耗竭指数 α。

为什么换窗口：WVS 的信任序列是 5—10 年一格，1978 这个断点根本不在样本里。
TFR 有年度序列，可以从 1978 起算——它不是 E_t，但文档把生育率当作 E_t 的下游指标，
所以"同一个函数形式能不能拟合"本身就是一个检验。

拟合：−dTFR/dt = k·TFR^α  ⇒  ln(−dTFR/dt) = ln k + α·ln TFR
只取下降年（dTFR<0），并对比指数模型（α=1）与线性模型。

输出 data/derived/alpha_tfr.json + alpha_tfr.csv
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived"
COUNTRIES = {"CHN": "中国", "KOR": "韩国", "JPN": "日本", "USA": "美国"}
START, END = 1978, 2024


def load(code: str) -> pd.DataFrame:
    j = json.loads((ROOT / "data" / "raw" / f"wb_tfr_{code.lower()}.json").read_text(encoding="utf-8"))
    rows = [(int(x["date"]), float(x["value"])) for x in j[1] if x["value"] is not None]
    df = pd.DataFrame(rows, columns=["year", "tfr"]).sort_values("year")
    return df[(df.year >= START) & (df.year <= END)].reset_index(drop=True)


def fit(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["d"] = df["tfr"].diff()
    dec = df[(df.d < 0) & df.tfr.notna()].dropna()
    x = np.log(dec.tfr.values)
    y = np.log(-dec.d.values)
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    s2 = resid @ resid / (len(x) - 2)
    se = float(np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1]))
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    return {"n_declining_years": int(len(x)), "alpha": round(float(beta[1]), 3),
            "se": round(se, 3), "ci95": [round(float(beta[1] - 1.96 * se), 3),
                                         round(float(beta[1] + 1.96 * se), 3)],
            "r2": round(float(r2), 3)}


def main() -> None:
    out, rows = {}, []
    for code, name in COUNTRIES.items():
        df = load(code)
        out[name] = fit(df)
        out[name]["first"] = {"year": int(df.year.iloc[0]), "tfr": round(float(df.tfr.iloc[0]), 3)}
        out[name]["last"] = {"year": int(df.year.iloc[-1]), "tfr": round(float(df.tfr.iloc[-1]), 3)}
        out[name]["min"] = {"year": int(df.loc[df.tfr.idxmin(), "year"]),
                            "tfr": round(float(df.tfr.min()), 3)}
        rows.append(df.assign(country=name))
    pd.concat(rows).to_csv(OUT / "alpha_tfr.csv", index=False, encoding="utf-8")
    res = {"window": [START, END], "model": "-dTFR/dt = k*TFR^alpha", "results": out,
           "caveat": "TFR 受政策冲击（计划生育、二孩）与经济周期影响，不是纯耗竭过程；"
                     "α 在这里测的是'曲线形状'，不是'共情资源'。"}
    (OUT / "alpha_tfr.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
