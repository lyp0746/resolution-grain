#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""逐条检验文档里的经验断言（第一批：可作为 A/B 级的那些）。

测试项
  A  P7 生育率作为 E_t 下游：WVS 信任 × OWID 生育率
  B  "利女爱女" 是否可测：WVS 性别态度跨波趋势（C001、D059）
  C  中国侧"通报—报道"时差分布（Bing 事件簇）
  D  V-Dem 的制度变化是渐变还是跃变（与 Seshat 同法对照）
  E  Gallup 原文里的代际梯度（65+ vs 65−）

输出 data/derived/claims_tests.json
"""
from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "claims_tests.json"
WAVE_YEAR = {1: 1982, 2: 1991, 3: 1996, 4: 2001, 5: 2007, 6: 2012}
NAME_MAP = {
    "Bosnia": "Bosnia and Herzegovina", "Bosnian Federation": "Bosnia and Herzegovina",
    "Cyprus (G)": "Cyprus", "Czech Rep.": "Czechia", "Dominican Rep.": "Dominican Republic",
    "Great Britain": "United Kingdom", "Macedonia": "North Macedonia",
    "Serbia and Montenegro": "Serbia", "Viet Nam": "Vietnam",
}


def wvs() -> pd.DataFrame:
    z = zipfile.ZipFile(ROOT / "data" / "raw" / "datasets" / "kg_wvs.zip")
    rows = list(csv.DictReader(io.StringIO(z.read("WVS_per_Country.csv").decode("utf-8", errors="replace"))))
    out = []
    for r in rows:
        try:
            w = int(float(r["Wave"]))
        except (KeyError, ValueError):
            continue
        rec = {"country": NAME_MAP.get(r["Country"], r["Country"]),
               "wave": w, "year": WAVE_YEAR.get(w)}
        for k, v in (("trust", "A165"), ("c001", "C001"), ("d059", "D059")):
            try:
                rec[k] = float(r[v])
            except (KeyError, ValueError):
                rec[k] = np.nan
        if not np.isnan(rec["trust"]):
            rec["E"] = 2.0 - rec["trust"]
        else:
            rec["E"] = np.nan
        out.append(rec)
    return pd.DataFrame(out)


def owid(name: str) -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "raw" / f"{name}.csv")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    for c in df.columns:
        if c not in ("Entity", "Code", "Year"):
            num = pd.to_numeric(df[c], errors="coerce")
            if num.notna().mean() > 0.5:
                df[c] = num
    return df


def valcol(df: pd.DataFrame) -> str:
    for c in df.columns:
        if c not in ("Entity", "Code", "Year") and pd.api.types.is_numeric_dtype(df[c]):
            return c
    raise KeyError("no numeric value column")


def test_A(w: pd.DataFrame) -> dict:
    f = owid("owid_fertility")
    col = valcol(f)
    rows = []
    for _, r in w.iterrows():
        if np.isnan(r["E"]) or pd.isna(r["year"]):
            continue
        sub = f[(f["Entity"] == r["country"]) & ((f["Year"] - r["year"]).abs() <= 2)]
        if sub.empty:
            continue
        tfr = float(sub.sort_values("Year", key=lambda s: (s - r["year"]).abs()).iloc[0][col])
        rows.append({"country": r["country"], "year": r["year"], "E": r["E"], "tfr": tfr})
    d = pd.DataFrame(rows).dropna()
    if len(d) < 20:
        return {"n": len(d), "note": "匹配不足"}
    pooled = float(d["E"].corr(d["tfr"]))
    # 组内（去掉国家均值）
    dm = d.copy()
    for c in ("E", "tfr"):
        dm[c] = dm[c] - dm.groupby("country")[c].transform("mean")
    within = float(dm["E"].corr(dm["tfr"]))
    # 控制人均 GDP（Maddison）
    g = owid("owid_maddison")
    gcol = valcol(g)
    gdp = []
    for _, r in d.iterrows():
        s = g[(g["Entity"] == r["country"]) & ((g["Year"] - r["year"]).abs() <= 3)]
        gdp.append(float(s[gcol].mean()) if not s.empty else np.nan)
    d["lgdp"] = np.log(pd.Series(gdp).replace(0, np.nan))
    dd = d.dropna()
    if len(dd) > 20:
        X = np.column_stack([np.ones(len(dd)), dd["lgdp"], dd["E"]])
        beta, *_ = np.linalg.lstsq(X, dd["tfr"], rcond=None)
        resid = dd["tfr"] - X @ beta
        s2 = resid @ resid / (len(dd) - 3)
        se = float(np.sqrt(s2 * np.linalg.inv(X.T @ X)[2, 2]))
        coef_ctrl = float(beta[2]); se_ctrl = se
    else:
        coef_ctrl = se_ctrl = None
    return {"n": len(d), "pooled_corr": round(pooled, 3), "within_country_corr": round(within, 3),
            "tfr_coef_on_E_ctrl_lgdp": round(coef_ctrl, 3) if coef_ctrl is not None else None,
            "se": round(se_ctrl, 3) if se_ctrl is not None else None,
            "n_with_gdp": int(len(dd))}


def test_B(w: pd.DataFrame) -> dict:
    out = {}
    for k in ("c001", "d059"):
        s = w.dropna(subset=[k])
        by = s.groupby("wave")[k].agg(["mean", "count"]).round(3)
        out[k] = {"by_wave": {int(i): [float(r["mean"]), int(r["count"])] for i, r in by.iterrows()}}
        # 同一国家波 1 与波 6 的配对变化
        p = s[s["wave"].isin([1, 6])].pivot_table(index="country", columns="wave", values=k).dropna()
        p.columns = [int(c) for c in p.columns]
        if len(p) >= 5 and {1, 6}.issubset(set(p.columns)):
            out[k]["paired_w1_w6"] = {"n": int(len(p)),
                                      "mean_change": round(float((p[6] - p[1]).mean()), 3),
                                      "share_moving_egalitarian": round(float(((p[6] - p[1]) > 0).mean()), 3)}
    return out


def test_C() -> dict:
    p = ROOT / "data" / "derived" / "events_candidates.csv"
    if not p.exists():
        return {"note": "no events"}
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    lags = []
    for r in rows:
        if r["first_tongbao"] and r["first_report"]:
            d = (pd.Timestamp(r["first_tongbao"]) - pd.Timestamp(r["first_report"])).days
            lags.append(d)
    a = np.array(lags)
    return {"n": int(len(a)),
            "median": float(np.median(a)), "p25": float(np.percentile(a, 25)),
            "p75": float(np.percentile(a, 75)),
            "share_negative": round(float((a < 0).mean()), 3),
            "share_0_3": round(float(((a >= 0) & (a <= 3)).mean()), 3)}


def test_D() -> dict:
    df = pd.read_csv(ROOT / "data" / "raw" / "owid_democracy.csv")
    col = valcol(df)
    df = df.dropna(subset=[col])
    changes = []
    for _, g in df.groupby("Entity"):
        g = g.sort_values("Year")
        changes.extend(np.diff(g[col].values))
    a = np.abs(np.array(changes))
    a = a[a > 0]
    if len(a) < 100:
        return {"note": "insufficient"}
    return {"n_changes": int(len(a)),
            "mean_abs": round(float(a.mean()), 4),
            "kurtosis": round(float(pd.Series(a).kurt()), 2),
            "share_top10pct_of_total_change": round(float(np.sort(a)[-int(len(a) * 0.1):].sum() / a.sum()), 3),
            "share_ge_0.02": round(float((a >= 0.02).mean()), 3)}


def test_E() -> dict:
    p = ROOT / "data" / "raw" / "gallup_media_trust.html"
    if not p.exists():
        return {"note": "no gallup snapshot"}
    txt = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="ignore"))
    txt = re.sub(r"\s+", " ", txt)
    hits = [m.strip() for m in re.findall(r".{0,80}(?:65|43%).{0,80}", txt)]
    return {"n_hits": len(hits), "samples": hits[:5]}


def main() -> None:
    w = wvs()
    res = {
        "source": "WVS per-country (kaggle), OWID fertility/maddison/democracy, Bing clusters, Gallup snapshot",
        "A_P7_trust_vs_tfr": test_A(w),
        "B_gender_attitudes": test_B(w),
        "C_china_tongbao_lag": test_C(),
        "D_vdem_punctuation": test_D(),
        "E_gallup_age": test_E(),
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
