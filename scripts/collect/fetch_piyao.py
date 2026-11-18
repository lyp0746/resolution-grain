#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""中国互联网联合辟谣平台：前向采集器。

为什么是它
  `REQUESTS.md` 的 τ 中国侧一直卡着。实测过的三条路：
    知乎      搜索 API 与问题页均 403（反爬），搜索引擎也不收录 → **不可采**
    辟谣平台  首页可访问，正文完整，但**无 sitemap / RSS / 分页 / 上一篇** → 只能前向采
    人民日报  体裁不对（报道政策，不报道个案，295 条候选只有 4 条是个案）

  所以：历史补不回来，**从今天起每天采**。首页约 24 条，含每日「今日辟谣（YYYY年MM月DD日）」。

纪律
  - 幂等：按 URL 去重，重复跑只追加新条目
  - 一文件一账：每次抓取记 UTC、状态码、字节数、SHA256（`data/MANIFEST_PIYAO.tsv`）
  - 只采公开页面，不绕验证

用法
  python collect/fetch_piyao.py            # 抓一次
  python collect/fetch_piyao.py --content  # 同时抓每条正文（慢，但给 τ 用）
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parents[2]
HOME = "https://www.piyao.org.cn/"
RAW = ROOT / "data" / "raw" / "piyao"
OUT = ROOT / "data" / "derived" / "piyao_items.csv"
MANIFEST = ROOT / "data" / "MANIFEST_PIYAO.tsv"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"}
PAT = re.compile(r'<a[^>]+href="([^"]*?(\d{8})/([0-9a-f]{32})/c\.html)"[^>]*>(.*?)</a>', re.S)
COLS = ("url", "post_date", "title", "first_seen_utc", "has_content")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_seen() -> dict[str, dict]:
    d = {}
    if OUT.exists():
        with OUT.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                d[r["url"]] = r
    return d


def get(url: str) -> requests.Response:
    return requests.get(url, headers=HEADERS, timeout=40, verify=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", action="store_true", help="同时抓正文")
    ap.add_argument("--sleep", type=float, default=1.2)
    a = ap.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    r = get(HOME)
    body = r.content
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (RAW / f"home_{stamp}.html").write_bytes(body)

    new_row = not MANIFEST.exists()
    with MANIFEST.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        if new_row:
            w.writerow(["id", "url", "fetched_at_utc", "status", "bytes", "sha256", "n_items"])
        w.writerow([f"piyao_home_{stamp}", HOME, now(), r.status_code, len(body),
                    hashlib.sha256(body).hexdigest(), 0])

    html = body.decode("utf-8", "replace")
    items = []
    for href, day, _, title in PAT.findall(html):
        t = re.sub(r"<[^>]+>", "", title).strip()
        if not t:
            continue
        url = href if href.startswith("http") else "https://www.piyao.org.cn/" + href.lstrip("/")
        items.append({"url": url, "post_date": f"{day[:4]}-{day[4:6]}-{day[6:]}", "title": t})

    seen = load_seen()
    added = []
    for it in items:
        if it["url"] in seen:
            continue
        it["first_seen_utc"] = now()
        it["has_content"] = 0
        if a.content:
            try:
                rr = get(it["url"])
                txt = rr.content.decode("utf-8", "replace")
                slug = re.sub(r"[^0-9a-zA-Z]+", "", it["post_date"]) + "_" + it["url"].rsplit("/", 2)[-2][:8]
                (RAW / f"{slug}.html").write_bytes(rr.content)
                it["has_content"] = 1 if len(txt) > 3000 else 0
                time.sleep(a.sleep)
            except Exception:  # noqa: BLE001
                pass
        added.append(it)
        seen[it["url"]] = it

    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(COLS))
        w.writeheader()
        for it in sorted(seen.values(), key=lambda x: (x["post_date"], x["url"]), reverse=True):
            w.writerow({k: it.get(k, "") for k in COLS})

    print(f"首页 {len(items)} 条，新增 {len(added)} 条，累计 {len(seen)} 条")
    for it in added[:8]:
        print("  ", it["post_date"], it["title"][:56])
    print("→", OUT)


if __name__ == "__main__":
    main()
