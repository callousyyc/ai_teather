"""在知识库里按关键词找页面。

用法:
    python tools/search.py <关键词> [关键词 ...] [--book pe6] [--top 8]

按命中关键词种类数、再按命中次数排序, 打印页码和上下文片段。
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("terms", nargs="+")
    ap.add_argument("--book", default="")
    ap.add_argument("--top", type=int, default=8)
    args = ap.parse_args()

    books = [ROOT / "kb" / args.book] if args.book else sorted(p for p in (ROOT / "kb").iterdir() if p.is_dir())
    hits = []
    for book in books:
        for f in (book / "pages").glob("p*.txt"):
            text = f.read_text(encoding="utf-8")
            flat = re.sub(r"\s+", "", text)
            counts = [flat.count(t) for t in args.terms]
            kinds = sum(1 for c in counts if c)
            if kinds:
                hits.append((kinds, sum(counts), book.name, int(f.stem[1:]), flat))

    hits.sort(key=lambda h: (-h[0], -h[1], h[3]))
    for kinds, total, name, page, flat in hits[: args.top]:
        term = next(t for t in args.terms if t in flat)
        k = flat.index(term)
        snippet = flat[max(0, k - 40): k + 60]
        print(f"[{name} p{page}] 命中 {kinds}/{len(args.terms)} 词 {total} 次  …{snippet}…")
        print(f"    图片: kb/{name}/pages/p{page:04d}.jpg")
    if not hits:
        print("没有找到。试试同义词或更短的关键词。")


if __name__ == "__main__":
    main()
