#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""命名体检：抓"改号脚本抓不到"的章号。

为什么要有这个脚本
  改号脚本（`plan_renumber_v4.py`）认七类 token：第 N 章／§N.M／表N.M／图N.M／
  N.M 节／id="secN-M"／式(N.M)。它**认不出裸数字**：表格里单独一列 `<td>25</td>`、
  路线图里的章号列、以及"第 29—34 章"这种**区间**。
  本书已经因此踩过三次：附录 B 表 B.1、附录 F 章列、表 R.1 整表（第 25—38 行错位）。
  三次都不是笔误，是同一类盲区。所以留一个常驻的，每次改号后跑一次。

查四件事
  1 **裸数字行**：`<td>N</td>` 的行，若同一行里出现的主题词指向另一章，判错。
  2 **路线图题名**：表 R.1 的"题"列必须与各章 `<h2>` 逐字相同。
  3 **区间**：`第 N—M 章` 必须落在某个部分的边界上（部分边界从 parts.json 读）。
  4 **主题词与章号**：正文"第N章"后面紧跟的主题词若属于另一章，判错（V4 §9 的判据）。

用法
  "$PY" -X utf8 analysis/check_naming.py            # 只报，写 analysis/NAMING-AUDIT.md
  "$PY" -X utf8 analysis/check_naming.py --strict   # 有硬错则退出码 1（供 selfcheck 用）
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "source"

# 主题词 -> 应在的章（改号或换章时同步这张表；它只用来"指路"，不用来判定语义）
TOPIC = {
    "核实": 23, "账单": 24, "转移": 25, "跨格": 26, "内卷": 27, "负卷": 27,
    "漂移": 28, "改码": 29, "临界": 30, "转型": 31, "长时段": 32, "分期": 33,
    "翻译": 34, "边缘": 35, "语义": 36, "边界": 37, "判决": 38, "结语": 39,
    "共用码": 13, "标签": 14, "讲述": 15, "权力": 16, "维护": 17, "变异": 18,
    "红皇后": 19, "场域": 20, "文化": 21, "爱": 9, "好奇": 10, "审美": 11,
    "创造": 12, "旋钮": 6, "记住": 7, "跟上": 8,
}


# 人工复核过的例外：短语级，不是文件级——这样才能保证别的同类错误仍被抓住。
EXEMPT = {
    "第3章的判决场": "“判决场”是第 3 章注意盲视的判决场，不是第 38 章",
    "第6章把改码的来": "改码成本 C 在第 6 章是一只旋钮（四个旋钮之一）",
}


def load():
    parts = json.loads((SRC / "parts.json").read_text(encoding="utf-8"))
    titles, bounds = {}, []
    for p in parts:
        nos = [int(c["no"]) for c in p["chapters"]]
        bounds.append((min(nos), max(nos), p["part"]))
        for c in p["chapters"]:
            f = SRC / c["file"]
            t = f.read_text(encoding="utf-8")
            m = re.search(r"<h2[^>]*>(.*?)</h2>", t, re.S)
            titles[int(c["no"])] = re.sub(r"<[^>]+>", "", m.group(1)).split("　", 1)[-1].strip()
    return parts, titles, bounds


def txt(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    parts, titles, bounds = load()
    files = sorted(SRC.glob("*.html"))
    hard, soft = [], []

    # 1 裸数字行
    #    陷阱：附录 E 与第 39 章表 39.1 的第一列是"序号"（六核心 1—6、空白 1—9），
    #    不是章号；对它们做章号比对只会造假。所以先按文件排除。
    SKIP_BARE = {"appendix_e.html", "ch39.html"}
    for f in files:
        if f.name in SKIP_BARE:
            continue
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"<tr>(.*?)</tr>", t, re.S):
            row = m.group(1)
            c = re.match(r"\s*<td[^>]*>\s*(\d{1,2})\s*</td>", row)
            if not c:
                continue
            n = int(c.group(1))
            if n not in titles:
                continue
            body = txt(row)
            # 硬错：同一行里自己写了"第 M 章"，而 M 与行首的 N 不一致
            mm = re.search(r"第\s*(\d{1,2})\s*章", body)
            if mm and int(mm.group(1)) != n:
                hard.append(f"{f.name}: 行首章号 {n}，行内却写「{mm.group(0)}」｜{body[:60]}")
                continue
            # 待看：行内紧跟的第一个词若指向另一章，提示一次（不判错）
            lead = re.sub(r"[^\u4e00-\u9fff]", "", body)[:6]
            for w, cn in TOPIC.items():
                if w in lead and cn != n:
                    soft.append(f"{f.name}: 行首章号 {n}，但行文以「{w}」开头（该词主在第 {cn} 章）｜{body[:50]}")
                    break

    # 2 路线图题名
    road = SRC / "front_roadmap.html"
    if road.exists():
        t = road.read_text(encoding="utf-8")
        for m in re.finditer(r"<tr><td>(\d{1,2})</td><td>([^<]*)</td>", t):
            n = int(m.group(1))
            if n in titles and m.group(2).strip() != titles[n]:
                hard.append(f"表 R.1: 第 {n} 章题为「{m.group(2).strip()}」，实际「{titles[n]}」")

    # 3 区间
    for f in files:
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"第\s*(\d{1,2})\s*[—－–-]\s*(\d{1,2})\s*章", t):
            lo, hi = int(m.group(1)), int(m.group(2))
            ok = any(lo == b[0] and hi == b[1] for b in bounds)
            if (not ok) and (hi - lo + 1) >= 3:
                soft.append(f"{f.name}: {m.group(0)}（不是任何部分的边界："
                            + "／".join(f"{b[0]}—{b[1]}" for b in bounds) + "）")

    # 4 主题词与章号
    for f in files:
        if not f.name.startswith("ch"):
            continue
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"第\s*(\d{1,2})\s*章([\u4e00-\u9fff]{0,5})", t):
            n, tail = int(m.group(1)), m.group(2)
            for w, cn in TOPIC.items():
                if w in tail and cn != n and not (w == "语义" and "漂移" in tail):
                    phrase = f"第{n}章{tail}"
                    if any(phrase.startswith(k) for k in EXEMPT):
                        break
                    hard.append(f"{f.name}: {phrase}（「{w}」应在第 {cn} 章）")
                    break

    lines = ["# 命名体检（裸数字／路线图／区间／主题词）", "",
             f"共 {len(files)} 个源文件；章 {len(titles)}；部分边界 "
             + "／".join(f"{b[0]}—{b[1]}" for b in bounds), "",
             f"## 硬错（{len(hard)}）", ""]
    lines += [f"- {x}" for x in hard] or ["- 无"]
    lines += ["", f"## 待看（{len(soft)}）", ""]
    lines += [f"- {x}" for x in soft] or ["- 无"]
    (ROOT / "analysis" / "NAMING-AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    io.open(1, "w", encoding="utf-8", closefd=False).write(
        f"命名体检：硬错 {len(hard)}，待看 {len(soft)}（明细见 analysis/NAMING-AUDIT.md）\n")
    for x in hard[:10]:
        io.open(1, "w", encoding="utf-8", closefd=False).write("  ! " + x + "\n")
    return 1 if (a.strict and hard) else 0


if __name__ == "__main__":
    sys.exit(main())
