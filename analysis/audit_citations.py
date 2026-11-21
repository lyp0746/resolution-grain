#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全书两件审计（2026-11-17 起，作者要求：引用必须有文献，机制不许一句话带过）。

一、引用账（CITATION）：正文里出现的每一条引用，是否在本章「本章文献」里有条目。
   抓四类：
     ① 拉丁姓＋年份      Sims（2003） / Shannon 1948 / Kahneman & Tversky (1979)
     ② 单独的拉丁姓      Shepard / Kuran …（不含常见英文词）
     ③ 书名号           《叫魂》《区分的语言》
     ④ 中文译名＋动词     布迪厄说过 / 韦伯讲 / 孔飞力指出（用 analysis 文档里的名单核对）
   输出：analysis/CITATION-AUDIT.md

二、机制账（MECHANISM）：全书术语表里的每个机制名／符号，在每章首次出现时，
   同一段里是否给了 >=MECH_MIN 字的因果说明（谁对谁、经由什么、在什么单位上）。
   只报「首现段 < MIN 字」的行，按章排列。
   输出同一份报告的后半。

用法：
    "$PY" analysis/audit_citations.py            # 写报告
    "$PY" analysis/audit_citations.py --strict   # 引用缺口 >0 时退出码 1（机制表不影响退出码）
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
OUT = os.path.join(ROOT, "analysis", "CITATION-AUDIT.md")

CJK = re.compile(r"[\u4e00-\u9fff]")

# 正文里常见的英文字（不是引用）
STOP = {
    "The", "This", "That", "These", "Those", "And", "But", "For", "With", "From",
    "Journal", "Science", "Nature", "American", "Review", "University", "Press",
    "Harvard", "Cambridge", "Oxford", "Blackwell", "Doubleday", "Politics",
    "World", "Economic", "Psychological", "Sociological", "Annual", "Studies",
    "Theory", "Society", "Research", "Behavior", "Behaviour", "Social", "Public",
    "Political", "Economics", "Economy", "Quarterly", "Bulletin", "Letters",
    "Proceedings", "National", "Academy", "Sciences", "China", "Chinese", "English",
    "ISBN", "DOI", "PDF", "HTML", "SVG",
    # 数据集/产品名，不是引用（2026-11-18 加：Seshat 的各发布名）
    "Equinox", "CanonDat", "TSDat", "TSDat123", "PropCoded", "cliopatria",
    "Federal", "Register", "FederalRegister", "eCFR", "CFR", "API", "RULE",
    # 非引用：产品名与记号（2026-11-19 加；均为正文里的物件或公式，不是文献）
    "Google", "Linux", "Glass", "Glasshole", "Explorer", "UqUw", "UwUq",
    "Julius", "Sextus", "Pierre", "Adam", "Christoph",
    # 2026-11-21 加（搬号前先修引用审计的漏抓／误抓）：
    #   Round   —— "European Social Survey, Round 8" 是调查轮次，不是人名；
    #   TLGq    —— 二次型 qᵀLq 去掉上标标签后的串，不是人名。
    # 只加这两个精确串，不放宽任何别的判据；加完重跑，缺口必须是 0。
    "Round", "TLGq",
}

