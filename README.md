# 粗码 · Coarse Codes

**为什么越省力分得越粗，而核实为何总是追不上**
*How Saving Effort Reshapes Resolution, and Why Verification Trails Behind*

> **系列**：《有限系统的取舍》第十册（未入 `inventory.tsv`、不进合集）
> **上一版本**：2026-11-20，DOI [10.5281/zenodo.24390257](https://doi.org/10.5281/zenodo.24390257)（概念 DOI [10.5281/zenodo.24339909](https://doi.org/10.5281/zenodo.24339909)）
> **本版 DOI**：[10.5281/zenodo.24413735](https://doi.org/10.5281/zenodo.24413735)（V3，750 页；概念 DOI 10.5281/zenodo.24339909 不变）
> **当前版本**：**2026-11-21**——**8 部分 38 章**；正文 **385,969 汉字**；192 表／48 图；印刷版 **750 页**（阅读版 944 页）（EPUB／网页版／Markdown 齐备）
> **许可**：CC BY 4.0 ｜ **下载**：见 [Releases](../../releases)，**先看 `resolution-grain-print.pdf`**（印刷版，默认预览）

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
| 结构 Structure | 8 部分 38 章；正文 352 节 ＋ 附录与后置 39 节 |
| 正文 Body text | **385,969** 汉字（全书 425,900） |
| 表／图 Tables / figures | **192** 表 ／ **48** 图 |
| 印刷版 Print edition | **750** 页（A4，含封面与四级目录书签） |
| 阅读版 E-reader | **944** 页（重排；EPUB 3／网页／Markdown 齐备） |
| 术语／索引 Terms / index | 术语 **123** 条 ／ 索引 **144** 条 |
| 证据分级 Evidence grades | A（官方可复现）／B（稳定公开估计）／C（稀疏·构造·思辨） |
| 否证线 Falsification lines | **18** 条在表（附录 F.1）＋ **20** 条在正文 |
| 登记簿 Ledger | 附录 D **16** 行（append-only，D1—D15 未改） |
| 空白 Gaps | **9** 处（第 38 章：缺数据／缺概念／边界／未验） |
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
2. **不可测就说不可测**：第 38 章单列九处空白；附录 F 收 18 条否证线，正文另留 20 条；附录 D 的 16 行登记只追加、不改旧行。
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
bash scripts/selfcheck.sh          # 六项自查：结构／引用／目录／密度／产物／标签
"$PY" build_book.py --pdf          # 印刷版 → output/book.pdf
"$PY" build_book.py --ereader --pdf
"$PY" build_epub.py && "$PY" build_markdown.py
"$PY" analysis/make_theory_map.py  # 图 4.3 知识图谱、图 7.2 理论地图、3D 交互版
```

---

## 七、数据与可核性 ｜ Data and verifiability

- 定量结论都标了**快照日**（本版冻结于 2026-11-21；统计类 11-15/16、新闻类 11-16、文献类 11-19、A 股窗口 10-20 至 11-20）；原始文件的抓取时间（UTC）与 SHA256 在 `data/MANIFEST*.tsv`。
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
> https://doi.org/10.5281/zenodo.24413735

*Li, Y. (2026). Coarse Codes: How Saving Effort Reshapes Resolution, and Why Verification Trails Behind. Zenodo.*

**许可 ｜ License**：正文与图表 CC BY 4.0；代码 MIT（见 `LICENSE`、`LICENSE-MIT`）。
