#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""改号空跑（V3：七部分 33 章 → 八部分 36 章）。

为什么要有这个脚本
  这一轮要把第 18—33 章整体后移三格（18→21 … 33→36），并在 18—20 插入新部分。
  正文里跟号走的token有七类（第 N 章／§N.M／表N.M／图N.M／N.M 节／id="secN-M"／式(N.M)），
  各自都有两种空格写法；再加文件名与 parts.json。手改必然漏，漏法还有一种特别坏：
  **多轮替换会把上一轮刚写出来的新号再替一次**（18→21 造出“第 21 章”，下一轮 21→24 又把它改成 24）。

  所以这里的做法是**一次扫描＋回调**：整段文本只走一遍，每个匹配只被访问一次，
  旧号先进占位符 `\\x00CH18\\x00`，全部扫完之后再把占位符换成新号。
  这样任何新写出来的号都不会被二次命中，替换顺序也无关。

查五件事
  1. 映射是否单射、是否覆盖 18—33、是否与 parts.json 的章号一致
  2. 七类token各命中多少、其中落在 18—33 的有多少、按文件排在哪儿
  3. 后置不变量：改号后**不许**出现对 18—20 的引用（新章还没写，引用无处可指）
  4. 表号／图号引用是否都能在本章找到对应 caption（改号后同章内相对号不变，应全对）
  5. 文件名与 parts.json 的 `file` 字段是否同批改到位

用法
  "$PY" -X utf8 analysis/plan_renumber_v3.py                    # 只报（空跑，不写盘）
  "$PY" -X utf8 analysis/plan_renumber_v3.py --out _temp/preview # 写一份改号副本（不动 source-v2）
  "$PY" -X utf8 analysis/plan_renumber_v3.py --out _temp/preview --apply-source  # 真改 source-v2（有备份才允许）

纪律
  * 默认只读；写盘必须显式给 --out。
  * --apply-source 要求 _backup_source-v2_YYYYMMDD 至少存在一个，否则拒绝执行。
  * 本脚本不写正文：新章 18—20 由人写，脚本只搬号。
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
MAP_PATH = os.path.join(ROOT, "analysis", "chapter_map_v3.json")

TOKEN = "@@CH{}@@"              # 占位符：正文里不会自然出现；万一泄进产物，一眼看得见


