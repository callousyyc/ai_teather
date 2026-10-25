"""把教材 PDF 解析成 AI 老师用的知识库。

用法:
    python tools/ingest.py <book.pdf> [--name pe6] [--start 1] [--end N] [--dpi 150]

输出 (kb/<name>/):
    pages/p0001.jpg   每页图片 (讲课时看原图核对公式和电路图)
    pages/p0001.txt   每页 OCR 文字 (用于检索)
    book.md           全书文字, 每页以 "<!-- page N -->" 分隔
    meta.json         书名、页数、PDF 自带书签

可重复运行: 已经 OCR 过的页面会跳过, 中断后再跑会接着做。
"""
import argparse
import json
import sys
import time
from pathlib import Path

import pymupdf as fitz
from rapidocr_onnxruntime import RapidOCR

ROOT = Path(__file__).resolve().parent.parent


def boxes_to_text(result):
    """把 OCR 文本框按阅读顺序拼成行: 先按纵坐标分行, 行内按横坐标排序。"""
    if not result:
        return ""
    items = []
    for box, text, _score in result:
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        items.append((min(ys), max(ys), min(xs), text))
    items.sort(key=lambda t: (t[0] + t[1]) / 2)

    lines, cur, cur_bottom = [], [], None
    for top, bottom, left, text in items:
        center = (top + bottom) / 2
        if cur and center > cur_bottom:
            lines.append(cur)
            cur = []
        if not cur:
            cur_bottom = bottom
        cur.append((left, text))
        cur_bottom = max(cur_bottom, (top + bottom) / 2 + (bottom - top) * 0.3)
    if cur:
        lines.append(cur)
    return "\n".join(" ".join(t for _, t in sorted(line)) for line in lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--name", default="book")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=0)
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    out = ROOT / "kb" / args.name
    pages_dir = out / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(args.pdf)
    if doc.needs_pass or not doc.is_pdf:
        sys.exit("无法打开: 文件被加密或不是 PDF (企业加密的文件请先用授权阅读器导出未加密副本)")
    n = doc.page_count
    end = min(args.end or n, n)

    meta = {
        "source": str(Path(args.pdf).name),
        "pages": n,
        "outline": [{"level": lv, "title": t, "page": p} for lv, t, p in doc.get_toc()],
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    ocr = RapidOCR()
    t0 = time.time()
    for i in range(args.start, end + 1):
        txt_path = pages_dir / f"p{i:04d}.txt"
        if txt_path.exists():
            continue
        page = doc[i - 1]
        img_path = pages_dir / f"p{i:04d}.jpg"
        page.get_pixmap(dpi=args.dpi).save(img_path, jpg_quality=80)

        text = page.get_text().strip()  # 有文字层就直接用
        if len(text) < 20:
            result, _ = ocr(str(img_path))
            text = boxes_to_text(result)
        txt_path.write_text(text, encoding="utf-8")
        done = i - args.start + 1
        eta = (time.time() - t0) / done * (end - i)
        print(f"page {i}/{end}  {len(text)} chars  eta {eta/60:.1f} min", flush=True)

    parts = []
    for p in sorted(pages_dir.glob("p*.txt")):
        parts.append(f"<!-- page {int(p.stem[1:])} -->\n{p.read_text(encoding='utf-8')}")
    (out / "book.md").write_text("\n\n".join(parts), encoding="utf-8")
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
