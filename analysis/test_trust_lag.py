#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""删数据之前必须做的最后一件分析：信任滞后于收益变化吗？

为什么这是"该做的"
  `FIRST-PRINCIPLE.md` §5.4 把 `E_t` 降为 `θ` 的一阶矩（导出量），
  由此给出一条可判推论：**`E_t` 的变化应当滞后于收益变化**——因为要先把 `θ` 的分布改掉，
  而分布靠选择（复制子）改变，不是当期反应。

  这条推论**只能在大样本面板上测**，而 ESS 11 轮（283 个国家-轮次）正好是那份数据。
  所以：**先做这一件，再删 1.7 GB。**

做法
  每国相邻两轮之间的：
    Δtrust  = trust(t) − trust(t−1)
    g_same  = Δlog GDPpc，区间 [t−1, t]（同期）
    g_lag   = Δlog GDPpc，区间 [t−2, t−1]（前一期）
  比较 Δtrust 与两者的相关。**滞后强于同期 ⇒ 支持"θ 靠选择改变"。**

输出
  data/derived/trust_lag.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ESS = ROOT / "data" / "raw" / "datasets" / "ess_full" / "european_social_survey_2002-2023.csv"
MADDISON = ROOT / "data" / "raw" / "owid_maddison.csv"
OUT = ROOT / "data" / "derived" / "trust_lag.csv"

ISO2 = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus",
    "CZ": "Czechia", "DE": "Germany", "DK": "Denmark", "EE": "Estonia", "ES": "Spain",
    "FI": "Finland", "FR": "France", "GB": "United Kingdom", "GR": "Greece", "HR": "Croatia",
    "HU": "Hungary", "IE": "Ireland", "IL": "Israel", "IS": "Iceland", "IT": "Italy",
    "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "ME": "Montenegro", "NL": "Netherlands",
    "NO": "Norway", "PL": "Poland", "PT": "Portugal", "RO": "Romania", "RS": "Serbia",
    "RU": "Russia", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "TR": "Turkey",
    "UA": "Ukraine", "XK": "Kosovo",
}

ROUND_YEAR = {1: 2002, 2: 2004, 3: 2006, 4: 2008, 5: 2010, 6: 2012,
              7: 2014, 8: 2016, 9: 2018, 10: 2020, 11: 2023}


def main() -> None:
    if not ESS.exists():
        print("ESS 全量文件不存在，跳过")
        return

    # 1) 分块读，只取三列
    use = ["cntry", "essround", "ppltrst"]
    chunks = []
    for ch in pd.read_csv(ESS, usecols=use, chunksize=400_000, low_memory=False):
        chunks.append(ch)
    d = pd.concat(chunks, ignore_index=True)
    d["ppltrst"] = pd.to_numeric(d["ppltrst"], errors="coerce")
    d = d[d["ppltrst"].between(0, 10)]
    g = (d.groupby(["cntry", "essround"])["ppltrst"]
         .agg(["mean", "count"]).reset_index())
    g = g[g["count"] >= 300]
    g["year"] = g["essround"].map(ROUND_YEAR)
    g["entity"] = g["cntry"].map(ISO2)
    g = g.dropna(subset=["entity", "year"])
    print(f"国家-轮次 {len(g)}（每轮 ≥300 人）")

    # 2) GDP per capita（Maddison 长序列）
    m = pd.read_csv(MADDISON)
    col = [c for c in m.columns if "gdp" in c.lower() and "annot" not in c.lower()][0]
    m = m.rename(columns={"Entity": "country", "Year": "year", col: "gdppc"})
    m["year"] = pd.to_numeric(m["year"], errors="coerce")
    m = m.dropna(subset=["year", "gdppc"])
    m["year"] = m["year"].astype(int)
    print(f"Maddison 覆盖 {m.country.nunique()} 个实体，{m.year.min()}—{m.year.max()}")

    rows = []
    for cntry, sub in g.sort_values("year").groupby("entity"):
        sub = sub.reset_index(drop=True)
        for i in range(1, len(sub)):
            t0, t1 = sub.loc[i - 1, "year"], sub.loc[i, "year"]
            if t1 - t0 < 1:
                continue
            gf = lambda a, b: np.log(_gdppc(m, cntry, b)) - np.log(_gdppc(m, cntry, a))  # noqa: E731
            try:
                g_same = gf(t0, t1)
                g_lag = gf(t0 - (t1 - t0), t0)
            except Exception:  # noqa: BLE001
                continue
            if not (np.isfinite(g_same) and np.isfinite(g_lag)):
                continue
            rows.append({"country": cntry, "t0": t0, "t1": t1,
                         "d_trust": sub.loc[i, "mean"] - sub.loc[i - 1, "mean"],
                         "g_same": g_same, "g_lag": g_lag})
    r = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    r.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"\n可配对转移 {len(r)} 条")
    print(f"Δtrust × 同期增长 r = {r.d_trust.corr(r.g_same):+.3f}")
    print(f"Δtrust × 前期增长 r = {r.d_trust.corr(r.g_lag):+.3f}")
    print(f"Δtrust 均值 {r.d_trust.mean():+.4f}；同期增长均值 {r.g_same.mean():+.3f}")


def _gdppc(m: pd.DataFrame, country: str, year: int) -> float:
    s = m[(m.country == country) & (m.year == year)]["gdppc"]
    if len(s):
        return float(s.iloc[0])
    # 邻近插值（±2 年）
    for k in (1, 2):
        for y in (year - k, year + k):
            s = m[(m.country == country) & (m.year == y)]["gdppc"]
            if len(s):
                return float(s.iloc[0])
    raise ValueError("no gdp")


if __name__ == "__main__":
    main()
