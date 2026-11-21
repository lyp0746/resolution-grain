#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把本书手写的 <i>/<sub>/<sup> 式子转成 MathML（系列版式）。

用途：`.mblock` / `.eq` 里的式子必须走 `<math display="block">`，
与《错位的时间》《容量的级联》等件一致；表格里的定义式走 `<math>` 行内式。

设计原则：
  1. 只做“形状”转换，不改公式内容；转不动的记号原样留在 <mtext> 里，宁可难看，不可算错。
  2. 分式一律保留 `a/b` 线性写法（MathML 的 <mo>/</mo> 有正常间距），
     除非源文已经用括号写明分子分母；不自动猜 <mfrac>。
  3. 幂与下标按 <msup>/<msub> 输出。

用法：
  python analysis/eq2mathml.py --check          # 只打印转换结果，不写文件
  python analysis/eq2mathml.py --apply          # 就地改写 source/*.html 的 .mblock/.eq
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "source"

GREEK = "αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΘΛΞΠΣΦΨΩ"
OPS = set("=+-−·×÷/<>≤≥≠≡≈⇒⇔⟺→←↔∈∉∝∞∂∫∮Σ∏√±∓|()[]{},;:!'″")
SUBSCRIPT_DIGITS = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
                    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"}
SUPERSCRIPT = {"²": "2", "³": "3", "¹": "1", "⁰": "0", "⁴": "4",
               "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}
FUNCS = {"log", "ln", "max", "min", "exp", "supp", "sin", "cos", "Pr"}
LATIN_WORD = re.compile(r"[A-Za-z]+")


def _esc(text: str) -> str:
    return html.escape(text, quote=False)


def _mi(name: str) -> str:
    if name in FUNCS:
        return f'<mi mathvariant="normal">{name}</mi>'
    if len(name) == 1 or name in {"own", "other"}:
        return f"<mi>{name}</mi>"
    return f'<mi mathvariant="normal">{name}</mi>'


def _num(digits: str) -> str:
    return f"<mn>{digits}</mn>"


def tokens(text: str) -> list[str]:
    """把一段纯文本切成 MathML 原子。"""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in " \t\n\u3000":
            if not out or not out[-1].startswith("<mspace"):
                out.append("<mspace width=\"0.17em\"/>")
            i += 1
            continue
        if ch in SUBSCRIPT_DIGITS:
            atom = f"<mn>{SUBSCRIPT_DIGITS[ch]}</mn>"
            if out:
                out.append(f"<msub>{out.pop()}{atom}</msub>")
            else:
                out.append(f"<msub><mrow/>{atom}</msub>")
            i += 1
            continue
        if ch in SUPERSCRIPT:
            atom = f"<mn>{SUPERSCRIPT[ch]}</mn>"
            if out:
                out.append(f"<msup>{out.pop()}{atom}</msup>")
            else:
                out.append(f"<msup><mrow/>{atom}</msup>")
            i += 1
            continue
        if ch == "½":
            out.append("<mfrac><mn>1</mn><mn>2</mn></mfrac>")
            i += 1
            continue
        if ch == "⅓":
            out.append("<mfrac><mn>1</mn><mn>3</mn></mfrac>")
            i += 1
            continue
        if ch.isdigit() or (ch == "." and i + 1 < n and text[i + 1].isdigit()):
            j = i
            while j < n and (text[j].isdigit() or text[j] == "."):
                j += 1
            out.append(_num(text[i:j]))
            i = j
            continue
        if ch in GREEK:
            out.append(f"<mi>{ch}</mi>")
            i += 1
            continue
        m = LATIN_WORD.match(text, i)
        if m:
            out.append(_mi(m.group(0)))
            i = m.end()
            continue
        if ord(ch) > 0x2E80:  # 中日韩、全角标点
            j = i
            while j < n and ord(text[j]) > 0x2E80 and text[j] not in "，。；：！？（）「」『』“”‘’":
                j += 1
            if j == i:
                j = i + 1
            out.append(f"<mtext>{_esc(text[i:j])}</mtext>")
            i = j
            continue
        if ch in OPS:
            out.append(f"<mo>{_esc(ch)}</mo>")
            i += 1
            continue
        if ch == "*":
            if out:
                out.append(f"<msup>{out.pop()}<mo>*</mo></msup>")
            else:
                out.append("<mo>*</mo>")
            i += 1
            continue
        out.append(f"<mtext>{_esc(ch)}</mtext>")
        i += 1
    return out


def _render_inner(inner: str) -> str:
    return "".join(tokens(html.unescape(inner)))


def convert_simple(fragment: str) -> str:
    """两遍法：先处理 <sub>/<sup>（其内一般不含再嵌套），再切原子。"""
    fragment = html.unescape(fragment)
    # 先把 <sub>…</sub> / <sup>…</sup> 换成哨兵，避免被 tokens() 拆散
    holds: list[tuple[str, str]] = []

    def hold(m: re.Match) -> str:
        kind = "sub" if m.group(1) == "sub" else "sup"
        inner = _render_inner(re.sub(r"</?(i|b|em|strong)>", "", m.group(2)))
        inner = f"<mrow>{inner}</mrow>"
        holds.append((kind, inner))
        return f"\x01{len(holds)-1}\x01"

    prev = None
    while prev != fragment:
        prev = fragment
        fragment = re.sub(r"<(sub|sup)>(.*?)</\1>", hold, fragment, flags=re.S)
    fragment = re.sub(r"<(/?)(i|b|em|strong)\b[^>]*>", "", fragment)
    fragment = fragment.replace("<br>", "\n")

    out: list[str] = []
    i = 0
    for m in re.finditer(r"\x01(\d+)\x01", fragment):
        out.extend(tokens(fragment[i:m.start()]))
        out.append(f"\x02{m.group(1)}\x02")
        i = m.end()
    out.extend(tokens(fragment[i:]))

    res: list[str] = []
    for atom in out:
        if atom.startswith("\x02") and atom.endswith("\x02"):
            kind, inner = holds[int(atom[1:-1])]
            wrapper = "msub" if kind == "sub" else "msup"
            if res:
                prev_atom = res.pop()
                res.append(f"<{wrapper}>{prev_atom}{inner}</{wrapper}>")
            else:
                res.append(f"<{wrapper}><mrow/>{inner}</{wrapper}>")
        else:
            res.append(atom)
    return "".join(res)


DISPLAY = re.compile(
    r'<div class="(mblock|eq)">(?:<span class="body">)?(.*?)(?:</span><span class="num">\((.*?)\)</span>)?</div>',
    re.S,
)


def convert_file(path: Path, apply: bool) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    changes: list[tuple[str, str]] = []

    def repl(m: re.Match) -> str:
        cls, body, num = m.group(1), m.group(2), m.group(3)
        if "<math" in body:
            return m.group(0)
        cjk = len(re.findall(r"[\u4e00-\u9fff]", body))
        if cls == "mblock" and (cjk > 10 or "<br>" in body):
            return m.group(0)  # 文字式／流程式：保持原样
        math = convert_simple(body)
        if num is None:
            new = f'<div class="eq"><span class="body"><math display="block">{math}</math></span></div>'
        else:
            new = (f'<div class="eq"><span class="body"><math display="block">{math}</math></span>'
                   f'<span class="num">({num})</span></div>')
        changes.append((body.strip()[:60], new.strip()[:90]))
        return new

    new_text = DISPLAY.sub(repl, text)
    if apply and new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    files = sorted(SRC.glob("*.html"))
    total = 0
    for f in files:
        ch = convert_file(f, apply=args.apply)
        if ch:
            total += len(ch)
            print(f"== {f.name}: {len(ch)}")
            if args.check:
                for a, b in ch:
                    print("  -", a)
                    print("  +", b)
    print(f"total {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
