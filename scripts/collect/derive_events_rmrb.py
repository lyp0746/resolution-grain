#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从人民日报全文里捞「反转事件」候选（2022—2026）。

为什么
  `events_template.tsv` 要 20—50 条事件四元组，`REQUESTS.md` 说这得人工填。
  但「哪一天发生了什么」这一步不该靠记忆——报纸上写着。

做法（两步，都可复核）
  1. **召回**：正文命中断言词（摆拍/自导自演/剧情演绎/辟谣/造谣/不实信息/反转）
     **且** 命中处置侧（通报/警方/公安/行政拘留/调查组/平台）。
  2. **打分**：命中的断言词越多、越靠前（标题里优先），分数越高。
     只排序，不判定——判定仍要人读。

输出
  data/derived/events_rmrb.csv   date, title, score, hits（逗号分隔）, lead（正文首 80 字）

纪律
  这是**候选名单**，不是事件表。τ 需要 begin / fbegin / fend 三个日期，
  这份文件只提供 begin 的线索（报道日），其余仍要查原始通报。
"""
from __future__ import annotations

import csv
import io
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIP = ROOT / "data" / "raw" / "datasets" / "kg_rmrb.zip"
OUT = ROOT / "data" / "derived" / "events_rmrb.csv"

ASSERT = ["摆拍", "自导自演", "剧情演绎", "辟谣", "造谣", "不实信息", "反转", "虚假视频", "AI生成"]
HANDLE = ["通报", "警方", "公安", "行政拘留", "调查组", "平台", "账号封禁", "查处"]


def main() -> None:
    csv.field_size_limit(50_000_000)
    zf = zipfile.ZipFile(ZIP)
    rows = []
    for y in (2022, 2023, 2024, 2025, 2026):
        name = f"RenMin_Daily_{y}.csv"
        if name not in zf.namelist():
            continue
        txt = zf.read(name).decode("utf-8-sig", errors="replace")
        for r in csv.DictReader(io.StringIO(txt)):
            title = (r.get("title") or "").strip()
            body = (r.get("content") or "").strip()
            both = title + "\n" + body
            ha = [w for w in ASSERT if w in both]
            hh = [w for w in HANDLE if w in both]
            if not (ha and hh):
                continue
            score = 2 * len([w for w in ha if w in title]) + len(ha) + len(hh)
            rows.append({"date": r.get("date", ""), "title": title, "score": score,
                         "hits": ",".join(ha + hh),
                         "lead": re.sub(r"\s+", " ", body)[:80]})
    rows.sort(key=lambda x: (-x["score"], x["date"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "title", "score", "hits", "lead"])
        w.writeheader()
        w.writerows(rows)
    by_year: dict[str, int] = {}
    for r in rows:
        by_year[r["date"][:4]] = by_year.get(r["date"][:4], 0) + 1
    print(f"候选 {len(rows)} 条：{by_year}")
    print(f"其中 title 里就带断言词的 {sum(1 for r in rows if r['score'] >= 3)} 条")
    print("→", OUT)


if __name__ == "__main__":
    main()
