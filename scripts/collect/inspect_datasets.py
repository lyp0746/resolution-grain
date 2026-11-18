#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查已下载数据集的模式与覆盖，写 data/INSPECT.md（UTF-8，避免终端乱码）。"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DS = ROOT / "data" / "raw" / "datasets"
OUT = ROOT / "data" / "INSPECT.md"
L = []


def p(s: str = "") -> None:
    L.append(s)


def politifact() -> None:
    zp = DS / "kg_politifact.zip"
    p("## 1. PolitiFact（τ 的美国侧）")
    p("")
    if not zp.exists():
        p("- 未取得"); return
    with zipfile.ZipFile(zp) as z:
        name = z.namelist()[0]
        data = [json.loads(x) for x in z.read(name).decode("utf-8").splitlines() if x.strip()]
    p(f"- 文件：`{name}`，记录 {len(data)} 条")
    p(f"- 字段：{', '.join(sorted(data[0].keys()))}")
    p("")
    # τ = factcheck_date - statement_date
    from datetime import datetime as _dt
    def _d(s):
        for f in ("%m/%d/%Y", "%Y-%m-%d"):
            try: return _dt.strptime(s, f)
            except Exception: pass
        return None
    lags, by_year = [], {}
    for d in data:
        a, b = _d(d.get("statement_date", "")), _d(d.get("factcheck_date", ""))
        if a and b and b >= a:
            lag = (b - a).days
            lags.append(lag)
            by_year.setdefault(b.year, []).append(lag)
    if lags:
        lags.sort()
        q = lambda x: lags[min(len(lags) - 1, int(len(lags) * x))]
        p(f"- **τ 可算**：{len(lags):,} 条；中位 {q(.5)} 天，P25 {q(.25)}，P75 {q(.75)}，P90 {q(.9)}")
        p(f"- τ > 30 天占比：{sum(1 for x in lags if x > 30)/len(lags):.1%}；τ > 365 天：{sum(1 for x in lags if x > 365)/len(lags):.1%}")
        sy = sorted(by_year)
        p("- 按年（中位 τ）：" + "；".join(f"{y}: {sorted(by_year[y])[len(by_year[y])//2]}" for y in sy))
        p(f"- 年份覆盖：{sy[0]}–{sy[-1]}")
    p("")
    keys = sorted(data[0].keys())
    # 日期字段与覆盖
    for k in keys:
        vals = [d.get(k) for d in data]
        miss = sum(1 for v in vals if v in (None, "", "N/A"))
        v0 = next((v for v in vals if v not in (None, "")), "")
        p(f"  - `{k}`：缺失 {miss}/{len(vals)}；示例 {str(v0)[:70]}")
    p("")


def hotlists() -> None:
    zp = DS / "kg_hotlists.zip"
    p("## 2. 中国三平台小时榜（π_L 的当期切片）")
    p("")
    if not zp.exists():
        p("- 未取得"); return
    with zipfile.ZipFile(zp) as z:
        names = [n for n in z.namelist() if n.endswith(".csv")]
        rows = []
        for n in names:
            if not n.startswith("snapshots_"):
                continue
            txt = z.read(n).decode("utf-8", errors="replace")
            rows.extend(csv.DictReader(io.StringIO(txt)))
    p(f"- 快照文件 {len([n for n in names if n.startswith('snapshots_')])} 个，行数 {len(rows):,}")
    p(f"- 覆盖：{min(r['snapshotHour'] for r in rows)} → {max(r['snapshotHour'] for r in rows)}")
    c = Counter(r["platform"] for r in rows)
    p(f"- 平台分布：{dict(c)}")
    cat = Counter(r["category"] for r in rows if r["category"])
    p(f"- 分类前 8：{cat.most_common(8)}")
    p("")


def weibo() -> None:
    zp = DS / "kg_weibo_hot.zip"
    p("## 3. 微博热搜（π_L 的长序列候选）")
    p("")
    if not zp.exists():
        p("- 未取得"); return
    with zipfile.ZipFile(zp) as z:
        for n in [x for x in z.namelist() if x.endswith(".csv")]:
            txt = z.read(n).decode("utf-8", errors="replace")
            rd = list(csv.reader(io.StringIO(txt)))
            head, body = rd[0], rd[1:]
            p(f"### `{n}`：{len(body):,} 行")
            p(f"- 表头：{head}")
            p(f"- 首行：{[x[:40] for x in body[0]]}")
            p(f"- 末行：{[x[:40] for x in body[-1]]}")
            dates = [r[0] for r in body if r and r[0][:4].isdigit()]
            if dates:
                p(f"- 日期范围：{min(dates)} → {max(dates)}（{len(set(dates))} 个不同日期）")
            # π_L 可行性：标题关键词命中率（低命中 = 该代理不可用）
            import re as _re
            kw = {"摆拍": r"摆拍", "剧本": r"剧本", "反转": r"反转", "辟谣/谣言": r"辟谣|谣言", "道歉": r"道歉"}
            p("- 标题关键词命中（占全部行）：" + "；".join(
                f"{k} {sum(1 for r in body if len(r) > 1 and _re.search(v, r[1]))}"
                for k, v in kw.items()))
            p("")


def main() -> None:
    p("# 数据集检查 v0.1")
    p("")
    p("> 由 `collect/inspect_datasets.py` 生成。只报模式与覆盖，不报结论。")
    p("")
    politifact(); hotlists(); weibo()
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"written {OUT}")


if __name__ == "__main__":
    main()
