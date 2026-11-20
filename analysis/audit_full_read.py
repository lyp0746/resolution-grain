#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通读审计：source-v2 全书的机器可查项。

不替代人读；它只把“能数出来的问题”一次数完，供 REVIEW-FULL 报告引用。

用法：
    "$PY" analysis/audit_full_read.py            # 写 analysis/REVIEW-FULL-2026-11-20.md
    "$PY" analysis/audit_full_read.py --stdout   # 打到屏幕
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "source-v2"
OUT = ROOT / "analysis" / "REVIEW-FULL-MACHINE.md"

BANNED = ["必然", "注定", "不可避免", "无法消除", "死路"]
V1_MARKS = ["第一版", "第二版", "V1", "本版", "旧写法", "上一版"]
OK_GRADES = ("A", "B", "C")


def hanzi(t: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", re.sub(r"<[^>]+>", "", t)))


def strip_tags(t: str) -> str:
    return re.sub(r"<[^>]+>", "", t)


def chapter_files():
    return sorted(SRC.glob("ch[0-9][0-9].html"))


def chno(path: Path) -> int:
    return int(re.search(r"ch(\d+)", path.name).group(1))


def sections(t: str):
    return [(a, b, re.sub(r"<[^>]+>", "", h))
            for a, b, h in re.findall(r'<h3 id="sec(\d+)-(\d+)">(.*?)</h3>', t, re.S)]


def subsections(t: str):
    return re.findall(r'<h4 id="sec(\d+)-(\d+)-(\d+)">(.*?)</h4>', t, re.S)


def build_index():
    idx = {"sec": set(), "tab": set(), "fig": set(), "eq": set()}
    for f in sorted(SRC.glob("*.html")):
        t = f.read_text(encoding="utf-8")
        for a, b, _ in sections(t):
            idx["sec"].add(f"{a}.{b}")
        for a, b, c, _ in subsections(t):
            idx["sec"].add(f"{a}.{b}")
            idx["sec"].add(f"{a}.{b}.{c}")
        for m in re.findall(r"表(\d+\.\d+)", t):
            idx["tab"].add(m)
        for m in re.findall(r"图(\d+\.\d+)", t):
            idx["fig"].add(m)
        for m in re.findall(r'class="num">\(([0-9A-F]+\.\d+)\)<', t):
            idx["eq"].add(m)
    return idx


def audit():
    idx = build_index()
    rows = []
    issues = defaultdict(list)   # severity -> [(where, msg)]

    for f in chapter_files():
        t = f.read_text(encoding="utf-8")
        n = chno(f)
        body = re.sub(r"<[^>]+>", "", t)
        row = {
            "ch": n,
            "file": f.name,
            "hanzi": hanzi(t),
            "secs": len(sections(t)),
            "tables": len(re.findall(r"<table", t)),
            "figs": len(re.findall(r"<figure", t)),
            "paras": len(re.findall(r"<p[ >]", t)),
            "epi": len(re.findall(r'class="epi"', t)),
            "lead": "class=\"lead\"" in t,
            "take": "box-takeaway" in t,
            "sum": "本章小结" in t,
            "oneliner": "一句话带走" in t,
            "counter": bool(re.search(r"反例|失败|不成立|失效", t)),
            "datasrc": len(re.findall(r'class="datasrc"', t)),
            "define": len(re.findall(r'class="define"', t)),
            "dash": body.count("——"),
            "bold": len(re.findall(r"<b>", t)),
            "ask": body.count("？"),
        }
        rows.append(row)

        # 1) 章内节号必须属于本章
        for a, b, _ in sections(t):
            if int(a) != n:
                issues["P0"].append((f.name, f"节号 sec{a}-{b} 属于第 {a} 章，本章是第 {n} 章"))
        # 2) 表/图号前缀
        for m in re.findall(r"表(\d+)\.(\d+)", t):
            if m[0] != str(n) and int(m[0]) not in range(1, 34):
                issues["P1"].append((f.name, f"表号 {m[0]}.{m[1]} 不像本章"))
        # 3) 八段缺件
        missing = []
        if not row["lead"]:
            missing.append("场景开篇(lead)")
        if not row["take"]:
            missing.append("主提问/带走框")
        if not row["sum"]:
            missing.append("本章小结")
        if not row["oneliner"]:
            missing.append("一句话带走")
        if not row["counter"]:
            missing.append("反例/失败")
        if row["tables"] == 0 and row["figs"] == 0:
            missing.append("一表一图")
        if missing:
            issues["P1"].append((f.name, "缺：" + "、".join(missing)))
        # 4) 禁词 / 版本史
        for w in BANNED:
            for m in re.finditer(w, t):
                ln = t[: m.start()].count("\n") + 1
                issues["P0"].append((f.name, f"禁词「{w}」第 {ln} 行"))
        for w in V1_MARKS:
            for m in re.finditer(w, t):
                ln = t[: m.start()].count("\n") + 1
                issues["P1"].append((f.name, f"版本史「{w}」第 {ln} 行"))
        # 5) 交叉引用有效性
        for m in re.finditer(r"§(\d+)\.(\d+)(?:\.(\d+))?", t):
            key = f"{m.group(1)}.{m.group(2)}" + (f".{m.group(3)}" if m.group(3) else "")
            if key not in idx["sec"]:
                issues["P1"].append((f.name, f"指向不存在的 §{key}"))
        for m in re.finditer(r"式 ?\((\d+\.\d+)\)", t):
            if m.group(1) not in idx["eq"]:
                issues["P1"].append((f.name, f"指向不存在的式 ({m.group(1)})"))
        for m in re.finditer(r"第 ?(\d+) ?章", t):
            k = int(m.group(1))
            if k < 1 or k > 33:
                issues["P1"].append((f.name, f"指向不存在的第 {k} 章"))
        # 6) HTML 异常
        if re.search(r"<p[^>]*>\s*<p", t):
            issues["P0"].append((f.name, "嵌套 <p>"))
        if re.search(r"</b>\s*[^<>\n]{0,8}</b>", t):
            issues["P0"].append((f.name, "重复 </b>（可能是换代残句）"))
        for tag in ("b", "i", "sub", "sup"):
            o = len(re.findall(rf"<{tag}(?:\s[^>]*)?>", t))
            c = len(re.findall(rf"</{tag}>", t))
            if o != c:
                issues["P0"].append((f.name, f"<{tag}> 不平衡 {o}/{c}"))
    # 7) 引用：正文《》是否进文献/系列页/本章文献
    corpus = "".join((SRC / x).read_text(encoding="utf-8")
                     for x in ("back_references.html", "back_series.html"))
    corpus += "".join(re.findall(r"本章文献（引用与延伸）.*?</div>",
                                 "".join(f.read_text(encoding="utf-8") for f in chapter_files()), re.S))
    for f in chapter_files():
        t = f.read_text(encoding="utf-8")
        for title in set(re.findall(r"《([^》]{2,30})》", t)):
            if f"《{title}》" not in corpus:
                issues["P2"].append((f.name, f"《{title}》未在文献/系列页/本章文献登记"))
    return rows, issues, idx


def dup_paragraphs():
    seen = {}
    dups = []
    for f in chapter_files():
        t = f.read_text(encoding="utf-8")
        for p in re.findall(r"<p[^>]*>(.*?)</p>", t, re.S):
            txt = re.sub(r"\s+", "", strip_tags(p))
            if len(txt) < 80:
                continue
            key = txt[:60]
            if key in seen and seen[key][0] != f.name:
                dups.append((f.name, seen[key][0], txt[:70]))
            elif key not in seen:
                seen[key] = (f.name, txt)
    return dups


def symbol_usage():
    letters = Counter()
    first = {}
    files = sorted(SRC.glob("ch[0-9][0-9].html")) + sorted(SRC.glob("*.html"))
    for f in files:
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"<i>([A-Za-zΑ-ωα-βγδεζηθλμνξπρστφχψω])</i>", t):
            L = m.group(1)
            letters[L] += 1
            first.setdefault(L, f.name)
    return letters, first