# 中文译名 → 拉丁姓（只收本书确实用到的）
ZH2LATIN = {
    "香农": "Shannon", "西姆斯": "Sims", "西蒙": "Simon", "卡尼曼": "Kahneman",
    "特沃斯基": "Tversky", "吉仁泽": "Gigerenzer", "谢泼德": "Shepard",
    "诺索夫斯基": "Nosofsky", "罗施": "Rosch", "米勒": "Miller",
    "特罗普": "Trope", "利伯曼": "Liberman", "布迪厄": "Bourdieu",
    "戈夫曼": "Goffman", "斯科特": "Scott", "韦伯": "Weber", "涂尔干": "Durkheim",
    "帕特南": "Putnam", "蒂利": "Tilly", "诺斯": "North", "卢曼": "Luhmann",
    "米尔格拉姆": "Milgram", "阿希": "Asch", "格兰诺维特": "Granovetter",
    "扎勒": "Zaller", "恩特曼": "Entman", "萨托利": "Sartori",
    "尼汉": "Nyhan", "赖夫勒": "Reifler", "彭尼库克": "Pennycook",
    "兰德": "Rand", "沃索吉": "Vosoughi", "拉泽": "Lazer",
    "孔飞力": "Kuhn, P.", "黄宗智": "Huang", "费孝通": "Fei", "朱苏力": "Zhu",
    "库兰": "Kuran", "斯彭斯": "Spence", "谢弗": "Scheffer",
    "格拉诺维特": "Granovetter", "斯塔": "Staw", "伯杰": "Burger",
    "麦晋": "Maćkowiak", "维德霍尔特": "Wiederholt", "魏": "Wei",
    "斯托克": "Stocker", "巴洛": "Barlow", "阿蒂克": "Atick",
    "雷德利希": "Redlich", "尼尔": "Knill", "波热": "Pouget",
    "安德森": "Anderson", "佩恩": "Payne", "贝特曼": "Bettman",
    "约翰逊": "Johnson", "考恩": "Cowan", "帕克斯顿": "Paxton",
    "纳克": "Knack", "基弗": "Keefer", "盖斯": "Guess", "科波克": "Coppock",
    "伍德": "Wood", "波特": "Porter", "德鲁克曼": "Druckman",
    "藤田": "Fujita", "古特曼": "Guttman", "卡利什": "Kalish",
    "奥尔波特": "Allport", "波斯特曼": "Postman", "特威切特": "Twitchett",
    "皮亚杰": "Piaget", "布卢姆": "Bloom", "维果茨基": "Vygotsky", "马顿": "Marton",
    "布劳": "Blau", "阎云翔": "Yan", "赵鼎新": "Zhao", "齐美尔": "Simmel",
    "道格拉斯": "Douglas", "列维-斯特劳斯": "Lévi-Strauss", "曼海姆": "Mannheim",
    "莫斯": "Mauss", "熊彼特": "Schumpeter", "凡勃伦": "Veblen", "哈贝马斯": "Habermas",
    "李泽厚": "Li", "余英时": "Yu", "金耀基": "King", "黄仁宇": "Huang",
    "周雪光": "Zhou", "吴思": "Wu", "阎步克": "Yan", "瞿同祖": "Qu",
    "顾炎武": "Gu", "王朴": "Wang",
    "内藤": "Naito", "彭兰": "Peng", "加芬克尔": "Garfinkel", "贝克": "Beck",
    "奥斯特罗姆": "Ostrom", "波兰尼": "Polanyi", "卡拉布雷西": "Calabresi",
    "梅拉梅德": "Melamed", "何友晖": "Ho", "哈耶克": "Hayek", "默顿": "Merton",
    "吉登斯": "Giddens", "福柯": "Foucault", "维特根斯坦": "Wittgenstein",
    "加芬克尔": "Garfinkel", "列维-斯特劳斯": "Lévi-Strauss", "波兰尼": "Polanyi",
}

# 机制／术语表：符号 + 中文名（来自 front_terms，脚本读表）
MECH_MIN = 90  # 首现段至少要有这么多汉字，才算“不是一句话带过”


def read(p):
    return io.open(p, encoding="utf-8").read()


def text_of(h):
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", "", h)


def refs_block(s):
    """取本章文献块（<div class="refs">…</div>）；没有则空。"""
    m = re.search(r'<div class="refs">(.*?)</div>', s, re.S)
    return m.group(1) if m else ""


def paras(s):
    out = []
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", s, re.S):
        seg = m.group(1)
        if 'class="refh"' in m.group(0):
            continue
        out.append(text_of(seg))
    return out


NON_CITATION = ["比亚韦斯托克",       # 地名，含“斯托克”；不是人名
                 "Potamopyrgus", "Microphallus",   # 属名（泥螺／吸虫）；2026-11-21 加，以后每章的属名都往这里加
                 "Gini", "OpenAlex", "EuropePMC"]   # 2026-11-21：指标名与数据库名，不是作者


