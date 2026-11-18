#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""断点续传下载器（Kaggle / HuggingFace）。

为什么单独写：Kaggle 实测只有 0.2—0.3 MB/s，250 MB 要十几分钟，
一次 HTTP 超时就会白跑。这里用 Range 续传，可反复重跑，直到落满。

用法
  python collect/fetch_resumable.py --url <url> --out data/raw/datasets/kg_rmrb.zip \
      --expect 252884723 --note "人民日报语料 2021-01-01—2026-04，CC0"

纪律（同 fetch_datasets.py）：
  - 落盘成功才写 MANIFEST_DATASETS.tsv（含 SHA256、UTC、字节数）
  - 没落满就退出码 2，账上记 partial，不记成功
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "MANIFEST_DATASETS.tsv"
HEADERS = {"User-Agent": "RuleEnergyInfo/0.1 (academic; local)"}
COLS = ("id", "platform", "ref", "path", "url", "fetched_at_utc", "status", "bytes", "sha256", "note")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def append(row: dict) -> None:
    new = not MANIFEST.exists()
    with MANIFEST.open("a", encoding="utf-8", newline="") as f:
        if new:
            f.write("\t".join(COLS) + "\n")
        f.write("\t".join(str(row.get(c, "")) for c in COLS) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect", type=int, default=0)
    ap.add_argument("--id", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--platform", default="kaggle")
    ap.add_argument("--ref", default="")
    ap.add_argument("--budget", type=int, default=600, help="秒；超时就退出，下次续传")
    a = ap.parse_args()

    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    have = out.stat().st_size if out.exists() else 0
    if a.expect and have >= a.expect:
        print(f"already complete: {have} bytes")
        code = 0
    else:
        t0 = time.time()
        hdrs = dict(HEADERS)
        if have:
            hdrs["Range"] = f"bytes={have}-"
        try:
            r = requests.get(a.url, headers=hdrs, stream=True, timeout=60)
            if r.status_code not in (200, 206):
                print(f"HTTP {r.status_code}")
                append({"id": a.id, "platform": a.platform, "ref": a.ref, "url": a.url,
                        "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "status": r.status_code, "bytes": have, "note": a.note + f" | HTTP {r.status_code}"})
                return 1
            mode = "ab" if (have and r.status_code == 206) else "wb"
            if mode == "wb":
                have = 0
            with out.open(mode) as f:
                for ch in r.iter_content(1 << 20):
                    f.write(ch)
                    have += len(ch)
                    if time.time() - t0 > a.budget:
                        break
        except Exception as e:  # noqa: BLE001
            print("transfer stopped:", type(e).__name__, str(e)[:120])
        size = out.stat().st_size
        print(f"have {size} / expect {a.expect} ({size / max(a.expect, 1) * 100:.1f}%)")
        code = 0 if (not a.expect or size >= a.expect) else 2

    if code == 0:
        digest = sha256(out)
        append({"id": a.id, "platform": a.platform, "ref": a.ref, "url": a.url,
                "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "status": 200, "bytes": out.stat().st_size, "sha256": digest, "note": a.note})
        print("manifest written; sha256", digest[:16], "...")
    else:
        append({"id": a.id, "platform": a.platform, "ref": a.ref, "url": a.url,
                "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "status": "partial", "bytes": out.stat().st_size, "note": a.note + " | resumable"})
    return code


if __name__ == "__main__":
    sys.exit(main())
