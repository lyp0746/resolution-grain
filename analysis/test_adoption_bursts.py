#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A16：在没有统一排班的地方，采纳的“时刻”成团吗？——历法采纳（1582—2016）。

A15 的结论是：成文法规的改版时刻**不成团**（B=−0.20），因为被排班与预算盖住。
这一节换一类事件：**历法采纳**。它不是由某一个组织统一排期的（除了 1582 那一次诏书），
所以如果“闸口”真的存在，成团性应当露出来。

判法（先写死）
  B = (σ−μ)/(σ+μ)：>0 成团、≈0 随机（泊松）、<0 更规则。
  P-G1：若 B>0.3 ⇒ 采纳时刻显著成团，与 A15 对照成立；
  P-G2：若成团的年份能对上“上位层面的约束集改写”（诏书、战后重建、政权更替），
        那么成团的不是阈值，而是**复位**——这正是 ch28 表 28.3 第四行。

数据：维基百科 "List of adoption dates of the Gregorian calendar by country" 的表格
（原始 wikitext 已缓存 data/raw/wiki_gregorian_by_country.txt；解析取每行第一个四位年份）。
质量：B（条目本身有引注，但"国家"边界与年内的具体日期不齐；只用于分布形状）。

输出 data/derived/gregorian_adoption.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "wiki_gregorian_by_country.txt"
OUT = ROOT / "data" / "derived" / "gregorian_adoption.json"


def parse(txt: str) -> dict[str, int]:
    rows, cur = [], []
    for line in txt.split("\n"):
        if line.startswith("|-"):
            if cur:
                rows.append(cur)
            cur = []
        elif line.startswith("|"):
            cur.append(line.strip("|").strip())
    if cur:
        rows.append(cur)

    out: dict[str, int] = {}
    for r in rows:
        years = [int(m.group(0)) for c in r for m in re.finditer(r"\b1[5-9]\d\d\b|\b20\d\d\b", c)]
        name = next((c for c in r if re.match(r"^\[\[[A-Z]", c)), None)
        if years and name:
            key = re.sub(r"\[\[|\]\]", "", name).split("|")[0].strip()
            out.setdefault(key, min(years))
    return out


def burstiness(g: np.ndarray) -> float:
    return float((g.std() - g.mean()) / (g.std() + g.mean()))


def main() -> None:
    txt = SRC.read_text(encoding="utf-8")
    ad = parse(txt)
    ys = np.array(sorted(ad.values()), dtype=float)
    gaps = np.diff(ys)
    B = burstiness(gaps)
    top = {}
    for y in ys:
        top[int(y)] = top.get(int(y), 0) + 1
    top_years = sorted(top.items(), key=lambda kv: -kv[1])[:5]

    res = {
        "source": SRC.name,
        "n_countries": int(len(ys)),
        "year_range": [int(ys.min()), int(ys.max())],
        "mean_gap": round(float(gaps.mean()), 2),
        "sd_gap": round(float(gaps.std()), 2),
        "cv": round(float(gaps.std() / gaps.mean()), 2),
        "burstiness_B": round(B, 3),
        "top_years": top_years,
        "years": [int(y) for y in ys],
        "share_in_top4_years": round(sum(c for _, c in top_years[:4]) / len(ys), 3),
        "poisson_B": 0.0,
        "verdict": ("成团（B>0.3）：采纳时刻聚在上位事件附近" if B > 0.3
                    else "不成团：与 A15 同向"),
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
