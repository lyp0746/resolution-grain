#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bing News RSS 采集器。

为什么换 Bing：Google News RSS 的链接是加密跳转，取不到正文；
Bing News RSS 的 <link> 里带着出版商明文 URL，<description> 里带 60—200 字摘要，
摘要经常直接写出「X月X日……发布情况通报」——这正是 τ 的中国侧所需。

输出
  data/raw/news_bing/<id>.xml
  data/derived/news_bing.csv   query,title,url,pub_date,source,description
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
from urllib.parse import parse_qs, unquote, urlparse

import requests

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "scripts" / "collect" / "queries_news.tsv"
RAW = ROOT / "data" / "raw" / "news_bing"
MANIFEST = ROOT / "data" / "MANIFEST_BING.tsv"
OUTCSV = ROOT / "data" / "derived" / "news_bing.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}
COLS = ("id", "query", "url", "fetched_at_utc", "status", "bytes", "sha256", "n_items", "date_min", "date_max")


def read_tasks() -> list[dict]:
    rows = []
    for line in TASKS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        p = line.split("\t")
        if len(p) >= 2:
            rows.append({"id": p[0], "query": p[1]})
    return rows


def publisher_url(bing_link: str) -> str:
    """从 apiclick.aspx?url=<encoded> 里取回出版商 URL。"""
    try:
        q = parse_qs(urlparse(bing_link).query)
        if "url" in q:
            return unquote(q["url"][0])
    except Exception:  # noqa: BLE001
        pass
    return bing_link


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    OUTCSV.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    if OUTCSV.exists():
        with OUTCSV.open(encoding="utf-8") as f:
            seen = {r["url"] for r in csv.DictReader(f)}

    rows_out, ok = [], 0
    head = not MANIFEST.exists() or MANIFEST.stat().st_size == 0
    with MANIFEST.open("a", encoding="utf-8", newline="") as mf:
        if head:
            mf.write("\t".join(COLS) + "\n")
        for t in read_tasks():
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                time.sleep(1.5)
                r = requests.get("https://www.bing.com/news/search",
                                 params={"q": t["query"], "format": "rss"},
                                 headers=HEADERS, timeout=40)
            except Exception as e:  # noqa: BLE001
                mf.write("\t".join([t["id"], t["query"], "", now, "ERR", "0", "", "0", "", ""]) + "\n")
                print(f"[fail] {t['id']} {type(e).__name__}")
                continue
            if r.status_code != 200:
                mf.write("\t".join([t["id"], t["query"], r.url, now, str(r.status_code), str(len(r.content)), "", "0", "", ""]) + "\n")
                print(f"[warn] {t['id']} HTTP {r.status_code}")
                continue
            (RAW / f"{t['id']}.xml").write_bytes(r.content)
            try:
                root = ET.fromstring(r.content)
            except ET.ParseError:
                root = None
            items = []
            if root is not None:
                for it in root.iter("item"):
                    link = publisher_url((it.findtext("link") or "").strip())
                    title = (it.findtext("title") or "").strip()
                    desc = (it.findtext("description") or "").strip()
                    src = (it.findtext("{*}Source") or "").strip()
                    pub = (it.findtext("pubDate") or "").strip()
                    try:
                        d = parsedate_to_datetime(pub).astimezone(timezone.utc).strftime("%Y-%m-%d")
                    except Exception:  # noqa: BLE001
                        d = ""
                    if link and title:
                        items.append({"query": t["query"], "title": title, "url": link,
                                      "pub_date": d, "source": src, "description": desc})
            fresh = [x for x in items if x["url"] not in seen]
            for x in fresh:
                seen.add(x["url"])
            rows_out += fresh
            dates = sorted(x["pub_date"] for x in items if x["pub_date"])
            mf.write("\t".join([t["id"], t["query"], r.url, now, "200", str(len(r.content)),
                                hashlib.sha256(r.content).hexdigest(), str(len(items)),
                                dates[0] if dates else "", dates[-1] if dates else ""]) + "\n")
            print(f"[ok] {t['id']:<5} items={len(items):<3} new={len(fresh):<3} {dates[0] if dates else '?'} → {dates[-1] if dates else '?'}")
            ok += 1

    fields = ["query", "title", "url", "pub_date", "source", "description"]
    new = not OUTCSV.exists()
    with OUTCSV.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerows(rows_out)
    print(f"\n完成：queries={ok} 新增 {len(rows_out)} → {OUTCSV.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
