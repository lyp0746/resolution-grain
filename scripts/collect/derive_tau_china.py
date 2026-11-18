#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""中国侧 τ（核实延迟）：用「反转事件」数据集算首次曝光 → 反转/辟谣的时间差。

数据：`Rachel74mx/reversed_weibo_event`（HF，27 个反转事件，2016—2022）
  begin   首次曝光（发帖/报道）
  fbegin  反转窗口起点（该窗口内出现辟谣/通报/翻转）
  fend    反转窗口终点

口径
  τ_low  = fbegin − begin   （最早的可能性：下界）
  τ_high = fend   − begin   （最晚的可能性：上界）
  窗口通常 <24 小时，所以区间很窄。

输出
  data/derived/tau_china.csv
  stdout：分位数表 + 与 PolitiFact 美国侧的对照

纪律
  27 个事件是**便利样本**（作者按「有代表性」挑的），且都发生在 2022 年以前。
  它是量级参考，不是代表性抽样；报告时必须写这一句。
"""
from __future__ import annotations

import csv
import io
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "raw" / "hf" / "reversed_events" / "data_case.csv"
OUT = ROOT / "data" / "derived" / "tau_china.csv"


def parse_begin(s: str) -> datetime | None:
    s = str(s).strip()
    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def parse_stamp(s: str) -> datetime | None:
    """fbegin 形如 '21-08-13 10'（年-月-日 时），两位年份。"""
    s = str(s).strip()
    m = re.match(r"(\d{2,4})-(\d{1,2})-(\d{1,2})\s*(?:(\d{1,2}))?", s)
    if not m:
        return None
    y, mo, d, h = m.groups()
    y = int(y)
    y += 2000 if y < 100 else 0
    return datetime(y, int(mo), int(d), int(h or 0))


def main() -> None:
    raw = SRC.read_bytes()
    for enc in ("utf-8-sig", "gb18030"):
        try:
            txt = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    d = pd.read_csv(io.StringIO(txt))
    rows = []
    for _, r in d.iterrows():
        b = parse_begin(r["begin"])
        fb, fe = parse_stamp(r["fbegin"]), parse_stamp(r["fend"])
        if not (b and fb and fe):
            continue
        rows.append({"event": str(r["name"]).strip(), "begin": b.date().isoformat(),
                     "first_reversal": fb.isoformat(sep=" "),
                     "tau_low_days": (fb - b).total_seconds() / 86400,
                     "tau_high_days": (fe - b).total_seconds() / 86400,
                     "weibo_posts": r["csvname"]})
    out = pd.DataFrame(rows).sort_values("begin")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")

    t = out["tau_low_days"].values
    q = lambda p: float(np.percentile(t, p))  # noqa: E731
    print(f"n = {len(t)}  （2016—2022，便利样本）")
    print(f"中位 τ = {q(50):.1f} 天   P25 = {q(25):.1f}   P75 = {q(75):.1f}   P90 = {q(90):.1f}   最大 = {t.max():.1f}")
    print(f"τ ≤ 2 天：{(t <= 2).mean() * 100:.0f}%   τ ≤ 7 天：{(t <= 7).mean() * 100:.0f}%   τ > 30 天：{(t > 30).mean() * 100:.0f}%")
    print("\n对照：PolitiFact 美国侧（n=21,063）中位 6 天，P25 2，P75 13，P90 26")
    print("→", OUT)


if __name__ == "__main__":
    main()
