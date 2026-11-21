#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补洞：搬号第一遍漏掉的三种写法（区间与内部记法）。

第一遍（plan_renumber_v3.py）只认"单点"引用：第 N 章／§N.M／表N.M／图N.M／N.M 节／secN-M／(N.M)。
漏掉的是**区间的第二半**与**内部记法**，共三类；它们都不是号错，是"半截号"——
读者会在正文里看到 "第 25 章 §25.1—22.2" 这种前后不一致的写法。

  ① §21.1—18.5      §A.B—C.D：第一半已改，第二半没改（同章区间，C 应为 A）
  ② 第 24—29 章      第N—M 章：两端都没改（正则要求数字后紧跟"章"）
  ③ ch27            内部记法（附录 A 的指针行、ch10 的摆表）：整串没进映射

判据（写死，避免越修越偏）
  ① 只在 C≠A、且 A 已是新号（≥21）、且 C 是旧号（在 chapter_map 的键里）时改；
  ② 只在两端都是旧号时按表改；一端是旧号一端不是 ⇒ 报出来，不猜；
  ③ 只在 chNN 的 NN 是旧号时改。

**这是一次性脚本（一次性由标记文件管，不靠人记）。**
  为什么不能随便重跑：新号 21—33 与旧号 21—33 **同一批数字**，映射表分不开。
  第一遍修完后再跑一次，会把"第 27—32 章"当成旧号再搬成"第 30—35 章"——
  实测第二遍会报 7 处"可改"，全是假的。所以 --write 成功后写 `_temp/.fix_ranges_v3.applied`，
  再跑 --write 会被拒绝；只报（不带 --write）仍可用来查残留。

用法
  "$PY" -X utf8 analysis/fix_ranges_v3.py            # 只报
  "$PY" -X utf8 analysis/fix_ranges_v3.py --check     # 查不变量（§区间两半必须同章）
  "$PY" -X utf8 analysis/fix_ranges_v3.py --write     # 写回 source-v2（只许一次）
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")
MAP = os.path.join(ROOT, "analysis", "chapter_map_v3.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stamp = os.path.join(ROOT, "_temp", ".fix_ranges_v3.applied")
    if a.write and os.path.exists(stamp):
        print("拒绝：这个脚本已经写过一次（_temp/.fix_ranges_v3.applied 存在）。")
        print("      新号与旧号在 21—33 重叠，再跑会把新号二次搬迁。要重来请从备份恢复后整链重跑。")
        return 1

    with io.open(MAP, encoding="utf-8") as fh:
        cmap = json.load(fh)["chapter_map"]

    if a.check:
        bad = 0
        for f in sorted(glob.glob(os.path.join(SRC, "*.html"))):
            t = io.open(f, encoding="utf-8").read()
            for m in re.finditer(r"§\s*(\d{1,2})\.(\d{1,2})—\s*(\d{1,2})\.(\d{1,2})", t):
                if m.group(1) != m.group(3):
                    bad += 1
                    print(f"  ! {os.path.basename(f)} {m.group(0)}（区间两半不同章）")
        print(f"§区间不变量：{'OK' if bad == 0 else str(bad) + ' 处'}")
        return 1 if bad else 0

    tot = {"§区间": 0, "第N—M章": 0, "chNN": 0}
    ambiguous = []
    changes = []

    for f in sorted(glob.glob(os.path.join(SRC, "*.html"))):
        t0 = io.open(f, encoding="utf-8").read()
        t = t0
        base = os.path.basename(f)

        # ① §A.B—C.D：同章区间的第二半
        def fix_sec(m):
            A, B, C, D = int(m.group(1)), m.group(2), int(m.group(3)), m.group(4)
            if C == A or A < 21 or str(C) not in cmap:
                return m.group(0)
            tot["§区间"] += 1
            changes.append((base, m.group(0), f"§{A}.{B}—{A}.{D}"))
            return f"§{A}.{B}—{A}.{D}"
        t = re.sub(r"§\s*(\d{1,2})\.(\d{1,2})—\s*(\d{1,2})\.(\d{1,2})", fix_sec, t)

        # ② 第N—M章：两端都是旧号才改
        def fix_chrange(m):
            n, k = int(m.group(1)), int(m.group(2))
            in_n, in_k = str(n) in cmap, str(k) in cmap
            if in_n and in_k:
                tot["第N—M章"] += 1
                changes.append((base, m.group(0), f"第 {cmap[str(n)]}—{cmap[str(k)]} 章"))
                return f"第 {cmap[str(n)]}—{cmap[str(k)]} 章"
            if in_n != in_k:
                ambiguous.append((base, m.group(0), "两端一新一旧"))
            return m.group(0)
        t = re.sub(r"第\s*(\d{1,2})—(\d{1,2})\s*章", fix_chrange, t)

        # ③ chNN
        def fix_ch(m):
            n = m.group(1)
            if n not in cmap:
                return m.group(0)
            tot["chNN"] += 1
            changes.append((base, m.group(0), f"ch{cmap[n]}"))
            return f"ch{cmap[n]}"
        t = re.sub(r"ch(1[89]|2[0-9]|3[0-3])\b", fix_ch, t)

        if a.write and t != t0:
            io.open(f, "w", encoding="utf-8").write(t)

    for k, v in tot.items():
        print(f"  {k:10s} {v}")
    print(f"  合计 {sum(tot.values())} 处" + ("" if not ambiguous else f"；另有 {len(ambiguous)} 处需人工判"))
    for b in ambiguous:
        print("    ! ", b)
    if a.write:
        os.makedirs(os.path.dirname(stamp), exist_ok=True)
        io.open(stamp, "w", encoding="utf-8").write("2026-11-21 applied\n")
        print("\n  已写回 source-v2（并落标记，防止二次搬迁）")
    else:
        print("\n  （只报；加 --write 才写）")
    for c in changes:
        print("   ", c[0], c[1], "→", c[2])
    return 0


if __name__ == "__main__":
    sys.exit(main())
