#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""公开数据集采集器（Kaggle / HuggingFace）。

与 fetch_open.py 同一纪律：一文件一账（SHA256 + UTC + 状态）。
区别：这里采的是「别人已发表的成品数据集」，只需引用，不需自算。

用法
  python collect/fetch_datasets.py
  python collect/fetch_datasets.py --only kg_politifact --force
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
TASKS = ROOT / "scripts" / "collect" / "tasks_datasets.tsv"
OUT = ROOT / "data" / "raw" / "datasets"
MANIFEST = ROOT / "data" / "MANIFEST_DATASETS.tsv"
HEADERS = {"User-Agent": "RuleEnergyInfo/0.1 (academic; local)"}
COLS = ("id", "platform", "ref", "path", "url", "fetched_at_utc", "status", "bytes", "sha256", "note")
TIMEOUT = 120


def read_tasks() -> list[dict]:
    rows = []
    for line in TASKS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        p = line.split("\t")
        if len(p) < 3:
            continue
        rows.append({"id": p[0], "platform": p[1], "ref": p[2],
                     "path": p[3] if len(p) > 3 else "",
                     "note": p[4] if len(p) > 4 else ""})
    return rows


def manifest() -> dict[str, dict]:
    d = {}
    if MANIFEST.exists():
        lines = MANIFEST.read_text(encoding="utf-8").splitlines()
        head = lines[0].split("\t")
        for line in lines[1:]:
            p = line.split("\t")
            if len(p) >= 8:
                d[p[0]] = dict(zip(head, p))
    return d


def append(row: dict) -> None:
    new = not MANIFEST.exists()
    with MANIFEST.open("a", encoding="utf-8", newline="") as f:
        if new:
            f.write("\t".join(COLS) + "\n")
        f.write("\t".join(str(row.get(c, "")) for c in COLS) + "\n")


def url_of(t: dict) -> str:
    if t["platform"] == "kaggle":
        return f"https://www.kaggle.com/api/v1/datasets/download/{t['ref']}"
    return f"https://huggingface.co/datasets/{t['ref']}/resolve/main/{t['path']}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    done = manifest()
    OUT.mkdir(parents=True, exist_ok=True)
    ok = skip = fail = 0

    for t in [x for x in read_tasks() if not only or x["id"] in only]:
        target = OUT / (t["id"] + (".csv" if t["platform"] == "hf" else ".zip"))
        if done.get(t["id"], {}).get("status") == "200" and target.exists() and not args.force:
            print(f"[skip] {t['id']}")
            skip += 1
            continue
        u = url_of(t)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            time.sleep(1.0)
            r = requests.get(u, headers=HEADERS, timeout=TIMEOUT)
        except Exception as e:  # noqa: BLE001
            append({"id": t["id"], "platform": t["platform"], "ref": t["ref"], "path": t["path"],
                    "url": u, "fetched_at_utc": now, "status": "ERR", "bytes": 0,
                    "sha256": "", "note": type(e).__name__})
            print(f"[fail] {t['id']:<16} {type(e).__name__}")
            fail += 1
            continue
        if r.status_code == 200 and r.content:
            target.write_bytes(r.content)
            digest = hashlib.sha256(r.content).hexdigest()
            append({"id": t["id"], "platform": t["platform"], "ref": t["ref"], "path": t["path"],
                    "url": u, "fetched_at_utc": now, "status": "200", "bytes": len(r.content),
                    "sha256": digest, "note": t["note"]})
            print(f"[ok]   {t['id']:<16} {len(r.content)/1e6:6.1f} MB  {digest[:12]}")
            ok += 1
        else:
            append({"id": t["id"], "platform": t["platform"], "ref": t["ref"], "path": t["path"],
                    "url": u, "fetched_at_utc": now, "status": r.status_code, "bytes": len(r.content),
                    "sha256": hashlib.sha256(r.content).hexdigest(), "note": t["note"] + " | HTTP"})
            print(f"[warn] {t['id']:<16} HTTP {r.status_code}")
            fail += 1

    print(f"\n完成：ok={ok} skip={skip} fail={fail} → {MANIFEST.relative_to(ROOT)}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
