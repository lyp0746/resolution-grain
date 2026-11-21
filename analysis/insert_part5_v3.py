#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把第五部分写成五章（18—22），并生成第 21—22 章的结构骨架。

背景（v3.1）
  第五部分原定三章（18—20），量不够：三章装不下“变异／选择／场域／第二种遗传／收不进”五件事。
  改成五章后，后面的部分整体再移两格（社会 23—28、文明 29—34、边界 35—38），全书 8 部分 38 章。
  **第二次搬号已经跑完**（plan_renumber_v3.py --step step2），所以本脚本只做三件事：
  改 parts.json 里第五部分的章目、按源文件同步全部章节目录、给缺的两章写空骨架。

  与第一版（三章、从底本重算）的区别：base 现在是**已经搬好号的 parts.json**，
  不再从 `_backup_source-v2_20261121` 重算——那份是搬号前的底本，用它会把号又搬回去。
  幂等性靠两点：第五部分的章目整段重写；其它章的 sections 一律以源文件为准。

用法
  "$PY" -X utf8 analysis/insert_part5_v3.py            # 只报
  "$PY" -X utf8 analysis/insert_part5_v3.py --write     # 写 parts.json 与缺的骨架
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")
MAP = os.path.join(ROOT, "analysis", "chapter_map_v3.json")

# 骨架里先放的那一条文献（只为让引用审计不空转：章节标题里出现的名字，必须在文献里有条目）
SEED_REFS = {
    "22": ("进化与错误阈值",
           "<p>Eigen, M. (1971). Selforganization of matter and the evolution of biological macromolecules. "
           "<i>Naturwissenschaften</i>, 58(10), 465–523.（错误阈值与准物种；第 22 章用它说明“第一个复制子”"
           "是起源问题，不是动力学问题。）</p>"),
}

SKELETON_BODY = """<h2 class="chapter">{chapter}</h2>
<div class="box box-takeaway"><p><b>本章主张。</b>（待写：一句话主提问，句式“如果……那么……还能放在哪里？”）</p></div>

<p class="lead" data-story="1">（待写：场景开篇 ≤250 字，一个具体人／一次具体事；不许以“本章将”“本节讨论”开头）</p>

<!-- 导论（3 段，不编号）：上一部分给了什么 → 本章追问什么 → 为什么现在才问得出 -->

{secs}

<h3>本章文献（引用与延伸）</h3>
<div class="refs">
<p class="refh">{refhead}</p>
{refbody}
</div>
"""


def hanzi(t: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", re.sub(r"<[^>]+>", "", t)))


def h3_labels(path: str) -> list[str]:
    t = io.open(path, encoding="utf-8").read()
    return [re.sub(r"\s*\n\s*", "", x) for x in re.findall(r"<h3[^>]*>(.*?)</h3>", t, flags=re.S)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    m = json.load(io.open(MAP, encoding="utf-8"))
    skel = m["new_chapter_skeleton"]
    total = m["to"]["chapters"]

    # 收工守卫（2026-11-21）：五章正文写完之后，本脚本不再允许 --write——
    # 它会从底本重算 parts.json，把后来手改的部导语／小结覆盖掉。
    if a.write and any(hanzi(io.open(os.path.join(SRC, f"ch{n}.html"), encoding="utf-8").read()) > 2000
                       for n in ("18", "19", "20", "21", "22")):
        print("拒绝：第 18—22 章正文已存在，本脚本已收工；部导语／小结请直接改 parts.json。")
        return 1

    path = os.path.join(SRC, "parts.json")
    parts = json.load(io.open(path, encoding="utf-8"))
    problems = []

    # 1. 第五部分的章目整段重写（18—22）
    pv = next((p for p in parts if p["part"].startswith("第五部分")), None)
    if pv is None:
        problems.append("parts.json 里没有第五部分")
    else:
        pv["chapters"] = []
        for no in ("18", "19", "20", "21", "22"):
            s = skel[no]
            pv["chapters"].append({
                "no": no, "title": s["title"], "file": f"ch{no}.html", "written": True,
                "sections": [],       # 下面统一按源文件同步
            })

    # 2. 其它部分：章号若还在旧位上，报出来（本脚本不搬号）
    expect = {str(n): f"ch{n:02d}.html" for n in range(1, total + 1)}
    for p in parts:
        if p["part"].startswith("第五部分"):
            continue
        for c in p.get("chapters", []):
            if c["file"] != expect.get(c["no"]):
                problems.append(f"{p['part'][:6]} 第 {c['no']} 章的 file 是 {c['file']}，应为 {expect.get(c['no'])}")

    # 5. 缺的骨架：只写“不足 500 汉字”的章，绝不覆盖已有正文
    missing = []
    for no in ("18", "19", "20", "21", "22"):
        f = os.path.join(SRC, f"ch{no}.html")
        if not os.path.exists(f):
            missing.append(no)
        elif hanzi(io.open(f, encoding="utf-8").read()) <= 500:
            missing.append(no)
    print(f"\n  骨架待写：{missing or '无'}")

    # 5a. 先写缺的骨架（必须在“按源文件同步目录”之前，否则新章第一次的 sections 是空的）
    if a.write:
        for no in missing:
            s0 = skel[no]
            secs = "\n".join(
                f'<h3 id="sec{no}-{sec["no"].split(".")[1]}">{sec["no"]}　{sec["title"]}</h3>\n'
                f'<p><i>（本节待写）</i></p>\n'
                for sec in s0["sections"]
            )
            head, body = SEED_REFS.get(
                no, ("本组件待补",
                     "<p>（待补：本章正文提到的每一个人名、每一条结论、每一份材料，都要在这里有原文条目与卷期）</p>"))
            io.open(os.path.join(SRC, f"ch{no}.html"), "w", encoding="utf-8").write(
                SKELETON_BODY.format(chapter=f'第{no}章　{s0["title"]}', secs=secs,
                                     refhead=head, refbody=body))
            print(f"  写骨架 source/ch{no}.html（{len(s0['sections'])} 节）")

    # 3. 全部章目以源文件为准
    for p in parts:
        for c in p.get("chapters", []):
            f = os.path.join(SRC, c.get("file", ""))
            if os.path.exists(f):
                c["sections"] = h3_labels(f)
                c["written"] = True

    # 4. 自检
    nos = [c["no"] for p in parts for c in p.get("chapters", [])]
    if len(parts) != 8:
        problems.append(f"部分数不是 8：{len(parts)}")
    if nos != [str(i) for i in range(1, total + 1)]:
        problems.append(f"章号不是 1—{total} 连续：{nos}")

    print(f"目标：{len(parts)} 部分／{total} 章")
    for p in parts:
        ns = [c["no"] for c in p["chapters"]]
        print(f"  {p['part']}  →  {ns[0]}—{ns[-1]}（{len(ns)} 章）")

    print("\n  自检：" + ("OK" if not problems else "；".join(problems)))

    if a.write:
        json.dump(parts, io.open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("  写 parts.json")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
