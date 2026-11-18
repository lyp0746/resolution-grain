"""破折号削减：批量版（第六十二轮 ch03 试点之后的手工规则的机械化）。

规则（三条，都是 ch03 试点里用过的判断）：
1. **留**：破折号后面的分句很短（≤12 汉字）且以句号类收尾（。！？）。**分号不算**——
   否则同一串并列结构会出现“一边破折号、一边逗号”。这是节拍，是这本书的声音。
2. **留**：破折号后面是转折（而／但／可／却／不过／然而／偏偏／反倒）——转折靠这个符号顶着。
3. **改**：其余一律改掉——
   - 后接定义／说明（这是／这就是／不是／即／也就是／因为／这句话／数字／第一／①…）→ 冒号；
   - 其余 → 逗号。
   同一个块里只留一处（不出现"一段三破折号"）。

不动的：`<div class="box">` 里的（本章主张与一句话带走是装置）；`<pre>`；属性里的。

用法：
    python analysis/trim_dashes.py --dry ch24     # 看前 20 处改了什么样
    python analysis/trim_dashes.py --write        # 全部写回（ch03 已做过，可重跑，幂等）
"""
import re
import sys
import glob
import io

ADV = ("而", "但", "可", "却", "不过", "然而", "偏偏", "反倒")
DEF = ("这是因为", "这是", "这就是", "这正是", "它不是", "这不是", "不是",
       "它就是", "也就是", "即", "换句话说", "这句话", "一句话",
       "第一", "第二", "第三", "①", "②", "③", "④", "⑤", "因为")


def plain(s):
    return re.sub(r"<[^>]+>", "", s)


PAIR = re.compile(r"——([^—。！？；\n]{0,80}?)——")


def fix_pairs(block):
    """成对的破折号（插入语）必须成对处理：一起留或一起改，不能只改一半。

    判据：夹在中间的若是短插入语（≤12 汉字、无句读）→ 保留；否则两头都改成逗号
    （插入语本来就可以用逗号引）。
    """
    def repl(m):
        inner = plain(m.group(1))
        if len(inner) <= 12:
            return "——" + m.group(1) + "——"
        return "，" + m.group(1) + "，"
    return PAIR.sub(repl, block)


def convert_block(block):
    """返回 (新块, 改动数)。块内只留第一处合格破折号。"""
    block = fix_pairs(block)
    # 并列结构（破折号分散在多个“；”段里）必须同进退，否则会出现
    # “缩覆盖，只守……；或者缩精度——把整段糊成一片”这种一边逗号一边破折号。
    segs = block.split("；")
    parallel = sum(1 for x in segs if "——" in x) >= 2
    idx = [m.start() for m in re.finditer("——", block)]
    if not idx:
        return block, 0
    kept = set()
    out = []
    last = 0
    changed = 0
    for i in idx:
        tail = block[i + 2:]
        m = re.match(r"([^。！？\n]{0,40})[。！？]", tail)
        seg = plain(m.group(1)) if m else ""
        nxt = plain(tail)[:1]
        keep = ((len(seg) <= 12) or (nxt in ADV)) and not parallel
        if keep and not kept:
            kept.add(i)
            continue
        # 决定替换符
        head = plain(tail)[:4]
        prev = block[max(0, i - 1):i]
        if head.startswith(DEF) or prev in ("）", "」"):
            rep = "："
        elif nxt in ADV or True:
            rep = "，"
        # 避免标点叠加
        if prev in ("：", "，", "；", "、", "。", "！", "？"):
            rep = ""
        out.append(block[last:i])
        out.append(rep)
        last = i + 2
        changed += 1
    out.append(block[last:])
    return "".join(out), changed


def process(path, write=False, dry=False):
    s = io.open(path, encoding="utf-8").read()
    boxes = {}

    def stash(m):
        k = "\x00BOX%d\x00" % len(boxes)
        boxes[k] = m.group(0)
        return k

    s = re.sub(r'<div class="box[^"]*">.*?</div>', stash, s, flags=re.S)
    total = 0
    samples = []

    def sub(m):
        nonlocal total
        new, ch = convert_block(m.group(0))
        if dry and ch and len(samples) < 20:
            old_pl = plain(m.group(0))
            new_pl = plain(new)
            for a, b in zip(re.findall(r"[^，。：]{0,18}——[^，。：]{0,18}", m.group(0)), []):
                pass
            samples.append((old_pl, new_pl))
        total += ch
        return new

    s = re.sub(r"<p[^>]*>.*?</p>|<li>.*?</li>|<figcaption[^>]*>.*?</figcaption>",
               sub, s, flags=re.S)
    for k, v in boxes.items():
        s = s.replace(k, v)
    if dry:
        for old, new in samples[:8]:
            print("OLD:", old[:120])
            print("NEW:", new[:120])
            print()
    before = io.open(path, encoding="utf-8").read().count("——")
    after = s.count("——")
    print("%-26s —— : %d -> %d (改 %d)" % (path, before, after, total))
    if write:
        io.open(path, "w", encoding="utf-8").write(s)


def main():
    args = sys.argv[1:]
    write = "--write" in args
    dry = "--dry" in args
    files = sorted(glob.glob("source/ch*.html"))
    rest = [a for a in args if a.startswith("ch")]
    if rest:
        files = [f for f in files if any(r in f for r in rest)]
    for f in files:
        process(f, write=write, dry=dry)


if __name__ == "__main__":
    main()