def strip_non_citation(t):
    for w in NON_CITATION:
        t = t.replace(w, "")
    return t


def latin_names(t):
    out = set()
    for m in re.finditer(r"[A-Z][A-Za-z'’\-]{2,}", t):
        w = m.group(0)
        if w in STOP or w in NON_CITATION:      # NON_CITATION：地名与属名，不是作者
            continue
        out.add(w)
    return out


def body_citations(t):
    """① 姓＋年份；② 书名号。"""
    y = set()
    for m in re.finditer(
        r"([A-Z][A-Za-z'’\-]{2,}(?:\s*(?:&|与|、|和|,)\s*[A-Z][A-Za-z'’\-]{2,})*)"
        r"\s*[（(]\s*(\d{4})", t):
        if m.group(1).split()[0] in STOP:      # 产品名／发行年份，不是引用
            continue
        y.add((m.group(1), m.group(2)))
    for m in re.finditer(r"([A-Z][A-Za-z'’\-]{2,})\s+(\d{4})", t):
        if m.group(1) in STOP:
            continue
        y.add((m.group(1), m.group(2)))
    books = set(re.findall(r"《([^》]{1,30})》", t))
    return y, books


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--src", default="source", help="相对于仓根的源目录（V2 用 source-v2）")
    ap.add_argument("--out", default=os.path.join("analysis", "CITATION-AUDIT.md"))
    args = ap.parse_args()
    src = os.path.join(ROOT, args.src)
    out = os.path.join(ROOT, args.out)
    globals()["SRC"] = src
    globals()["OUT"] = out

    files = sorted(glob.glob(os.path.join(src, "ch*.html")))
    core_p = os.path.join(SRC, "back_references.html")
    core = text_of(read(core_p)) if os.path.exists(core_p) else ""
    all_refs = core + "\n" + "\n".join(refs_block(read(p)) for p in files)

    rows_cite, rows_mech = [], []
    first_seen = {}
    for p in files:
        name = os.path.basename(p)
        s = read(p)
        refs = refs_block(s)
        refs_t = text_of(refs)
        body = re.sub(r'<div class="refs">.*?</div>', "", s, flags=re.S)
        t = text_of(body)
        # 公式不是引用：去掉 <math> 之后再抽人名（否则 P^field_t 会变成 "Ptfield" 这种假人名）。
        # 2026-11-21 加；机制检查仍用未去公式的 t。
        t_cite = text_of(re.sub(r"<math.*?</math>", "", body, flags=re.S))

        # ---- 一、引用
        pairs, books = body_citations(t_cite)
        missing = []
        for who, yr in sorted(pairs):
            first = who.split()[0]
            if first not in refs_t and first not in core:
                missing.append(f"{who}（{yr}）")
        for nm in sorted(latin_names(t_cite)):
            if nm in refs_t:
                continue
            # 只在“像人名”时才报：全大写缩写、常见词已在 STOP 里
            if nm.isupper() or len(nm) < 4:
                continue
            # 该书其它章的文献里也没有 → 一定是没出处
            if nm not in core and nm not in all_refs:
                missing.append(f"{nm}（正文提及，全书文献无此人）")
        for bk in sorted(books):
            if bk in refs_t or bk in core or bk in all_refs:
                continue
            if len(bk) < 3:
                continue
            missing.append(f"《{bk}》")
        _t_no_place = strip_non_citation(t)
        for zh, lat in ZH2LATIN.items():
            if zh in _t_no_place and lat not in refs_t and zh not in refs_t and lat not in core:
                missing.append(f"{zh}（→{lat}，本章文献无）")
        rows_cite.append((name, sorted(set(missing))))

        # ---- 二、机制：短段里的机制断言（可能的“一句话带过”）
        for q in paras(body):
            q = q.strip()
            n = len(CJK.findall(q))
            if n == 0:
                continue
            hit = [t for t in TERMS if t in q]
            # 首现段：不论长短都记（这才是“首现”）
            for t_ in hit:
                if t_ not in first_seen:
                    first_seen[t_] = (name, n, q[:90])
            if not hit or n > MECH_MIN:
                continue
            if q.endswith("：") or q.endswith(":"):   # 列表引导句
                continue
            rows_mech.append((name, "、".join(hit), n, q[:90]))

    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write("# 引用与机制审计（脚本产出，勿手改）\n\n")
        f.write("> 生成：`analysis/audit_citations.py`。规则见文件头。\n\n")
        f.write("## 一、引用账：正文提及、本章文献无条目\n\n")
        f.write("| 章 | 缺口 |\n|---|---|\n")
        tot = 0
        for name, miss in rows_cite:
            tot += len(miss)
            f.write("| %s | %s |\n" % (name, "；".join(miss) if miss else "—"))
        f.write("\n合计缺口：**%d**\n\n" % tot)
        f.write("## 二、机制账：短段（<%d 字）里的机制断言 —— **这是清单，不是失败项**\n\n" % MECH_MIN)
        f.write("判据是「机制名**首次出现**处有没有写清：谁在选 → 经由什么 → 在什么单位上 → 什么条件下会翻转」。\n"
                "同一机制在别章再出现时只给指针是允许的（例如「第 20 章那条迟滞环」）；下表里多数属于这种回指，\n"
                "需要人工判一次。2026-11-17 已全书判过一轮：真属“一句话带过”的 4 处已补（ch05 迟滞、ch06 双稳、\n"
                "ch20 沉没成本＋分离态、ch24 自设成本），其余为回指。\n\n")
        f.write("| 章 | 机制 | 段长 | 段文 |\n|---|---|---|---|\n")
        for name, term, n, head in rows_mech:
            f.write("| %s | %s | %d | %s… |\n" % (name, term, n, head.replace("|", "｜")))
        f.write("\n合计：**%d** 处\n" % len(rows_mech))
        f.write("\n## 二b、只看首现段（真正的“一句话带过”候选）\n\n")
        f.write("上表把**所有**短段都列出来，所以多数是回指。下面这张表只取每个机制名的**首次出现段**；\n"
                "若首现段仍 < %d 字，才是需要动手的候选。\n\n" % MECH_MIN)
        f.write("| 机制 | 章 | 首现段字数 | 段文 |\n|---|---|---|---|\n")
        short = [(k, v) for k, v in sorted(first_seen.items()) if v[1] < MECH_MIN]
        for k, (name, n, head) in short:
            f.write("| %s | %s | %d | %s… |\n" % (k, name, n, head.replace("|", "｜")))
        f.write("\n首现段候选：**%d** 处（机制名共 %d 个，正文里出现 %d 个）\n" % (len(short), len(TERMS), len(first_seen)))
        print("首现段候选 %d（机制名 %d／正文出现 %d）" % (len(short), len(TERMS), len(first_seen)))

    print("wrote", OUT)
    print("引用缺口 %d / 机制疑点 %d" % (tot, len(rows_mech)))
    # 只有“引用缺口”能让它失败；机制表是给人读的清单（回指是允许的）
    if args.strict and tot:
        return 1
    return 0


# 机制名单（只收“有名字的机制”，不收单个符号）
MECH_NAMES = [
    "迟滞", "双稳", "多稳", "偏好伪造", "代价信号", "沉没成本", "自设成本",
    "分离态", "伪分辨率", "外部性", "正反馈", "同质性", "极化", "边际递减",
    "边际", "机会成本", "规模经济", "路径依赖", "逆向选择", "道德风险",
    "委托代理", "纳什均衡", "协调问题", "公地悲剧", "选择性激励",
    "符号暴力", "内卷", "溢出", "锁定", "门槛", "阈值", "复制子",
    "贝叶斯", "共线", "选择偏差", "幸存者偏差", "代理变量", "分母",
    "编码", "解码", "信噪", "先验", "后验",
]


def load_terms():
    return MECH_NAMES


TERMS = load_terms()

if __name__ == "__main__":
    sys.exit(main())
