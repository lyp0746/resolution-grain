#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给正文补“（表 N.M）／（图 N.M）”编号引用。

只做一件事：每张表/图，若它前面最近的段落没有按号提到它，就在那一段的句末补一个括号引用。
不跨表、不跨图、不跨节；碰到上一张表/图的尾巴就跳过（说明这一段不是给它做引子的）。

用法：
  "$PY" analysis/add_figrefs.py --check   # 只报告
  "$PY" analysis/add_figrefs.py --apply   # 就地改 source-v2
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "source"


def num_of(kind: str, seg: str) -> str | None:
    if kind == "table":
        m = re.search(r'<caption class="cap">表\s*([0-9A-F]+\.\d+)', seg)
    else:
        m = re.search(r'<figcaption class="cap"><b>图\s*([0-9A-F]+\.\d+)', seg)
    return m.group(1) if m else None


def add_ref(text: str, kind: str, num: str, pos: int) -> tuple[str, bool]:
    seg = text[:pos]
    ps = list(re.finditer(r"<p[^>]*>.*?</p>", seg, re.S))
    if not ps:
        return text, False
    p = ps[-1]
    between = seg[p.end():pos]
    # 这一段与表/图之间若已经隔了另一张表/图或一个新节，说明不是引子
    if re.search(r"</table>|</figure>|<h[234]\b", between):
        return text, False
    body = p.group(0)
    plain = re.sub(r"<[^>]+>", "", body)
    key = f"表{num}" if kind == "table" else f"图{num}"
    if key in plain or (f"表 {num}" in plain) or (f"图 {num}" in plain):
        return text, False
    # 只在句末补；段落以冒号/分号结尾时，补在标点之前
    m = re.search(r"([。；：，])(\s*(?:<[^>]+>\s*)*)$", body)
    ins = f"（{key}）"
    if m:
        new = body[: m.start(1)] + ins + body[m.start(1):]
    else:
        new = body + ins
    return text[: p.start()] + new + text[p.end():], True


def process(path: Path, apply: bool):
    t = path.read_text(encoding="utf-8")
    changes = []
    # 从后往前处理，避免位置漂移
    hits = []
    for m in re.finditer(r"<table\b", t):
        end = t.find("</table>", m.start())
        num = num_of("table", t[m.start():end + 8])
        if num:
            hits.append(("table", num, m.start()))
    for m in re.finditer(r"<figure\b", t):
        end = t.find("</figure>", m.start())
        num = num_of("figure", t[m.start():end + 9])
        if num:
            hits.append(("figure", num, m.start()))
    for kind, num, pos in sorted(hits, key=lambda x: -x[2]):
        t2, ok = add_ref(t, kind, num, pos)
        if ok:
            changes.append((kind, num))
            t = t2
    if apply and changes:
        path.write_text(t, encoding="utf-8")
    return changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    files = sorted(SRC.glob("ch*.html")) + sorted(SRC.glob("appendix_*.html"))
    total = 0
    for f in files:
        ch = process(f, args.apply)
        if ch:
            total += len(ch)
            print(f"{f.name}: {len(ch)}  " + " ".join(f"{k}{n}" for k, n in ch))
    print("total", total, "applied" if args.apply else "checked")


if __name__ == "__main__":
    main()
