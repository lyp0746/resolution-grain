# 第二版的装配与构建（2026-11-19，第八十二轮）

> 本页只写**怎么跑**与**每一条检查管什么**。V2 的源只在一处：`source-v2/`；
> `source/`（第一版）不动。所有脚本都加了 `--src`（以及 `build_book.py` 的 `--out`），
> 不设参数时行为与第一版完全一致。

---

## 1 一条命令的收口

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"

"$PY" analysis/check_v2_sources.py                                   # 30 章：字数/节/表图号/图/标签/禁词/**
"$PY" analysis/check_order.py --src source-v2 --strict               # 表图号顺序、节号、引用悬空、caption
"$PY" analysis/audit_citations.py --src source-v2 --out analysis/CITATION-AUDIT-V2.md   # 引用缺口必须 0
"$PY" -X utf8 analysis/sync_sections.py --src source-v2 --write      # parts.json 的 sections 与 <h3> 对齐
"$PY" build_book.py --src source-v2 --out output-v2                  # 自包含 HTML（→ output-v2/book.html）
"$PY" build_book.py --src source-v2 --out output-v2 --pdf            # 加 A4 PDF（未跑：等排版轮）
```

**注意两处 Windows/WSL 的坑**：
1. `python.exe` **不继承** WSL 的环境变量（`RG_SOURCE=… python` 看不见），所以源目录走**命令行参数**，不走 env。
2. 终端是 GBK，脚本打印 `⟨i⟩C⟨/i⟩` 这类下标会抛 `UnicodeEncodeError`——跑 `sync_sections.py` 时加 `-X utf8`。

---

## 2 每一条检查管什么

| 命令 | 查什么 | 现在的状态 |
|---|---|---|
| `check_v2_sources.py` | 汉字数（≥8,000）、`<h3>` 节数、表／图号、图片存在、标签平衡、禁词、`**` 残留、`id` 唯一 | **OK（30 章）** |
| `check_order.py --src source-v2 --strict` | 表号／图号按**文档顺序**连续；节号连续且前缀＝章号；正文引用的表图**存在**；caption／figcaption 齐全 | **0 问题** |
| `audit_citations.py --src source-v2` | 正文出现的姓＋年份、《书名》、中文人名，在本章文献或全书文献里有没有条目 | **引用缺口 0 / 机制疑点 61（清单，非失败项）** |
| `sync_sections.py --src source-v2 --write` | `parts.json` 的 `sections` 与源文件 `<h3>` 一致（目录用） | 一致 |
| `build_book.py --src source-v2 --out output-v2` | 组装：部分扉页＋导语＋小结、章前扉页（题记＋本章结构）、四级目录、图内嵌、页眉 | **book.html 5.1 MB，7 部分／30 章／360 个目录链接** |

---

## 3 这一轮为通过检查所做的改动（都在 `source-v2/`）

1. **表／图重编号（8 章）**：ch01、02、03、05、06、08、09、11 的表号原先是“插入顺序”，与文档顺序不一致（ch06 为 1,2,5,3,6,4）。按文档顺序重编，并把正文里的引用一并改。
2. **三级标题 `x.y.z` 由 `<h3>` 改为 `<h4>`**：`spec` 里“节”只有 `N.M` 一级；三级标题属于节内小节（第一版也用 `h4`）。共改 51 处（ch09 14、ch10 20 等），锚点 `secN-M-K` 不变。
3. **补 34 条文献条目**：ch01（图灵 1950）、ch02（Gigerenzer、North）、ch05（波菲利、康德、图灵 1936/1950、弗雷格、维特根斯坦、福柯）、ch07（斯密、孟子、Legendre 变换）、ch08（亚里士多德《形而上学》、波兰尼）、ch09（布迪厄、康德《判断力批判》、本雅明、库恩、莫奈、马奈、《人民日报》）、ch10（廷代尔、路德、纳尔逊）、ch11（道格拉斯、齐美尔、《区分的语言》、《人民日报》）、ch14（弗朗提努斯）、ch21（王朴《平边策》）、ch22（《末日审判书》）、ch23（Cellarius 全名）。
4. **审计工具的三处修正**（不是放水，是把“不是引用”的东西排除）：产品名与记号（Google／Linux／Glass／Glasshole／Explorer／Xanadu 的年份写法／`UqUw`／`UwUq`）与作者首名（Julius／Sextus／Pierre／Adam／Christoph）进 `STOP`；`比亚韦斯托克` 是地名、含“斯托克”，扫描人名前先剥掉；姓＋年份的匹配也过一遍 `STOP`。
5. **ch21 的一处自造文献**：原表注写“《明治史》基本年表”，那本书并不存在，改为“明治通行的基本年表”。

---

## 3b 前置页与后置页（本轮新增 7 件）

| 文件 | 内容 | 字数 |
|---|---|---:|
| `front_epigraph.html` | 题记（木匠那句 ＋ “它不懂我”） | 120 |
| `front_preface.html` | 前言：问题、不主张什么、第二版做了什么、三条纪律、数据声明 | 1,418 |
| `front_quickstart.html` | 两条轨（故事／证据）＋三条路线＋可跳清单＋符号三约定 | 960 |
| `front_cast.html` | 五张脸（老陈／小林／阿伟／小吴／小满）与各自的 T、λ、w | 953 |
| `front_terms.html` | 符号表 20 行＋四组不许混的词＋**θ 的两处用法**（修 V1 的重载） | 1,055 |
| `front_roadmap.html` | 七部分三十章路线图（表 R.1，由 `parts.json` 生成） | 1,036 |
| `back_references.html` | 全书参考文献（30 章“本章文献”汇总、去重 222 条） | — |

**构建结果**：`output-v2/book.pdf` **404 页**，33 个一级／二级书签，索引 24 条，页脚页码 404 页全部盖上。
抽查过四页：版权／提要页、目录、表 2.2、图 22.1、部分扉页。

## 3c 这轮改了两处 CSS（`assets/css/paper.css`，第一版同样受益）

1. `table.nat { break-inside: avoid }` ＋ `table.nat + .datasrc { break-before: avoid }`——**小表不再跨页**（改前表 2.2 断在第 40／41 页之间，且表注与表体分离）。代价：全书 400 → 404 页（+4）。
2. `.cap { text-align: left }` ＋ `.cap code, .datasrc code { word-break: break-all }`——**图注不再被两端对齐拉开**（表 22.1 的图注原来出现“偏 数 据 ：”这种断口）。

两条都只影响打印／电子版的重建；**已发布的 PDF 不变**。若要重出第一版 PDF，页数会变（预期 +4 页左右）。

## 3d 一条构建脚本的改动

`build_book.py` 的后置分组标题原先写死为“结语与附录”（V1 有 `back_epilogue.html`）。第二版没有独立结语（第 30 章就是结语），现按“源目录里有没有 `back_epilogue.html`”自动选：“结语与附录”或“附录与参考文献”。

## 4 仍未做

- **PDF**：已跑（404 页）。但 V2 还缺后置页，页码与索引仍是“半套”：索引只有 24 条（没有术语表就没有索引的主体）；附录 A—F 缺失，按规范“书须有 A—F”这一条还没满足。
- **EPUB**：`build_epub.py` 未跑（它依赖 nav／ncx 与后置页，等附录齐了再跑）。
- **前置／后置页**：V2 目前只有 `front_map.html`（图0.1／0.2）。缺失的七件前置（题记、前言、怎么读、人物页、术语与符号、路线图、硬核入口）与后置（结语、导读、后记、本系列、术语表、附录 A—F、参考文献）需要按 V2 的 30 章重写，不能从第一版直接搬（章号全变了）。
- **目录项**：`parts.json` 的 `desc` 字段在第 2—7 部分是我按章题机械重建的（原 `desc` 已在一次误写中丢失，见 §5），它只在 `intro` 缺失时被用到；`intro`／`summary` 已从第一版构建产物逐字恢复。
