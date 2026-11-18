#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检验：文字是否把"切点成本 b"降下来，从而提高最优分类粒度 k*（第 6 章 6.14）。

设计（A 档，一天以内，公开数据）
  数据：Seshat 社会复杂度公开导出（data/raw/seshat/sc_dataset.xlsx，95 个变量 × 398 政体 × 30 NGA）。
  处理：每个（政体, 变量）取**最晚一次观测**作为该政体的值；`present`/`inferred present` 记 1；
        数值型（层级量表 1—6）取原值；`absent`/`unknown` 记 0。
  自变量：writing = 「Written records」或「Script」为 present。
  因变量（四个块，按"这批切点要不要靠文字存活"排）：
        ① 记录类（Information 去掉 4 个文字变量本身）：列表／历法／圣典／史书／哲学／科学／小说……
        ② 法律类（Law 5 变量）③ 官僚类（Bureaucracy 5 变量）④ 层级类（Hierarchical Complexity 四层之和）
        ⑤ 职业类（Professions 4 变量）
  控制：log10 人口、log10 领土，**NGA 固定效应**（去掉"哪个地区本来就更复杂"）。
  标准误：按 NGA 聚类（30 个簇）。

三条预言与判法（先写死，再看数）
  P-W1（主预言）：writing 系数 > 0，且在"切点必须被记住"的块里最大；
  P-W2（可被打掉处）：若在**不需要文字存活**的块（层级／职业）里 writing 也显著为正，
        那么"文字降的是 b"这个机制就不成立，只能说"文字伴随复杂度"；
  P-W3（标度律）：k 对 w 的弹性应落在 1/3—1/2（6.14 的 √／∛ 两律）。

输出：data/derived/writing_grain.json（+ 控制台摘要）
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "seshat" / "sc_dataset.xlsx"
OUT = ROOT / "data" / "derived" / "writing_grain.json"

WRITING_VARS = ["Written records", "Written records_1", "Script",
                "Non-phonetic writing", "Non-phonetic  writing",
                "Non-phonetic alphabetic writing", "Phonetic alphabetic writing"]
WRITE_FLAG = ["Written records", "Script"]


TEXT_VARS = ["Lists tables and classifications", "Sacred Texts", "Religious literature",
             "Practical literature", "History", "Philosophy", "Scientific literature",
             "Fiction", "Articles"]
MET_VARS = ["Calendar", "Time", "Length", "Area", "Volume", "Weight", "Geometrical"]


def to_value(v: str) -> float:
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


def build_panel() -> pd.DataFrame:
    d = pd.read_excel(SRC)
    d["val"] = d["Value From"].astype(str).str.strip().str.lower()
    d["ss"] = d["Subsection"].fillna("none").astype(str).str.strip().str.lower()
    d["date"] = pd.to_numeric(
        d["Date From"].astype(str).str.replace("CE", "").str.replace("BCE", ""),
        errors="coerce").fillna(-9e9)
    d = d.sort_values(["Polity", "Variable", "date"])
    snap = d.groupby(["Polity", "Variable"], as_index=False).last()
    snap["ss"] = snap["ss"].fillna("none").astype(str)
    snap["x"] = snap["val"].map(to_value)
    snap["obs"] = snap["val"].eq("present")          # 只留"实测 present"
    snap["inf"] = snap["val"].isin(["inferred present"])

    pols = sorted(snap["Polity"].unique())
    out = pd.DataFrame(index=pols)
    out["nga"] = snap.groupby("Polity")["NGA"].first().reindex(pols).astype(str)

    def single(var: str, col: str = "x") -> pd.Series:
        return snap[snap["Variable"] == var].set_index("Polity")[col].reindex(pols)

    for v in ["Polity Population", "Polity territory", "Settlement hierarchy",
              "Administrative levels", "Religious levels", "Military levels",
              "Indigenous coins", "Formal legal code"] + WRITE_FLAG:
        out[v] = single(v)

    out["levels"] = out[["Settlement hierarchy", "Administrative levels",
                         "Religious levels", "Military levels"]].sum(axis=1, min_count=1)

    # 四个块：k_* = 该块里"有"的变量数（块按"切点要不要靠文字存活"分）
    blocks = {"text": TEXT_VARS, "met": MET_VARS}
    for name, vs in blocks.items():
        g = snap[snap["Variable"].isin(vs)]
        out["k_" + name] = g.groupby("Polity")["x"].sum().reindex(pols)
    for name, ss in {"law": "law", "bur": "bureaucracy characteristics",
                     "prof": "professions"}.items():
        g = snap[snap["ss"] == ss]
        out["k_" + name] = g.groupby("Polity")["x"].sum().reindex(pols)

    # 只用"实测"的版本（把 inferred 全记 0），做稳健性
    snap_o = snap.copy()
    snap_o["x"] = np.where(snap["inf"], 0.0, snap["x"])   # 把 inferred present 全部记 0
    for name, vs in blocks.items():
        g = snap_o[snap_o["Variable"].isin(vs)]
        out["ko_" + name] = g.groupby("Polity")["x"].sum().reindex(pols)
    for name, ss in {"law": "law", "bur": "bureaucracy characteristics",
                     "prof": "professions"}.items():
        g = snap_o[snap_o["ss"] == ss]
        out["ko_" + name] = g.groupby("Polity")["x"].sum().reindex(pols)
    out["levels_obs"] = (snap_o[snap_o["Variable"].isin(
        ["Settlement hierarchy", "Administrative levels", "Religious levels", "Military levels"])]
        .groupby("Polity")["x"].sum().reindex(pols))

    out["writing"] = ((out["Written records"].fillna(0) > 0) |
                      (out["Script"].fillna(0) > 0)).astype(float)
    out.loc[out["Written records"].isna() & out["Script"].isna(), "writing"] = np.nan
    out["lpop"] = np.log10(out["Polity Population"].where(out["Polity Population"] > 0))
    out["lterr"] = np.log10(out["Polity territory"].where(out["Polity territory"] > 0))
    return out


