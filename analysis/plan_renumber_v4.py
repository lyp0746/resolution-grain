#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""改号空跑／落地（V4：38 章 → 39 章，转移搬进第六部分＋新写跨格者）。

两步，必须分开跑、每步过四项检查：

  step1（搬章，38 章不变）：第 36 章「转移」搬成第 25 章，25—35 各后移一格。
    映射是一个**循环移位**：{25→26, 26→27, …, 35→36, 36→25}。
  step2（插章，38 → 39）：在 25 之后空出第 26 章给「跨格」，原 26—38 各后移一格。
    映射：{26→27, 27→28, …, 38→39}。

为什么不用一次映射：一次做完等于 {25..35→27..37, 36→25, 37→38, 38→39}，
中间不留空位，新章无处落脚，而且出错时无法判断是"搬错"还是"插错"。

七类 token 的处理照 V3 的做法：**一次扫描＋占位符**，避免多轮替换把新号再替一次。

用法
  "$PY" -X utf8 analysis/plan_renumber_v4.py --step 1              # 只报
  "$PY" -X utf8 analysis/plan_renumber_v4.py --step 1 --apply      # 落地（需 backup）
  "$PY" -X utf8 analysis/plan_renumber_v4.py --step 2 --apply

纪律
  * 默认只读；--apply 要求 `_backup_source_YYYYMMDD` 至少存在一个。
  * 不写正文、不写 parts.json 的部名与导语（那是人写的，见 V4-RESTRUCTURE.md §2）。
  * 落盘只写**真有差异**的文件（原地写整目录会撞 Windows 文件锁，V3 踩过）。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")
TOKEN = "@@CH{}@@"

# ---------------------------------------------------------------- 映射
STEP1 = {n: (n + 1 if n <= 35 else 25) for n in range(25, 37)}    # 25..36 循环移位
STEP2 = {n: n + 1 for n in range(26, 39)}                        # 26..38 → 27..39


def token_patterns():
    return [
        ("chapter_ref", re.compile(r"第(\s*)(\d{1,2})(\s*)章")),
        ("section_ref", re.compile(r"§(\s*)(\d{1,2})\.(\d{1,2})")),
        ("table_ref", re.compile(r"表(\s*)(\d{1,2})\.(\d{1,2})")),
        ("figure_ref", re.compile(r"图(\s*)(\d{1,2})\.(\d{1,2})")),
        ("section_word", re.compile(r"(\d{1,2})\.(\d{1,2})(\s*)节")),
        ("anchor_id", re.compile(r'id="sec(\d{1,2})-(\d{1,2})')),
        ("eq_num", re.compile(r'class="num">\((\d{1,2})\.(\d{1,2})\)')),
        ("heading_label", re.compile(r'(<h[234][^>]*>\s*)(\d{1,2})(\.\d{1,2}(?:\.\d{1,2})?)')),
    ]


def rewrite(text, cmap, stats):
    for name, pat in token_patterns():
        def sub(m, name=name):
            g = m.groups()
            if name == "chapter_ref":
                n = int(g[1]); stats[name][0] += 1
                if n not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                return "第" + g[0] + TOKEN.format(n) + g[2] + "章"
            if name in ("section_ref", "table_ref", "figure_ref"):
                n = int(g[1]); stats[name][0] += 1
                if n not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                head = m.group(0)[: m.start(2) - m.start(0)]
                return head + TOKEN.format(n) + "." + g[2]
            if name == "section_word":
                n = int(g[0]); stats[name][0] += 1
                if n not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                return TOKEN.format(n) + "." + g[1] + g[2] + "节"
            if name == "anchor_id":
                n = int(g[0]); stats[name][0] += 1
                if n not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                return 'id="sec' + TOKEN.format(n) + "-" + g[1]
            if name == "heading_label":
                n = int(g[1]); stats[name][0] += 1
                if n not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                return g[0] + TOKEN.format(n) + g[2]
            if name == "eq_num":
                n = int(g[0]); stats[name][0] += 1
                if n not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                return 'class="num">(' + TOKEN.format(n) + "." + g[1] + ")"
            return m.group(0)
        text = pat.sub(sub, text)
    return re.sub(r"@@CH(\d{1,2})@@", lambda m: str(cmap[int(m.group(1))]), text)


