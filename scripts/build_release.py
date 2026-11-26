#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建 release/（读者可见交付包）—— 一源一轮，不手抄。

来源（唯一）：
  output/book.pdf                 -> resolution-grain-print.pdf
  output/book-ereader.pdf         -> resolution-grain-ereader.pdf
  合集/单行本/make_combined.py    -> resolution-grain-print-combined.pdf（先跑那个脚本）
  output/book.epub                -> resolution-grain.epub
  output/book.html                -> resolution-grain.html
  output/book-ereader.html        -> resolution-grain-ereader.html
  output/markdown/                -> resolution-grain.md + resolution-grain-markdown/
  assets/svg/cover.svg            -> cover.svg
  assets/charts|svg/knowledge-map -> visuals -> resolution-grain-visuals.zip
  README.md                       -> release/README.md      （同一份，不再另抄）
  docs/RELEASE-NOTES.md           -> release/修订说明.md
  docs/DATA-GAPS.md               -> release/数据缺口清单.md
  docs/REQUESTS.md                -> release/欢迎补充数据.md

产出：14 个主文件 + 分章 Markdown 目录；MANIFEST.txt（字节数＋SHA256 前 16 位＋页数）；
SHA256SUMS（全 64 位）。

用法：  "$PY" scripts/build_release.py
"""
from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
REL = ROOT / "release"
DATE = "2026-11-26"
SLUG = "resolution-grain"

# 名称 -> 来源（None 表示由本脚本或上游脚本就地生成，只校验存在）
MAIN = [
    ("README.md", ROOT / "README.md"),
    ("cover.svg", ROOT / "assets" / "svg" / "cover.svg"),
    ("resolution-grain.html", OUT / "book.html"),
    ("resolution-grain-ereader.html", OUT / "book-ereader.html"),
    ("resolution-grain-print.pdf", OUT / "book.pdf"),
    ("resolution-grain-print-combined.pdf", None),
    ("resolution-grain-ereader.pdf", OUT / "book-ereader.pdf"),
    ("resolution-grain.epub", OUT / "book.epub"),
    ("resolution-grain.md", OUT / "markdown" / "book.md"),
    ("resolution-grain-markdown.zip", None),
    ("resolution-grain-visuals.zip", None),
    ("修订说明.md", ROOT / "docs" / "RELEASE-NOTES.md"),
    ("数据缺口清单.md", ROOT / "docs" / "DATA-GAPS.md"),
    ("欢迎补充数据.md", ROOT / "docs" / "REQUESTS.md"),
]

# 清单里的说明行（与实物一一对应；页数由 PDF 实测）
DESC = {
    "README.md": "仓库首页",
    "cover.svg": "封面",
    "resolution-grain.html": "网页版",
    "resolution-grain-ereader.html": "网页版（电子阅读版式）",
    "resolution-grain-print.pdf": "印刷版 PDF（A4，独册，{print} 页）",
    "resolution-grain-print-combined.pdf": "印刷版合一版（A4，{comb} 页：卷首《得鹿梦鱼》26 页＋正文 {print} 页）",
    "resolution-grain-ereader.pdf": "电子阅读版 PDF（重排单册，{er} 页）",
    "resolution-grain.epub": "EPUB 3",
    "resolution-grain.md": "合并 Markdown",
    "resolution-grain-markdown.zip": "分章 Markdown（压缩包）",
    "resolution-grain-visuals.zip": "可视化包（图件＋knowledge-map.html）",
    "修订说明.md": "本版改了什么",
    "数据缺口清单.md": "本书的缺口、边界与可改写条件",
    "欢迎补充数据.md": "想帮忙的话",
}


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


def pages(path: Path) -> int:
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(path)).pages)
    except Exception:
        return 0


def main() -> int:
    REL.mkdir(exist_ok=True)

    # 1) 主文件（有来源的复制；无来源的必须已存在，不静默跳过）
    for name, src in MAIN:
        dst = REL / name
        if src is not None:
            shutil.copy2(src, dst)
        elif not dst.exists():
            raise SystemExit(f"缺文件：{name}（合一版请先跑 合集/单行本/make_combined.py）")

    # 2) 分章 Markdown：目录 + zip
    md_dir = REL / "resolution-grain-markdown"
    if md_dir.exists():
        shutil.rmtree(md_dir)
    shutil.copytree(OUT / "markdown", md_dir)
    zip_dir(OUT / "markdown", REL / "resolution-grain-markdown.zip")

    # 3) 可视化包（图件 + 交互版），打一个 zip
    vis = OUT / "viz-release"
    if vis.exists():
        shutil.rmtree(vis)
    (vis / "charts").mkdir(parents=True)
    (vis / "svg").mkdir(parents=True)
    for p in sorted((ROOT / "assets" / "charts").glob("*.png")):
        shutil.copy2(p, vis / "charts" / p.name)
    for p in sorted((ROOT / "assets" / "svg").glob("*.svg")):
        shutil.copy2(p, vis / "svg" / p.name)
    shutil.copy2(ROOT / "assets" / "knowledge-map.html", vis / "knowledge-map.html")
    zip_dir(vis, REL / "resolution-grain-visuals.zip")

    # 4) MANIFEST / SHA256SUMS
    n_print = pages(REL / "resolution-grain-print.pdf")
    n_comb = pages(REL / "resolution-grain-print-combined.pdf")
    n_er = pages(REL / "resolution-grain-ereader.pdf")
    rows = []
    for name, _ in MAIN:
        p = REL / name
        rows.append((name, p.stat().st_size, sha(p)))

    with (REL / "MANIFEST.txt").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# {SLUG} — 发布包清单（{DATE}）\n")
        fh.write(f"# 印刷版 {n_print} 页 ／ 合一版 {n_comb} 页 ／ 阅读版 {n_er} 页\n")
        fh.write("# 路径\t字节数\tSHA256 前 16 位\t说明\n")
        for (name, size, h), _ in zip(rows, MAIN):
            d = DESC.get(name, "").format(print=n_print, comb=n_comb, er=n_er)
            fh.write(f"{name}\t{size}\t{h[:16]}\t{d}\n")
        fh.write("resolution-grain-markdown/\t-\t-\t分章 Markdown（目录）\n")
        fh.write("\n不包含：analysis/ 脚本、data/ 原始数据、source/ 源文件、*.py。\n")

    with (REL / "SHA256SUMS").open("w", encoding="utf-8", newline="\n") as fh:
        for name, _, h in rows:
            fh.write(f"{h}  {name}\n")

    print(f"release: {len(rows)} 主文件（印刷 {n_print} / 合一 {n_comb} / 阅读 {n_er} 页）")
    print(f"visuals: {len(list(vis.rglob('*')))} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
