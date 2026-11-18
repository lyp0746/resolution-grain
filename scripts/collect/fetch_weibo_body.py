#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""微博热搜正文：增量采集（HF `alexxhchen/comap-weibo-bilibili-data`）。

为什么采它
  `π_L` 要的是**正文**里的标签词频。热搜标题的精度代理只有 12.5%，
  而微博正文的精度代理是 97%（见 `data/DIGEST-CORPUS.md` §3）。
  这个仓库的 `weibo/processed/` 每个文件是一条热搜话题的完整时间线，带正文、排名、热度值。

为什么是"增量"
  整个目录 321 个文件、141 MB。一次拉完会挤掉带宽，且旧文件不会再变。
  所以：**只下本地没有的，每次最多 N 个**。

纪律
  - 幂等：按文件名去重
  - 一文件一账：`data/MANIFEST_WEIBO.tsv`
  - 限速：每个文件之间睡 --sleep

用法
  python scripts/collect/fetch_weibo_body.py            # 最多下 20 个新文件
  python scripts/collect/fetch_weibo_body.py --max 60
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
REPO = "alexxhchen/comap-weibo-bilibili-data"
API = f"https://huggingface.co/api/datasets/{REPO}/tree/main/weibo/processed"
BASE = f"https://huggingface.co/datasets/{REPO}/resolve/main/"
OUT = ROOT / "data" / "raw" / "hf" / "weibo_hot_processed"
MANIFEST = ROOT / "data" / "MANIFEST_WEIBO.tsv"
HEADERS = {"User-Agent": "RuleEnergyInfo/0.2 (academic; local)"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=20)
    ap.add_argument("--sleep", type=float, default=1.0)
    a = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    r = requests.get(API, headers=HEADERS, timeout=60)
    r.raise_for_status()
    files = sorted(x["path"] for x in r.json() if x["type"] == "file")

    have = {p.name for p in OUT.glob("*.csv")}
    todo = [f for f in files if Path(f).name not in have][: a.max]
    print(f"远端 {len(files)} 个，本地已有 {len(have)} 个，本次下 {len(todo)} 个")

    new = not MANIFEST.exists()
    with MANIFEST.open("a", encoding="utf-8", newline="") as mf:
        w = csv.writer(mf, delimiter="\t")
        if new:
            w.writerow(["file", "url", "fetched_at_utc", "status", "bytes", "sha256"])
        for f in todo:
            url = BASE + f
            try:
                rr = requests.get(url, headers=HEADERS, timeout=120)
                if rr.status_code != 200:
                    w.writerow([Path(f).name, url, datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                rr.status_code, 0, ""])
                    print("  ", Path(f).name, "HTTP", rr.status_code)
                    continue
                (OUT / Path(f).name).write_bytes(rr.content)
                w.writerow([Path(f).name, url, datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            200, len(rr.content), hashlib.sha256(rr.content).hexdigest()])
                print("  ", Path(f).name, f"{len(rr.content) / 1e6:.2f} MB")
            except Exception as e:  # noqa: BLE001
                print("  ", Path(f).name, "ERR", type(e).__name__)
            time.sleep(a.sleep)

    print("累计", len(list(OUT.glob("*.csv"))), "个文件 →", OUT)


if __name__ == "__main__":
    main()
