#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""新闻检索采集器（Google News RSS，zh-CN）。

为什么用它：知乎 403、微博 visitor、GDELT 429；Google News RSS 是本机唯一
能稳定拿到「带日期」的中文新闻索引。它给的是摘要与链接，不是全文——
全文抽取留给下一步（见 collect/extract_bodies.py）。

输出
  data/raw/news/<id>.xml            原始 RSS 快照
  data/MANIFEST_NEWS.tsv            采集账（含条目数与日期跨度）
  data/derived/news_items.csv       去重后的条目：query, title, link, pub_date, source
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "scripts" / "collect" / "queries_news.tsv"
RAW = ROOT / "data" / "raw" / "news"
MANIFEST = ROOT / "data" / "MANIFEST_NEWS.tsv"
ITEMS = ROOT / "data" / "derived" / "news_items.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}
COLS = ("id", "query", "url", "fetched_at_utc", "status", "bytes", "sha256", "n_items", "date_min", "date_max")


def read_tasks() -> list[dict]:
    rows = []
    for line in TASKS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        p = line.split("\t")
        if len(p) >= 2:
            rows.append({"id": p[0], "query": p[1], "note": p[2] if len(p) > 2 else ""})
    return rows


def parse_items(xml_text: str, query: str) -> list[dict]:
    out = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return out
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        src = (it.findtext("source") or "").strip()
        try:
            dt = parsedate_to_datetime(pub).astimezone(timezone.utc).strftime("%Y-%m-%d")
        except Exception:  # noqa: BLE001
            dt = ""
        if title and link:
            out.append({"query": query, "title": title, "link": link, "pub_date": dt, "source": src})
    return out


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    ITEMS.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    if ITEMS.exists():
        with ITEMS.open(encoding="utf-8") as f:
            seen = {r["link"] for r in csv.DictReader(f)}

    new_rows, ok = [], 0
    with MANIFEST.open("a", encoding="utf-8", newline="") as mf:
        if MANIFEST.stat().st_size == 0:
            mf.write("\t".join(COLS) + "\n")
        for t in read_tasks():
            url = "https://news.google.com/rss/search"
            params = {"q": t["query"], "hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"}
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                time.sleep(1.2)
                r = requests.get(url, params=params, headers=HEADERS, timeout=40)
            except Exception as e:  # noqa: BLE001
                mf.write("\t".join([t["id"], t["query"], url, now, "ERR", "0", "", "0", "", ""]) + "\n")
                print(f"[fail] {t['id']} {type(e).__name__}")
                continue
            if r.status_code != 200:
                mf.write("\t".join([t["id"], t["query"], r.url, now, str(r.status_code), str(len(r.content)), "", "0", "", ""]) + "\n")
                print(f"[warn] {t['id']} HTTP {r.status_code}")
                continue
            (RAW / f"{t['id']}.xml").write_bytes(r.content)
            items = parse_items(r.text, t["query"])
            fresh = [x for x in items if x["link"] not in seen]
            for x in fresh:
                seen.add(x["link"])
            new_rows += fresh
            dates = sorted(x["pub_date"] for x in items if x["pub_date"])
            mf.write("\t".join([t["id"], t["query"], r.url, now, "200", str(len(r.content)),
                                hashlib.sha256(r.content).hexdigest(), str(len(items)),
                                dates[0] if dates else "", dates[-1] if dates else ""]) + "\n")
            print(f"[ok]   {t['id']:<5} {t['query']:<22} items={len(items):<3} new={len(fresh):<3} {dates[0] if dates else '?'} → {dates[-1] if dates else '?'}")
            ok += 1

    fields = ["query", "title", "link", "pub_date", "source"]
    write_head = not ITEMS.exists()
    with ITEMS.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if write_head:
            w.writeheader()
        w.writerows(new_rows)
    print(f"\n完成：queries={ok}  新增条目前 {len(new_rows)} → {ITEMS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
