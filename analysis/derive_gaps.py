#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 `DERIVATION.md` §6 里三个「无」换成「有代理」。

三个参数，三条代理，全部来自盘上已有数据：
  ρ     可信具象替代供给 → PolitiFact 每年核查条数（核查产能）
  p     惩罚期望         → 人民日报每年「处置」类词条数 / 总条数
  κ     技术弹性         → 「AI 生成/换脸/伪造」占「谣言类」的比重（伪造的技术含量）

为什么这样代理，以及为什么每个都只是代理
  ρ：事实核查的产出量是「可信的具体核实」最直接的可数代理；但它只覆盖被核查的，
      且 2022 年后 PolitiFact 数据集停更——只到 2022。
  p：报纸上的处置报道不等于实际处置率，它是**可见性**。真正的 p 需要「通报数 / 事件数」。
  κ：用「AI 相关伪造 / 全部谣言类」当技术含量，是**文本份额**，不是伪造成功率。

输出
  data/derived/gap_proxies.csv   year, rho_checks, p_rate, kappa_share
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLITIFACT = ROOT / "data" / "raw" / "datasets" / "kg_politifact.zip"
RMRB = ROOT / "data" / "raw" / "datasets" / "kg_rmrb.zip"
OUT = ROOT / "data" / "derived" / "gap_proxies.csv"

AI_WORDS = ["AI生成", "AI换脸", "AI技术", "深度伪造", "智能生成", "换脸"]
RUMOR_WORDS = ["谣言", "辟谣", "造谣", "不实信息"]
PUNISH_WORDS = ["行政拘留", "查处", "被处罚", "依法处罚", "刑事拘留"]


def rho_by_year() -> dict[int, int]:
    zf = zipfile.ZipFile(POLITIFACT)
    name = zf.namelist()[0]
    data = [json.loads(l) for l in zf.read(name).decode("utf-8", "replace").splitlines() if l.strip()]
    out: dict[int, int] = {}
    for r in data:
        d = r.get("factcheck_date") or ""
        for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
            try:
                from datetime import datetime
                out[datetime.strptime(d, fmt).year] = out.get(datetime.strptime(d, fmt).year, 0) + 1
                break
            except ValueError:
                continue
    return out


def rmrb_rates() -> dict[int, dict]:
    csv.field_size_limit(50_000_000)
    zf = zipfile.ZipFile(RMRB)
    out: dict[int, dict] = {}
    for name in sorted(zf.namelist()):
        if not name.endswith(".csv"):
            continue
        year = int(name.split("_")[-1].split(".")[0])
        txt = zf.read(name).decode("utf-8-sig", errors="replace")
        n = pun = rum = ai = 0
        for r in csv.DictReader(io.StringIO(txt)):
            body = (r.get("title") or "") + " " + (r.get("content") or "")
            n += 1
            if any(w in body for w in PUNISH_WORDS):
                pun += 1
            if any(w in body for w in RUMOR_WORDS):
                rum += 1
                if any(w in body for w in AI_WORDS):
                    ai += 1
        out[year] = {"n": n, "p_rate": pun / max(n, 1),
                     "rumor_n": rum, "kappa_share": ai / max(rum, 1)}
    return out


def main() -> None:
    rho = rho_by_year()
    rm = rmrb_rates()
    years = sorted(set(rho) | set(rm))
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "rho_checks", "p_rate", "rumor_n", "kappa_share"])
        for y in years:
            r = rm.get(y, {})
            w.writerow([y, rho.get(y, ""), round(r.get("p_rate", float("nan")), 4) if r else "",
                        r.get("rumor_n", ""), round(r.get("kappa_share", float("nan")), 4) if r else ""])

    print(f"{'年':6}{'核查条数(ρ)':>13}{'处置率(p)':>11}{'谣言类条数':>11}{'AI占比(κ代理)':>15}")
    for y in years:
        r = rm.get(y, {})
        print(f"{y:6}{rho.get(y, 0):>13}" + (f"{r['p_rate']:>10.2%}{r['rumor_n']:>12}{r['kappa_share']:>14.1%}"
                                            if r else f"{'—':>10}{'—':>12}{'—':>14}"))
    print("→", OUT)


if __name__ == "__main__":
    main()
