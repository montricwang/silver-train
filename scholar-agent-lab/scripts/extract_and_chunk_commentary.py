from __future__ import annotations

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup


RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
RESULTS_DIR = Path("results")

OUTPUT_JSONL = OUTPUT_DIR / "commentary_chunks_v1.jsonl"
STATS_JSON = RESULTS_DIR / "commentary_chunk_stats_v1.json"

HTML_SUFFIXES = {".html", ".xhtml", ".htm"}

# 第一版先用最朴素的固定字数切块
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80

CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
WHITESPACE_RE = re.compile(r"\s+")


def extract_text_from_html(path: Path) -> str:
    """从 html/xhtml 中抽纯文本。"""
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    # 去掉无关标签
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # 行清洗：去空行、压缩空白
    lines = []
    for line in text.splitlines():
        line = WHITESPACE_RE.sub(" ", line).strip()
        if line:
            lines.append(line)

    return "\n".join(lines)


def count_chinese(text: str) -> int:
    return len(CHINESE_RE.findall(text))


def split_into_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    """按固定字数切块。第一版先按字符切，不做复杂语义切分。"""
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


def get_book_name(file_path: Path) -> str:
    """
    假设文件路径像：
    data/raw/人间词话讲疏/OEBPS/Text/Section0001.xhtml
    那么 book_name = 人间词话讲疏
    """
    relative = file_path.relative_to(RAW_DIR)
    return relative.parts[0]


def build_chunk_records() -> tuple[list[dict], dict]:
    all_records = []

    file_count = 0
    total_text_chars = 0
    total_chinese_chars = 0
    total_chunks = 0

    per_book_stats: dict[str, dict] = {}

    for path in RAW_DIR.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in HTML_SUFFIXES:
            continue

        try:
            text = extract_text_from_html(path)
        except Exception as e:
            print(f"[跳过] 读取失败: {path} | {e}")
            continue

        chinese_count = count_chinese(text)

        # 过滤掉几乎没有正文的文件，比如目录页、版权页等
        if chinese_count < 50:
            continue

        book_name = get_book_name(path)
        chunks = split_into_chunks(text, CHUNK_SIZE, CHUNK_OVERLAP)

        if book_name not in per_book_stats:
            per_book_stats[book_name] = {
                "file_count": 0,
                "text_chars": 0,
                "chinese_chars": 0,
                "chunk_count": 0,
            }

        file_count += 1
        total_text_chars += len(text)
        total_chinese_chars += chinese_count
        total_chunks += len(chunks)

        per_book_stats[book_name]["file_count"] += 1
        per_book_stats[book_name]["text_chars"] += len(text)
        per_book_stats[book_name]["chinese_chars"] += chinese_count
        per_book_stats[book_name]["chunk_count"] += len(chunks)

        for idx, chunk_text in enumerate(chunks):
            record = {
                "chunk_id": f"{book_name}_{path.stem}_{idx}",
                "book": book_name,
                "file": str(path.relative_to(RAW_DIR)),
                "chunk_index": idx,
                "text": chunk_text,
            }
            all_records.append(record)

    stats = {
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "total_files": file_count,
        "total_text_chars": total_text_chars,
        "total_chinese_chars": total_chinese_chars,
        "total_chunks": total_chunks,
        "per_book": per_book_stats,
    }

    return all_records, stats


def save_jsonl(records: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def save_stats(stats: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"未找到目录：{RAW_DIR}")

    records, stats = build_chunk_records()

    save_jsonl(records, OUTPUT_JSONL)
    save_stats(stats, STATS_JSON)

    print("=" * 60)
    print("抽取与切块完成")
    print("=" * 60)
    print(f"输出 chunk 文件: {OUTPUT_JSONL}")
    print(f"输出统计文件: {STATS_JSON}")
    print(f"有效文件数: {stats['total_files']}")
    print(f"总字符数: {stats['total_text_chars']}")
    print(f"总汉字数: {stats['total_chinese_chars']}")
    print(f"总 chunk 数: {stats['total_chunks']}")
    print("\n分书统计：")
    for book, info in stats["per_book"].items():
        print(
            f"- {book}: "
            f"files={info['file_count']}, "
            f"chinese={info['chinese_chars']}, "
            f"chunks={info['chunk_count']}"
        )


if __name__ == "__main__":
    main()
