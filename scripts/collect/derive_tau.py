#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 PolitiFact 快照派生 τ（声明日 → 核查日）的记录级数据。

输出
  data/derived/tau_politifact.csv   每行：id, statement_date, factcheck_date, lag_days, verdict, year
  data/derived/tau_summary.json     分位数、按年、按判定
"""
from __future__ import annotations

import csv
import json
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "raw" / "datasets" / "kg_politifact.zip"
OUT = ROOT / "data" / "derived"


def parse(s: str):
    for f in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, f)
        except (ValueError, TypeError):
            pass
    return None


def main() -> None:
    with zipfile.ZipFile(SRC) as z:
        name = z.namelist()[0]
        recs = [json.loads(x) for x in z.read(name).decode("utf-8").splitlines() if x.strip()]

    rows = []
    for i, r in enumerate(recs):
        a, b = parse(r.get("statement_date")), parse(r.get("factcheck_date"))
        if not (a and b) or b < a:
            continue
        rows.append({
            "id": f"pf{i:05d}",
            "statement_date": a.strftime("%Y-%m-%d"),
            "factcheck_date": b.strftime("%Y-%m-%d"),
            "lag_days": (b - a).days,
            "year": b.year,
            "verdict": r.get("verdict", ""),
            "originator": r.get("statement_originator", ""),
        })

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "tau_politifact.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    lags = sorted(r["lag_days"] for r in rows)
    n = len(lags)
    q = lambda x: lags[min(n - 1, int(n * x))]
    by_year, by_verdict = defaultdict(list), defaultdict(list)
    for r in rows:
        by_year[r["year"]].append(r["lag_days"])
        by_verdict[r["verdict"]].append(r["lag_days"])
    summary = {
        "n": n,
        "snapshot_source": "kaggle:rmisra/politifact-fact-check-dataset",
        "median": q(.5), "p25": q(.25), "p75": q(.75), "p90": q(.9), "p99": q(.99),
        "share_gt_30d": round(sum(1 for x in lags if x > 30) / n, 4),
        "share_gt_365d": round(sum(1 for x in lags if x > 365) / n, 4),
        "by_year_median": {y: sorted(v)[len(v) // 2] for y, v in sorted(by_year.items())},
        "by_verdict_median": {k: sorted(v)[len(v) // 2] for k, v in sorted(by_verdict.items())},
        "caveat": "PolitiFact 只核查其选中的声明，存在选择偏差；τ 是'被核查者'的延迟，不是全语料的延迟。",
    }
    (OUT / "tau_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
