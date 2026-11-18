#!/usr/bin/env bash
# 本书的六项自查（收口用；本书不在 _series/lint 的 24 件之内，所以另立一条）
# 用法： bash scripts/selfcheck.sh
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe}"
export PYTHONIOENCODING=utf-8
fail=0
say() { printf '\n== %s\n' "$1"; }

say "1/6 结构：节号／表号／图号／禁词／markdown 残留"
"$PY" analysis/check_order.py --strict || fail=1

say "2/6 引用：缺口必须 0"
"$PY" analysis/audit_citations.py --strict || fail=1

say "3/6 目录：parts.json 与源文件对齐（只报差异）"
"$PY" analysis/sync_sections.py || true

say "4/6 密度：加粗、破折号、段落中位、每章节数"
"$PY" analysis/restyle.py --report | head -3
"$PY" - <<'PY'
import glob, io, re, statistics as st
def cn(s): return len(re.findall(r"[\u4e00-\u9fff]", re.sub(r"<[^>]+>", "", s)))
body, secs, paras = 0, {}, []
for f in sorted(glob.glob("source/ch*.html")):
    s = io.open(f, encoding="utf-8").read()
    body += cn(s)
    secs[f.split("/")[-1]] = len(re.findall(r'<h3 id=', s))
    s = re.sub(r'<div class="(?:refs|datasrc|box[^"]*)">.*?</div>', '', s, flags=re.S)
    s = re.sub(r"<ul>.*?</ul>", "", s, flags=re.S)
    paras += [cn(m.group(1)) for m in re.finditer(r"<p\b[^>]*>(.*?)</p>", s, re.S)]
out = [k for k, v in secs.items() if not (8 <= v <= 10)]
print("正文 %d 字；段落中位 %.0f" % (body, st.median(paras)))
print("节数不在 8—10 的章：", out or "无")
PY

say "5/6 产物：页数、字数、表图数"
"$PY" - <<'PY'
import glob, io, re
try:
    import pymupdf
    n = len(pymupdf.open("output/book.pdf"))
except Exception:
    n = "（打不开）"
tab = sum(len(re.findall("<table", io.open(f, encoding="utf-8").read())) for f in glob.glob("source/*.html"))
fig = sum(len(re.findall("<figure", io.open(f, encoding="utf-8").read())) for f in glob.glob("source/*.html"))
print("印刷版 %s 页；%d 表／%d 图" % (n, tab, fig))
PY

say "6/6 标签平衡（<b>/<p>/<i>/<table>/<div> 计数与嵌套）"
"$PY" - <<'PY'
import glob, io, re
bad = 0
for f in sorted(glob.glob("source/*.html")):
    s = io.open(f, encoding="utf-8").read()
    for t in ("b", "p", "i", "h3", "table", "div", "ul", "td", "tr"):
        o, c = len(re.findall(r"<%s[ >]" % t, s)), len(re.findall(r"</%s>" % t, s))
        if o != c:
            print("  ", f, t, o, c); bad += 1
    if re.search(r"<b>(?:(?!</b>).)*?<b>", s, re.S):
        print("  ", f, "nested <b>"); bad += 1
print("标签问题：", bad)
raise SystemExit(1 if bad else 0)
PY
[ $? -ne 0 ] && fail=1

printf '\n== 结论：%s\n' "$([ $fail -eq 0 ] && echo '全过' || echo '有失败项')"
exit $fail
