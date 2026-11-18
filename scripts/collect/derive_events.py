#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 Bing News 摘要派生「事件候选」：把同一事件的多条报道聚成一簇，
并抽出摘要里出现的官方通报日期。

输入  data/derived/news_bing.csv
输出  data/derived/events_candidates.csv
      data/derived/events_candidates.md

方法（刻意保守，便于人工否决）
  1) 标题去掉「 - 媒体名」后缀，按 difflib 相似度 ≥ 0.55 做并查集聚类；
  2) 摘要里匹配「M月D日」或「YYYY年M月D日」，只保留离「通报/经查/警方/行拘/立案」≤12 字的；
  3) 年份缺省时用该条 pub_date 的年份补；
  4) 输出最小/最大报道日、通报日集合、簇内条数——不做任何因果解读。
"""
from __future__ import annotations

import csv
import difflib
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "derived" / "news_bing.csv"
OUT_CSV = ROOT / "data" / "derived" / "events_candidates.csv"
OUT_MD = ROOT / "data" / "derived" / "events_candidates.md"

DATE_RE = re.compile(r"(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日")
TRIGGER = ("通报", "经查", "警方", "行拘", "立案", "调查组", "辟谣")


def norm_title(t: str) -> str:
    t = re.sub(r"\s*[-–—_|]\s*[^-–—_|]{2,12}$", "", t.strip())
    return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", t)


def extract_dates(desc: str, fallback_year: int) -> list[str]:
    hits = []
    for m in DATE_RE.finditer(desc):
        y, mo, d = m.group(1), int(m.group(2)), int(m.group(3))
        ctx = desc[max(0, m.start() - 12): m.end() + 12]
        if not any(k in ctx for k in TRIGGER):
            continue
        year = int(y) if y else fallback_year
        try:
            hits.append(date(year, mo, d).isoformat())
        except ValueError:
            continue
    return hits


def main() -> None:
    rows = list(csv.DictReader(SRC.open(encoding="utf-8")))
    rows = [r for r in rows if r.get("title") and r.get("pub_date")]
    for r in rows:
        r["norm"] = norm_title(r["title"])

    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        a, b = find(i), find(j)
        if a != b:
            parent[b] = a

    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i]["norm"], rows[j]["norm"]
            if not a or not b:
                continue
            if abs(len(a) - len(b)) > max(len(a), len(b)) * 0.6:
                continue
            if difflib.SequenceMatcher(None, a, b).ratio() >= 0.55:
                union(i, j)

    clusters = defaultdict(list)
    for i in range(len(rows)):
        clusters[find(i)].append(rows[i])

    out = []
    for k, (_, items) in enumerate(sorted(clusters.items(), key=lambda kv: -len(kv[1])), 1):
        items.sort(key=lambda r: r["pub_date"])
        tb = []
        for r in items:
            tb += extract_dates(r.get("description", ""), int(r["pub_date"][:4]))
        tbs = sorted(set(tb))
        first, last = items[0]["pub_date"], items[-1]["pub_date"]
        head = items[0]["title"]
        out.append({
            "event_id": f"e{k:03d}",
            "n_reports": len(items),
            "head_title": head,
            "first_report": first,
            "last_report": last,
            "tongbao_dates": ";".join(tbs),
            "first_tongbao": tbs[0] if tbs else "",
            "lag_days": (date.fromisoformat(tbs[0]) - date.fromisoformat(first)).days if tbs else "",
            "sources": ";".join(sorted({r["source"] for r in items if r["source"]}))[:80],
            "url": items[0]["url"],
        })

    out.sort(key=lambda r: (-r["n_reports"], r["first_report"]))
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    md = ["# 事件候选（自动派生，待人工否决）", "",
          f"- 输入：{len(rows)} 条 Bing News 报道；聚成 {len(out)} 簇",
          f"- 口径：标题相似度 ≥ 0.55；通报日期只取紧邻触发词的「M月D日」",
          "- **用法**：只做删减，不做录入。删掉误聚的簇即可。", "",
          "| id | 条数 | 首次报道 | 通报日 | lag | 标题 |", "|---|---|---|---|---|---|"]
    for r in out[:25]:
        md.append(f"| {r['event_id']} | {r['n_reports']} | {r['first_report']} | "
                  f"{r['first_tongbao'] or '—'} | {r['lag_days'] if r['lag_days'] != '' else '—'} | "
                  f"{r['head_title'][:38]} |")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"clusters={len(out)}  → {OUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
