#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""用 ESS 11 轮（2002—2023）重估耗竭指数 α。

比 WVS 强在两点：轮次间隔约 2 年（WVS 是 5—10 年），轮次多（11 vs 6）。
E_t 代理：ppltrst（0—10，"多数人可信任"）的轮次×国家均值，除以 10。

模型：−dE/dt = k·E^α  ⇒  ln(−dE/dt) = ln k + α·ln E
只取下降的转移；同时报告全样本与分段。

输出 data/derived/alpha_ess.json + alpha_ess_panel.csv
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = r"C:\Users\16103\Downloads\european_social_survey_2002-2023.csv"
OUT = ROOT / "data" / "derived"
ROUND_YEAR = {1: 2002, 2: 2004, 3: 2006, 4: 2008, 5: 2010, 6: 2012,
              7: 2014, 8: 2016, 9: 2018, 10: 2020, 11: 2023}


def aggregate() -> pd.DataFrame:
    acc = defaultdict(lambda: [0.0, 0])   # (cntry, round) -> [sum, n]
    reader = pd.read_csv(SRC, usecols=["cntry", "essround", "ppltrst"],
                         chunksize=300_000, low_memory=False)
    for ch in reader:
        ch["ppltrst"] = pd.to_numeric(ch["ppltrst"], errors="coerce")
        ch = ch[(ch["ppltrst"] >= 0) & (ch["ppltrst"] <= 10)]
        g = ch.groupby(["cntry", "essround"])["ppltrst"].agg(["sum", "count"])
        for (c, r), row in g.iterrows():
            a = acc[(c, int(r))]
            a[0] += float(row["sum"]); a[1] += int(row["count"])
    rows = [{"cntry": c, "round": r, "year": ROUND_YEAR.get(r),
             "mean": s / n, "n": n} for (c, r), (s, n) in acc.items() if n >= 100]
    df = pd.DataFrame(rows)
    df["E"] = df["mean"] / 10.0
    return df.sort_values(["cntry", "round"])


def fit(sel: pd.DataFrame) -> dict:
    x = np.log(sel["E_mid"].values)
    y = np.log(sel["rate"].values)
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    s2 = resid @ resid / (len(x) - 2)
    se = float(np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1]))
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    return {"n": int(len(x)), "alpha": round(float(beta[1]), 3),
            "se": round(se, 3),
            "ci95": [round(float(beta[1] - 1.96 * se), 3), round(float(beta[1] + 1.96 * se), 3)],
            "r2": round(float(r2), 3)}


def drift_test(p: pd.DataFrame) -> dict:
    """不做"只取下降"的选择：直接回归 dE/dt 对 E 与 E²。"""
    d = p.dropna(subset=["E_mid", "rate"]).copy()
    d["dEdt"] = d["dE"] / d["dt"]
    X = np.column_stack([np.ones(len(d)), d["E_mid"], d["E_mid"] ** 2])
    beta, *_ = np.linalg.lstsq(X, d["dEdt"].values, rcond=None)
    resid = d["dEdt"].values - X @ beta
    s2 = resid @ resid / (len(d) - 3)
    cov = s2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    return {"n": int(len(d)), "b_linear": round(float(beta[1]), 3),
            "se_linear": round(float(se[1]), 3),
            "c_quadratic": round(float(beta[2]), 3),
            "se_quadratic": round(float(se[2]), 3),
            "note": "加速耗竭要求 c<0（E 越低，下降越快）；不显著即不支持"}


def main() -> None:
    df = aggregate()
    df.to_csv(OUT / "ess_country_round.csv", index=False, encoding="utf-8")
    panel = []
    for c, g in df.groupby("cntry"):
        g = g.sort_values("round").reset_index(drop=True)
        for i in range(1, len(g)):
            dt = g["year"][i] - g["year"][i - 1]
            dE = g["E"][i] - g["E"][i - 1]
            if dt <= 0:
                continue
            panel.append({"cntry": c, "round_from": g["round"][i - 1], "round_to": g["round"][i],
                          "year_from": g["year"][i - 1], "year_to": g["year"][i], "dt": dt,
                          "E_from": g["E"][i - 1], "E_to": g["E"][i], "dE": dE,
                          "rate": -dE / dt, "E_mid": (g["E"][i - 1] + g["E"][i]) / 2})
    p = pd.DataFrame(panel)
    p.to_csv(OUT / "alpha_ess_panel.csv", index=False, encoding="utf-8")
    dec = p[p["rate"] > 0].dropna(subset=["E_mid"])
    res = {
        "source": "ESS 2002-2023 combined (11 rounds), ppltrst/10",
        "n_countries": int(df["cntry"].nunique()),
        "n_country_rounds": int(len(df)),
        "n_transitions": int(len(p)),
        "share_declining": round(float((p["dE"] < 0).mean()), 3),
        "alpha_all_declines": fit(dec),
        "alpha_by_half": [
            fit(dec[dec["year_from"] < 2012]),
            fit(dec[dec["year_from"] >= 2012]),
        ],
        "drift_test_noselection": drift_test(p),
        "per_country_mean_range": [round(float(df["E"].min()), 3), round(float(df["E"].max()), 3)],
        "caveat": "ESS 是重复横截面，不是面板；国家均值受样本构成变化影响；"
                  "ppltrst 为单题 0—10；未加权（权重变量存在但未用）。",
    }
    (OUT / "alpha_ess.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
