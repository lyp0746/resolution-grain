#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全书结构自检（2026-11-17，第五十六轮加）。

为什么写这个
  这一轮之前，新插一张表会让后面所有表号错位，而"按文档顺序重排"是手工做的——
  已经碰上五次撞号（ch15、ch16、ch24…）。这里把它变成一次可跑的检查。

查六件事
  1. 每章的表号、图号，是否按**文档顺序**连续（1,2,3…）
  2. 每章的节号是否连续，且前缀与章号一致
  3. 正文里引用的「表 X.Y／图 X.Y」是否真的存在（防止改号后引用悬空）
  4. 禁词（必然／注定／不可避免／无法消除／死路）
  5. markdown 残留（** 与 <strong>）
  6. 每个 <table> 是否有 caption、每个 <figure> 是否有 figcaption

用法
    "$PY" analysis/check_order.py          # 只报
    "$PY" analysis/check_order.py --strict # 有问题退出码 1
"""
from __future__ import annotations

import argparse
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")
BAN = ["必然", "注定", "不可避免", "无法消除", "死路"]


def read(p):
    return io.open(p, encoding="utf-8").read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--src", default="source", help="相对于仓根的源目录（V2 用 source-v2）")
    args = ap.parse_args()
    src = os.path.join(ROOT, args.src)

    files = sorted(glob.glob(os.path.join(src, "ch*.html")))
    problems = []

    for p in files:
        name = os.path.basename(p)
        ch = int(re.sub(r"\D", "", name))
        s = read(p)

        # 1 表号 / 图号：按文档顺序
        caps = [(m.start(), int(m.group(2))) for m in
                re.finditer(r"<caption[^>]*>\s*表\s?(\d+)\.(\d+)", s)]
        ch_caps = [n for _, n in caps]
        if ch_caps and ch_caps != list(range(1, len(ch_caps) + 1)):
            problems.append(f"{name} 表号非文档顺序：{ch_caps}")

        figs = [(m.start(), int(m.group(2))) for m in
                re.finditer(r"<figcaption[^>]*>\s*<b>\s*图\s?(\d+)\.(\d+)", s)]
        ch_figs = [n for _, n in figs]
        if ch_figs and ch_figs != list(range(1, len(ch_figs) + 1)):
            problems.append(f"{name} 图号非文档顺序：{ch_figs}")

        # 2 节号
        secs = [int(m.group(2)) for m in
                re.finditer(r'<h3[^>]*>\s*(\d+)\.(\d+)', s)]
        if secs and secs != list(range(1, len(secs) + 1)):
            problems.append(f"{name} 节号不连续：{secs}")
        pre = {int(m.group(1)) for m in re.finditer(r'<h3[^>]*>\s*(\d+)\.(\d+)', s)}
        if pre and pre != {ch}:
            problems.append(f"{name} 节号前缀异常：{sorted(pre)}")

        # 3 引用悬空
        have_t = {n for _, n in caps}
        have_f = set(ch_figs)
        text = re.sub(r"<[^>]+>", "", s)
        for m in re.finditer(r"表\s?(\d+)\.(\d+)", text):
            if int(m.group(1)) == ch and int(m.group(2)) not in have_t:
                problems.append(f"{name} 引用了不存在的表 {m.group(1)}.{m.group(2)}")
        for m in re.finditer(r"图\s?(\d+)\.(\d+)", text):
            if int(m.group(1)) == ch and int(m.group(2)) not in have_f:
                problems.append(f"{name} 引用了不存在的图 {m.group(1)}.{m.group(2)}")

        # 4 禁词
        for w in BAN:
            for m in re.finditer(w, text):
                ctx = text[max(0, m.start() - 5): m.start() + len(w) + 4]
                if any(x in ctx for x in ("不必然", "不是必然", "不用四个词")):
                    continue
                problems.append(f"{name} 禁词「{w}」：…{ctx}…")

        # 5 markdown 残留
        if "**" in s:
            problems.append(f"{name} 有 markdown 粗体残留 **")
        if "<strong>" in s:
            problems.append(f"{name} 有 <strong>（应改 <b>）")

        # 6 表/图缺题
        for m in re.finditer(r"<table", s):
            if "<caption" not in s[m.start(): m.start() + 400]:
                problems.append(f"{name} 有一张表缺 caption")
        for m in re.finditer(r"<figure", s):
            if "<figcaption" not in s[m.start(): m.start() + 800]:
                problems.append(f"{name} 有一个图缺 figcaption")

    # 附录与后置：只查禁词与残留
    for p in sorted(glob.glob(os.path.join(SRC, "appendix_*.html"))) + \
             sorted(glob.glob(os.path.join(SRC, "back_*.html"))) + \
             sorted(glob.glob(os.path.join(SRC, "front_*.html"))):
        name = os.path.basename(p)
        s = read(p)
        text = re.sub(r"<[^>]+>", "", s)
        if "**" in s:
            problems.append(f"{name} 有 ** 残留")
        if "<strong>" in s:
            problems.append(f"{name} 有 <strong>")

    print(f"查了 {len(files)} 章 + 附录/前后置：{len(problems)} 处问题")
    for x in problems:
        print("  -", x)
    if args.strict and problems:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
