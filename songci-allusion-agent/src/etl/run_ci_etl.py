import os
import json
import csv
import glob
from pathlib import Path
from tqdm import tqdm
from src.ci_parser import CiJSONParser


def run_ci_pipeline():
    # 1. 动态定位根目录 (保证在任何地方执行 python -m 都能对齐)
    # __file__ 是 run_ci_etl.py, parent 是 etl/, parent.parent 是 src/, 再 parent 是根目录
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # 2. 拼接绝对路径
    # 先测试单文件，成功后只需把 "ci.song.0.json" 改回 "ci.song.*.json"
    input_pattern = str(
        BASE_DIR / "raw_data" / "chinese-poetry" / "宋词" / "ci.song.*.json"
    )
    output_file = str(BASE_DIR / "data" / "quansongci_sentences.csv")

    # 3. 自动创建输出目录
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    parser = CiJSONParser()

    # glob 会返回绝对路径列表
    raw_files = glob.glob(input_pattern)

    if not raw_files:
        print(f"❌ 错误：在路径下找不到文件！\n检测路径为: {input_pattern}")
        return

    print(f"✅ 找到 {len(raw_files)} 个文件，准备转换...")

    fieldnames = [
        "content",
        "author",
        "title",
        "genre",
        "punc",
        "parent_id",
        "line_idx",
    ]

    count = 0
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        writer.writeheader()

        for file_path in tqdm(raw_files, desc="解析全宋词"):
            try:
                # 这里的 file_path 现在是绝对路径， open 一定能找到
                with open(file_path, "r", encoding="utf-8") as f_json:
                    data = json.load(f_json)
                    for entry in data:
                        atoms = parser.parse_entry(entry)
                        for atom in atoms:
                            writer.writerow(
                                {
                                    "content": atom["content"],
                                    "author": atom["author"],
                                    "title": atom["title"],
                                    "genre": atom["genre"],
                                    "punc": atom["meta"]["punc"],
                                    "parent_id": atom["meta"]["parent_id"],
                                    "line_idx": atom["meta"]["line_idx"],
                                }
                            )
                            count += 1
            except Exception as e:
                print(f"\n❌ 处理文件 {file_path} 时出错: {e}")

    print("\n✨ 转换完成！")
    print(f"📊 生成原子句: {count} 条")
    print(f"📂 结果保存至: {output_file}")


if __name__ == "__main__":
    run_ci_pipeline()
