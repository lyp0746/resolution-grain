#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""source-v2 收口检查（V2 专用；lint.py 只校已登记的 24 件，本书不在内）。

用法：
    "$PY" analysis/check_v2_sources.py            # 全部 source-v2/ch*.html + front_*.html
    "$PY" analysis/check_v2_sources.py ch01.html  # 指定文件

查六项：汉字数、节数（<h3 id="sec...">）、表号／图号、图片是否存在、
HTML 标签是否平衡、禁词与残留 ** / 反引号。
退出码 1 表示有问题。
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "source-v2"
BANNED = ["必然", "注定", "不可避免", "无法消除", "死路"]
TAGS = ("div", "p", "table", "figure", "ul", "ol", "li", "tr", "td", "th",
        "h2", "h3", "figcaption", "caption", "pre", "blockquote")
LO, HI = 8000, 10 ** 9   # 每章下限 8,000 汉字（2026-11-19 作者定：上限取消，篇幅越多越好）


def hanzi(text):
    return len(re.findall(r"[\u4e00-\u9fff]", re.sub(r"<[^>]+>", "", text)))


def check(path):
    t = path.read_text(encoding="utf-8")
    issues = []
    for tag in TAGS:
        o = len(re.findall(rf"<{tag}[\s>]", t))
        c = len(re.findall(rf"</{tag}>", t))
        if o != c:
            issues.append(f"标签不平衡 <{tag}> {o}/{c}")
    for w in BANNED:
        n = t.count(w)
        if n:
            for m in re.finditer(w, t):
                issues.append(f"禁词「{w}」第 {t[:m.start()].count(chr(10)) + 1} 行")
    if "**" in t:
        issues.append("残留 ** （粗体漏成星号）")
    if "`" in re.sub(r"<code>.*?</code>", "", t, flags=re.S):
        issues.append("残留反引号（<code> 外）")
    for im in re.findall(r'<img src="([^"]+)"', t):
        if not (ROOT / im).exists():
            issues.append(f"图片不存在 {im}")
    figs = re.findall(r'<figure>', t)
    caps = re.findall(r'figcaption class="cap"', t)
    if len(figs) != len(caps):
        issues.append(f"figure/figcaption 不配对 {len(figs)}/{len(caps)}")
    n = hanzi(t)
    if path.name.startswith("ch") and not (LO <= n <= HI):
        issues.append(f"汉字 {n} 不在 {LO}—{HI}（正文章）")
    return n, len(re.findall(r'<h3 id="sec', t)), \
        sorted(set(re.findall(r"表(\d+\.\d+)", t))), \
        sorted(set(re.findall(r"图(\d+\.\d+)", t))), issues


def main(argv):
    files = [SRC / a for a in argv[1:]] or sorted(SRC.glob("*.html"))
    bad = 0
    for p in files:
        n, secs, tabs, figs, issues = check(p)
        print(f"{p.name:16s} 汉字 {n:5d}  节 {secs:2d}  表 {','.join(tabs) or '-':14s} 图 {','.join(figs) or '-'}")
        for it in issues:
            print("   !! " + it)
            bad += 1
    print("OK" if not bad else f"{bad} issue(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
