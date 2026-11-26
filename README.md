# 粗码 · Coarse Codes

**为什么越省力分得越粗，而核实为何总是追不上**
*How Saving Effort Reshapes Resolution, and Why Verification Trails Behind*

> **系列**：《有限系统的取舍》第十册（未入 `inventory.tsv`、不进合集）
> **上一版本**：2026-11-21，DOI [10.5281/zenodo.24413735](https://doi.org/10.5281/zenodo.24535619)（概念 DOI [10.5281/zenodo.24339909](https://doi.org/10.5281/zenodo.24339909)）
> **本版 DOI**：[10.5281/zenodo.24535619](https://doi.org/10.5281/zenodo.24535619)（776 页；概念 DOI 10.5281/zenodo.24339909 不变）
> **当前版本**：**2026-11-26**（本地修订，**尚未发布**）——**8 部分 39 章**；正文 **406,453 汉字**；199 表／49 图；印刷版 **786 页**（合一版 812 页，阅读版 987 页）（EPUB／网页版／Markdown 齐备）
> **本版新增**：§33.6 由五个动作扩为**六个**（新增「纲领型」：锚搬进一份可按期修改的纲领，纠错取决于条文里有没有「判自己错」的程序），并补**表 33.5「六个动作，四格：锚、分类器、纠错、代价」**；此后两张表顺延为表 33.6／33.7。
> **付印版**：**2026-11-26**（786 页；合一版 812 页）。不发布，不覆盖已发布 DOI；要发布时概念 DOI 不变、版本 DOI 另取。
> **许可**：CC BY 4.0 ｜ **下载**：见 [Releases](../../releases)，**先看 `resolution-grain-print.pdf`**（印刷版，默认预览）

---

## English summary

**What it is.** A falsifiable popular-theory book, bilingual in apparatus but written in Chinese.
One principle (partition minimisation under a budget), four interfaces (price, cut, group, ledger),
four layers (person, group, society, civilisation) drawn as a graph with loops rather than a ladder.

**The claim.** What a code costs is set by the decision it has to answer: the budget of time and
attention, the price of being wrong, and the price of changing the code. From one stationarity
condition, `v* = (T + λ) / (2w)`, the book derives: doubling coverage halves precision; writing the
cost of cut points into the ledger gives two scaling laws; recoding costs once each way, so travel
and return are asymmetric (bandwidth `2C`). Nothing is claimed beyond its evidence: every number is
graded A/B/C, and every chapter ends with what would refute it.

**What is new in the 2026-11-26 local revision.** Eight parts, thirty-nine chapters, 786 pages
(812 in the bound-in edition with the prefatory essay, 987 in the e-reader layout). §33.6 gains a
sixth action — *programme-type* codes, where the anchor moves into a revisable document and error
correction depends on whether that document contains a clause letting the code judge itself —
with a four-fold comparison table (T33.5: anchor, classifier, correction, who pays). Two tables
that followed are renumbered 33.6 and 33.7.
Part VI now runs "six rings, one conveyor belt, one ledger": *transfer* moved in from the closing
part as ch. 25, and a new ch. 26 — *Crossbox: the person who signs in two ledgers* — gives a name to
the beneficiary that the earlier editions left unnamed. The second principle is narrowed to its one
non-redundant core ("weights can be negative"); "cost can be externalised" becomes a corollary, and
its test becomes a cross-partial derivative rather than a parameter, so its verdict changes from
"untested" to "two segments verified, the third not done". Seven new subsections, a new preface table
(four pairs of words not to be confused), and a real-data replacement for the verification-lag figure
(21,063 records, empirical survival curve).

**What it does not claim.** No new first principle, no population parameters, no causal direction,
no global universality, no policy prescription. The four layers are a formal analogy to
renormalisation, not a theorem. The weakest layer is the selector: the model gives direction and
position, not the person or the year.

**Read it in five minutes.** Ch. 2 (§2.5.2 for the one non-redundant core), ch. 13 (shared codes),
ch. 25 (transfer), ch. 26 (crossbox), ch. 38 (the verdict table), ch. 39 (nine gaps).

**Cite.** Li Yipeng (2026). *粗码 / Coarse Codes*. Zenodo. https://doi.org/10.5281/zenodo.24535619
(concept DOI 10.5281/zenodo.24339909).

---

## 一、这本书在讲什么 ｜ What this book is about

同一份力气，花在两个地方，会得到两种完全不同的结果。时间紧、睡得少、后果重的时候，人不是变懒了，
而是把有限的码率换了一种花法：环境宽的时候缩支撑，只剩一条隧道；环境窄的时候缩刻度，糊成一片。

> **不是「他分得粗」，而是「他的预算只买得起这种粗」。**
> 全书从一个驻点式出发，推到个人、群体、社会、文明四层；四层不是一条阶梯，是一张有环的图（第 3 章 §3.7，图 3.3）：
> 上行把慢量当参数送进快层（涌现），下行只在阈值处改写慢层的可行集（重置）。
> 最后说清一件事：**位置算得出来，时刻算不出来**。

*The same effort, spent in two different places, buys two entirely different results. Under time pressure,
sleep debt and high stakes, people do not become lazy — they spend a limited code budget differently.
The book starts from one first-order condition and carries it through the individual, the group and the society.*

**核心式子 ｜ The core**

```
v* = (T + λ) / (2w)        分辨率是「工夫 + 疲劳」与「错了有多疼」的驻点
δ  = Δ / 2^R               覆盖面翻倍，精度减半（一份预算，两个出口）
```

---

## 二、读数 ｜ By the numbers

| 项 / Item | 值 / Value |
|---|---|
| 结构 Structure | 8 部分 39 章；正文 362 节 ＋ 附录与后置 55 节 |
| 正文 Body text | **406,453** 汉字（全书 449,091） |
| 表／图 Tables / figures | **199** 表 ／ **49** 图 |
| 印刷版 Print edition | **786** 页（A4，含封面与四级目录书签） |
| 合一版 Bound-in edition | **812** 页（A4，卷首《得鹿梦鱼》26 ＋ 正文 786） |
| 阅读版 E-reader | **987** 页（重排；EPUB 3／网页／Markdown 齐备） |
| 术语／索引 Terms / index | 术语 **138** 条 ／ 索引 **154** 条 |
| 证据分级 Evidence grades | A（官方可复现）／B（稳定公开估计）／C（稀疏·构造·思辨） |
| 否证线 Falsification lines | **26** 条在表（附录 F.1）＋ 各章“反例与边界” |
| 登记簿 Ledger | 附录 D **23** 行（append-only，D1—D23） |
| 空白 Gaps | **9** 处（第 39 章：缺数据／缺概念／边界／未验） |
| 题记 Epigraphs | **36** 处；部分导语 8 段 |

---

## 三、骨架 ｜ Structure

| 部分 Part | 章 Chapters | 主提问 Question |
|---|---|---|
| 一 舞台 | 1—3 | 五个人为什么会在同一张桌上吵？ |
| 二 个人 | 4—8 | 码围着什么建？ |
| 三 两笔预算 | 9—12 | 爱与好奇要付什么码率？ |
| 四 群体 | 13—17 | 为什么两个人必须用同一套切法？ |
| 五 演化 | 18—22 | 变异、选择、场域如何改写可行集？ |
| 六 社会 | 23—28 | 核实、账单、内卷、漂移与临界能测到什么？ |
| 七 文明 | 29—34 | 转型、分期、翻译与边缘如何换码？ |
| 八 边界 | 35—38 | 这本书在哪里停？ |

六个核心（看见／记住／跟上／选择／讲述／临界）各落一章；六个标签读成**两条原理＋四个接触面**：
原理一＝预算下的划分极小化（P1、P2，带出 P3、P4）；原理二＝账可外置、权重可为负（P6）；
接触面＝价格、切法、群体、账。**P5 不是公设**，是「世界会变」这句描述世界的话。

---

## 四、怎么读 ｜ How to read

- **通识轨**：正文一路读下去；公式只在第 5 章出现一次，之后都可用文字替代。
- **同行轨**：附录 A（形式化）、附录 F（否证线总表）、附录 D（可证伪登记簿）。
- **三种读者可以停的地方**：第 5 章的三行推导、第 7 章与理性疏忽的关系、附录 A。

*Two tracks: the body for general readers; appendices A, F and D for specialists.
The formal core is three lines in chapter 5; everything after it can be read in words.*

---

## 五、诚实纪律 ｜ Honesty discipline

1. **结论强度 ≤ 证据强度**；每个数字带 A/B/C，等级写在表注与图注里，不逐句挂。
2. **不可测就说不可测**：第 39 章单列九处空白；附录 F 收 27 条否证线，各章另留“反例与边界”；附录 D 的 25 行登记只追加、不改旧行。
3. **失败与反例写在正文**，不放进脚注；**并置不是检验**（把两套理论放一张表上只说明它有位置）。
4. **反身性写「方向＋条件」**，不写宿命；凡需要第七个公设才讲得通的话，降为情景或删。

*Conclusion strength never exceeds evidence strength; what cannot be measured is said to be unmeasurable;
failures and counterexamples are reported in the body; juxtaposition is not a test.*

---

## 六、仓库里有什么 ｜ What is in this repo

```
source/    正文唯一来源（book.json / parts.json / front_* / ch01–ch38 / appendix_a–f / back_*）
assets/    css（paper / ereader / book）· svg · charts · knowledge-map.html（3D 交互版 ＋ 章节网络、演化环、极限退化矩阵、场域竞争四块）
analysis/  推导、审计、协议、图件脚本（`INDEX.md` 是唯一入口）
data/      raw（本地缓存，不入版本，账在 MANIFEST*.tsv）· derived · DIGEST*.md
docs/      变量表、源登记簿、需求单、事件台账、工作日志
scripts/   collect/（采集器）+ build.sh / release.sh / selfcheck.sh
archive/   过程日志与已归档的计划文档（logs/）
versions/  CHANGELOG.md
output/    build 产物（gitignore）      release/  组装产物（gitignore）
```

**构建 ｜ Build**

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
bash scripts/selfcheck.sh          # 七项自查：结构／引用／目录／密度／产物／标签／命名
"$PY" build_book.py --pdf          # 印刷版 → output/book.pdf
"$PY" build_book.py --ereader --pdf
"$PY" build_epub.py && "$PY" build_markdown.py
"$PY" analysis/make_theory_map.py  # 图 4.3 知识图谱、图 7.2 理论地图、3D 交互版
```

---

## 七、数据与可核性 ｜ Data and verifiability

- 定量结论都标了**快照日**（本版冻结于 2026-11-24；统计类 11-15/16、新闻类 11-16、文献类 11-19、A 股窗口 10-20 至 11-20）；原始文件的抓取时间（UTC）与 SHA256 在 `data/MANIFEST*.tsv`。
- 原始数据不入版本；派生读数在 `data/derived/`，由脚本生成，不手改。
- 主要公开来源：PolitiFact（21,063 条核实记录）、Seshat 古政体编码集（398 政体）、
  eCFR／Federal Register（266 个节级修订间隔）、历法采纳（125 国）、ESS／WVS、OEWN 义项清单（12.4 万条）。

---

## 八、系列 ｜ The series

《有限系统的取舍》九本书 ＋ 十五篇工作论文 ＋ 一部合集（共 24 件，以 `../inventory.tsv` 为准）。
本书是**第十册**，按作者决定：**不进入 `inventory.tsv`、不进合集**；归档记录见
`_zenodo/published_resolution-grain.json` 与 `_zenodo/REGISTRY.md`「未入册」一节。

*Item 10 of the series The Tradeoffs of Finite Systems. By the author's decision it is **not** counted
in `inventory.tsv` and **not** included in the 24-item collection.*

---

**引用 ｜ Cite**

> 李毅芃（2026）.《粗码：为什么越省力分得越粗，而核实为何总是追不上》. Zenodo.
> https://doi.org/10.5281/zenodo.24535619

*Li, Y. (2026). Coarse Codes: How Saving Effort Reshapes Resolution, and Why Verification Trails Behind. Zenodo.*

**许可 ｜ License**：正文与图表 CC BY 4.0；代码 MIT（见 `LICENSE`、`LICENSE-MIT`）。

<!-- viz-console -->
## 可视化阅读台 ｜ Reading console

这一件配了两个**离线单文件**：双击就能开，断网可用，零外部依赖、零服务器、零 API 账单。
Two offline single-file entries ship with this item. Double-click and it runs — no network, no server, no API bill.

| 入口 | 文件 | 体积 | 里面是什么 |
|---|---|---|---|
| 阅读页 | `assets/resolution-grain-reader.html` | 8499 KB | 三档切换（**骨架**＝只留标题与高亮框／**阅读**＝正文全显、表与证据折叠／**全展**＝全部展开，可用 Ctrl+F 搜全书表格）＋ **39 张章末审问卡** |
| 结构地图 | `assets/resolution-grain-explorer.html` | 3523 KB | 章际引用的 3D 螺旋、部 × 部矩阵、附录原表台账（按表号/章/单元格搜索）、图件账（SVG 内联，不缺图） |

- **审问卡**四行全部原文摘录，一个字不增写：`带走`（一句话带走／本章小结末句）／`打脸条件`（表 F.1、附录登记簿、或「反例与边界」节首段）／`封顶`（本章标过的 A/B/C 等级，没有就不印）／`动手`（【动手试试】）。右上角一键复制，粘到自己的 AI 里当严苛伴读。
  The audit card quotes four things verbatim — takeaway, falsification condition, evidence ceiling, hands-on prompt — and offers a one-click copy for your own AI, with the discipline written into the clipboard.
- **两页互跳**：阅读页顶部「结构地图 →」，结构地图工具栏「正文阅读页 →」，螺旋上点第 N 章直接落到 `#chN`。
- **算式装置**：三块算式装置（v\*=(T+λ)/2w、n\*=[s−(γ₀/α)e^{−λC}]/κ、t½=(ln2/γ₀)e^{λC}）＋ 十条极限退化表。滑块上没有一个是编的系数，式子照抄正文，页内按钮可当场复算。
- **已验证**：`375px` 窄屏与桌面均无横向溢出；0 个 JS 报错；三档切换 10–40 ms（纯 CSS class，不遍历 DOM）。
- **Computational bench** — three sliders-plus-recompute devices (stationarity, entry equilibrium, ebb half-life) and a ten-limit degeneration table; every parameter is quoted from the text.
- 本件规模：正文 **39 章**；审问卡 **39 张**。
  Size: **39 chapters**, **39** audit cards.


## 可视化阅读台 / Reading console

`粗码` 每件都有两个入口，**离线单文件、断网可开、零外部依赖**：

| 入口 | 文件 | 里面是什么 |
|---|---|---|
| 阅读页 | [`assets/resolution-grain-reader.html`](assets/resolution-grain-reader.html) | 三档切换（骨架／阅读／全展）＋ 每章末尾「审问卡」（带走／打脸条件／封顶／动手，四行全部原文摘录，可一键复制给自己的 AI 当严苛伴读） |
| 结构地图 | [`assets/resolution-grain-explorer.html`](assets/resolution-grain-explorer.html) | 章际引用的 3D 螺旋、部 × 部矩阵、附录原表台账（可搜）、图件账 |

另含 **三块算式装置**（驻点式 v\*、攒局规模 n\*、退潮半衰期 t½）与 **十条极限退化表**（把参数推到 0/∞，看方程退化成谁）。

两个页面顶部互跳；`375px` 窄屏与桌面都验过，0 外部请求。

Every item ships two offline single-file entries: a **reading console** (three density levels + a per-chapter audit card quoting the text verbatim) and a **structure map** (chapter-citation spiral, part × part matrix, appendix ledgers). No server, no external requests — double-click and it runs.

