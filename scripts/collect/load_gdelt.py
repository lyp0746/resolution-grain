#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""解析 GDELT Volume Intensity 日序列。

输入（二选一，优先 full）
  data/raw/gdelt/gdelt_deepfake_full.json          完整序列
  data/raw/gdelt/gdelt_deepfake_USER_PARTIAL_*.json 摘录（仅峰值日）
输出
  data/derived/gdelt_<label>.csv
  data/derived/gdelt_<label>_summary.json
"""
from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GD = ROOT / "data" / "raw" / "gdelt"
OUT = ROOT / "data" / "derived"


def find_input() -> tuple[Path, bool]:
    full = GD / "gdelt_deepfake_full.json"
    if full.exists():
        return full, True
    parts = sorted(GD.glob("gdelt_*PARTIAL*.json"))
    if parts:
        return parts[0], False
    raise SystemExit("no GDELT input found")


def main() -> None:
    src, is_full = find_input()
    j = json.loads(src.read_text(encoding="utf-8"))
    series = j["timeline"][0]["data"]
    rows = []
    for d in series:
        dt = datetime.strptime(d["date"], "%Y%m%dT%H%M%SZ").date()
        rows.append({"date": dt.isoformat(), "value": float(d["value"])})
    rows.sort(key=lambda r: r["date"])

    label = "deepfake" + ("" if is_full else "_partial")
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"gdelt_{label}.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "value"])
        w.writeheader()
        w.writerows(rows)

    vals = [r["value"] for r in rows]
    ds = [date.fromisoformat(r["date"]) for r in rows]
    span = (ds[-1] - ds[0]).days + 1
    gaps = [(ds[i + 1] - ds[i]).days - 1 for i in range(len(ds) - 1)]
    top = sorted(rows, key=lambda r: -r["value"])[:10]
    by_year: dict[str, list[float]] = {}
    for r in rows:
        by_year.setdefault(r["date"][:4], []).append(r["value"])

    summary = {
        "source": src.name,
        "is_full_series": is_full,
        "query": j["query_details"]["title"],
        "resolution": j["query_details"]["date_resolution"],
        "n_points": len(rows),
        "date_min": ds[0].isoformat(),
        "date_max": ds[-1].isoformat(),
        "calendar_days": span,
        "missing_days": span - len(rows),
        "mean": round(sum(vals) / len(vals), 5),
        "median": round(sorted(vals)[len(vals) // 2], 5),
        "max": max(vals),
        "top10_spikes": [{"date": r["date"], "value": r["value"]} for r in top],
        "yearly_mean": {y: round(sum(v) / len(v), 5) for y, v in sorted(by_year.items())},
        "note_even_full": "GDELT 的 Volume Intensity 是'占全部报道的比例'，不是绝对篇数；中文覆盖弱，"
                          "缺日不等于零报道。",
    }
    (OUT / f"gdelt_{label}_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in
                      ["is_full_series", "n_points", "date_min", "date_max",
                       "missing_days", "mean", "median", "max", "yearly_mean"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
