#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""知识图谱与理论地图（2026-11-18 重做）。

上一版的两个毛病（作者 2026-11-18 指出）：
  ① 知识图谱是一团毛线（Kamada–Kawai 力导向），节点只标编号，看不出"7 部 4 章"的结构，
     而图注却在讲"横着看是顺序、竖着看是枢纽"——图与注对不上；
  ② 理论地图是十根细辐条，字叠在一起，读不出"哪九条退得回去、哪一条退不回去"。
本版改成就支持图注的两句话：

  图 4.3  双联图
      上：**书序弧线图**——28 章按阅读顺序排一行，7 部用底色分带；弧＝一次交叉引用，
          同部内弧浅、跨部弧深；点大小＝被引次数；越靠前的章名直接标出来。
          图下方一小排橙点＝这一章把读者指向附录 A 的哪几节。
      下：**部×部矩阵**——把 277 条边按 7 部聚合成 7×7 计数，对角＝部内互引。
  图 7.2  撤退图（扇形）
      左：总账；右：十条极限各一格（极限条件／退回谁／现实里长什么样）；
          九格蓝、一格橙——橙的那格（ν&lt;0）是唯一退不回去的。

产出
  assets/charts/c04_kgraph.png / .svg
  assets/charts/c04_tmap.png  / .svg
  assets/knowledge-map.html               交互版（分组网格＋悬停，非力导向）
  data/derived/kgraph.json                节点与边的原始数据（含部分分组）

用法：  "$PY" analysis/make_theory_map.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "charts"
SVG = ROOT / "assets" / "svg"
DER = ROOT / "data" / "derived"
C_MAIN, C_ALT, C_GREY = "#1f3b57", "#b5651d", "#8c8c8c"
C_PALE, C_WASH = "#8fa8bd", "#f2eee4"