def load_map():
    with open(MAP_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def token_patterns():
    """七类 token；第 1 组是章号，其余组原样保留（.M 与 '-' 分隔不变）。"""
    return [
        ("chapter_ref", re.compile(r"第(\s*)(\d{1,2})(\s*)章")),
        ("section_ref", re.compile(r"§(\s*)(\d{1,2})\.(\d{1,2})")),
        ("table_ref", re.compile(r"表(\s*)(\d{1,2})\.(\d{1,2})")),
        ("figure_ref", re.compile(r"图(\s*)(\d{1,2})\.(\d{1,2})")),
        ("section_word", re.compile(r"(\d{1,2})\.(\d{1,2})(\s*)节")),
        ("anchor_id", re.compile(r'id="sec(\d{1,2})-(\d{1,2})')),
        ("eq_num", re.compile(r'class="num">\((\d{1,2})\.(\d{1,2})\)')),
        # h3／h4 的节标题本身（"18.1　……"、"23.8.3　……"）——check_order 读的就是它
        ("heading_label", re.compile(r'(<h[34][^>]*>\s*)(\d{1,2})(\.\d{1,2}(?:\.\d{1,2})?)')),
    ]


def rewrite(text, cmap, stats):
    """一次扫描＋回调；旧号→占位符，最后统一放号。"""
    for name, pat in token_patterns():
        def sub(m, name=name, pat=pat):
            g = m.groups()
            if name == "chapter_ref":
                n = int(g[1])
                stats[name][0] += 1
                if str(n) not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                return "第" + g[0] + TOKEN.format(n) + g[2] + "章"
            if name in ("section_ref", "table_ref", "figure_ref"):
                n = int(g[1])
                stats[name][0] += 1
                if str(n) not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                head = m.group(0)[: m.start(2) - m.start(0)]
                return head + TOKEN.format(n) + "." + g[2]
            if name == "section_word":
                n = int(g[0])
                stats[name][0] += 1
                if str(n) not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                return TOKEN.format(n) + "." + g[1] + g[2] + "节"
            if name == "anchor_id":
                n = int(g[0])
                stats[name][0] += 1
                if str(n) not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                return 'id="sec' + TOKEN.format(n) + "-" + g[1]
            if name == "heading_label":
                n = int(g[1])
                stats[name][0] += 1
                if str(n) not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                return g[0] + TOKEN.format(n) + g[2]
            if name == "eq_num":
                n = int(g[0])
                stats[name][0] += 1
                if str(n) not in cmap:
                    return m.group(0)
                stats[name][1] += 1
                return 'class="num">(' + TOKEN.format(n) + "." + g[1] + ")"
            return m.group(0)
        text = pat.sub(sub, text)
    # 放号：占位符 → 新号
    def release(m):
        return str(cmap[m.group(1)])
    text = re.sub(r"@@CH(\d{1,2})@@", release, text)
    return text


def chapter_of(path):
    d = re.sub(r"\D", "", os.path.basename(path))
    return int(d) if d else 0


def check_map(cmap, parts, total_chapters=38):
    """映射自检（两轮通用）：单射、键连续、新号不越界、parts.json 章数对不对。"""
    errs = []
    new = list(cmap.values())
    if len(set(new)) != len(new):
        errs.append("映射不是单射")
    old = sorted(int(k) for k in cmap)
    if old != list(range(old[0], old[-1] + 1)):
        errs.append(f"映射的键不连续：{old}")
    if len(set(cmap.values()) & set(old)) and old != sorted(new):
        # 两轮都会出现"新号与旧号重叠"（第二轮的 23—36 既是新号又是旧号），
        # 这不是错，但必须靠占位符一次性替换；这里只提示。
        pass
    for n in new:
        if n < 1 or n > total_chapters:
            errs.append(f"新号越界：{n}")
    pch = [c["no"] for p in parts for c in p.get("chapters", [])]
    if len(pch) != total_chapters:
        errs.append(f"parts.json 章数不是 {total_chapters}：{len(pch)}")
    return errs


def caption_refs(text, kind):
    """本章 caption 里的表号／图号（本本相对号），与正文引用的同章号对照。"""
    if kind == "表":
        caps = re.findall(r"<caption[^>]*>\s*表(\d{1,2})\.(\d{1,2})", text)
        refs = re.findall(r"表(\d{1,2})\.(\d{1,2})", text)
    else:
        caps = re.findall(r"figcaption[^>]*>\s*(?:<b>)?图(\d{1,2})\.(\d{1,2})", text)
        refs = re.findall(r"图(\d{1,2})\.(\d{1,2})", text)
    return caps, refs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="写改号副本到此目录（相对仓根）；缺省只报")
    ap.add_argument("--apply-source", action="store_true", help="直接改 source-v2（需已有备份）")
    ap.add_argument("--step", default="step1",
                    help="step1 用 step1_chapter_map（18—33 → 21—36，已执行）；"
                         "step2 用 step2_chapter_map（21—36 → 23—38，第五部分扩到五章时执行）")
    ap.add_argument("--forbid", default="18,19,20",
                    help="后置不变量：改号后不许出现的章号（逗号分隔）。写完新章后改这里")
    a = ap.parse_args()

    m = load_map()
    key = "step1_chapter_map" if a.step == "step1" else a.step + "_chapter_map"
    cmap = m.get(key) or m["chapter_map"]
    forbid = {int(x) for x in a.forbid.split(",") if x.strip()}
    with open(os.path.join(SRC, "parts.json"), encoding="utf-8") as fh:
        parts = json.load(fh)

    print("=" * 72)
    print(f"V3.1 改号空跑（{a.step}）：映射 {min(int(k) for k in cmap)}—{max(int(k) for k in cmap)}"
          f" → {min(cmap.values())}—{max(cmap.values())}；共 {len(cmap)} 章")
    print("=" * 72)

    total = m.get("to", {}).get("chapters", 38)
    errs = check_map(cmap, parts, total)
    inj = len(set(cmap.values())) == len(cmap)
    print(f"\n[1] 映射：{len(cmap)} 章　单射 {'是' if inj else '否'}")
    for e in errs:
        print("    ! " + e)

    files = sorted(glob.glob(os.path.join(SRC, "*.html")), key=chapter_of)
    stats = {name: [0, 0] for name, _ in token_patterns()}
    per_file = []
    out_texts = {}
    for f in files:
        t = open(f, encoding="utf-8").read()
        before = sum(v[0] for v in stats.values())
        nt = rewrite(t, cmap, stats)
        out_texts[os.path.basename(f)] = nt
        n = sum(v[0] for v in stats.values()) - before
        if n:
            per_file.append((os.path.basename(f), n, chapter_of(f)))

    print("\n[2] token（命中／其中落在映射键内）")
    for name, (tot, hit) in stats.items():
        print(f"    {name:14s} {tot:5d} / {hit:5d}")
    print(f"    合计 {sum(v[0] for v in stats.values())} 处，需改 {sum(v[1] for v in stats.values())} 处")

    print("\n    按文件（需改处数，降序前 15）")
    for name, n, ch in sorted(per_file, key=lambda x: -x[1])[:15]:
        tag = f"（第 {ch} 章 → 第 {cmap.get(str(ch), ch)} 章）" if ch else "（前置／后置／附录）"
        print(f"      {name:22s} {n:5d}  {tag}")

    # [3] 后置不变量：不许有对 18—20 的引用
    bad = []
    for name, nt in out_texts.items():
        own = chapter_of(name)          # 章自己的 h2 会写自己的章号，不算悬空引用
        for mm in re.finditer(r"第\s*(\d{1,2})\s*章", nt):
            n = int(mm.group(1))
            if n in forbid and n != own:
                bad.append((name, mm.group(0)))
    print(f"\n[3] 后置不变式：改号后不得出现对 {sorted(forbid)} 的引用")
    if bad:
        print(f"    ! {len(bad)} 处：{bad[:5]}")
    else:
        print("    OK（新号全部落在 1—17 与 21—36）")

    # [4] 章内表／图号自洽（同章相对号不变，改号不该影响）
    prob = 0
    for f in glob.glob(os.path.join(SRC, "ch*.html")):
        t = open(f, encoding="utf-8").read()
        ch = chapter_of(f)
        for kind in ("表", "图"):
            caps, refs = caption_refs(t, kind)
            have = {c[1] for c in caps if int(c[0]) == ch}
            want = {r[1] for r in refs if int(r[0]) == ch}
            miss = want - have
            if miss:
                prob += 1
                print(f"    ! {os.path.basename(f)} {kind}{sorted(miss)} 引用无 caption")
    print(f"\n[4] 章内表／图号自洽：{'OK' if prob == 0 else str(prob) + ' 处待查'}（每章内部 .N 不变，改号不影响）")

    # [5] 文件名与 parts.json
    renames = []
    for f in glob.glob(os.path.join(SRC, "ch*.html")):
        ch = chapter_of(f)
        if str(ch) in cmap:
            renames.append((os.path.basename(f), f"ch{cmap[str(ch)]:02d}.html"))
    print(f"\n[5] 需改名文件 {len(renames)} 个（降序搬，避免撞名）")
    for a_, b_ in sorted(renames, key=lambda x: -int(re.sub(r"\D", "", x[0]))):
        print(f"      {a_} → {b_}")

    if a.out or a.apply_source:
        dst = SRC if a.apply_source else os.path.join(ROOT, a.out)
        if a.apply_source:
            if not glob.glob(os.path.join(ROOT, "_backup_source-v2_*")):
                print("\n拒绝：--apply-source 前必须先做 _backup_source-v2_YYYYMMDD 备份")
                return 1
        os.makedirs(dst, exist_ok=True)
        inplace = os.path.abspath(dst) == os.path.abspath(SRC)
        # 只写**真的变了**的文件（2026-11-21 修：原地落盘时整目录重写会撞上
        #  Windows 的文件锁——半途 PermissionError，留下"内容改了、文件名没改"的混合态。
        #  那次是从备份整目录恢复后才继续的；所以这里改成只写有差异的文本。）
        n_written = 0
        for name, txt in out_texts.items():
            dstp = os.path.join(dst, name)
            try:
                same = os.path.exists(dstp) and open(dstp, encoding="utf-8").read() == txt
            except (OSError, UnicodeDecodeError):
                same = False
            if same:
                continue
            open(dstp, "w", encoding="utf-8").write(txt)
            n_written += 1
        # 新建副本时才需要把未改的文件搬过去；原地落盘时它们本来就在
        if not inplace:
            for extra in glob.glob(os.path.join(SRC, "*")):
                base = os.path.basename(extra)
                if base in out_texts or base == "parts.json":
                    continue
                if os.path.isfile(extra):
                    shutil.copy2(extra, os.path.join(dst, base))
        print(f"    [写] 文本 {n_written} 个（只写有差异的）")
        # 章文件改名（**降序**搬：先 33→36，再 32→35……否则会踩掉同名旧文件；
        #  这个坑 2026-11-21 空跑时真踩了一次：升序搬完只剩 3 章）
        for old, new in sorted(renames, key=lambda x: -int(re.sub(r"\D", "", x[0]))):
            srcp = os.path.join(dst, old)
            if os.path.exists(srcp):
                os.replace(srcp, os.path.join(dst, new))
        # parts.json：章号、文件名、部件名与范围
        pj = json.loads(json.dumps(parts))
        for p in pj:
            for c in p.get("chapters", []):
                n = int(c["no"])
                if str(n) in cmap:
                    c["no"] = str(cmap[str(n)])
                    c["file"] = f"ch{cmap[str(n)]:02d}.html"
        with open(os.path.join(dst, "parts.json"), "w", encoding="utf-8") as fh:
            json.dump(pj, fh, ensure_ascii=False, indent=1)
        print(f"\n[写] 改号副本：{os.path.relpath(dst, ROOT)}（章节号已改；**部分名与导语未改，那是人写的**）")

    print("\n提示：parts.json 的部名／导语／小结与 front_roadmap 的“七部分”说法不在这七类 token 里，")
    print("      属人工改写；改完跑 check_order --src <副本> --strict 与 sync_sections --src <副本>。")
    return 1 if (errs or bad) else 0


if __name__ == "__main__":
    sys.exit(main())
