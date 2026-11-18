#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""知识图谱与理论地图（2026-11-18）。

两样东西，一个脚本：
  ① **知识图谱**：把 28 章、7 部、6 个附录、以及 12 个核心量画成一张网，
     边＝正文里的交叉引用（"第 N 章""N.M 节""附录 A.x"）。用于回答"这本书到底是一张网还是一条线"。
  ② **理论地图**：把表 7.3 的十条极限画成从泛函向外辐射的辐条，每条辐条末端是
     "退回去的那支理论"。用于回答"统摄是怎么发生的"。

产出
  assets/charts/c04_kgraph.png / .svg     知识图谱（印刷用，300 dpi）
  assets/charts/c04_tmap.png  / .svg      理论地图（印刷用）
  assets/knowledge-map.html               交互版（自带力导向，双击打开即可）
  data/derived/kgraph.json                节点与边的原始数据

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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "charts"
SVG = ROOT / "assets" / "svg"
DER = ROOT / "data" / "derived"
C_MAIN, C_ALT, C_GREY = "#1f3b57", "#b5651d", "#8c8c8c"

plt.rcParams.update({
    "font.sans-serif": ["Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False, "figure.dpi": 300, "font.size": 9,
})


# ------------------------------------------------------------------ 解析
CHAPTER_NAMES = {}


def load_chapters() -> dict[int, dict]:
    out = {}
    for p in sorted(ROOT.glob("source/ch*.html")):
        n = int(re.search(r"ch(\d+)", p.name).group(1))
        h = p.read_text(encoding="utf-8")
        title = re.sub(r"<[^>]+>", "", re.search(r"<h2[^>]*>(.*?)</h2>", h, flags=re.S).group(1)).strip()
        CHAPTER_NAMES[n] = title.split("　")[-1]
        t = re.sub(r"<[^>]+>", "", h)
        refs = set()
        for m in re.finditer(r"第\s*(\d{1,2})\s*章", t):
            k = int(m.group(1))
            if 1 <= k <= 28 and k != n:
                refs.add(k)
        for m in re.finditer(r"(?<!\d)(\d{1,2})\.(\d{1,2})\s*节", t):
            k = int(m.group(1))
            if 1 <= k <= 28 and k != n:
                refs.add(k)
        for m in re.finditer(r"附录\s*A\.(\d{1,2})", t):
            refs.add(100 + int(m.group(1)))
        out[n] = {"title": CHAPTER_NAMES[n], "refs": sorted(refs)}
    return out


def parts_map() -> dict[int, int]:
    """章 → 部（4 章一部，取自 parts.json 的 sections 计数）。"""
    p = json.loads((ROOT / "source" / "parts.json").read_text(encoding="utf-8"))
    mapping, cur = {}, 1
    for part in p:
        secs = part.get("sections") or []
        if secs:
            for s in secs:
                n = int(re.search(r"ch(\d+)", s).group(1)) if "ch" in s else None
                if n:
                    mapping[n] = cur
        cur += 1
    return mapping


# ------------------------------------------------------------------ 布局（Kamada–Kawai）
def layout(nodes, edges):
    """用 networkx 的 Kamada–Kawai（图距≈欧氏距），比自写力导向稳得多。"""
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(nodes)
    for a, b in edges:
        if a in G and b in G and a != b:
            G.add_edge(a, b)
    for comp in nx.connected_components(G):          # 孤立点也给个位置
        pass
    pos = nx.kamada_kawai_layout(G)
    # 归一化到 [-1,1]
    xy = np.array([pos[v] for v in nodes])
    xy -= xy.mean(0)
    xy /= (np.abs(xy).max() or 1.0)
    return {v: xy[i] for i, v in enumerate(nodes)}


def draw_kgraph(ch: dict[int, dict], fname: str = "c04_kgraph") -> dict:
    nodes = [f"ch{n}" for n in sorted(ch)] + [f"apA{i}" for i in range(17)]
    edges = []
    for n, d in ch.items():
        for r in d["refs"]:
            edges.append((f"ch{n}", f"ch{r}" if r < 100 else f"apA{r-100}"))
    edges = [(a, b) for a, b in edges if a in nodes and b in nodes]
    pos = layout(nodes, edges)
    degree = {v: 0 for v in nodes}
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1

    fig, ax = plt.subplots(figsize=(8.4, 8.4))
    for a, b in edges:
        x1, y1 = pos[a]; x2, y2 = pos[b]
        ax.plot([x1, x2], [y1, y2], color=C_GREY, lw=0.5, alpha=0.40, zorder=1)
    for v in nodes:
        x, y = pos[v]
        if v.startswith("ch"):
            s = 90 + 10 * degree[v]
            ax.scatter([x], [y], s=s, color=C_MAIN, zorder=3, edgecolor="white", linewidth=0.9)
            ax.text(x, y - 0.045, v[2:], fontsize=7.6, ha="center", va="top", color=C_MAIN)
        else:
            ax.scatter([x], [y], s=24, color=C_ALT, marker="s", zorder=3,
                       edgecolor="white", linewidth=0.6)
    ax.set_axis_off()
    ax.set_title("知识图谱：28 章与 17 个附录节之间的引用网", fontsize=11, pad=10)
    ax.text(0.01, 0.02, "点大＝被引更多；灰色细线＝正文里的一次交叉引用", transform=ax.transAxes,
            fontsize=7.4, color=C_GREY)
    fig.tight_layout()
    fig.savefig(OUT / f"{fname}.png", bbox_inches="tight")
    try:
        fig.savefig(SVG / f"{fname}.svg", bbox_inches="tight")
    except Exception:
        pass
    plt.close(fig)
    DER.mkdir(exist_ok=True)
    (DER / "kgraph.json").write_text(json.dumps(
        {"nodes": [{"id": v, "degree": degree[v], "x": round(float(pos[v][0]), 4),
                    "y": round(float(pos[v][1]), 4),
                    "label": (ch[int(v[2:])]["title"] if v.startswith("ch") else v)} for v in nodes],
         "edges": [{"source": a, "target": b} for a, b in edges]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print("  ", fname, "nodes", len(nodes), "edges", len(edges))
    return {"nodes": len(nodes), "edges": len(edges), "degree": degree}


# ------------------------------------------------------------------ 理论地图
LIMITS = [
    ("w → ∞", "极细码", "法律条文／会计准则／诊断标准"),
    ("w → 0 或 T → ∞", "极粗码", "口号／刻板印象／MBTI"),
    ("γ > δ", "更差的码被维持", "习俗／教义／行话"),
    ("C 大", "迟滞：错了也不改", "制度惯性／身份／职业路径"),
    ("β 小", "双稳＋突变", "革命／崩盘／雪崩"),
    ("β 大", "渐变、无阈值", "渐进改革／缓慢污名化"),
    ("βγ|λmin| 过阈", "对称破缺", "一个正统 vs 碎片"),
    ("zγ > δ", "公共码出现", "规范／共同语／正统"),
    ("ν < 0", "解跑到边界", "代价外置／粗码＋全责"),
    ("d → 0", "观测变清、双稳消失", "留痕／审计／公开"),
]


def draw_tmap(fname="c04_tmap") -> None:
    fig, ax = plt.subplots(figsize=(8.6, 6.4))
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.scatter([0], [0], s=7000, color="#eef2f6", edgecolor=C_MAIN, linewidth=1.2, zorder=1)
    ax.text(0, 0.26, "总账（泛函）", ha="center", fontsize=11, color=C_MAIN)
    ax.text(0, 0.06, "w·D + (T+λ)·R", ha="center", fontsize=8.2, color=C_GREY)
    ax.text(0, -0.10, "＋ γ·(平均失真)", ha="center", fontsize=8.2, color=C_GREY)
    ax.text(0, -0.26, "－ 噪声项 H/β", ha="center", fontsize=8.2, color=C_GREY)

    n = len(LIMITS)
    for i, (lim, what, theory) in enumerate(LIMITS):
        ang = np.pi / 2 - 2 * np.pi * i / n
        x, y = 1.55 * np.cos(ang), 1.55 * np.sin(ang)
        ax.plot([0.42 * np.cos(ang), (1.55 - 0.30) * np.cos(ang)],
                [0.42 * np.sin(ang), (1.55 - 0.30) * np.sin(ang)],
                color=C_GREY, lw=1.0, alpha=0.8, zorder=1)
        ax.scatter([x], [y], s=44, color=C_ALT, zorder=3)
        ha = "left" if np.cos(ang) > 0.15 else ("right" if np.cos(ang) < -0.15 else "center")
        ax.text(x + 0.08 * np.cos(ang), y + 0.10 * np.sin(ang), lim,
                ha=ha, va="center", fontsize=8.6, color=C_ALT, weight="bold")
        ax.text(x + 0.08 * np.cos(ang), y - 0.09 + 0.10 * np.sin(ang), what,
                ha=ha, va="center", fontsize=7.8, color=C_MAIN)
        ax.text(x + 0.08 * np.cos(ang), y - 0.20 + 0.10 * np.sin(ang), theory,
                ha=ha, va="center", fontsize=7.2, color=C_GREY)
    ax.set_xlim(-2.6, 2.9)
    ax.set_ylim(-2.0, 2.1)
    ax.set_title("理论地图：十条极限，十支理论退回去的地方", fontsize=11, pad=6)
    fig.tight_layout()
    fig.savefig(OUT / f"{fname}.png", bbox_inches="tight")
    try:
        fig.savefig(SVG / f"{fname}.svg", bbox_inches="tight")
    except Exception:
        pass
    plt.close(fig)
    print("  ", fname)


# ------------------------------------------------------------------ 交互版
HTML = """<!doctype html>
<meta charset="utf-8">
<title>《分辨的预算》知识图谱</title>
<style>
 body{margin:0;background:#0f1720;color:#e8eef5;font:14px/1.5 -apple-system,"Noto Sans SC",sans-serif}
 header{padding:14px 18px 6px}
 h1{font-size:16px;margin:0 0 4px;font-weight:600}
 .sub{color:#8ba0b5;font-size:12px}
 #wrap{position:relative}
 canvas{display:block;width:100vw;height:calc(100vh - 64px);cursor:grab}
 .tip{position:fixed;pointer-events:none;background:#1b2836;border:1px solid #2c3f52;
      padding:6px 9px;border-radius:6px;font-size:12px;opacity:0;transition:opacity .12s}
 .legend{position:fixed;left:18px;bottom:14px;color:#8ba0b5;font-size:12px}
</style>
<header><h1>《分辨的预算》· 知识图谱</h1>
<div class="sub">拖动节点可移动；悬停看名字；滚轮缩放。边＝正文中的一次交叉引用。</div></header>
<div id="wrap"><canvas id="c"></canvas><div class="tip" id="tip"></div></div>
<div class="legend">大圆＝章（点越大被引越多）；小方＝附录 A 的节</div>
<script>
const DATA = __DATA__;
const cv = document.getElementById('c'), ctx = cv.getContext('2d'), tip = document.getElementById('tip');
let W, H, scale = 1, ox = 0, oy = 0, drag = null, hover = null;
function resize(){ const r = devicePixelRatio || 1; W = cv.clientWidth; H = cv.clientHeight;
  cv.width = W * r; cv.height = H * r; ctx.setTransform(r,0,0,r,0,0); draw(); }
addEventListener('resize', resize);
const N = DATA.nodes.map(n => ({...n}));
const byId = Object.fromEntries(N.map(n => [n.id, n]));
const E = DATA.edges.map(e => ({s: byId[e.source], t: byId[e.target]}));
function tx(x){ return (x * 160 + W/2) * scale + ox; }
function ty(y){ return (y * 160 + H/2) * scale + oy; }
function draw(){
  ctx.clearRect(0,0,W,H);
  ctx.strokeStyle = 'rgba(140,165,190,0.28)'; ctx.lineWidth = 0.7;
  for(const e of E){ if(!e.s||!e.t) continue; ctx.beginPath(); ctx.moveTo(tx(e.s.x),ty(e.s.y)); ctx.lineTo(tx(e.t.x),ty(e.t.y)); ctx.stroke(); }
  for(const n of N){
    const X = tx(n.x), Y = ty(n.y);
    if(n.id.startsWith('ch')){
      const r = (5 + Math.min(14, Math.sqrt(n.degree)*3.2)) * Math.max(0.7, Math.min(1.6, scale));
      ctx.fillStyle = (hover===n) ? '#e8b06a' : '#4a86c5'; ctx.beginPath(); ctx.arc(X,Y,r,0,7); ctx.fill();
      if(scale > 0.75){ ctx.fillStyle='rgba(232,238,245,0.85)'; ctx.font='11px sans-serif'; ctx.textAlign='center';
        ctx.fillText(n.id.slice(2), X, Y - r - 4); }
    } else {
      const s = 4.5 * Math.max(0.7, Math.min(1.6, scale));
      ctx.fillStyle = '#a8763f'; ctx.fillRect(X-s/2, Y-s/2, s, s);
    }
  }
}
function pick(mx,my){
  let best=null, bd=1e9;
  for(const n of N){ const d=(tx(n.x)-mx)**2+(ty(n.y)-my)**2; if(d<bd){bd=d;best=n;} }
  return bd < 500 ? best : null;
}
cv.addEventListener('mousemove', ev=>{
  const r = cv.getBoundingClientRect(), mx = ev.clientX-r.left, my = ev.clientY-r.top;
  if(drag){ drag.node.x += (mx-drag.x)/160/scale; drag.node.y += (my-drag.y)/160/scale; drag.x=mx; drag.y=my; draw(); return; }
  const h = pick(mx,my); hover = h;
  if(h){ const label = h.label || h.id; tip.textContent = label; tip.style.left=(mx+14)+'px'; tip.style.top=(my+10)+'px'; tip.style.opacity=1; cv.style.cursor='pointer'; }
  else { tip.style.opacity=0; cv.style.cursor='grab'; }
  draw();
});
cv.addEventListener('mousedown', ev=>{ const r=cv.getBoundingClientRect(); const h=pick(ev.clientX-r.left, ev.clientY-r.top); if(h) drag={node:h,x:ev.clientX-r.left,y:ev.clientY-r.top}; });
addEventListener('mouseup', ()=>drag=null);
cv.addEventListener('wheel', ev=>{ ev.preventDefault(); scale *= ev.deltaY<0 ? 1.08 : 0.93; scale=Math.max(0.35, Math.min(3, scale)); draw(); }, {passive:false});
resize();
</script>
"""


def main() -> None:
    ch = load_chapters()
    info = draw_kgraph(ch)
    draw_tmap()
    data = json.loads((DER / "kgraph.json").read_text(encoding="utf-8"))
    (ROOT / "assets" / "knowledge-map.html").write_text(
        HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
    print("  knowledge-map.html")
    print(json.dumps({"nodes": info["nodes"], "edges": info["edges"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
