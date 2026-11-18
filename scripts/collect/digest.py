#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 data/raw 的可复现快照里抽取关键读数，生成 data/DIGEST.md。

只做"读数"，不做推断；推断留给正文。所有数字都带来源文件与快照日。
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "DIGEST.md"


def wb(name: str, label: str) -> str:
    p = RAW / f"{name}.json"
    if not p.exists():
        return f"- {label}：**未取得**（见 MANIFEST）"
    j = json.loads(p.read_text(encoding="utf-8"))
    rows = [(x["date"], x["value"]) for x in j[1] if x["value"] is not None]
    rows.sort()
    tail = rows[-6:]
    body = "；".join(f"{y}: {v:.3f}" if isinstance(v, float) else f"{y}: {v}" for y, v in tail)
    return f"- {label}（{name}）：{body}"


def owid(name: str, entity: str, label: str, col: str | None = None) -> str:
    p = RAW / f"{name}.csv"
    if not p.exists():
        return f"- {label}：**未取得**"
    with p.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return f"- {label}：空文件"
    ent_col = "Entity" if "Entity" in rows[0] else list(rows[0])[0]
    sel = [r for r in rows if r.get(ent_col) == entity]
    if not sel:
        return f"- {label}：文件中无 {entity}"
    val_col = col or [c for c in rows[0] if c not in (ent_col, "Code", "Year")][-1]
    sel.sort(key=lambda r: int(float(r["Year"])))
    tail = sel[-5:]
    body = "；".join(f"{int(float(r['Year']))}: {r[val_col]}" for r in tail)
    return f"- {label}（OWID/{entity}）：{body}"


def wiki_pv(name: str, label: str) -> str:
    p = RAW / f"{name}.json"
    if not p.exists():
        return f"- {label}：**未取得**"
    items = json.loads(p.read_text(encoding="utf-8")).get("items", [])
    by_year: dict[str, int] = defaultdict(int)
    for it in items:
        by_year[it["timestamp"][:4]] += it["views"]
    body = "；".join(f"{y}: {v:,}" for y, v in sorted(by_year.items()))
    return f"- {label}（月浏览量合计）：{body}"


def gallup_check(name: str) -> str:
    p = RAW / f"{name}.html"
    if not p.exists():
        return "- Gallup 28%：**未取得原文**"
    txt = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="ignore"))
    txt = re.sub(r"\s+", " ", txt)
    hits = re.findall(r".{0,90}(?:28%|record low|all-time low).{0,90}", txt)
    uniq = []
    for h in hits:
        h = h.strip()
        if h not in uniq:
            uniq.append(h)
    if not uniq:
        return "- Gallup 28%：原文中未检索到 28%/record low —— **该断言降为 C**"
    show = "\n".join(f"  > …{h}…" for h in uniq[:4])
    return f"- Gallup 28%：原文命中 {len(uniq)} 处\n{show}"


def main() -> None:
    lines = [
        "# 数据读数 v0.1",
        "",
        "> 由 `collect/digest.py` 从 `data/raw/` 生成。快照日见 `data/MANIFEST.tsv`。",
        "> 只列读数，不作推断；每个数字的可靠性按来源登记簿的等级读。",
        "",
        "## 一、生育率（E_t 的下游指标）",
        "",
        wb("wb_tfr_chn", "中国 TFR"),
        wb("wb_tfr_usa", "美国 TFR"),
        wb("wb_tfr_jpn", "日本 TFR"),
        wb("wb_tfr_kor", "韩国 TFR"),
        owid("owid_fertility", "China", "OWID 中国 TFR"),
        "",
        "## 二、平台化的前置条件（λ 与规则谱跃迁的背景）",
        "",
        wb("wb_net_chn", "中国互联网普及率（%）"),
        wb("wb_gdppc_chn", "中国的人均 GDP（现价美元）"),
        wb("wb_urb_chn", "中国城镇化率（%）"),
        "",
        "## 三、注意力代理（π_L 的可行性演示）",
        "",
        wiki_pv("wiki_pv_zhongguoren", "zh.wikipedia「中国人」条目"),
        "- 说明：「伪人」在 zh.wikipedia 无独立条目（实测 404），故 π_L 不能用该条目；"
        "该读数的用途是证明**管道可用**，不是证明标签在扩张。",
        "",
        "## 四、断言核验（把对话里的数字拉回原文）",
        "",
        gallup_check("gallup_media_trust"),
        "",
        "## 五、仍未取得（2026-11-16 改）",
        "",
        "- GDELT：**已取得**（`data/raw/gdelt/gdelt_deepfake_full.json`，677 天，2024-11—2026-11）。"
        "最早那次 429 是限速，不是封锁；完整序列已推翻摘录版的趋势（见 README §3c）。",
        "- 国家统计局：SSL 失败，需代理或手工下载。",
        "- CGSS / CFPS / WVS / PIAAC：登记制，需申请，不在本轮范围（WVS 已由 Kaggle 公开集补齐）。",
        "- WGI（`d` 的代理）：World Bank API 对该指标返回空集，需改从 WGI 官网 xlsx 取。",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
