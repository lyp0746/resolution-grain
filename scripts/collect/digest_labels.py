#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""标签密度与精度：三份语料一起量（热搜标题 / 人民日报正文 / 微博正文）。

为什么需要这个脚本
  `REQUESTS.md` 说「热搜标题法失败」，命中率 0.006%—0.2%。
  但那只是**密度低**，还是**词选错**？两个原因要分开量。

做法
  对每个标签词，同时算两个数：
    raw      正文里出现该词的条数 / 总条数
    anchored 正文里出现该词**且**出现「网传/网友/视频/自媒体/当事人/平台/通报」
             之一的条数 / 总条数
  anchored/raw 是**精度的下界代理**（不是人工标注）：它筛掉「电影剧本」「行情反转」
  这类非本义的用法。

输出
  data/derived/label_density.csv

纪律
  这是**词表法**，不是人工编码。报告时必须写：密度是下界、精度是代理，
  真正的标签需要抽样人工核验（每语料 100 条即可）。
"""
from __future__ import annotations

import csv
import io
import random
import re
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "derived" / "label_density.csv"
RMRB = ROOT / "data" / "raw" / "datasets" / "kg_rmrb.zip"
WEIBO = ROOT / "data" / "raw" / "hf" / "weibo_hot_processed"

LABELS = {
    "摆拍": ["摆拍", "自导自演", "剧情演绎"],
    "剧本": ["剧本"],
    "反转": ["反转"],
    "谣言": ["谣言", "辟谣", "造谣", "不实信息"],
    "官方介入": ["公安", "警方", "通报", "行政拘留"],
}
ANCHOR = ["网传", "网友", "视频", "自媒体", "当事人", "平台", "通报", "热搜"]


def score(docs) -> dict:
    n = 0
    raw = Counter()
    anch = Counter()
    for b in docs:
        n += 1
        has_anchor = any(a in b for a in ANCHOR)
        for k, ws in LABELS.items():
            if any(w in b for w in ws):
                raw[k] += 1
                if has_anchor:
                    anch[k] += 1
    return {"n": n, **{f"raw_{k}": raw[k] for k in LABELS}, **{f"anch_{k}": anch[k] for k in LABELS}}


def rmrb_docs(years):
    zf = zipfile.ZipFile(RMRB)
    for y in years:
        name = f"RenMin_Daily_{y}.csv"
        if name not in zf.namelist():
            continue
        txt = zf.read(name).decode("utf-8-sig", errors="replace")
        for row in csv.DictReader(io.StringIO(txt)):
            yield row.get("title", "") + " " + row.get("content", "")


def weibo_docs():
    for p in sorted(WEIBO.glob("*.csv")):
        txt = p.read_bytes().decode("utf-8-sig", errors="replace")
        for row in csv.DictReader(io.StringIO(txt)):
            yield (row.get("title") or "") + " " + (row.get("text") or "")


def hot_search_titles():
    """2020—21 微博热搜标题（已有抽样，标题字段）。"""
    p = ROOT / "data" / "raw" / "datasets" / "kg_weibo_hot.zip"
    if not p.exists():
        return
    zf = zipfile.ZipFile(p)
    for name in zf.namelist():
        if not name.endswith(".csv"):
            continue
        txt = zf.read(name).decode("utf-8-sig", errors="replace")
        for row in csv.DictReader(io.StringIO(txt)):
            yield " ".join(str(v) for v in list(row.values())[:3])


def main() -> None:
    rows = []
    for lab, gen in [("人民日报正文 2022—2025", lambda: rmrb_docs([2022, 2023, 2024, 2025])),
                     ("人民日报正文 2024", lambda: rmrb_docs([2024])),
                     ("微博正文（热搜话题，2026-11 抽样）", weibo_docs),
                     ("微博热搜标题 2020—21", hot_search_titles)]:
        r = score(gen())
        if not r["n"]:
            continue
        r["corpus"] = lab
        rows.append(r)
        print(f"== {lab}  n={r['n']}")
        for k in LABELS:
            pr = r[f"anch_{k}"] / r[f"raw_{k}"] * 100 if r[f"raw_{k}"] else float("nan")
            print(f"   {k:6s} raw {r[f'raw_{k}'] / r['n'] * 100:7.3f}%   "
                  f"anchored {r[f'anch_{k}'] / r['n'] * 100:7.3f}%   精度代理 {pr:5.1f}%")

    keys = ["corpus", "n"] + [f"raw_{k}" for k in LABELS] + [f"anch_{k}" for k in LABELS]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})
    print("→", OUT)


if __name__ == "__main__":
    main()
