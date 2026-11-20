# 第九十七轮（2026-11-20）：附录 B—E、术语表与索引、六核心补节

> 过程日志。结论已搬进 `analysis/HANDOFF.md` §0j、`versions/CHANGELOG.md`、`AGENTS.md` §8。
> 这一页只记**怎么做**与**踩到什么**，供下一轮复用。

---

## 1 顺序

1. 读五份（`AGENTS.md`、`AGENTS-DERIVATION.md`、`analysis/V2-EXPERIENCE.md`、`HANDOFF.md` §0i、`ROUND-PLAN-V2.md`），确认基线：33 章、正文 287,637、全书 303,467、451 页。
2. **A**：写 `appendix_b/c/d/e.html`（先 B，再 C、D、E），每写完一份跑一次 `check_v2_sources`。
3. **B**：`back_glossary/series/postscript/popular_guide.html`。
4. **C**：`ch04`、`ch06`、`ch15` 补节；`ch03` 表 3.3 重写；`ch23` §23.4＋图 23.2。
5. 收口：四项检查 → `sync_sections --write` → `build_book --pdf` → 抽页看版式。

## 2 三处必须记住的做法

### 2.1 “补节”= 先算好重编号，再一次改完

补一节会牵动三样东西：`<h3>` 号与 `id`、表号、正文里的 `见 x.y`／`§x.y`。

做法固定为：**先改文本引用（此时标题还是旧号，不会撞），再按降序改标题与 `id`，最后插入新节**。
- ch04：新节插在 §4.3 后 → 旧 4.4—4.9 → 4.5—4.10；表 4.3—4.6 → 4.4—4.7（新表占 4.3）。
- ch06：新节插在 §6.7 后 → 旧 6.8—6.10 → 6.9—6.11；**表号踩过一次坑**：新表先写成 6.7，`check_order` 报 `[1,2,3,4,5,7,6]`——因为原 表 6.6 在“格式塔”那一节（新 6.9），位置更后。改法：新表 6.6、旧 6.6 → 6.7。
- ch15：新节插在 §15.4 后 → 旧 15.5—15.9 → 15.6—15.10；旧 表 15.3 → 15.4。
- ch23：新节插在 §23.3 后 → 旧 23.4—23.8 → 23.5—23.9，h4 23.7.1 → 23.8.1；旧 表 23.3 → 23.4。

**验证**：`check_order --strict` 查表／图／节号连续性；另写一次性脚本查“所有 `§x.y` 是否都有对应标题”（本轮报 0 悬空）。

### 2.2 长表跨页：`table.nat.tbl-flow`

第一版 PDF 里附录 B 的十二行表被整张推到下一页，前一页剩 2/3 空白——因为 `paper.css` 有一条 `table.nat {break-inside: avoid}`（为小表加的），长表也吃了它。
改法：加 `table.nat.tbl-flow {break-inside: auto}`，行内仍 `tr {break-inside: avoid}`，表头由 `thead` 自动重复。给 表 B.1、D.1、D.2、F.1、G.1 挂上。页数 484 → 482，空白消失。

### 2.3 术语表要能喂索引

`build_book.load_terms()` 取**第一张首列表头含“术语／词”的表**，把第一列当词条；`compute_indexmap` 再回 PDF 里检索页码。
于是有两条硬要求：① 表头第一格必须叫“术语”；② **每个词条必须在正文里真出现**，否则索引里是一条没有页码的死条目。
本轮做法：先写 78 条，再用脚本对 `ch*.html` 的纯文本逐一 `count`，报出 12 条 0 命中（“支撑与刻度”“命名三件套”“五格编码”“转型三条件”等复合名），逐条改成正文里真出现的写法（支撑／命名的三件套／五格／三个条件）。索引 24 → 98 条。

## 3 两处“顺手修”

- **附录 F 的章号全线过期**：F 是 28 章／30 章时代写的，18 行里 15 行的章号与标题还是旧号（“第15章 核实”等）。本轮按 33 章逐行重排，并把“留在正文”的清单从 12 条改成 15 条（18＋15＝33，且与表内 18 行不重叠）。
- **九处悬空节引用**（重排遗留，`check_order` 不管）：ch24 五处 21.7/21.8、ch25 22.9、ch27 24.7、ch28 25.8／25.5、ch29 26.5、ch31 28.8。逐条按语境改成本章或对应章的现号（记在 CHANGELOG 里）。
  **判据**：读到“见 x.y”时先问“它要说的是哪一件事”，再到 `source-v2` 里 `grep` 那件事的现址；不要按数字直觉平移。

## 4 图 23.2

`analysis/make_v2_figures.py` 新增 `fig_yanduan()`，三幅 6.4 in：
- 左：阈值两种写法（常数线＋三条 <i>w</i> 曲线），参数设定，标“C 级”；
- 中：冲击卷积 <i>A</i>(<i>t</i>) 与慢变量 <i>S</i>（读 `data/derived/sim_yanduan.csv`）；
- 右：<i>w</i><sub>序</sub> 与 <i>w</i><sub>胜</sub>，底色是实现出来的码（`code` 列），标“翻过去，不回头”。

返工两次：① 图例与曲线颜色顺序对不上、右幅注释压住图例；② 底注放在 `ax` 里与曲线重叠。最终把底注改为 `fig.text`（页脚一行），`subplots_adjust` 让出底部。**图内字号最小 7.0 pt**。

## 5 复跑命令（本轮实际用的）

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
"$PY" analysis/check_v2_sources.py
"$PY" analysis/check_order.py --src source-v2 --strict
"$PY" -X utf8 analysis/audit_citations.py --src source-v2 --out analysis/CITATION-AUDIT-V2.md
"$PY" -X utf8 analysis/sync_sections.py --src source-v2 --write
"$PY" build_book.py --src source-v2 --out output-v2 --pdf
```

**坑**：`sync_sections.py` 在 GBK 控制台上打印含 `₀₁₂` 的标题会抛 `UnicodeEncodeError`（在写回之前就崩，因此 `--write` 等于没跑）。**一律加 `-X utf8`**。另：`--write` 前先 `cp parts.json` 到 `_temp/`，写完整段 diff 一次（本轮只动 `sections`）。

## 6 留给下一轮

- 20 张图（清单在 `analysis/BUILD-V2.md`）。
- 章型分化（枢纽章加厚、收口章压缩）。
- EPUB（附录齐了，`build_epub.py` 可跑）。
- `data/DATA-LEDGER.md` 四行“未入仓的引用”补 URL 或改口径。
- `PART-VI/VII-CLOSEOUT.md` 里 30 章时代的指针。
