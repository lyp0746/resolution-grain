#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A12：用 Equinox 的百年面板（TSDat123）做“文字 × 切点数”的时间检验。

这份面板给了 A9／A10 缺的两样：**时间**与**编码密度**。
  - 1,494 个（政体 × 世纪）观测，373 个政体，48 个社会复杂度变量（含 WRecord／Script）；
  - `PropCoded`＝这一行里被编码的变量比例——**证据密度的直接读数**。

两个检验
  T-A（时间）：同一政体内，文字出现之后，“非文字的切点数”是否上升；
  T-B（决定性）：把 `PropCoded` 放进回归，文字的系数塌不塌。
       若塌 ⇒ 文字效应主要是“记录密度”的影子（A10 的读法 a）；
       若不塌 ⇒ 它不只是可核性（读法 b 成立）。

判法先写死
  P-A：writing 系数 > 0；
  P-B：加上 PropCoded 后，writing 系数下降超过一半 ⇒ 读法 a；下降不到三成 ⇒ 读法 b；
       中间地带就写“判不了”。

输出 data/derived/writing_tsdat.json
"""
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "seshat_equinox" / "Equinox_Data-v.1.zip"
OUT = ROOT / "data" / "derived" / "writing_tsdat.json"

WRITE_COLS = ["WRecord", "Script", "NonPhWrit", "PhAlph"]
# 48 个社会复杂度变量里，凡不是文字类的
SC_COLS = ["PolPop", "PolTerr", "CapPop", "AdmLev", "MilLev", "ReligLev", "SettlHier",
           "ProfOfficer", "ProfSoldier", "ProfPriest", "FullTBur", "ExamSyst", "MeritProm",
           "GovtBldg", "Court", "LegCode", "Judge", "Lawyer", "Irrigation", "WaterSuppl",
           "Market", "FoodStor", "Road", "Bridge", "Canal", "Port", "Mine", "Courier",
           "PostStation", "PostService", "Mnemonic", "NonWRecord", "Lists", "Calendar",
           "SacrTxt", "ReligLit", "PractLit", "History", "Philosophy", "SciLit", "Fiction",
           "Article", "Token", "PrecMetal", "ForCoin", "IndigCoin", "PaperCurr"]
BINARY_ALL = [c for c in SC_COLS if c not in ("PolPop", "PolTerr", "CapPop")]


def load() -> pd.DataFrame:
    z = zipfile.ZipFile(SRC)
    xlsx = [n for n in z.namelist() if n.endswith(".xlsx")][0]
    t = pd.read_excel(io.BytesIO(z.read(xlsx)), sheet_name="TSDat123")
    t = t.replace(-999, np.nan)
    t["writing"] = (t[WRITE_COLS].max(axis=1) > 0.5).astype(float)
    t.loc[t[WRITE_COLS].max(axis=1).isna(), "writing"] = np.nan
    t["k_nw"] = (t[BINARY_ALL].fillna(0) > 0.5).sum(axis=1)
    t["k_w"] = (t[WRITE_COLS].fillna(0) > 0.5).sum(axis=1)
    t["k_all"] = t["k_nw"] + t["k_w"]
    t["lpop"] = np.log10(t["PolPop"].where(t["PolPop"] > 0))
    t["aged"] = t.groupby("PolID")["Time"].transform(lambda s: s - s.min()) / 100.0
    onset = t[t["writing"] == 1].groupby("PolID")["Time"].min()
    t["w_onset"] = t["PolID"].map(onset)
    t["yrs_since_w"] = (t["Time"] - t["w_onset"]) / 100.0
    return t


def fe_ols(t: pd.DataFrame, y: str, X: list[str], group: str = "PolID") -> dict:
    df = t.dropna(subset=[y] + X).copy()
    for c in [y] + X:
        df[c] = df[c] - df.groupby(group)[c].transform("mean")
    M = np.column_stack([df[c].values for c in X])
    Y = df[y].values
    b = np.linalg.lstsq(M, Y, rcond=None)[0]
    e = Y - M @ b
    n, k = M.shape
    bread = np.linalg.pinv(M.T @ M)
    meat = np.zeros((k, k))
    for _, g in df.groupby(group):
        gi = df.index.get_indexer(g.index)
        Mg, eg = M[gi], e[gi]
        meat += Mg.T @ (eg[:, None] * eg[None, :]) @ Mg
    G = df[group].nunique()
    V = bread @ meat @ bread * (G / max(G - 1, 1)) * ((n - 1) / max(n - k, 1))
    se = np.sqrt(np.diag(V))
    return {"n": int(n), "clusters": int(G),
            "coef": {nm: round(float(v), 3) for nm, v in zip(X, b)},
            "t": {nm: round(float(v), 2) for nm, v in zip(X, b / se)}}


def main() -> None:
    t = load()
    t.to_csv(ROOT / "data" / "derived" / "writing_tsdat_panel.csv", index=False)
    res = {"n_rows": int(len(t)), "n_polity": int(t["PolID"].nunique()),
           "share_writing": round(float(t["writing"].mean()), 3),
           "prop_coded_mean": round(float(t["PropCoded"].mean()), 1)}

    res["T_A_time"] = fe_ols(t, "k_nw", ["writing", "lpop", "aged"])
    res["T_A_time_all"] = fe_ols(t, "k_all", ["writing", "lpop", "aged"])
    res["T_B_density"] = fe_ols(t, "k_nw", ["writing", "PropCoded", "lpop", "aged"])
    res["T_B_density_only"] = fe_ols(t, "k_nw", ["PropCoded", "lpop", "aged"])
    res["T_C_density_on_writing"] = fe_ols(t, "PropCoded", ["writing", "lpop", "aged"])
    res["T_D_years"] = fe_ols(t, "k_nw", ["yrs_since_w", "lpop", "aged"])

    base = res["T_A_time"]["coef"]["writing"]
    with_d = res["T_B_density"]["coef"]["writing"]
    res["verdict"] = {"coef_without_density": base, "coef_with_density": with_d,
                      "drop_share": (round(1 - with_d / base, 3) if base else None)}

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