def chapter_of(path):
    d = re.sub(r"\D", "", os.path.basename(path))
    return int(d) if d else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", default="1", choices=["1", "2"])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default=None, help="写副本到此目录（相对仓根）")
    a = ap.parse_args()

    cmap = STEP1 if a.step == "1" else STEP2
    total = 38 if a.step == "1" else 39

    print("=" * 72)
    print(f"V4 改号 step{a.step}：{len(cmap)} 章 → 新号 {min(cmap.values())}—{max(cmap.values())}；全书 {total} 章")
    print("=" * 72)

    files = sorted(glob.glob(os.path.join(SRC, "*.html")), key=chapter_of)
    stats = {name: [0, 0] for name, _ in token_patterns()}
    out, per_file = {}, []
    for f in files:
        t = open(f, encoding="utf-8").read()
        before = sum(v[0] for v in stats.values())
        out[os.path.basename(f)] = rewrite(t, cmap, stats)
        n = sum(v[0] for v in stats.values()) - before
        if n:
            per_file.append((os.path.basename(f), n, chapter_of(f)))

    print("\n[1] token（命中／落在映射键内）")
    for name, (tot, hit) in stats.items():
        print(f"    {name:14s} {tot:5d} / {hit:5d}")
    print(f"    合计 {sum(v[0] for v in stats.values())} 处，需改 {sum(v[1] for v in stats.values())} 处")
    for name, n, ch in sorted(per_file, key=lambda x: -x[1])[:12]:
        tag = f"第 {ch} 章 → 第 {cmap[ch]} 章" if ch in cmap else "前置／后置／附录"
        print(f"      {name:22s} {n:5d}  {tag}")

    # 后置不变量：改号后不许出现 @ 占位符残留；章号必须落在 1..total
    bad = []
    for name, nt in out.items():
        if "@@CH" in nt:
            bad.append((name, "占位符残留"))
        own = chapter_of(name)
        for mm in re.finditer(r"第\s*(\d{1,2})\s*章", nt):
            n = int(mm.group(1))
            if not (1 <= n <= total):
                bad.append((name, f"越界 第{n}章"))
    print(f"\n[2] 后置不变量：{'OK' if not bad else bad[:5]}")

    # 表／图 caption 与引用自洽（同章相对号不变）
    prob = 0
    for f in glob.glob(os.path.join(SRC, "ch*.html")):
        t = out[os.path.basename(f)]
        ch_new = cmap.get(chapter_of(f), chapter_of(f))
        for kind, cap_pat in (("表", r"<caption[^>]*>\s*表(\d{1,2})\.(\d{1,2})"),
                              ("图", r"figcaption[^>]*>\s*(?:<b>)?图(\d{1,2})\.(\d{1,2})")):
            caps = re.findall(cap_pat, t)
            have = {c[1] for c in caps if int(c[0]) == ch_new}
            refs = re.findall(kind + r"(\d{1,2})\.(\d{1,2})", t)
            want = {r[1] for r in refs if int(r[0]) == ch_new}
            miss = want - have
            if miss:
                prob += 1
                print(f"    ! {os.path.basename(f)} {kind}{sorted(miss)} 引用无 caption")
    print(f"[3] 章内表／图号自洽：{'OK' if prob == 0 else str(prob) + ' 处待查'}")

    renames = []
    for f in glob.glob(os.path.join(SRC, "ch*.html")):
        ch = chapter_of(f)
        if ch in cmap:
            renames.append((os.path.basename(f), f"ch{cmap[ch]:02d}.html"))
    print(f"\n[4] 需改名文件 {len(renames)} 个")
    for x, y in sorted(renames, key=lambda z: -int(re.sub(r"\D", "", z[0]))):
        print(f"      {x} → {y}")

    if not (a.apply or a.out):
        print("\n（空跑。加 --apply 落地，或 --out <目录> 写副本）")
        return 0 if not bad else 1

    dst = SRC if a.apply else os.path.join(ROOT, a.out)
    if a.apply and not glob.glob(os.path.join(ROOT, "_backup_source_*")):
        print("\n拒绝：--apply 前必须先做 _backup_source_YYYYMMDD 备份")
        return 1
    os.makedirs(dst, exist_ok=True)
    inplace = os.path.abspath(dst) == os.path.abspath(SRC)

    n_written = 0
    for name, txt in out.items():
        dstp = os.path.join(dst, name)
        try:
            same = os.path.exists(dstp) and open(dstp, encoding="utf-8").read() == txt
        except (OSError, UnicodeDecodeError):
            same = False
        if same:
            continue
        open(dstp, "w", encoding="utf-8").write(txt)
        n_written += 1
    if not inplace:
        for extra in glob.glob(os.path.join(SRC, "*")):
            b = os.path.basename(extra)
            if b in out or b == "parts.json" or not os.path.isfile(extra):
                continue
            shutil.copy2(extra, os.path.join(dst, b))

    # 改名：先全部搬到临时名，再搬到终名。
    # （V4 踩过：这一步是**循环移位**（36→25 同时 25→26），降序单向搬会先写掉 ch25，
    #  导致内卷一章的正文被转移章覆盖、且 ch25 最终不存在。临时名法对环也安全。）
    for old, new in renames:
        srcp = os.path.join(dst, old)
        if os.path.exists(srcp):
            os.replace(srcp, srcp + ".v4tmp")
    for old, new in renames:
        tmpp = os.path.join(dst, old + ".v4tmp")
        if os.path.exists(tmpp):
            os.replace(tmpp, os.path.join(dst, new))

    # parts.json：章号与文件名（部名、导语、小结是人写的，不在这里改）
    pj = json.load(open(os.path.join(SRC if inplace else dst, "parts.json"), encoding="utf-8"))
    for p in pj:
        for c in p.get("chapters", []):
            n = int(c["no"])
            if n in cmap:
                c["no"] = str(cmap[n])
                c["file"] = f"ch{cmap[n]:02d}.html"
    json.dump(pj, open(os.path.join(dst, "parts.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"\n[写] 文本 {n_written} 个，改名 {len(renames)} 个，parts.json 已同步章号")
    print("下一步：跑四项检查 + 人工改部名／导语／字数口径（见 analysis/V4-RESTRUCTURE.md §2）")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
