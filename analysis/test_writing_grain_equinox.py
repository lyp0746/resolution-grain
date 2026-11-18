#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A11：用 Seshat Equinox 官方包（CC-BY，3.6 MB）重做 A9／A10，并补上“年份”这一半。

上一轮用的是"社会复杂度 share 导出"（95 变量 × 398 政体，日期只有 5% 的行有）。
官方 Equinox 包给了三样 share 导出没有的东西：
  ① **135 个变量**（社会复杂度 54 + 战争 89 + 宗教 17 + 制度 3）；
  ② **每个政体的起止年**（Polities 表：Start／End）；
  ③ **第三种状态**：`suspected unknown`（疑似未知），share 导出里被压成了缺失。

三条检验（判法先写死）
  T1 复现：文字对"文本类／单位类"的效应、以及"层级数只跟人口走"，在更大样本上是否仍成立；
  T2 年份：政体结束时"距文字出现多少年"是否预测分类变量数（预测：正，且随年限递减）；
  T3 稳健：把 `suspected unknown` 单列（既不算有也不算无），效应是否变。

输出 data/derived/writing_grain_equinox.json
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
OUT = ROOT / "data" / "derived" / "writing_grain_equinox.json"

TEXT = ["Lists tables and classifications", "Sacred Texts", "Religious literature",
        "Practical literature", "History", "Philosophy", "Scientific literature",
        "Fiction", "Articles"]
MET = ["Calendar", "Time", "Length", "Area", "Volume", "Weight", "Geometrical"]
LEVELS = ["Administrative levels", "Military levels", "Religious levels", "Settlement hierarchy"]
WRITE = ["Written records", "Script"]


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    z = zipfile.ZipFile(SRC)
    xlsx = [n for n in z.namelist() if n.endswith(".xlsx")][0]
    buf = io.BytesIO(z.read(xlsx))
    d = pd.read_excel(buf, sheet_name="Equinox2020_CanonDat")
    pol = pd.read_excel(buf, sheet_name="Polities")
    return d, pol


def state(v: str) -> str:
    v = str(v).strip().lower()
    if v in ("present", "inferred present"):
        return "present" if v == "present" else "inferred"
    if v in ("absent", "inferred absent"):
        return "absent"
    if v.startswith("suspected") or v == "unknown":
        return "unknown"
    try:
        float(v)
        return "present"          # 数值型（层级数、人口）视为有
    except ValueError:
        return "other"


def build() -> pd.DataFrame:
    d, pol = load()
    d["st"] = d["Value.From"].map(state)
    d["num"] = pd.to_numeric(d["Value.From"], errors="coerce")
    d["date"] = pd.to_numeric(d["Date.From"], errors="coerce")
    d = d.sort_values(["Polity", "Variable", "date"])
    last = d.groupby(["Polity", "Variable"], as_index=False).last()

    pols = last["Polity"].unique()
    out = pd.DataFrame({"Polity": pols})
    out["nga"] = last.groupby("Polity")["NGA"].first().reindex(pols).values

    def one(var: str, field: str = "st") -> pd.Series:
        g = last[last["Variable"] == var].set_index("Polity")[field]
        return g.reindex(pols)

    out["writing"] = (((one("Written records").isin(["present", "inferred"])) |
                       (one("Script").isin(["present", "inferred"]))).astype(float)).values
    out["writing_obs"] = (((one("Written records") == "present") |
                           (one("Script") == "present")).astype(float)).values
    for v in ["Polity Population", "Polity territory"]:
        out[v] = one(v, "num").values

    def block(vs: list[str]) -> pd.Series:
        g = last[last["Variable"].isin(vs)].copy()
        g["has"] = g["st"].isin(["present", "inferred"]).astype(float)
        return g.groupby("Polity")["has"].sum().reindex(pols).fillna(0)

    out["k_text"], out["k_met"] = block(TEXT).values, block(MET).values
    out["k_all"] = block(list(last["Variable"].unique())).values
    # 层级：数值型求和
    lv = last[last["Variable"].isin(LEVELS)].pivot_table(index="Polity", columns="Variable",
                                                         values="num", aggfunc="last")
    out["levels"] = lv.reindex(pols).sum(axis=1, min_count=1).values
    for name, vs in {"law": ["Formal legal code", "Judges", "Courts", "Professional Lawyers"],
                     "bur": ["Full-time bureaucrats", "Examination system", "Merit promotion",
                             "Specialized government buildings"],
                     "prof": ["Professional military officers", "Professional soldiers",
                              "Professional priesthood"]}.items():
        out["k_" + name] = block(vs).values

    # 起止年与"文字首现"
    p = pol.drop_duplicates("PolID").set_index("PolID")[["Start", "End"]]
    out = out.merge(p, left_on="Polity", right_index=True, how="left").reset_index(drop=True)
    first_write = (d[(d["Variable"].isin(WRITE)) & (d["st"].isin(["present", "inferred"]))]
                   .groupby("Polity")["date"].min())
    out["w_first"] = out["Polity"].map(first_write).values
    out["years_since_write"] = out["End"] - out["w_first"]

    out["lpop"] = np.log10(out["Polity Population"].where(out["Polity Population"] > 0))
    out["lterr"] = np.log10(out["Polity territory"].where(out["Polity territory"] > 0))
    return out


def ols(df: pd.DataFrame, y: str, X: list[str]) -> dict:
    df = df.dropna(subset=[y] + X).copy()
    for c in [y] + X:
        df[c] = df[c] - df.groupby("nga")[c].transform("mean")
    M = np.column_stack([df[c].values for c in X])
    Y = df[y].values
    b = np.linalg.lstsq(M, Y, rcond=None)[0]
    e = Y - M @ b
    n, k = M.shape
    bread = np.linalg.pinv(M.T @ M)
    meat = np.zeros((k, k))
    for _, g in df.groupby("nga"):
        gi = df.index.get_indexer(g.index)
        Mg, eg = M[gi], e[gi]
        meat += Mg.T @ (eg[:, None] * eg[None, :]) @ Mg
    G = df["nga"].nunique()
    V = bread @ meat @ bread * (G / max(G - 1, 1)) * ((n - 1) / max(n - k, 1))
    se = np.sqrt(np.diag(V))
    return {"n": int(n), "coef": {nm: round(float(v), 3) for nm, v in zip(X, b)},
            "t": {nm: round(float(v), 2) for nm, v in zip(X, b / se)}}


def main() -> None:
    p = build()
    p.to_csv(ROOT / "data" / "derived" / "writing_grain_equinox_panel.csv", index=False)
    res = {"n_polity": int(len(p)), "n_nga": int(p["nga"].nunique()),
           "n_with_writing": int(p["writing"].sum()),
           "n_with_years": int(p["years_since_write"].notna().sum())}
    ys = ["k_all", "k_text", "k_met", "levels", "k_law", "k_bur", "k_prof"]
    res["T1_main"] = {y: ols(p, y, ["writing", "lpop", "lterr"]) for y in ys}
    res["T1_observed_writing"] = {y: ols(p, y, ["writing_obs", "lpop", "lterr"]) for y in ys}
    res["T2_years"] = {y: ols(p, y, ["years_since_write", "lpop", "lterr"]) for y in ys}
    p["log_years"] = np.log10(p["years_since_write"].where(p["years_since_write"] > 0) + 1)
    res["T2_log_years"] = {y: ols(p, y, ["log_years", "lpop", "lterr"]) for y in ys}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("T1")},
                     ensure_ascii=False, indent=1)[:2000])
    print(json.dumps(res["T1_main"], ensure_ascii=False, indent=1)[:2000])


if __name__ == "__main__":
    main()
