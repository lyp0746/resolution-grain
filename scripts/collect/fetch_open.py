#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""规则—能量—信息项目：第一批公开数据采集器。

原则
  1) 只取公开 API / 公开 CSV / 公开 HTML，不绕验证、不伪造 UA 为浏览器以外的身份。
  2) 每个文件落盘即记账：URL、UTC 时间、HTTP 状态、字节数、SHA256。
  3) 幂等：已有 200 记录且文件在，默认跳过；--force 重取。
  4) 限速：按 host 最小间隔；429/5xx 指数退避。宁可失败，不硬闯。

用法
  python collect/fetch_open.py                 # 采全部未完成项
  python collect/fetch_open.py --only wb_tfr_chn,owid_fertility
  python collect/fetch_open.py --force --only gdelt_deepfake
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "scripts" / "collect" / "tasks.tsv"
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "MANIFEST.tsv"

HEADERS = {"User-Agent": "RuleEnergyInfo/0.1 (academic data collection; local)"}
THROTTLE = {"api.gdeltproject.org": 6.0, "api.worldbank.org": 1.5, "default": 1.0}
TIMEOUT = 30
RETRIES = 2
COLS = ("task_id", "kind", "url", "fetched_at_utc", "status", "bytes", "sha256", "note")


def read_tasks() -> list[dict]:
    rows = []
    for line in TASKS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        p = line.split("\t")
        if len(p) < 4:
            continue
        rows.append({"id": p[0], "kind": p[1], "url": p[2], "ext": p[3],
                     "note": p[4] if len(p) > 4 else ""})
    return rows


def read_manifest() -> dict[str, dict]:
    done = {}
    if MANIFEST.exists():
        lines = MANIFEST.read_text(encoding="utf-8").splitlines()
        head = lines[0].split("\t") if lines else []
        for line in lines[1:]:
            p = line.split("\t")
            if len(p) >= 7:
                done[p[0]] = dict(zip(head, p))
    return done


def append_manifest(row: dict) -> None:
    new = not MANIFEST.exists()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("a", encoding="utf-8", newline="") as f:
        if new:
            f.write("\t".join(COLS) + "\n")
        f.write("\t".join(str(row.get(c, "")) for c in COLS) + "\n")


def fetch(url: str, host_delay: float) -> requests.Response:
    last = None
    for attempt in range(RETRIES):
        try:
            time.sleep(host_delay if attempt == 0 else host_delay * (2 ** attempt))
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 429 or 500 <= r.status_code < 600:
                last = r
                continue
            return r
        except requests.RequestException as e:
            last = e
    if isinstance(last, requests.Response):
        return last
    raise last  # type: ignore[misc]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    tasks = [t for t in read_tasks() if not only or t["id"] in only]
    done = read_manifest()
    RAW.mkdir(parents=True, exist_ok=True)

    ok = skip = fail = 0
    for t in tasks:
        prev = done.get(t["id"])
        target = RAW / f"{t['id']}.{t['ext']}"
        if prev and prev.get("status") == "200" and target.exists() and not args.force:
            print(f"[skip] {t['id']:<22} 已有快照 {prev.get('fetched_at_utc')}")
            skip += 1
            continue

        host = urlparse(t["url"]).netloc
        delay = THROTTLE.get(host, THROTTLE["default"])
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            r = fetch(t["url"], delay)
            status = str(r.status_code)
            body = r.content
        except Exception as e:  # noqa: BLE001
            append_manifest({"task_id": t["id"], "kind": t["kind"], "url": t["url"],
                             "fetched_at_utc": now, "status": "ERR", "bytes": 0,
                             "sha256": "", "note": type(e).__name__})
            print(f"[fail] {t['id']:<22} {type(e).__name__}")
            fail += 1
            continue

        if status == "200":
            target.write_bytes(body)
            digest = hashlib.sha256(body).hexdigest()
            append_manifest({"task_id": t["id"], "kind": t["kind"], "url": t["url"],
                             "fetched_at_utc": now, "status": status, "bytes": len(body),
                             "sha256": digest, "note": t["note"]})
            print(f"[ok]   {t['id']:<22} {len(body):>8} B  {digest[:12]}")
            ok += 1
        else:
            append_manifest({"task_id": t["id"], "kind": t["kind"], "url": t["url"],
                             "fetched_at_utc": now, "status": status, "bytes": len(body),
                             "sha256": hashlib.sha256(body).hexdigest(),
                             "note": t["note"] + " | HTTP " + status})
            print(f"[warn] {t['id']:<22} HTTP {status} ({len(body)} B)")
            fail += 1

    print(f"\n完成：ok={ok} skip={skip} fail={fail} → {MANIFEST.relative_to(ROOT)}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
