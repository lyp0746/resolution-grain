#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""标题是一份多粗的码？——用报纸自己的两级编码量「粗码丢了什么」。

为什么做这件事
  `REWALK.md` 说"标签就是粗码"，但那是比喻。这里给一个**可数的版本**：
  同一篇报道，编辑给了两个码——标题与正文。标题的长度中位只有正文的 2.4%。
  那么问题变成：**在 1/42 的码率下，被丢掉的到底是什么？**

做法（三个正交的读数）
  1. 码率：标题字数 / 正文字数（分布，不做平均）。
  2. 限定词保留率：正文含「疑似/据称/网传/初步/未经证实…」时，标题还留着几个？
  3. 否定词保留率：**两种分母**——
       A 粗分母：正文任意位置出现否定词。这个数字会奇高，因为多数是顺带提及。
       B 紧分母：否定出现在正文前 120 字（导语就在说"这是假的"）。
     两个分母给出的答案差一个量级，**这个差本身就是本书第 21 章（三种口径）的实例**。

输出
  data/derived/code_rate.csv   年, n, 码率中位, 限定词保留率, 否定保留率(A/B)

纪律
  B 口径的 n 很小（几十篇），只能当信号。**不许把 A 口径的 99% 写进正文。**
"""
from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "data" / "raw" / "datasets" / "kg_rmrb.zip"
OUT = ROOT / "data" / "derived" / "code_rate.csv"

HEDGE = ["疑似", "据称", "网传", "初步", "尚未", "未经证实", "有可能", "或将", "传言", "据透露", "尚在"]
DENY = ["辟谣", "不实", "谣言", "系伪造", "并非", "不属实", "澄清"]
DENY_LEAD = 120  # 前 N 字内出现否定，才算"导语即否认"


def main() -> None:
    csv.field_size_limit(50_000_000)
    zf = zipfile.ZipFile(ZIP)
    rows = []
    for name in sorted(zf.namelist()):
        if not name.endswith(".csv"):
            continue
        year = name.split("_")[-1].split(".")[0]
        txt = zf.read(name).decode("utf-8-sig", errors="replace")
        n = hb = ht = a_n = a_keep = b_n = b_keep = 0
        ratio = []
        for r in csv.DictReader(io.StringIO(txt)):
            ti = (r.get("title") or "").strip()
            bo = (r.get("content") or "").strip()
            if not ti or not bo:
                continue
            n += 1
            ratio.append(len(ti) / max(len(bo), 1))
            if any(w in bo for w in HEDGE):
                hb += 1
                if any(w in ti for w in HEDGE):
                    ht += 1
            if any(w in bo for w in DENY):
                a_n += 1
                if any(w in ti for w in DENY):
                    a_keep += 1
            if any(w in bo[:DENY_LEAD] for w in DENY):
                b_n += 1
                if any(w in ti for w in DENY):
                    b_keep += 1
        rows.append({"year": year, "n": n, "code_rate_median": round(float(np.median(ratio)), 5),
                     "hedge_n": hb, "hedge_kept": ht,
                     "hedge_keep_rate": round(ht / max(hb, 1), 4),
                     "deny_loose_n": a_n, "deny_loose_keep": round(a_keep / max(a_n, 1), 4),
                     "deny_tight_n": b_n, "deny_tight_keep": round(b_keep / max(b_n, 1), 4)})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(f"{'年':6}{'篇数':>8}{'码率中位':>10}{'限定词保留':>11}{'否定保留(粗)':>13}{'否定保留(紧)':>13}")
    for r in rows:
        print(f"{r['year']:6}{r['n']:>8}{r['code_rate_median']:>9.1%}"
              f"{r['hedge_keep_rate']:>10.1%}{r['deny_loose_keep']:>12.1%}"
              f"{r['deny_tight_keep']:>12.1%}  (n={r['deny_tight_n']})")
    print("→", OUT)


if __name__ == "__main__":
    main()