def style_metrics():
    t = "".join(f.read_text(encoding="utf-8") for f in chapter_files())
    body = strip_tags(t)
    sents = [s for s in re.split(r"[。！？]", body) if s.strip()]
    paras = [p for p in re.findall(r"<p[^>]*>(.*?)</p>", t, re.S) if len(strip_tags(p)) > 20]
    import statistics
    return {
        "chars": len(re.findall(r"[\u4e00-\u9fff]", body)),
        "sents": len(sents),
        "sent_median": statistics.median(len(s) for s in sents),
        "sent_p90": sorted(len(s) for s in sents)[int(len(sents) * .9)],
        "para_median": statistics.median(len(strip_tags(p)) for p in paras),
        "dash": body.count("——"),
        "bang": body.count("！"),
        "bold": len(re.findall(r"<b>", t)),
        "paras": len(paras),
    }


def main():
    rows, issues, idx = audit()
    dups = dup_paragraphs()
    letters, first = symbol_usage()
    st = style_metrics()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    L = []
    L.append("# 通读审计（source-v2，2026-11-20）\n")
    L.append("> 机器可查项一次数完；人读结论另见各节评注。由 `analysis/audit_full_read.py` 生成。\n")
    L.append("## 一、每章读数\n")
    L.append("| 章 | 汉字 | 节 | 表 | 图 | 段 | 题记 | 数据源 | 定义框 | 破折号 | 加粗 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        L.append(f"| {r['ch']} | {r['hanzi']} | {r['secs']} | {r['tables']} | {r['figs']} | "
                 f"{r['paras']} | {r['epi']} | {r['datasrc']} | {r['define']} | {r['dash']} | {r['bold']} |")
    L.append(f"\n合计：汉字 {sum(r['hanzi'] for r in rows)}；"
             f"表 {sum(r['tables'] for r in rows)}；图 {sum(r['figs'] for r in rows)}；"
             f"节 {sum(r['secs'] for r in rows)}。\n")
    L.append("## 二、问题清单（按严重度）\n")
    for sev in ("P0", "P1", "P2"):
        items = issues.get(sev, [])
        L.append(f"### {sev}（{len(items)}）\n")
        if not items:
            L.append("无。\n")
            continue
        for where, msg in items:
            L.append(f"- `{where}`：{msg}")
        L.append("")
    L.append("## 三、重复段落\n")
    if not dups:
        L.append("未发现跨章重复的长段落（≥80 字，前 60 字相同）。\n")
    else:
        for a, b, txt in dups:
            L.append(f"- `{a}` 与 `{b}`：{txt}…")
        L.append("")
    L.append("## 四、符号使用频次（`<i>字母</i>`）\n")
    L.append("| 符号 | 次数 | 首见 |")
    L.append("|---|---|---|")
    for L_, c in letters.most_common():
        L.append(f"| {L_} | {c} | {first[L_]} |")
    L.append("")
    L.append("## 五、文风读数\n")
    L.append(f"- 正文汉字 {st['chars']}；句 {st['sents']}；句长中位 {st['sent_median']}，p90 {st['sent_p90']}")
    L.append(f"- 段 {st['paras']}；段长中位 {st['para_median']}")
    L.append(f"- 破折号 {st['dash']}（约 1/{max(1, st['chars']//max(1,st['dash']))} 字）；感叹号 {st['bang']}；加粗 {st['bold']}")
    L.append("")
    L.append("## 六、索引事实\n")
    for k, v in idx.items():
        L.append(f"- {k}：{len(v)}")
    L.append("")
    txt = "\n".join(L)
    if "--stdout" in sys.argv:
        print(txt)
    else:
        OUT.write_text(txt, encoding="utf-8")
        print("wrote", OUT)


if __name__ == "__main__":
    main()
