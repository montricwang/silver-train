# scripts/inspect_epub_html.py
from __future__ import annotations

from pathlib import Path
from bs4 import BeautifulSoup
import json
import re


RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("results/raw_html_stats.json")

HTML_SUFFIXES = {".html", ".xhtml", ".htm"}
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")


def extract_text_from_html(path: Path) -> str:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    # 去掉脚本和样式
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # 压缩空白
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def count_chinese_chars(text: str) -> int:
    return len(CHINESE_RE.findall(text))


def main() -> None:
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"目录不存在: {RAW_DIR}")

    stats = []
    total_files = 0
    total_chars = 0
    total_chinese = 0

    for path in RAW_DIR.rglob("*"):
        if path.is_file() and path.suffix.lower() in HTML_SUFFIXES:
            try:
                text = extract_text_from_html(path)
            except Exception as e:
                stats.append(
                    {
                        "file": str(path),
                        "error": str(e),
                    }
                )
                continue

            char_count = len(text)
            chinese_count = count_chinese_chars(text)

            stats.append(
                {
                    "file": str(path),
                    "char_count": char_count,
                    "chinese_count": chinese_count,
                    "preview": text[:120],
                }
            )

            total_files += 1
            total_chars += char_count
            total_chinese += chinese_count

    summary = {
        "total_files": total_files,
        "total_chars": total_chars,
        "total_chinese": total_chinese,
        "files": stats,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"HTML/XHTML 文件数: {total_files}")
    print(f"总字符数: {total_chars}")
    print(f"总汉字数: {total_chinese}")
    print(f"结果已保存到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
