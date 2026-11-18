#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A10：把"文字"的效应拆成两栏——编纂者的"实测"与"推断"。

问题（上一轮 A9 留下的）：Seshat 里"有文字 ⇒ 切点更多"的信号，只数实测值时消失。
这一条把它拆开，并给出一个**可读的谱**：哪些条目几乎从不靠推断，哪些条目过半靠推断。

产出三样
  1) **分解**：每个块的 writing 系数拆成 "实测 present" 与 "inferred present" 两栏（同一组控制）；
  2) **推断比谱**：每个变量的 "推断/(实测+推断)"，按条目类型排出高低；
  3) **一个可分的观测**：区域内"有"的条目越多，推断占比越低（证据越密，观测越多）——
     它只在方向上支持"编纂偏倚"这一读法，不是判决。

判法（先写死）
  P-M1：若"推断"那栏的系数 ≈ 0，而"实测"那栏正，则 A9 的判读错（工具没有影子）。
  P-M2：若"推断"那栏为正显著、而"实测"那栏为零或负，"影子"成立，但仍有两读：
         (a) 编纂偏倚（有文字 ⇒ 更容易被推断为有）；
         (b) 真存在但只留间接痕迹（这恰是文字的功能）。
  P-M3（可分的那个）：证据越密，推断占比应越低 ⇒ 支持 (a)。

输出 data/derived/inferred_spectrum.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "seshat" / "sc_dataset.xlsx"
OUT = ROOT / "data" / "derived" / "inferred_spectrum.json"

TEXT = ["Lists tables and classifications", "Sacred Texts", "Religious literature",
        "Practical literature", "History", "Philosophy", "Scientific literature",
        "Fiction", "Articles"]
MET = ["Calendar", "Time", "Length", "Area", "Volume", "Weight", "Geometrical"]
BLOCKS = {"text": TEXT, "met": MET}
DROP = ["RA", "Editor", "Expert"]


def value(v) -> float:
    v = str(v).strip().lower()
    if v in ("present", "inferred present"):
        return 1.0
    if v in ("absent", "inferred absent", "unknown") or v.startswith("suspected unknown") \
            or v.startswith("inferred inferred"):
        return 0.0
    try:
        return float(v)
    except ValueError:
        return np.nan


def panel() -> pd.DataFrame:
    d = pd.read_excel(SRC)
    d["val"] = d["Value From"].astype(str).str.strip().str.lower()
    d["ss"] = d["Subsection"].fillna("none").astype(str).str.strip().str.lower()
    d["date"] = pd.to_numeric(d["Date From"].astype(str).str.replace("CE", "").str.replace("BCE", ""),
                              errors="coerce").fillna(-9e9)
    d = d.sort_values(["Polity", "Variable", "date"])
    snap = d.groupby(["Polity", "Variable"], as_index=False).last()
    snap["ss"] = snap["ss"].fillna("none").astype(str)
    snap = snap[~snap["Variable"].isin(DROP)]
    snap["x"] = snap["val"].map(value)
    snap["p"] = (snap["val"] == "present").astype(float)          # 实测
    snap["i"] = (snap["val"] == "inferred present").astype(float)  # 推断

    pols = sorted(snap["Polity"].unique())
    o = pd.DataFrame(index=pols)
    o["nga"] = snap.groupby("Polity")["NGA"].first().reindex(pols).astype(str)
    for v in ["Polity Population", "Polity territory"]:
        o[v] = snap[snap["Variable"] == v].set_index("Polity")["x"].reindex(pols)
    w = snap[snap["Variable"].isin(["Written records", "Script"])]
    o["writing"] = w.groupby("Polity")["x"].max().reindex(pols)
    o["lpop"] = np.log10(o["Polity Population"].where(o["Polity Population"] > 0))
    o["lterr"] = np.log10(o["Polity territory"].where(o["Polity territory"] > 0))

    for name, vs in BLOCKS.items():
        sub = snap[snap["Variable"].isin(vs)]
        for tag, col in [("k_", "x"), ("p_", "p"), ("i_", "i")]:
            o[tag + name] = sub.groupby("Polity")[col].sum().reindex(pols)
    for name, ss in {"law": "law", "bur": "bureaucracy characteristics",
                     "prof": "professions"}.items():
        sub = snap[snap["ss"] == ss]
        for tag, col in [("k_", "x"), ("p_", "p"), ("i_", "i")]:
            o[tag + name] = sub.groupby("Polity")[col].sum().reindex(pols)
    return o, snap


def ols_cluster(df: pd.DataFrame, y: str, X: list[str]) -> dict:
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
    return {"n": int(n), "coef": round(float(b[0]), 2), "t": round(float(b[0] / se[0]), 2)}


def main() -> None:
    o, snap = panel()
    res: dict = {"source": SRC.name, "n_polity": int(len(o))}

    X = ["writing", "lpop", "lterr"]
    dec = {}
    for nm in ["text", "met", "law", "bur", "prof"]:
        dec[nm] = {"total": ols_cluster(o, "k_" + nm, X),
                   "observed": ols_cluster(o, "p_" + nm, X),
                   "inferred": ols_cluster(o, "i_" + nm, X)}
    res["decomposition"] = dec

    # 推断比谱：每个二值变量一行
    rows = []
    for var, g in snap.groupby("Variable"):
        if g["x"].dropna().isin([0.0, 1.0]).mean() < 0.9:      # 只留二值型条目
            continue
        pos = g["p"].sum() + g["i"].sum()
        if pos < 20:
            continue
        rows.append({"var": var, "ss": g["ss"].iloc[0],
                     "positives": int(pos),
                     "inferred_share": round(float(g["i"].sum() / pos), 3)})
    spec = pd.DataFrame(rows).sort_values("inferred_share", ascending=False)
    res["spectrum"] = spec.to_dict(orient="records")
    res["spectrum_summary"] = {
        "n": int(len(spec)),
        "median": round(float(spec["inferred_share"].median()), 3),
        "p90": round(float(spec["inferred_share"].quantile(0.9)), 3),
        "p10": round(float(spec["inferred_share"].quantile(0.1)), 3),
    }

    # 可分观测：区域内，"有"的条目数 vs 推断占比
    g = snap.groupby("Polity").agg(pos=("x", lambda s: float((s.fillna(0) > 0).sum())),
                                   inf=("i", "sum"), nga=("NGA", "first"))
    g = g[g["pos"] > 0]
    g["infshare"] = g["inf"] / g["pos"]
    a = g["infshare"] - g.groupby("nga")["infshare"].transform("mean")
    b = g["pos"] - g.groupby("nga")["pos"].transform("mean")
    rho = float((a * b).sum() / np.sqrt((a ** 2).sum() * (b ** 2).sum()))
    res["evidence_density"] = {"n_polity": int(len(g)),
                               "within_nga_rho": round(rho, 3),
                               "mean_infshare": round(float(g["infshare"].mean()), 3)}

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    spec.to_csv(ROOT / "data" / "derived" / "inferred_spectrum.csv", index=False)
    print(json.dumps({k: res[k] for k in ("decomposition", "spectrum_summary", "evidence_density")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
