#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""人民日报全文语料 → π_L 可算性体检。

为什么做这件事
  `REQUESTS.md` 里 π_L 一直卡着，因为微博热搜只有标题，
  「摆拍/剧本/反转/辟谣」在标题里的命中率只有 0.006%—0.2%。
  这份语料（`kg_rmrb`，2021-01-01—2026-04，CC0）有**正文**。

输出
  data/derived/rmrb_daily.csv    每日：条数、总字数、各标签命中条数
  data/derived/rmrb_digest.csv   每年：覆盖天数、条数、字数、命中率
  stdout 打印覆盖率表

纪律
  只做读数，不做结论；命中率是「词出现在正文里」的下界，不是人工核验的标签。
"""
from __future__ import annotations

import csv
import io
import re
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIP = ROOT / "data" / "raw" / "datasets" / "kg_rmrb.zip"
OUT_DIR = ROOT / "data" / "derived"

# 四类标签：摆拍/剧本（表演性）、反转（叙事翻转）、辟谣/谣言（核查）、通报/回应（官方介入）
LABELS = {
    "摆拍": ["摆拍"],
    "剧本": ["剧本", "表演性"],
    "反转": ["反转", "翻转"],
    "谣言": ["谣言", "辟谣", "不实", "编造"],
    "通报": ["通报", "回应", "调查组"],
}


def main() -> None:
    csv.field_size_limit(50_000_000)  # 整版文章会超过默认 128KB 上限
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    zf = zipfile.ZipFile(ZIP)
    daily: dict[str, dict] = defaultdict(lambda: {"n": 0, "chars": 0, **{k: 0 for k in LABELS}})
    per_year: dict[str, dict] = {}

    for name in sorted(zf.namelist()):
        if not name.endswith(".csv"):
            continue
        year = re.search(r"(\d{4})", name).group(1)
        raw = zf.read(name)
        text = raw.decode("utf-8-sig", errors="replace")
        rd = csv.DictReader(io.StringIO(text))
        n = chars = 0
        hit = {k: 0 for k in LABELS}
        days = set()
        for row in rd:
            d = (row.get("date") or "").strip()
            body = (row.get("title") or "") + "\n" + (row.get("content") or "")
            if not d:
                continue
            n += 1
            chars += len(body)
            days.add(d)
            dd = daily[d]
            dd["n"] += 1
            dd["chars"] += len(body)
            for lab, words in LABELS.items():
                if any(w in body for w in words):
                    dd[lab] += 1
                    hit[lab] += 1
        per_year[year] = {"n": n, "chars": chars, "days": len(days), "hit": hit}

    with (OUT_DIR / "rmrb_daily.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "n", "chars", *LABELS])
        for d in sorted(daily):
            r = daily[d]
            w.writerow([d, r["n"], r["chars"], *[r[k] for k in LABELS]])

    with (OUT_DIR / "rmrb_digest.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "days", "n", "chars", *LABELS])
        for y in sorted(per_year):
            r = per_year[y]
            w.writerow([y, r["days"], r["n"], r["chars"], *[r["hit"][k] for k in LABELS]])

    print(f"{'year':6}{'days':>6}{'items':>9}{'Mchars':>9}" + "".join(f"{k:>9}" for k in LABELS))
    for y in sorted(per_year):
        r = per_year[y]
        rates = "".join(f"{r['hit'][k] / max(r['n'], 1) * 100:>8.3f}%" for k in LABELS)
        print(f"{y:6}{r['days']:>6}{r['n']:>9}{r['chars'] / 1e6:>9.1f}" + rates)
    print("\n右列为「正文命中该词条的条数 / 该年条数」；这是下界，不是人工标签。")
    print("→", OUT_DIR / "rmrb_daily.csv")


if __name__ == "__main__":
    main()