def ols_cluster(df: pd.DataFrame, y: str, X: list[str], fe: bool = True) -> dict:
    df = df.dropna(subset=[y] + X).copy()
    if fe:
        for c in [y] + X:
            df[c] = df[c] - df.groupby("nga")[c].transform("mean")
        cols, names = [df[c].values for c in X], X
    else:
        cols, names = [np.ones(len(df))] + [df[c].values for c in X], ["const"] + X
    M = np.column_stack(cols)
    Y = df[y].values
    b = np.linalg.lstsq(M, Y, rcond=None)[0]
    e = Y - M @ b
    n, k = M.shape
    bread = np.linalg.pinv(M.T @ M)
    meat = np.zeros((k, k))
    for _, g in df.groupby("nga"):
        gi = df.index.get_indexer(g.index)
        Mg = M[gi]
        eg = e[gi]
        meat += Mg.T @ (eg[:, None] * eg[None, :]) @ Mg
    G = df["nga"].nunique()
    V = bread @ meat @ bread * (G / max(G - 1, 1)) * ((n - 1) / max(n - k, 1))
    se = np.sqrt(np.diag(V))
    r2 = 1 - e @ e / ((Y - Y.mean()) @ (Y - Y.mean()))
    return {"n": int(n), "nga": int(G), "r2": round(float(r2), 3),
            "coef": {nm: round(float(v), 3) for nm, v in zip(names, b)},
            "se": {nm: round(float(v), 3) for nm, v in zip(names, se)},
            "t": {nm: round(float(v), 2) for nm, v in zip(names, b / np.where(se == 0, np.nan, se))}}


def main() -> None:
    p = build_panel()
    p.to_csv(ROOT / "data" / "derived" / "writing_grain_panel.csv", index=False)
    res: dict = {"source": str(SRC.name), "n_polity": int(len(p)), "n_nga": int(p["nga"].nunique())}

    outcomes = ["k_text", "k_met", "levels", "k_law", "k_bur", "k_prof"]
    res["main"] = {y: ols_cluster(p, y, ["writing", "lpop", "lterr"]) for y in outcomes}
    obs_map = {"k_text": "ko_text", "k_met": "ko_met", "k_law": "ko_law",
               "k_bur": "ko_bur", "levels": "levels_obs", "k_prof": "ko_prof"}
    res["main_observed_only"] = {y: ols_cluster(p, obs_map[y], ["writing", "lpop", "lterr"])
                                  for y in outcomes}
    res["naive"] = {y: ols_cluster(p, y, ["writing"], fe=False) for y in outcomes}
    res["placebo_coins"] = {y: ols_cluster(p.assign(writing=p["Indigenous coins"]), y,
                                           ["writing", "lpop", "lterr"]) for y in outcomes}

    # 置换检验：只在 NGA 内部打乱 writing（n=2000），看真系数在分布里的位置
    rng = np.random.default_rng(20261118)
    perm = {}
    for y in outcomes:
        base = ols_cluster(p, y, ["writing", "lpop", "lterr"])["coef"]["writing"]
        null = []
        for _ in range(600):
            q = p.copy()
            q["writing"] = q.groupby("nga")["writing"].transform(
                lambda s: rng.permutation(s.values))
            null.append(ols_cluster(q, y, ["writing", "lpop", "lterr"])["coef"]["writing"])
        null = np.array(null)
        perm[y] = {"coef": base, "p_two_sided": round(float((np.abs(null) >= abs(base)).mean()), 4),
                   "null_sd": round(float(null.std()), 3)}
    res["permutation_within_nga"] = perm

    # 弹性：k 对人口的 dln k / dln pop（= 系数 / (中位数 k · ln10)）
    res["elasticity_pop"] = {
        y: round(res["main"][y]["coef"]["lpop"] / (float(p[y].median()) * np.log(10)), 3)
        for y in outcomes if p[y].median() > 0}

    # 描述：writing 两组的单纯对比（说明"不加控制会看到什么"）
    desc = p.groupby("writing")[["k_text", "k_met", "k_law", "k_bur", "levels", "k_prof",
                                 "Polity Population", "Polity territory"]].median()
    res["median_by_writing"] = {k: {str(i): (None if pd.isna(v) else round(float(v), 2))
                                    for i, v in row.items()} for k, row in desc.iterrows()}

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
