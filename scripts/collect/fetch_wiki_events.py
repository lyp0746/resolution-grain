#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从中文维基抓「年度新闻/热点事件」列表，解析成带日期的事件表。

用法: python collect/fetch_wiki_events.py
输出: data/derived/wiki_events_annual.csv, data/raw/wiki_events_<year>.wikitext
"""
from __future__ import annotations

import csv
import re
import time
from pathlib import Path

import requests

H = {"User-Agent": "RuleEnergyInfo/0.1 (academic research)"}
API = "https://zh.wikipedia.org/w/api.php"
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "derived" / "wiki_events_annual.csv"

TITLES = [f"中国大陆新闻事件列表 ({y}年)" for y in range(2022, 2027)]
TITLES.append("中国大陆网络热点事件列表")


def wikitext(title: str) -> str | None:
    for attempt in range(3):
        time.sleep(2.0 + attempt * 4)
        r = requests.get(API, params={"action": "parse", "page": title, "prop": "wikitext",
                                      "format": "json", "formatversion": "2", "redirects": "1"},
                         headers=H, timeout=40)
        if r.status_code == 429:
            continue
        try:
            j = r.json()
        except Exception:  # noqa: BLE001
            continue
        return j["parse"]["wikitext"] if "parse" in j else None
    return None


def parse(wt: str, page: str) -> list[dict]:
    rows = []
    # 年份段落
    parts = re.split(r"\n==+\s*(\d{4})年?\s*==+\n", wt)
    if len(parts) > 2:
        for i in range(1, len(parts) - 1, 2):
            y, body = int(parts[i]), parts[i + 1]
            for m in re.finditer(r"\n===+\s*(.+?)\s*===+\n", body):
                seg = body[m.end(): m.end() + 1200]
                d = (re.search(r"date\s*=\s*(\d{4})-(\d{1,2})-(\d{1,2})", seg)
                     or re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", seg))
                rows.append({"page": page, "year": y, "event": m.group(1).strip(),
                             "first_date": f"{d.group(1)}-{int(d.group(2)):02d}-{int(d.group(3)):02d}" if d else ""})
    else:
        # 月日列表型（年度页）
        y = int(re.search(r"(\d{4})年", page).group(1)) if re.search(r"(\d{4})年", page) else 0
        for m in re.finditer(r"\*\s*'''(?:(\d{1,2})月(\d{1,2})日)'''[:：]?\s*(.{2,80})", wt):
            mo, dd, ev = m.group(1), m.group(2), m.group(3)
            rows.append({"page": page, "year": y,
                         "event": re.sub(r"[\[\]{}|]", "", ev).strip()[:80],
                         "first_date": f"{y}-{int(mo):02d}-{int(dd):02d}" if mo else ""})
    return rows


def main() -> None:
    allrows = []
    for t in TITLES:
        wt = wikitext(t)
        if not wt:
            print(f"[missing] {t}")
            continue
        (RAW / f"wiki_{re.sub(r'[^0-9A-Za-z一-鿿]', '_', t)}.wikitext").write_text(wt, encoding="utf-8")
        rows = parse(wt, t)
        print(f"[ok] {t}  chars={len(wt)}  events={len(rows)}")
        allrows += rows
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["page", "year", "event", "first_date"])
        w.writeheader()
        w.writerows(allrows)
    print(f"total {len(allrows)} → {OUT}")


if __name__ == "__main__":
    main()
