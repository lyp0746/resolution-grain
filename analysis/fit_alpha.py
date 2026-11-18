#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""用 WVS 六波拟合耗竭指数 α。

模型（来自正文）：
    E_{t+1} = E_t − δ·s·E_t^α + ρ(1−E_t)
若暂令 ρ≈0（替代供给不足的社会），则
    −dE/dt = k·E^α        ⇒  ln(−dE/dt) = ln k + α·ln E
α<1 表示"越低越快"（加速耗竭），α=1 为指数衰减，α>1 为减速。

数据：WVS 国家×波次聚合（A165 "Most people can be trusted"，1=可信任，2=需小心）
      E = 2 − A165（转为 0—1 的信任份额）
波次中点：1:1982 2:1991 3:1996 4:2001 5:2007 6:2012

输出
  data/derived/alpha_wvs_panel.csv   每条波次转移一行
  data/derived/alpha_wvs.json        拟合结果与稳健性
注意：E 有测量误差，log-log 斜率会向 0 衰减（attenuation），α 的估计偏小。
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "datasets" / "kg_wvs.zip"
OUT = ROOT / "data" / "derived"
WAVE_YEAR = {1: 1982, 2: 1991, 3: 1996, 4: 2001, 5: 2007, 6: 2012}


def load() -> list[dict]:
    z = zipfile.ZipFile(SRC)
    rows = list(csv.DictReader(io.StringIO(z.read("WVS_per_Country.csv").decode("utf-8", errors="replace"))))
    out = []
    for r in rows:
        try:
            e = 2.0 - float(r["A165"])
            w = int(float(r["Wave"]))
        except (KeyError, ValueError, TypeError):
            continue
        if not (0.0 <= e <= 1.0) or w not in WAVE_YEAR:
            continue
        out.append({"country": r["Country"], "wave": w, "year": WAVE_YEAR[w], "E": e})
    return out


def main() -> None:
    rows = load()
    by_c = {}
    for r in rows:
        by_c.setdefault(r["country"], {})[r["wave"]] = r

    panel = []
    for c, ws in by_c.items():
        for w in sorted(ws):
            if w + 1 not in ws:
                continue
            a, b = ws[w], ws[w + 1]
            dt = b["year"] - a["year"]
            dE = b["E"] - a["E"]
            panel.append({"country": c, "wave_from": w, "wave_to": w + 1,
                          "year_from": a["year"], "year_to": b["year"], "dt": dt,
                          "E_from": a["E"], "E_to": b["E"], "dE": dE,
                          "rate_decline": -dE / dt, "E_mid": (a["E"] + b["E"]) / 2})

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "alpha_wvs_panel.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(panel[0]))
        w.writeheader()
        w.writerows(panel)

    def fit(sel, label):
        xs = np.log(np.array([p["E_mid"] for p in sel]))
        ys = np.log(np.array([p["rate_decline"] for p in sel]))
        X = np.column_stack([np.ones_like(xs), xs])
        beta, *_ = np.linalg.lstsq(X, ys, rcond=None)
        resid = ys - X @ beta
        dof = len(xs) - 2
        s2 = (resid @ resid) / dof
        cov = s2 * np.linalg.inv(X.T @ X)
        se = float(np.sqrt(cov[1, 1]))
        r2 = 1 - (resid @ resid) / ((ys - ys.mean()) @ (ys - ys.mean()))
        return {"label": label, "n": len(xs), "alpha": round(float(beta[1]), 4),
                "se": round(se, 4), "ci95": [round(float(beta[1] - 1.96 * se), 4),
                                             round(float(beta[1] + 1.96 * se), 4)],
                "intercept": round(float(beta[0]), 4), "r2": round(float(r2), 4)}

    dep = [p for p in panel if p["dE"] < 0]
    fits = [fit(dep, "all declining transitions")]
    # 按波次分段的稳健性
    for w in sorted({p["wave_from"] for p in dep}):
        sub = [p for p in dep if p["wave_from"] == w]
        if len(sub) >= 20:
            fits.append(fit(sub, f"wave {w}→{w+1}"))
    # 去掉极端值（|E-0.5| 小、噪声大的观测）
    fits.append(fit([p for p in dep if 0.05 < p["E_mid"] < 0.95], "trim E in (0.05,0.95)"))

    summary = {
        "source": "kaggle:fernandol/world-values-survey",
        "variable": "A165 (1=trusted, 2=careful) → E = 2 − A165",
        "n_countries": len(by_c), "n_transitions": len(panel),
        "n_declining": len(dep),
        "share_declining": round(len(dep) / len(panel), 4),
        "alpha_pooled": fits[0],
        "fits": fits,
        "caveat": "测量误差使 log-log 斜率向 0 衰减，α 偏向低估；波次间隔 5—10 年，"
                  "中间过程不可见；A165 为单题，信度有限。ρ 设为 0 是强假设。",
    }
    (OUT / "alpha_wvs.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
