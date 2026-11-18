#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ESS 完整 11 轮（182MB）下载，支持断点续传。"""
import hashlib, os, sys, time, requests
from pathlib import Path
URL = "https://www.kaggle.com/api/v1/datasets/download/aashkval/european-social-survey-2002-2023-round-1-11"
DEST = Path(__file__).resolve().parents[1] / "data" / "raw" / "datasets" / "kg_ess_full.zip"
H = {"User-Agent": "RuleEnergyInfo/0.1"}
def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    have = DEST.stat().st_size if DEST.exists() else 0
    headers = dict(H)
    if have:
        headers["Range"] = f"bytes={have}-"
    r = requests.get(URL, headers=headers, stream=True, timeout=(30, 120))
    print("status", r.status_code, "resume_from", have, flush=True)
    if r.status_code not in (200, 206):
        sys.exit(1)
    mode = "ab" if (have and r.status_code == 206) else "wb"
    if mode == "wb":
        have = 0
    with DEST.open(mode) as f:
        t0 = time.time()
        for c in r.iter_content(1 << 20):
            f.write(c); have += len(c)
            if have % (10 << 20) < (1 << 20):
                print(f"{have/1e6:.1f}MB {time.time()-t0:.0f}s", flush=True)
    print("done", have, hashlib.sha256(DEST.read_bytes()).hexdigest()[:16], flush=True)
if __name__ == "__main__":
    main()
