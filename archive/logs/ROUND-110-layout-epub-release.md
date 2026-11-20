# 第一百一十轮（2026-11-20）：排版轮、EPUB、索引、release-v2

> 作者四项：①再画 3—5 张；②排版轮（超宽图重画）；③EPUB；④索引扩到 150 条；完成后全面检查，并准备 release / GitHub / Zenodo。

---

## 1 排版轮：三张超宽图（这是本轮最实质的改动）

| 图 | 原尺寸 | 改成 | 做法 |
|---|---|---|---|
| 图 11.1 审美 | 11.2 in 三联 | **6.4 in，2×2 网格**（上左 W(Nov)、上右时间线、下跨栏 Cmp×Coh） | 图注同步改为“上左／上右／下” |
| 图 9.1 爱 | 9.6 in 双幅 | **6.4×2.9 双幅** | 字号统一 6.6—7.6 |
| 图 12.1 创造 | 10.4 in 单幅 | **6.4×3.9** | 盒子宽度与箭头重排 |

**为什么重要**：140 mm 版心里，11.2 in 的图只剩 52%，图内 8 pt 变成 4 pt。改完之后这三张图的图内字在版心里约 6.5—7 pt，可读。

**顺带修的两处**：①“刚好”标签原先压在倒 U 的峰上，移到 U 形内部；②生成的箭头指向 W(Nov)，应指向链头 Cmp——改成斜指左端。

---

## 2 EPUB 3

`build_epub.py` 原先只认默认 `source/`，本轮加 `--src/--out`（与 `build_book.py` 同规格）。

产物：99 个条目（52 XHTML、42 图）；`mimetype` 首位且 **STORED**（不压缩）；`OEBPS/nav.xhtml` 471 个链接；`toc.ncx` 回退齐备；`content.opf` 96 items／51 spine。

---

## 3 Markdown

`build_markdown.py` 同样加 `--src/--out`：51 个文件（`book.md` ＋ 分章）、41 个图。

---

## 4 索引 104 → 144 条

术语表补 27 条，每条都核过“正文里真出现”（脚本：把词条逐个在 `ch*.html` ＋ `appendix_*.html` 的纯文本里数，报 0 命中的）。补的词偏“读者会去查第二次”的：势博弈、复制子、渗流阈值、反身性、私码、闸口、罚则、举证责任、程序型／内化型、公共品／搭便车、选择性激励、类目数、自洽、双稳、沉没成本、伪分辨率、口径／版本／存量／流量／时刻／执行者、识别策略、稳态、均衡。

---

## 5 可视化按 33 章重生成

`make_theory_map.py` 加了 `--src/--out`，并把三处写死的 28 改成 33（章数、范围、画布宽）。

- **弧线图**：33 节点、**255 条边**；部带改为“一 舞台／二 个人／三 爱与好奇／四 群体／五 社会／六 文明／七 边界”。
- **修一处硬伤**：原先标注“被引最多的两章”写死为第 4、20 章（旧稿的枢纽），与图注里按度数算出的四章不符。改为按度数自动取前二。
- **交互版** `knowledge-map.html` 同步重生成（33 章）。
- **知会**：`assets/knowledge-map.html` 已被覆盖为 33 章版本；上一版发布包 `release/knowledge-map.html`（2026-11-18）未动。

---

## 6 release-v2/（64 个文件）

```
resolution-grain-print.pdf      635 页 / 551 书签
resolution-grain-ereader.pdf    794 页
resolution-grain.epub           EPUB 3
resolution-grain.html / -ereader.html
resolution-grain.md / -markdown.zip   51 文件 + 41 图
cover.svg
visuals/charts/*.png            43 张（只留正文引用的 + 弧线图/退回图）
visuals/svg/part-*.svg          7 张
visuals/knowledge-map.html      交互版（33 章）
README.md / 修订说明.md / 数据缺口与边界.md
MANIFEST.txt / SHA256SUMS       自校验 0 不一致
```

---

## 7 发布准备（未做网络操作）

- `.zenodo.json` 更新到 2026-11-20：描述重写为**中英各八段**（中文摘要／核心主张／结构与证据／本版修订／诚实纪律／边界／版本信息／系列，英文同构）；首段 `<p><b>中文摘要。</b>`；`*` 计数 **0**（用 ∗ 代替）；五条断言通过。
- `_zenodo/desc/resolution-grain.html` 与 `desc_plain/resolution-grain.txt` 同步。
- `docs/PUBLISH-V2.md`：GitHub 标签命令、Zenodo 新版本四步（开草稿 → 预留 DOI → 上传 → 断言）、**关联标识第三档**（自身仓库＋共用库＋六本专著新版本 DOI，逐个重取）、发布前五项包体核对。

---

## 8 收口状态

```
check_v2_sources   OK（33 章）
check_order        0
audit_citations    缺口 0（机制清单 77）
sync_sections      一致
<pre>              0
版本 token         0（软件版一处豁免）
附录 A.x 指针      只剩 A.7，存在
索引               144 条
```

**下一步只剩人按按钮**：`git tag v2026-11-20` → `gh release create` → Zenodo 开新版本、预留 DOI、上传 `release-v2/*`、断言元数据。
