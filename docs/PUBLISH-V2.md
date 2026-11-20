# 发布准备（第二版，2026-11-21）

> 这一页是**操作单**：把这一版推上 GitHub、发到 Zenodo 之前要跑的检查与要按的按钮。
> 本轮**没有**执行任何网络操作（不推、不发、不预留 DOI）；下面每一步都可照抄。

---

## 0 产物（已就位）

| 位置 | 内容 |
|---|---|
| `output-v2/` | 印刷版 PDF（642 页）、阅读版 PDF（807 页）、EPUB、两个 HTML、Markdown（51 个文件） |
| `release-v2/` | 读者可见交付包：8 个主文件 ＋ `visuals/`（43 PNG ＋ 7 SVG ＋ 交互版）＋ README／修订说明／数据缺口／MANIFEST／SHA256SUMS（**64 个文件**） |
| `.zenodo.json` | 完整 payload（**已更新到 2026-11-21**，描述含中英各八段） |
| `_zenodo/desc/resolution-grain.html` ／ `desc_plain/resolution-grain.txt` | 两种描述视图（已更新） |

**一处要知会**：`assets/knowledge-map.html` 已被重生成（33 章、255 条边），上一版发布包 `release/knowledge-map.html` 仍是 2026-11-18 的旧文件，未动。

---

## 1 发布前断言（已跑过，全过）

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
"$PY" analysis/check_v2_sources.py          # OK（33 章）
"$PY" analysis/check_order.py --src source-v2 --strict   # 0
"$PY" -X utf8 analysis/audit_citations.py --src source-v2 --out analysis/CITATION-AUDIT-V2.md  # 缺口 0
"$PY" -X utf8 analysis/sync_sections.py --src source-v2  # 一致
grep -c "<pre>" source-v2/*.html | grep -v ":0" || echo 无
grep -c "第一版\|第二版\|V2\|本版" source-v2/*.html | grep -v ":0" || echo 无
grep -oh "附录 [A-F]\.[0-9]*" source-v2/*.html | sort | uniq -c   # 只剩 A.7
```

Zenodo 元数据五条：

```bash
"$PY" - <<'EOF'
import json,io
z=json.load(io.open(".zenodo.json",encoding="utf-8"))
assert z["description"].count("*")==0
assert z["description"].startswith("<p><b>中文摘要。</b>")
assert " / " in z["title"] and len(z["title"])>60
assert z["license"]=="CC-BY-4.0" and z["keywords"] and z["creators"]
assert z["version"]=="2026-11-21" and z["publication_date"]=="2026-11-21"
print("五条通过")
EOF
```

---

## 2 GitHub（标签与发布）

```bash
cd /d/0_Article/resolution-grain
# 1) 只提交源与产物边界：source-v2/、analysis/、assets/、release-v2/、文档
git add source-v2 analysis assets release-v2 README.md AGENTS.md AGENTS-DERIVATION.md         versions analysis/HANDOFF.md analysis/ROUND-PLAN-V2.md docs/PUBLISH-V2.md         build_book.py build_epub.py build_markdown.py analysis/make_v2_figures.py analysis/make_theory_map.py
git status --short          # 确认没有 output-v2/ 与 data/raw/
git commit -m "v2: 7 parts / 33 chapters; 319,900 chars; 169 tables / 43 figures; print 635 pages"
git tag -a v2026-11-21 -m "Coarse Codes, second edition (2026-11-21)"
git push origin main --tags
gh release create v2026-11-21 release-v2/*    --title "粗码（第二版）/ Coarse Codes (2nd ed.)"    --notes-file "release-v2/修订说明.md"
```

**纪律**：`output-v2/` 与 `data/raw/` 不进版本；`release-v2/` 里每个文件都在 `MANIFEST.txt` 有字节数与哈希。

---

## 3 Zenodo（新版本，不覆盖旧 DOI）

**规则**：概念 DOI 不变（`10.5281/zenodo.24339909`），版本 DOI 变。
**先预留 DOI**，写进 `CITATION.cff` 与 `README.md`，再打包上传。

```bash
# 0) 取最新版本记录号（REGISTRY.md 里的会漂移）
curl -s -H "Authorization: Bearer $TOKEN"   "https://zenodo.org/api/records/24393431/versions" | jq -r '.hits.hits[].metadata.version'

# 1) 开新版本草稿
curl -s -X POST -H "Authorization: Bearer $TOKEN"   "https://zenodo.org/api/records/24393431/versions" -o draft.json
DRAFT=$(jq -r '.id' draft.json)

# 2) 预留 DOI，并写进 CITATION.cff / README
curl -s -X POST -H "Authorization: Bearer $TOKEN"   "https://zenodo.org/api/records/$DRAFT/draft/pids/doi"
```

上传文件（**新版本草稿会继承父版本文件，先逐个 DELETE**）：

```python
# _zenodo/republish_book.py 已按这套流程写好；这里只列四条要点
# ① 文件是"建条目 → PUT 内容 → commit 单个文件"三步，创建响应会把已有条目一并返回，按 key==name 选对
# ② 内容 PUT 用 requests（urllib 在内容 PUT 上会被重定向吞掉正文）
# ③ RDM 只认 metadata.rights / subjects / languages；legacy 的 license/keywords 会被静默丢弃
# ④ publisher 是 DOI 注册必填（用"独立出版 / Independently published"）
```

**发布后立刻断言**：`license`、`keywords`、`creators` 非空；`description.count("*")==0`；`version` 与 `2026-11-21` 一致。

---

## 4 关联标识（每次都重取，不抄上一版）

本件属**第三档**（论文与合集同档：共用库 ＋ 六本专著的新版本 DOI；有仓库的再加自身仓库）：

| 关系 | 目标 |
|---|---|
| `isSupplementedBy` | `https://github.com/lyp0746/resolution-grain` |
| `isPartOf` | 共用库 `series-workspace` |
| `isPartOf` × 6 | 六本学术专著**当前版本** DOI（逐个 `GET /versions` 取 `metadata.version` 最大者，跳过 `edition-2026-…` 伪版本） |

**不要去 `inventory.tsv` 抄**：本册未登记（作者决定），件数与 DOI 以 `_zenodo/published_resolution-grain.json` 与本单为准。

---

## 5 发布包内容核对（发之前逐项看一遍）

- [ ] 印刷版 635 页、551 书签；首页封面不缩水（打开第 1 页看边框）
- [ ] 阅读版 794 页（重排，无固定版心）
- [ ] EPUB：`unzip -p resolution-grain.epub mimetype` → `application/epub+zip`；目录可三级跳
- [ ] Markdown：51 个文件 ＋ 41 个图
- [ ] `visuals/`：43 PNG（300 dpi）＋ 7 SVG ＋ `knowledge-map.html`（33 章）
- [ ] `SHA256SUMS` 自校验：`cd release-v2 && sha256sum -c SHA256SUMS`
- [ ] 描述首段是 `<p><b>中文摘要。</b>`；`*` 计数为 0
