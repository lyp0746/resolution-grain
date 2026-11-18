"""排版密度的两个读数：加粗与破折号。

本轮（第六十二轮）用它做了两件事：
1. `--bold`：按一条固定规则削减 <b>（见下），全 28 章已跑过一遍。
2. `--report`：报每章的 加粗/破折号 密度，找出还需要手改的章。

规则（为什么这样削）：
- 加粗是"一句硬话"的装置，不是关键词高亮。全书的密度一度是 1/47 字（每 47 字一次加粗），
  读者的眼睛会把它当底色，于是"硬话"不再硬。
- 保留三类：① 每段至多一处、且是整句（≥8 字、以 。？！ 结尾）；② 短标签（≤9 字，以 ：。 结尾），
  如"断言：""来源："；③ `div class="box"` 里的全部（那是"本章主张"与"一句话带走"，是装置不是行文）。
- 其余一律去掉：行文里的关键词高亮、列表项里的议题词、句中强调。信息不丢（字一个都没动），只丢视觉重音。

破折号没有自动规则：哪一处换成逗号、哪一处换成冒号、哪一处该留，是语感判断。
`--report` 只给密度与最密的前几章，改由人做（第六十二轮只改了 ch03 一章作试点）。

用法：
    python analysis/restyle.py --report
    python analysis/restyle.py --bold --write        # 就地削 <b>（建议先 git diff）
"""
import re
import sys
import glob
import io

TARGET_BOLD = 150     # 目标：每 150 字至多一次加粗
TARGET_DASH = 300     # 目标：每 300 字至多一个破折号


def cn(s):
    return len(re.findall(r"[\u4e00-\u9fff]", re.sub(r"<[^>]+>", "", s)))


def _strip_b(inner, allow_one=False):
    kept = [0]

    def repl(m):
        t = m.group(1)
        plain = re.sub(r"<[^>]+>", "", t).strip()
        label = len(plain) <= 9 and plain.endswith(("：", "。"))
        if label or (allow_one and kept[0] == 0 and len(plain) >= 8
                     and plain.endswith(("。", "？", "！"))):
            if not label:
                kept[0] += 1
            return "<b>" + t + "</b>"
        return t

    return re.sub(r"<b>(.*?)</b>", repl, inner, flags=re.S)


def cut_bold(s):
    boxes = {}

    def keep_box(m):
        k = "\x00BOX%d\x00" % len(boxes)
        boxes[k] = m.group(0)
        return k

    s = re.sub(r'<div class="box[^"]*">.*?</div>', keep_box, s, flags=re.S)
    s = re.sub(r"<p>(.*?)</p>", lambda m: "<p>" + _strip_b(m.group(1), True) + "</p>", s, flags=re.S)
    s = re.sub(r"<li>(.*?)</li>", lambda m: "<li>" + _strip_b(m.group(1), False) + "</li>", s, flags=re.S)
    for k, v in boxes.items():
        s = s.replace(k, v)
    return s


def report(files):
    rows = []
    for f in files:
        s = io.open(f, encoding="utf-8").read()
        n = cn(s)
        b = len(re.findall("<b>", s))
        d = s.count("——")
        rows.append((f, n, b, d, n / max(b, 1), n / max(d, 1)))
    T = sum(r[1] for r in rows)
    B = sum(r[2] for r in rows)
    D = sum(r[3] for r in rows)
    print("全书 字 %d：加粗 %d（1/%.0f，目标 1/%d）／破折号 %d（1/%.0f，目标 1/%d）"
          % (T, B, T / B, TARGET_BOLD, D, T / D, TARGET_DASH))
    print("\n加粗最密（需要再削）：")
    for r in sorted(rows, key=lambda x: x[4])[:6]:
        print("  %-24s 字 %5d 粗 %4d 1/%.0f" % (r[0], r[1], r[2], r[4]))
    print("\n破折号最密（需要手改）：")
    for r in sorted(rows, key=lambda x: x[5])[:8]:
        print("  %-24s 字 %5d 号 %4d 1/%.0f" % (r[0], r[1], r[3], r[5]))


def main():
    args = sys.argv[1:]
    files = sorted(glob.glob("source/ch*.html"))
    if not args or "--report" in args:
        report(sorted(glob.glob("source/*.html")))   # 报全书：正文＋附录＋前置后置
        return
    if "--bold" in args:
        write = "--write" in args
        for f in files:
            s = io.open(f, encoding="utf-8").read()
            b0 = len(re.findall("<b>", s))
            new = cut_bold(s)
            b1 = len(re.findall("<b>", new))
            if write:
                io.open(f, "w", encoding="utf-8").write(new)
            print("%s %d -> %d" % (f, b0, b1))


if __name__ == "__main__":
    main()
