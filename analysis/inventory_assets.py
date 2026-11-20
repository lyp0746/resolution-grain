#!/usr/bin/env python3
"""V1 资产盘点：扫描 source/ch*.html，产出可复核的清单。

输出：
  analysis/results/v1_asset_scan.txt   逐章：节／表／图／datasrc／文献／数据文件，附全部表图题
  analysis/results/v1_asset_counts.json 逐章计数 + 全书合计 + 唯一数据文件

用法：
  python analysis/inventory_assets.py
"""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "source"
OUT = ROOT / "analysis" / "results"
OUT.mkdir(parents=True, exist_ok=True)


def clean(x: str) -> str:
    x = re.sub(r"<[^>]+>", "", x)
    return re.sub(r"\s+", " ", x).strip()


def scan_chapter(path: Path) -> dict:
    s = path.read_text(encoding="utf-8")
    h2 = re.search(r'<h2 class="chapter">(.*?)</h2>', s, re.S)
    title = clean(h2.group(1)) if h2 else "?"
    secs = [clean(x) for x in re.findall(r'<h3 id="sec[^"]*">(.*?)</h3>', s, re.S)]
    tabs = [clean(x) for x in re.findall(r'<caption class="cap">(.*?)</caption>', s, re.S)]
    figs = [clean(x) for x in re.findall(r'<figcaption class="cap">(.*?)</figcaption>', s, re.S)]
    datas = [clean(x) for x in re.findall(r'<div class="datasrc">(.*?)</div>', s, re.S)]
    refs = re.findall(r'<div class="refs">(.*?)</div>', s, re.S)
    nrefs = sum(len(re.findall(r'<p(?! class="refh")', r)) for r in refs)
    files = sorted(set(re.findall(r"(?:data|analysis)/[\w./-]+", s)))
    cn = len(re.findall(r"[\u4e00-\u9fff]", s))
    return {
        "file": path.name,
        "title": title,
        "cn": cn,
        "sections": len(secs),
        "tables": len(tabs),
        "figures": len(figs),
        "datasrc": len(datas),
        "refs": nrefs,
        "files": files,
        "section_titles": secs,
        "table_captions": tabs,
        "figure_captions": figs,
        "datasrc_texts": datas,
    }


def main() -> None:
    chapters = [scan_chapter(Path(p)) for p in sorted(glob.glob(str(SRC / "ch*.html")))]
    totals = {
        "chapters": len(chapters),
        "cn": sum(c["cn"] for c in chapters),
        "sections": sum(c["sections"] for c in chapters),
        "tables": sum(c["tables"] for c in chapters),
        "figures": sum(c["figures"] for c in chapters),
        "datasrc": sum(c["datasrc"] for c in chapters),
        "refs": sum(c["refs"] for c in chapters),
        "unique_files": len({f for c in chapters for f in c["files"]}),
    }

    whole = {"tables": 0, "figures": 0, "files": set()}
    for pat in ("appendix_*.html", "front_*.html", "back_*.html"):
        for p in sorted(glob.glob(str(SRC / pat))):
            s = Path(p).read_text(encoding="utf-8")
            whole["tables"] += len(re.findall(r'<table class="nat"', s))
            whole["figures"] += len(re.findall(r"<figure", s))

    lines = []
    for c in chapters:
        lines.append(f"## {c['file']} {c['title']}")
        lines.append(
            f"汉字 {c['cn']}｜节 {c['sections']}｜表 {c['tables']}｜图 {c['figures']}"
            f"｜datasrc {c['datasrc']}｜文献 {c['refs']}｜文件 {len(c['files'])}"
        )
        if c["files"]:
            lines.append("FILES: " + ", ".join(c["files"]))
        for t in c["section_titles"]:
            lines.append("  S: " + t)
        for t in c["table_captions"]:
            lines.append("  T: " + t)
        for t in c["figure_captions"]:
            lines.append("  F: " + t)
        for t in c["datasrc_texts"]:
            lines.append("  D: " + t[:500])
        lines.append("")

    (OUT / "v1_asset_scan.txt").write_text("\n".join(lines), encoding="utf-8")
    payload = {
        "totals": totals,
        "whole_book": {
            "tables": totals["tables"] + whole["tables"],
            "figures": totals["figures"] + whole["figures"],
            "note": "正文 28 章 + 附录 + 前置 + 后置；front_cast 的人物表也计入",
        },
        "chapters": chapters,
    }
    (OUT / "v1_asset_counts.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("chapters:", totals["chapters"])
    print("cn:", totals["cn"])
    print("sections:", totals["sections"])
    print("tables (body):", totals["tables"], "whole:", payload["whole_book"]["tables"])
    print("figures (body):", totals["figures"], "whole:", payload["whole_book"]["figures"])
    print("datasrc:", totals["datasrc"], "refs:", totals["refs"])
    print("unique data/analysis files:", totals["unique_files"])


if __name__ == "__main__":
    main()
