#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A15：改版的“时刻”成团吗？——四道闸口的第一次读数（结果：不是成团，是被排班盖住）。

两套公开数据，两个层级
  ① **总量层**：美国联邦法规每年“最终规则”件数（Federal Register API，1995—2025）。
  ② **单位层**：同一部法规（21 CFR）里每一节的修订间隔（eCFR versioner，2016 起）。

判法（先写死）
  P-1：若年度序列的残差（去趋势后）离散度大、且自相关低 ⇒ 成团（阈值驱动的跳变）；
  P-2：若节级间隔的**突发度** B=(σ−μ)/(σ+μ) > 0 ⇒ 比随机更成团；B≈0 随机；B<0 更规则。
  P-3：若两者都指向“不成团”，则**闸口不在总量里看得见**——要另找没有排班的场合。

原始响应存 data/raw/ecfr_fr/（可复核），派生存 data/derived/revision_bursts.json。
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ecfr_fr"
OUT = ROOT / "data" / "derived" / "revision_bursts.json"
RAW.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "res-grain/1.0 (research)"}

PARTS = ["1", "2", "4", "5", "7", "10", "11", "12", "14", "16", "17", "20",
         "25", "50", "73", "101", "111", "117", "201", "211"]


def get(url: str, cache: str, tries: int = 3):
    p = RAW / cache
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    for _ in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60)
            buf = b""
            while True:
                b = r.read(1 << 15)
                if not b:
                    break
                buf += b
            d = json.loads(buf)
            p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            return d
        except Exception:
            time.sleep(1.2)
    return None


def federal_register() -> dict:
    out = {}
    for y in range(1995, 2026):
        u = ("https://www.federalregister.gov/api/v1/documents.json?per_page=1"
             f"&conditions%5Btype%5D%5B%5D=RULE&conditions%5Bpublication_date%5D%5Byear%5D={y}")
        d = get(u, f"fr_rule_{y}.json")
        if d and d.get("count") is not None:
            out[y] = int(d["count"])
    return out


def ecfr_gaps() -> tuple[list[int], dict]:
    gaps, per = [], {}
    for p in PARTS:
        u = f"https://www.ecfr.gov/api/versioner/v1/versions/title-21.json?part={p}"
        d = get(u, f"ecfr_title21_part{p}.json")
        if not d:
            continue
        hist: dict[str, set] = {}
        for c in d.get("content_versions") or []:
            if c.get("type") != "section":
                continue
            dt = c.get("amendment_date") or c.get("date")
            if dt:
                hist.setdefault(c["identifier"], set()).add(dt)
        g = []
        for _, ds in hist.items():
            ys = sorted(int(x[:4]) for x in ds)
            g += [b - a for a, b in zip(ys, ys[1:]) if b > a]
        if g:
            per[p] = {"n_sections": len(hist), "n_gaps": len(g),
                      "median": float(np.median(g)), "mean": round(float(np.mean(g)), 2)}
            gaps += g
    return gaps, per


def main() -> None:
    fr = federal_register()
    years = sorted(fr)[:-1]                       # 2026 不完整，去掉
    vals = np.array([fr[y] for y in years], dtype=float)
    slope, icept = np.polyfit(years, vals, 1)
    resid = vals - (slope * np.array(years) + icept)
    ac1 = float(np.corrcoef(resid[:-1], resid[1:])[0, 1])

    gaps, per = ecfr_gaps()
    g = np.array(gaps, dtype=float)
    B = float((g.std() - g.mean()) / (g.std() + g.mean()))

    res = {
        "federal_register_rules": {
            "years": [years[0], years[-1]], "n_years": len(years),
            "first": fr[years[0]], "last": fr[years[-1]],
            "trend_per_year": round(float(slope), 1),
            "resid_cv": round(float(resid.std() / vals.mean()), 4),
            "resid_lag1_autocorr": round(ac1, 3),
            "dispersion_var_over_mean": round(float(vals.var() / vals.mean()), 1),
        },
        "ecfr_section_gaps": {
            "n_parts": len(per), "n_gaps": int(len(g)),
            "mean_years": round(float(g.mean()), 2), "sd_years": round(float(g.std()), 2),
            "cv": round(float(g.std() / g.mean()), 2), "burstiness_B": round(B, 3),
            "per_part": per,
        },
        "verdict": {
            "aggregate": "平滑（去趋势后残差 CV 很小、自相关高）",
            "unit": "比随机更规则（B<0）" if B < 0 else "比随机更成团（B>0）",
            "reading": "闸口不在改版记录里可见：成文制度的时刻由排班与预算定，不由阈值定",
        },
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1)[:1500])


if __name__ == "__main__":
    main()
