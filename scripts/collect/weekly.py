#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""每周一次的前向采集（三个源，串行，各留一份账）。

为什么单独一个入口
  数据侧只剩这一件活：**2022—2025 的社交正文补不回来，只能从今天起长**。
  三个源互补：
    piyao     中国互联网联合辟谣平台 → ρ 的中国侧日序列 + 事件候选
    weibo     微博热搜正文（alexxhchen/comap-*）→ π_L 的月度序列
    热搜榜     三平台小时榜（showlcw）→ 注意力背景 E_t 的当期切片

纪律
  - 全部幂等：重复跑只追加新条目
  - 每次抓取在对应 MANIFEST 里留痕（URL / UTC / 状态 / 字节数 / SHA256）
  - 限速：每个源之间睡 5 秒；单源内部由各自的 --sleep 控制

用法
  python scripts/collect/weekly.py            # 跑一遍
  python scripts/collect/weekly.py --dry-run  # 只打印要做什么
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
LOG = ROOT / "data" / "derived" / "weekly_runs.csv"

JOBS = [
    ("piyao", ["scripts/collect/fetch_piyao.py"]),
    # 微博正文：alexxhchen 的 processed/ 层由 collect/fetch_open.py 一类脚本抓；
    # 目前只采首页 20 个话题文件，避免一次拉 141 MB
    ("weibo_hot", ["scripts/collect/fetch_weibo_body.py", "--max", "20"]),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    if new:
        LOG.write_text("run_at_utc,job,script,exit_code,seconds\n", encoding="utf-8")

    for job, cmd in JOBS:
        script = ROOT / cmd[0]
        if not script.exists():
            print(f"[skip] {job}: {cmd[0]} 不存在")
            continue
        if a.dry_run:
            print(f"[dry] {job}: {PY} {' '.join(cmd)}")
            continue
        t0 = time.time()
        print(f"[run ] {job} ...", end="", flush=True)
        rc = subprocess.run([PY, *cmd], cwd=ROOT, capture_output=True, text=True).returncode
        dt = time.time() - t0
        print(f" rc={rc} {dt:.1f}s")
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')},"
                    f"{job},{cmd[0]},{rc},{dt:.1f}\n")
        time.sleep(5)

    print(f"\n账：{LOG}")


if __name__ == "__main__":
    main()