plt.rcParams.update({
    "font.sans-serif": ["Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False, "figure.dpi": 300, "font.size": 9,
})

PART_NAMES = ["一 形状", "二 第一性", "三 个人", "四 群体", "五 社会", "六 历史", "七 边界"]


# ------------------------------------------------------------------ 解析
def load_chapters() -> dict[int, dict]:
    out = {}
    for p in sorted(ROOT.glob("source/ch*.html")):
        n = int(re.search(r"ch(\d+)", p.name).group(1))
        h = p.read_text(encoding="utf-8")
        title = re.sub(r"<[^>]+>", "", re.search(r"<h2[^>]*>(.*?)</h2>", h, flags=re.S).group(1)).strip()
        short = title.split("　")[-1]
        t = re.sub(r"<[^>]+>", "", h)
        refs, aps = set(), set()
        for m in re.finditer(r"第\s*(\d{1,2})\s*章", t):
            k = int(m.group(1))
            if 1 <= k <= 28 and k != n:
                refs.add(k)
        for m in re.finditer(r"(?<!\d)(\d{1,2})\.(\d{1,2})\s*节", t):
            k = int(m.group(1))
            if 1 <= k <= 28 and k != n:
                refs.add(k)
        for m in re.finditer(r"附录\s*A\.(\d{1,2})", t):
            aps.add(int(m.group(1)))
        out[n] = {"title": short, "refs": sorted(refs), "aps": sorted(aps)}
    return out


def parts_map() -> dict[int, int]:
    p = json.loads((ROOT / "source" / "parts.json").read_text(encoding="utf-8"))
    mapping = {}
    for i, part in enumerate(p, 1):
        for ch in part.get("chapters", []):
            f = ch.get("file") or ""
            m = re.search(r"ch(\d+)", f)
            if m:
                mapping[int(m.group(1))] = i
    return mapping


# ------------------------------------------------------------------ 图 4.3
def fig_kgraph(ch: dict[int, dict], pm: dict[int, int]) -> dict:
    n_ch = 28
    deg = {n: 0 for n in range(1, n_ch + 1)}
    edges = []
    for n, d in ch.items():
        for r in d["refs"]:
            if 1 <= r <= n_ch:
                edges.append((n, r))
                deg[n] += 1
                deg[r] += 1
    mat = np.zeros((7, 7))
    for a, b in edges:
        mat[pm[a] - 1, pm[b] - 1] += 1

    fig = plt.figure(figsize=(7.2, 5.3))
    # 上：弧线图（占 0.40—0.99 的高度）
    ax = fig.add_axes([0.035, 0.36, 0.93, 0.62])
    # 左下：读法文字
    ax3 = fig.add_axes([0.035, 0.02, 0.52, 0.30])
    # 右下：矩阵
    ax2 = fig.add_axes([0.62, 0.03, 0.34, 0.29])

    # ---- 部带与部名（顶部一行，与弧分开）
    for pi in range(7):
        x0 = pi * 4 + 0.5
        if pi % 2 == 0:
            ax.axvspan(x0, x0 + 4, color=C_WASH, zorder=0, lw=0)
        ax.text(x0 + 2, 4.30, PART_NAMES[pi], ha="center", va="center",
                fontsize=6.6, color="#8a8272")
    ax.axhline(0, color="#c9c2b2", lw=0.9, zorder=1)

    # ---- 弧
    for a, b in edges:
        span = abs(b - a)
        h = 0.20 * span ** 0.85
        same = pm[a] == pm[b]
        col, lw, al = (C_PALE, 0.5, 0.5) if same else (C_MAIN, 0.7, 0.34)
        xs = np.linspace(a, b, 60)
        ys = h * np.sin(np.pi * (xs - a) / max(span, 1e-9))
        ax.plot(xs, ys, color=col, lw=lw, alpha=al, zorder=2, solid_capstyle="round")

    # ---- 点与编号
    for n in range(1, n_ch + 1):
        s_ = 14 + 5.4 * deg[n]
        ax.scatter([n], [0], s=s_, color=C_MAIN, zorder=4, edgecolor="white", linewidth=0.7)
        ax.text(n, -0.16, str(n), ha="center", va="top", fontsize=6.0, color=C_MAIN)

    # ---- 只标图注点名的两个枢纽（第 4 章、第 20 章）
    for n, dx in ((4, -1.6), (20, 1.6)):
        ax.annotate("第 %d 章　%s" % (n, ch[n]["title"][:9]), xy=(n, 0.06), xytext=(n + dx, 3.98),
                    ha="right" if dx < 0 else "left", va="center", fontsize=6.6, color=C_ALT,
                    arrowprops=dict(arrowstyle="-", lw=0.6, color=C_ALT, alpha=0.7,
                                    shrinkA=0, shrinkB=4))

    # 附录 A：这一章把读者指向哪几节（轴下小橙点）
    tot_ap = 0
    for n, d in ch.items():
        for j, a in enumerate(d["aps"]):
            tot_ap += 1
            ax.scatter([n + (j % 3 - 1) * 0.14], [-0.66 - 0.17 * (j // 3)],
                       s=7, color=C_ALT, alpha=0.8, zorder=4, marker="o", lw=0)
    ax.text(0.35, -0.66, "→ 附录 A·%d 处" % tot_ap, fontsize=6.0, color=C_ALT, ha="left", va="center")

    ax.set_xlim(0.2, 28.8)
    ax.set_ylim(-1.45, 4.55)
    ax.set_axis_off()

    # ---- 矩阵
    vmax = mat.max()
    ax2.imshow(mat, cmap="Blues", vmin=0, vmax=vmax)
    for i in range(7):
        for j in range(7):
            v = int(mat[i, j])
            if v:
                ax2.text(j, i, str(v), ha="center", va="center", fontsize=6.2,
                         color="white" if v > vmax * 0.55 else C_MAIN)
    ax2.set_xticks(range(7)); ax2.set_yticks(range(7))
    ax2.set_xticklabels([str(i + 1) for i in range(7)], fontsize=6.0)
    ax2.set_yticklabels([PART_NAMES[i][0] for i in range(7)], fontsize=6.0)
    ax2.set_xlabel("被引的部", fontsize=6.6, labelpad=1)
    ax2.set_ylabel("引用的部", fontsize=6.6, labelpad=1)
    for sp in ax2.spines.values():
        sp.set_visible(False)
    ax2.set_title("%d 条边，按部聚合" % len(edges), fontsize=7.0, pad=3, color=C_MAIN)

    # ---- 读法
    ax3.set_axis_off()
    hubs = sorted(range(1, n_ch + 1), key=lambda n: -deg[n])[:4]
    txt = ("怎么读\n"
           "· 一条弧是一次交叉引用：越长跨得越多；高度只为分开重叠，不代表强度。\n"
           "· 点越大被引越多。最多的四章：%s。\n"
           "· 右下矩阵的对角线是部内互引；跨部集中在少数几格——七部不是并列的，"
           "而是几条线反复回到同一处。"
           % "、".join("第%d章（%d）" % (n, deg[n]) for n in hubs))
    ax3.text(0, 1.0, txt, va="top", ha="left", fontsize=6.4, color="#333", linespacing=1.8)

    fig.savefig(OUT / "c04_kgraph.png", bbox_inches="tight")
    try:
        fig.savefig(SVG / "c04_kgraph.svg", bbox_inches="tight")
    except Exception:
        pass
    plt.close(fig)

    DER.mkdir(exist_ok=True)
    nodes = []
    for n in range(1, n_ch + 1):
        nodes.append({"id": "ch%d" % n, "degree": deg[n], "part": pm[n], "label": ch[n]["title"]})
    (DER / "kgraph.json").write_text(json.dumps({
        "nodes": nodes,
        "edges": [{"source": "ch%d" % a, "target": "ch%d" % b} for a, b in edges],
        "ap_edges": [{"source": "ch%d" % n, "target": "apA%d" % a}
                     for n, d in ch.items() for a in d["aps"]],
        "matrix": mat.astype(int).tolist(),
    }, ensure_ascii=False), encoding="utf-8")
    print("  c04_kgraph.png  节点 %d  边 %d" % (len(nodes), len(edges)))
    return {"nodes": len(nodes), "edges": len(edges), "degree": deg}


# ------------------------------------------------------------------ 图 7.2
LIMITS = [
    # (哪一项的极限, 极限, 退化到的既有理论, 接洽点（哪个量退化成对方的哪个量）, 现实里长什么样, in/out)
    ("一致性 γ", "γ → 0", "Sims 的理性疏忽",
     "P3 的第二项消失：势函数退化为单人泛函，v*=(T+λ)/2w 原样回来", "一个人的最优码", "in"),
    ("一致性 γ", "γ → ∞", "制度锁定（诺斯那一支）",
     "全体同码、k*→1：“锁死”是 γ 的极限，不是一种文化", "身份／职业路径的锁死", "in"),
    ("网络 A", "网络＝完全图", "Granovetter 的阈值模型",
     "A_ij→1：平均场 γz>δ 成立，“阈值分布”是它的投影", "规范／共同语／正统", "in"),
    ("网络 A", "网络有 k 个分量", "偏好伪造与双稳（Kuran）",
     "分量之间 γ 不传导：各自成篇＝图不连通", "沉默的螺旋／突然崩盘", "in"),
    ("换码 C", "C → 0", "新古典的弹性世界",
     "带宽 2C→0：去程回程同一阈值，没有迟滞", "一次重新优化", "in"),
    ("换码 C", "C → ∞", "路径依赖（历史制度主义）",
     "带宽→∞：换码永不发生，码冻结", "制度惯性／旧账重做", "in"),
    ("外置 ν", "ν = 0", "庇古式外部性",
     "w_i = w_i(自己)：P6 的第二项消失，只剩“你受损但我不在乎”", "罚款／赔偿的常规读法", "in"),
    ("外置 ν", "ν < 0", "无对应——这是第二条原理本身",
     "w_i = w_i(自己) + ν·w_i(别人)：目标失去势结构，解跑到边界", "代价外置／粗码＋全责", "out"),
    ("预算 R, Δ", "R 固定、Δ → ∞", "快而省的启发式（Gigerenzer）",
     "δ = Δ/2^R → ∞：整段压粗，“匹配”取代“越细越好”", "口号／刻板印象／MBTI", "in"),
    ("预算 R, Δ", "R → ∞", "标准统计决策",
     "δ → 0：精度上限不再是理论问题，是预算问题", "法律条文／诊断标准", "in"),
]
SURF = ["一致性 γ", "网络 A", "换码 C", "外置 ν", "预算 R, Δ"]
SURF_COLOR = {"一致性 γ": "#6b7f3a", "网络 A": "#2E86AB", "换码 C": "#8c6d3f",
              "外置 ν": "#b5651d", "预算 R, Δ": "#1f3b57"}


def _wrap(s, width=30):
    """按中文宽度折行（ASCII 记 0.55 个汉字宽）。"""
    out, cur, w = [], "", 0.0
    for ch in s:
        cw = 0.55 if ord(ch) < 128 else 1.0
        if w + cw > width:
            out.append(cur); cur, w = "", 0.0
        cur += ch; w += cw
    if cur:
        out.append(cur)
    return out


def fig_tmap(fname="c04_tmap") -> None:
    """十二格撤退图：每格四行——极限 / 退化到哪支理论 / 接洽点（折行）。按四个接触面着色。"""
    fig, ax = plt.subplots(figsize=(6.5, 7.4))
    ax.set_axis_off()
    ax.set_xlim(0, 10.2)
    ax.set_ylim(-0.95, 10.9)

    # 左：本书的模型
    ax.add_patch(FancyBboxPatch((0.08, 4.30), 2.24, 1.90, boxstyle="round,pad=0.07,rounding_size=0.14",
                                facecolor="#eef2f6", edgecolor=C_MAIN, linewidth=1.1))
    ax.text(1.20, 5.92, "本书的模型", ha="center", fontsize=10.4, color=C_MAIN, weight="bold")
    ax.text(1.20, 5.48, "w·D + (T+λ)·R", ha="center", fontsize=7.8, color=C_MAIN)
    ax.text(1.20, 5.16, "+ γ·(平均失真) − H/β", ha="center", fontsize=7.8, color=C_MAIN)
    ax.text(1.20, 4.80, "+ 切点成本 b、换码成本 C", ha="center", fontsize=7.0, color="#555")
    ax.text(1.20, 4.10, "十条极限，各退一支理论", ha="center", fontsize=6.4, color=C_GREY, va="top")

    cols = [2.52, 6.40]
    bw, bh = 3.76, 1.62
    rows = [10.05 - k * 1.62 for k in range(6)]
    for i, (surf, lim, theory, contact, real, kind) in enumerate(LIMITS):
        cx, cy = cols[i % 2], rows[i // 2]
        out = kind == "out"
        ec = SURF_COLOR[surf]
        ax.add_patch(FancyBboxPatch((cx, cy - bh), bw, bh,
                                    boxstyle="round,pad=0.04,rounding_size=0.09",
                                    facecolor="#fdf3e8" if out else "#fbfcfd",
                                    edgecolor=ec, linewidth=2.0 if out else 0.9))
        ax.add_patch(plt.Rectangle((cx, cy - bh), 0.05, bh, color=ec, lw=0))
        ax.text(cx + 0.14, cy - 0.26, lim, fontsize=8.6, color=ec, weight="bold", va="center")
        ax.text(cx + 0.14, cy - 0.66, "→ " + theory, fontsize=7.6, color="#1c1c1c", va="center")
        lines = _wrap("接洽：" + contact, 21)
        for k, ln in enumerate(lines[:3]):
            ax.text(cx + 0.14, cy - 1.00 - k * 0.28, ln, fontsize=6.3, color="#5a5a5a", va="center")

    # 图例
    lx = 2.52
    for surf in SURF:
        ax.add_patch(plt.Rectangle((lx, -0.30), 0.10, 0.15, color=SURF_COLOR[surf], lw=0))
        ax.text(lx + 0.17, -0.225, surf, fontsize=7.2, color="#333", va="center")
        lx += 1.42
    ax.text(2.52, -0.66, "粗框＝唯一退不回去的一条（ν<0）：ν 为负时目标失去势结构，不是任何既有理论的极限。", fontsize=7.0, color=C_ALT, va="center")
    ax.text(0.08, 10.05, "理论地图：十条极限各退回一支既有理论，并给出接洽点",
            fontsize=10.6, color=C_MAIN, weight="bold")
    fig.savefig(OUT / ("%s.png" % fname), bbox_inches="tight")
    try:
        fig.savefig(SVG / ("%s.svg" % fname), bbox_inches="tight")
    except Exception:
        pass
    plt.close(fig)
    print("  %s.png" % fname)


# ------------------------------------------------------------------ 交互版
HTML = """<!doctype html>
<html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>《分辨的预算》· 知识图谱（3D）与理论地图</title>
<style>
 :root{--ink:#1f3b57;--alt:#b5651d;--grey:#8c8c8c;--line:#e2dccd;--wash:#faf8f3}
 html,body{margin:0;background:#fbfaf7;color:#1c1c1c;
   font:14px/1.65 "Noto Sans SC","Microsoft YaHei",-apple-system,sans-serif}
 header{padding:20px 24px 4px}
 h1{font-size:18px;margin:0 0 4px;font-weight:600;color:var(--ink)}
 .sub{color:#6b6255;font-size:12.5px;max-width:960px}
 .bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:10px 24px 6px}
 .bar button{font:12.5px/1 inherit;padding:6px 11px;border:1px solid var(--line);background:#fff;
   color:#3a3a3a;border-radius:999px;cursor:pointer}
 .bar button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
 .bar .hint{color:#8c8c8c;font-size:12px;margin-left:6px}
 #stage{padding:0 18px 8px;position:relative}
 canvas{width:100%;height:600px;display:block;background:#fff;border:1px solid var(--line);
   border-radius:12px;cursor:grab;touch-action:none}
 .tip{position:fixed;pointer-events:none;background:#fff;border:1px solid var(--line);
   border-radius:8px;padding:8px 11px;font-size:12.5px;box-shadow:0 6px 20px rgba(30,40,50,.14);
   opacity:0;transition:opacity .1s;max-width:280px;z-index:9}
 .tip b{color:var(--ink)}
 .row{display:flex;gap:22px;padding:6px 24px 26px;flex-wrap:wrap;align-items:flex-start}
 .row>div{flex:1 1 320px}
 table{border-collapse:collapse;font-size:12px;width:100%;max-width:520px}
 td,th{padding:4px 6px;text-align:center;border:1px solid #e6e1d6}
 th{background:#f2eee4;color:var(--ink);font-weight:600}
 .diag{outline:1.5px solid #b5651d;outline-offset:-1.5px}
 .lg{color:#6b6255;font-size:12.5px;line-height:1.85}
 .lg b{color:var(--ink)}
 section#tm{padding:8px 24px 34px;border-top:1px solid var(--line);margin-top:8px}
 h2{font-size:16px;color:var(--ink);margin:18px 0 4px;font-weight:600}
 #tm .sub{margin:0 0 10px}
 svg.tm{width:100%;height:auto;display:block;background:#fff;border:1px solid var(--line);border-radius:12px}
 #tmtab td,#tmtab th{text-align:left;font-size:12px;padding:5px 8px}
 #tmtab th{white-space:nowrap}
</style>
<header>
 <h1>分辨的预算 · 知识图谱（3D）</h1>
 <div class="sub">28 章按书序盘成一条螺旋：<b>往下走＝往后读</b>，一圈约 15 章；一条线＝正文里的一次交叉引用。
  可拖动旋转、滚轮缩放、悬停高亮；按部过滤，或只看跨部引用——线太密时先过滤。</div>
</header>
<div class="bar">
 <button data-f="all" class="on">全部 250 条</button>
 <button data-f="cross">只看跨部</button>
 <button data-f="within">只看部内</button>
 <span style="width:14px"></span>
 <button id="spin" class="on">自动旋转</button>
 <button id="reset">复位</button>
 <span class="hint">拖动＝旋转 ／ 滚轮＝缩放 ／ 双击＝复位</span>
</div>
<div id="stage"><canvas id="c3"></canvas></div>
<div class="tip" id="tip"></div>

<div class="row">
 <div>
   <div style="font-size:13px;color:var(--ink);font-weight:600;margin:6px 0">部×部：边数（投影表）</div>
   <table id="mat"></table>
 </div>
 <div class="lg">
   <b>怎么读</b><br>
   · 螺旋的纵轴是书序：越靠下越靠后；同一圈的章在侧面上彼此引用最多——那是“部内互引”。<br>
   · 长斜线是跨部引用：它们集中在几章身上（第 4、5、6、10、20 章），这就是“枢纽”。<br>
   · 部×部矩阵的对角线是部内、其余是跨部；跨部只在少数几格，说明七部不是并列的。<br>
   · <b>点的大小＝度</b>（被引＋引用），不是重要性；颜色只有一种，避免七个颜色互抢。
 </div>
</div>

<section id="tm">
 <h2>理论地图（3D）· 十条极限，各退回一支既有理论</h2>
 <p class="sub">中心＝本书的模型；五个量各一条刻度（一致性 γ／网络 A／换码 C／外置 ν／预算 R,Δ），
  每条刻度上挂两枚极限，每枚末端是一支既有理论。<b>悬停看“接洽点”</b>——哪个量退化成对方的哪个量，
  像 c→∞ 退回伽利略变换那样，是等式不是比喻。橙色＝唯一退不回去的一条（ν&lt;0）。</p>
 <div class="bar" style="padding:6px 0 10px">
  <button data-s="all" class="on">全部 10 条</button>
  <button data-s="一致性 γ">一致性 γ</button><button data-s="网络 A">网络 A</button>
  <button data-s="换码 C">换码 C</button><button data-s="外置 ν">外置 ν</button>
  <button data-s="预算 R, Δ">预算 R, Δ</button>
  <span style="width:10px"></span>
  <button id="tspin" class="on">自动旋转</button>
  <span class="hint">拖动＝旋转 ／ 滚轮＝缩放</span>
 </div>
 <svg class="tm" id="tmsvg" viewBox="0 0 980 620" preserveAspectRatio="xMidYMid meet"></svg>
 <div class="lg" style="margin-top:10px">图上只标极限条件（如 γ→0）；<b>悬停看“退化到哪支理论＋接洽点”</b>，下表把十条一次列全。</div>
 <table id="tmtab" style="margin-top:6px;max-width:980px"></table>
</section>

<script>
const D = __DATA__;
const LIMITS = __LIMITS__;
const PART = ["一 形状","二 第一性","三 个人","四 群体","五 社会","六 历史","七 边界"];
const chs = D.nodes.filter(n => n.id.startsWith('ch'));
const idx = Object.fromEntries(chs.map((n, i) => [n.id, i]));
const part = Object.fromEntries(chs.map(n => [n.id, n.part]));
const deg = Object.fromEntries(chs.map(n => [n.id, n.degree]));
const label = Object.fromEntries(chs.map(n => [n.id, n.label]));
const maxDeg = Math.max(...Object.values(deg));

/* ---------- 三维位置：一条下行螺旋 ---------- */
const R = 152, TURN = 1.85, YSTEP = 26, H = 620;
const P = chs.map((n, i) => {
  const a = (i / chs.length) * Math.PI * 2 * TURN - Math.PI / 2;
  return { id: n.id, o: i,
           x: Math.cos(a) * R, y: (i - 13.5) * YSTEP, z: Math.sin(a) * R };
});
const EDGES = D.edges.map(e => ({ a: idx[e.source], b: idx[e.target] }));

const cv = document.getElementById('c3'), ctx = cv.getContext('2d'), tip = document.getElementById('tip');
let yaw = 0.5, pitch = -0.30, zoom = 1, autorot = true, filter = 'all', hover = -1, drag = null;
function resize(){ const r = devicePixelRatio || 1; const w = cv.clientWidth, h = cv.clientHeight;
  cv.width = w * r; cv.height = h * r; ctx.setTransform(r, 0, 0, r, 0, 0); draw(); }
addEventListener('resize', resize);

function viewW(){ return cv.clientWidth; }
function project(p){
  const cy = Math.cos(yaw), sy = Math.sin(yaw);
  let x = p.x * cy - p.z * sy, z = p.x * sy + p.z * cy;
  const cp = Math.cos(pitch), sp = Math.sin(pitch);
  let y = p.y * cp - z * sp; z = p.y * sp + z * cp;
  const f = 1100, s = f / (f + z + 330) * zoom;
  return { x: cv.clientWidth / 2 + x * s, y: H / 2 + y * s, s, z };
}

function draw(){
  const W = viewW();
  ctx.clearRect(0, 0, W, H);
  const pr = P.map(project);
  const W2 = viewW();
  // 螺旋导引线（很淡）
  ctx.beginPath();
  pr.forEach((q, i) => i ? ctx.lineTo(q.x, q.y) : ctx.moveTo(q.x, q.y));
  ctx.strokeStyle = 'rgba(200,195,182,0.55)'; ctx.lineWidth = 1; ctx.stroke();

  // 边：按深度排序，远的先画
  const list = EDGES.filter(e => {
    if (filter === 'within') return part[chs[e.a].id] === part[chs[e.b].id];
    if (filter === 'cross') return part[chs[e.a].id] !== part[chs[e.b].id];
    return true;
  });
  list.sort((u, v) => (pr[u.a].z + pr[u.b].z) - (pr[v.a].z + pr[v.b].z));
  list.forEach(e => {
    const A = pr[e.a], B = pr[e.b];
    const same = part[chs[e.a].id] === part[chs[e.b].id];
    const hot = hover >= 0 && (e.a === hover || e.b === hover);
    const depth = (A.z + B.z) / 2;
    const alpha = hot ? 0.95 : (same ? 0.20 : 0.28) * (depth > 0 ? 0.55 : 1);
    ctx.beginPath(); ctx.moveTo(A.x, A.y); ctx.lineTo(B.x, B.y);
    ctx.strokeStyle = hot ? '#b5651d' : (same ? 'rgba(159,180,198,1)' : 'rgba(31,59,87,1)');
    ctx.globalAlpha = hot ? 1 : alpha;
    ctx.lineWidth = hot ? 2.2 : (same ? 0.7 : 0.95);
    ctx.stroke();
  });
  ctx.globalAlpha = 1;

  // 点
  pr.forEach((q, i) => {
    const n = chs[i], d = deg[n.id];
    const r = (3.2 + 5.4 * Math.sqrt(d / maxDeg)) * Math.min(1.5, Math.max(0.8, q.s * 1.9));
    const hot = i === hover;
    ctx.beginPath(); ctx.arc(q.x, q.y, hot ? r + 2 : r, 0, 7);
    ctx.fillStyle = hot ? '#b5651d' : '#1f3b57';
    ctx.globalAlpha = q.z > 0 ? 0.55 : 1;
    ctx.fill();
    ctx.globalAlpha = 1;
    if (hot || zoom > 1.25) {
      ctx.font = '600 11px "Noto Sans SC",sans-serif';
      ctx.fillStyle = hot ? '#8f4c12' : '#5c6672';
      ctx.textAlign = 'left';
      ctx.fillText(n.id.slice(2), q.x + r + 3, q.y - 3);
    }
  });

  // 部名：该部四点的平均高度，强制最小间距，避免挤在一起
  const lab = [];
  for (let p = 1; p <= 7; p++) {
    const ys = pr.filter((_, i) => chs[i].part === p).map(q => q.y);
    if (ys.length) lab.push({ p, y: ys.reduce((a, b) => a + b, 0) / ys.length });
  }
  lab.sort((a, b) => a.y - b.y);
  for (let i = 1; i < lab.length; i++) {
    if (lab[i].y - lab[i - 1].y < 26) lab[i].y = lab[i - 1].y + 26;
  }
  ctx.font = '11.5px "Noto Sans SC",sans-serif';
  ctx.textAlign = 'left';
  lab.forEach(o => {
    ctx.fillStyle = 'rgba(150,143,130,0.95)';
    ctx.fillText(PART[o.p - 1], 12, o.y + 4);
    ctx.strokeStyle = 'rgba(214,208,196,0.9)'; ctx.lineWidth = 0.8;
    ctx.beginPath(); ctx.moveTo(12, o.y + 9); ctx.lineTo(64, o.y + 9); ctx.stroke();
  });
}

/* ---------- 交互 ---------- */
function nearest(mx, my){
  let best = -1, bd = 1e9;
  P.map(project).forEach((q, i) => {
    const d = (q.x - mx) ** 2 + (q.y - my) ** 2;
    if (d < bd) { bd = d; best = i; }
  });
  return bd < 260 ? best : -1;
}
cv.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY }; cv.setPointerCapture(e.pointerId); cv.style.cursor = 'grabbing'; });
cv.addEventListener('pointerup', e => { drag = null; cv.style.cursor = 'grab'; });
cv.addEventListener('pointermove', e => {
  const r = cv.getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top;
  if (drag) { yaw += (e.clientX - drag.x) * 0.008; pitch += (e.clientY - drag.y) * 0.005;
    pitch = Math.max(-1.1, Math.min(0.7, pitch)); drag = { x: e.clientX, y: e.clientY }; draw(); return; }
  const h = nearest(mx, my);
  if (h !== hover) { hover = h; draw(); }
  if (h >= 0) {
    const n = chs[h];
    tip.innerHTML = `<b>第 ${+n.id.slice(2)} 章</b>　${n.label}<br>被引＋引用：${n.degree} 次`;
    tip.style.left = (e.clientX + 14) + 'px'; tip.style.top = (e.clientY + 12) + 'px'; tip.style.opacity = 1;
  } else tip.style.opacity = 0;
});
cv.addEventListener('wheel', e => { e.preventDefault(); zoom *= e.deltaY < 0 ? 1.08 : 0.93;
  zoom = Math.max(0.55, Math.min(3.2, zoom)); draw(); }, { passive: false });
cv.addEventListener('dblclick', () => reset());
document.querySelectorAll('.bar button[data-f]').forEach(b => b.addEventListener('click', () => {
  filter = b.dataset.f;
  document.querySelectorAll('.bar button[data-f]').forEach(x => x.classList.toggle('on', x === b));
  draw();
}));
document.getElementById('spin').addEventListener('click', e => {
  autorot = !autorot; e.target.classList.toggle('on', autorot);
});
document.getElementById('reset').addEventListener('click', () => reset());
function reset(){ yaw = 0.5; pitch = -0.30; zoom = 1; draw(); }
(function loop(){ if (autorot) { yaw += 0.0016; draw(); } requestAnimationFrame(loop); })();

/* ---------- 部×部矩阵 ---------- */
const m = D.matrix, tb = document.getElementById('mat'), vmax = Math.max(...m.flat());
let html = '<tr><th>引\\被引</th>' + PART.map((p, i) => `<th>${i + 1}</th>`).join('') + '</tr>';
m.forEach((row, i) => {
  html += `<tr><th>${i + 1} ${PART[i].slice(0, 3)}</th>` + row.map((v, j) => {
    const sh = v ? Math.round(248 - 125 * v / vmax) : 252;
    return `<td style="background:rgb(${sh},${sh + 4},${sh + 10})"${i === j ? ' class="diag"' : ''}>${v || ''}</td>`;
  }).join('') + '</tr>';
});
tb.innerHTML = html;

/* ---------- 理论地图（3D，SVG 手写投影） ---------- */
(function(){
  const S = document.getElementById('tmsvg');
  const NS = 'http://www.w3.org/2000/svg';
  const COL = { '一致性 γ':'#6b7f3a', '网络 A':'#2E86AB', '换码 C':'#8c6d3f',
                '外置 ν':'#b5651d', '预算 R, Δ':'#1f3b57' };
  const SURF = ['一致性 γ','网络 A','换码 C','外置 ν','预算 R, Δ'];
  let yaw = 0.55, pitch = -0.28, zoom = 1, spin = true, filt = 'all', drag = null, hover = -1;

  // 位置：中心 → 五个量（向下排成一条竖列）→ 每量两枚叶子挂在两侧
  const N = [{ x:0, y:-150, z:0, r:18, col:'#1f3b57', kind:'hub',
               t1:'本书的模型', t2:'w·D+(T+λ)R+γD̄−H/β', lines:[] }];
  const ED = [];
  SURF.forEach((sf, si) => {
    const hy = -80 + si * 95;
    const hub = { x: 0, y: hy, z: 0, r: 10, col: COL[sf], kind:'surf', t1: sf, lines: [] };
    N.push(hub); const hi = N.length - 1; ED.push([0, hi, COL[sf], 2.0]);
    const items = LIMITS.map((it, k) => ({ it, k })).filter(o => o.it[0] === sf);
    items.forEach((o, m) => {
      const side = m % 2 ? 1 : -1;
      const leaf = { x: side * (215 + m * 20), y: hy + (m % 2 ? -26 : 26), z: (m % 2 ? 40 : -40),
                     r: 7, col: o.it[5] === 'out' ? '#b5651d' : COL[sf], kind: 'leaf',
                     t1: o.it[1], t2: o.it[2], contact: o.it[3],
                     lines: [o.it[1], '→ ' + o.it[2], '接洽：' + o.it[3], o.it[4]] };
      N.push(leaf); ED.push([hi, N.length - 1, leaf.col, 0.9]);
    });
  });

  const W = 980, H = 620;
  function proj(p){
    const cy = Math.cos(yaw), sy = Math.sin(yaw);
    let x = p.x*cy - p.z*sy, z = p.x*sy + p.z*cy;
    const cp = Math.cos(pitch), sp = Math.sin(pitch);
    let y = p.y*cp - z*sp; z = p.y*sp + z*cp;
    const f = 1400, s = f/(f + z + 210) * zoom;
    return { x: W/2 + x*s, y: H/2 + y*s, s, z };
  }
  function E(t, a){ const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); return e; }
  function draw(){
    S.innerHTML = '';
    const P = N.map(proj);
    // 边
    ED.slice().sort((u, v) => (P[u[0]].z + P[u[1]].z) - (P[v[0]].z + P[v[1]].z)).forEach(([a, b, col, w]) => {
      const A = P[a], B = P[b];
      const hot = hover >= 0 && (a === hover || b === hover);
      S.appendChild(E('line', { x1: A.x, y1: A.y, x2: B.x, y2: B.y, stroke: hot ? '#b5651d' : col,
        'stroke-opacity': hot ? 1 : 0.30, 'stroke-width': hot ? 2.6 : w }));
    });
    // 点与字
    P.forEach((q, i) => {
      const n = N[i];
      const hidden = filt !== 'all' && n.kind === 'leaf' && n.col !== COL[filt] && n.col !== '#b5651d';
      if (hidden) return;
      const r = n.r * q.s * (i === hover ? 1.25 : 1);
      S.appendChild(E('circle', { cx: q.x, cy: q.y, r, fill: n.col,
        'fill-opacity': n.kind === 'hub' ? 1 : 0.92, stroke: '#fff', 'stroke-width': 1.1 }));
      if (true) {
        const right = q.x >= W/2;
        const t = E('text', { x: q.x + (right ? r + 4 : -(r + 4)), y: q.y + 4,
          'text-anchor': right ? 'start' : 'end',
          fill: n.kind === 'surf' ? n.col : (i === hover ? '#8f4c12' : '#4a4a4a'),
          'font-size': n.kind === 'surf' ? 13 : (n.kind === 'hub' ? 14 : 12),
          'font-weight': n.kind === 'leaf' ? 400 : 700 });
        t.textContent = n.t1;
        S.appendChild(t);
        if (n.kind === 'leaf') {
          const t2 = E('text', { x: right ? q.x + r + 4 : q.x - r - 4, y: q.y + 15,
            'text-anchor': right ? 'start' : 'end', fill: '#9a9186', 'font-size': 8.6 });
          t2.textContent = n.t2;
          S.appendChild(t2);
        }
      }
    });
  }
  function nearest(mx, my){
    let best = -1, bd = 1e9;
    N.map(proj).forEach((q, i) => {
      const n = N[i];
      if (filt !== 'all' && n.kind === 'leaf' && n.col !== COL[filt] && n.col !== '#b5651d') return;
      const d = (q.x - mx) ** 2 + (q.y - my) ** 2;
      if (d < bd) { bd = d; best = i; }
    });
    return bd < 320 ? best : -1;
  }
  const TIP = document.getElementById('tip');
  S.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY }; S.setPointerCapture(e.pointerId); });
  S.addEventListener('pointerup', () => { drag = null; });
  S.addEventListener('pointermove', e => {
    const r = S.getBoundingClientRect();
    const mx = (e.clientX - r.left) * W / r.width, my = (e.clientY - r.top) * H / r.height;
    if (drag) { yaw += (e.clientX - drag.x) * 0.008; pitch += (e.clientY - drag.y) * 0.005;
      pitch = Math.max(-1.0, Math.min(0.6, pitch)); drag = { x: e.clientX, y: e.clientY }; draw(); return; }
    const h = nearest(mx, my);
    if (h !== hover) { hover = h; draw(); }
    if (h >= 0 && N[h].lines.length) {
      TIP.innerHTML = '<b>' + N[h].lines[0] + '</b><br>' + N[h].lines[1] +
        '<br><span style="color:#6b6255">' + N[h].lines[2] + '</span><br>' +
        '<span style="color:#8c8c8c">' + N[h].lines[3] + '</span>';
      TIP.style.left = (e.clientX + 14) + 'px'; TIP.style.top = (e.clientY + 12) + 'px'; TIP.style.opacity = 1;
    } else TIP.style.opacity = 0;
  });
  S.addEventListener('wheel', e => { e.preventDefault(); zoom *= e.deltaY < 0 ? 1.08 : 0.93;
    zoom = Math.max(0.6, Math.min(2.6, zoom)); draw(); }, { passive: false });
  document.querySelectorAll('button[data-s]').forEach(b => b.addEventListener('click', () => {
    filt = b.dataset.s;
    document.querySelectorAll('button[data-s]').forEach(x => x.classList.toggle('on', x === b));
    draw();
  }));
  document.getElementById('tspin').addEventListener('click', e => { spin = !spin; e.target.classList.toggle('on', spin); });
  (function loop(){ if (spin) { yaw += 0.0016; draw(); } requestAnimationFrame(loop); })();
  draw();

  // 表：把十二条的接洽点列全
  const tb = document.getElementById('tmtab');
  let html = '<tr><th>接触面</th><th>极限</th><th>退回到</th><th>接洽点（哪个量退化成对方的哪个量）</th><th>现实里</th></tr>';
  LIMITS.forEach(it => {
    const c = it[5] === 'out' ? '#b5651d' : COL[it[0]];
    html += `<tr><td style="color:${c};font-weight:700">${it[0]}</td><td><b>${it[1]}</b></td><td>${it[2]}</td><td>${it[3]}</td><td style="color:#8c8c8c">${it[4]}</td></tr>`;
  });
  tb.innerHTML = html;
})();

resize();
</script>
</html>
"""


def main() -> None:
    ch = load_chapters()
    pm = parts_map()
    info = fig_kgraph(ch, pm)
    fig_tmap()
    data = json.loads((DER / "kgraph.json").read_text(encoding="utf-8"))
    html = (HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False))
                .replace("__LIMITS__", json.dumps(LIMITS, ensure_ascii=False)))
    (ROOT / "assets" / "knowledge-map.html").write_text(html, encoding="utf-8")
    print("  knowledge-map.html")
    print(json.dumps({"nodes": info["nodes"], "edges": info["edges"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
