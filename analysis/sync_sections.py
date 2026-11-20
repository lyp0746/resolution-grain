#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 `source/parts.json` 的 `sections` 与各章源文件的 `<h3>` 对齐。

为什么要有这个脚本
  `build_book.py` 的三级目录读 `parts.json` 的 `sections`，四级的锚点来自源文件。
  扩写一章（增节、并节、改名）之后，两处不同步，目录就会出现"点进去是空锚"或
  "列出了源文件里没有的节"。手改 JSON 容易漏，所以用源文件当唯一真相。

用法
  "$PY" analysis/sync_sections.py            # 只报差异
  "$PY" analysis/sync_sections.py --write    # 写回 parts.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "source"
PARTS = SRC / "parts.json"


def h3_labels(path: Path) -> list[str]:
    """取 <h3> 的行内 HTML 标签原样保留（目录里要用 <i> 显示符号），只把换行压成空格。"""
    txt = path.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"<h3[^>]*>(.*?)</h3>", txt, flags=re.S):
        label = re.sub(r"\s*\n\s*", "", m.group(1))
        out.append(label.strip())
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--src", default="source", help="相对于仓根的源目录（V2 用 source-v2）")
    args = ap.parse_args()
    src = ROOT / args.src
    parts_path = src / "parts.json"
    globals()["SRC"] = src

    parts = json.loads(parts_path.read_text(encoding="utf-8"))
    diff = 0
    for part in parts:
        for ch in part.get("chapters", []):
            f = ch.get("file")
            if not f or not (SRC / f).exists():
                continue
            want = h3_labels(SRC / f)
            have = ch.get("sections", [])
            if want != have:
                diff += 1
                print(f"[ch{ch['no']:>2}] {len(have)} -> {len(want)} 节")
                for x in want:
                    if x not in have:
                        print("   + ", x)
                for x in have:
                    if x not in want:
                        print("   - ", x)
                ch["sections"] = want
    if args.write and diff:
        parts_path.write_text(json.dumps(parts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"written: {parts_path}  ({diff} 章有差异)")
    elif diff:
        print(f"{diff} 章有差异（未写回，加 --write）")
    else:
        print("sections 与源文件一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
