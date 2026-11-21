#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建 release/（读者可见交付包）。

来源：
  output-v2/book.pdf / book-ereader.pdf / book.epub / book.html / book-ereader.html
  output-v2/markdown/            -> resolution-grain.md + -markdown.zip
  assets/charts/*.png            -> visuals/charts/
  assets/svg/part-*.svg          -> visuals/svg/
  assets/knowledge-map.html      -> visuals/
  release/README.md / 修订说明.md / 数据缺口与边界.md / cover.svg  （手写，保留）

产出：
  12 个主文件 + visuals/；MANIFEST.txt（字节数＋SHA256 前 16 位）；SHA256SUMS（全 64 位）。
"""
from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
REL = ROOT / "release"
DATE = "2026-11-21"
SLUG = "resolution-grain"

MAIN = [
    ("cover.svg", None),
    ("README.md", None),
    ("resolution-grain-ereader.html", OUT / "book-ereader.html"),
    ("resolution-grain-ereader.pdf", OUT / "book-ereader.pdf"),
    ("resolution-grain-markdown.zip", None),
    ("resolution-grain-print.pdf", OUT / "book.pdf"),
    ("resolution-grain-visuals.zip", None),
    ("resolution-grain.epub", OUT / "book.epub"),
    ("resolution-grain.html", OUT / "book.html"),
    ("resolution-grain.md", OUT / "markdown" / "book.md"),
    ("修订说明.md", None),
    ("数据缺口与边界.md", None),
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def zip_dir(src: Path, dst: Path) -> None:
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(src).as_posix())


def main() -> int:
    REL.mkdir(exist_ok=True)

    # 1) 主文件
    for name, src in MAIN:
        dst = REL / name
        if src is not None:
            shutil.copy2(src, dst)

    # 2) Markdown 单文件已复制；分章 zip 重建
    zip_dir(OUT / "markdown", REL / "resolution-grain-markdown.zip")

    # 3) 可视化
    vis = REL / "visuals"
    if vis.exists():
        shutil.rmtree(vis)
    (vis / "charts").mkdir(parents=True)
    (vis / "svg").mkdir(parents=True)
    for p in sorted((ROOT / "assets" / "charts").glob("*.png")):
        shutil.copy2(p, vis / "charts" / p.name)
    for p in sorted((ROOT / "assets" / "svg").glob("part-*.svg")):
        shutil.copy2(p, vis / "svg" / p.name)
    for name in ("c04_kgraph.png", "c04_tmap.png"):
        shutil.copy2(ROOT / "assets" / "charts" / name, vis / name)
    shutil.copy2(ROOT / "assets" / "knowledge-map.html", vis / "knowledge-map.html")
    zip_dir(vis, REL / "resolution-grain-visuals.zip")

    # 4) MANIFEST / SHA256SUMS
    rows = []
    for name, _ in MAIN:
        p = REL / name
        rows.append((name, p.stat().st_size, sha(p)))
    with (REL / "MANIFEST.txt").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# 发布包清单（{DATE}）\n")
        fh.write("# 路径\t字节数\tSHA256 前 16 位\n")
        for name, size, h in rows:
            fh.write(f"{name}\t{size}\t{h[:16]}\n")
    with (REL / "SHA256SUMS").open("w", encoding="utf-8", newline="\n") as fh:
        for name, _, h in rows:
            fh.write(f"{h}  {name}\n")

    print(f"release: {len(rows)} files, "
          f"visuals {len(list(vis.rglob('*')))} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
