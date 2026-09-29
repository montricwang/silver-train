# build_dataset.py
import json
import pandas as pd
from pathlib import Path
from src.utils.parsers import CSVParser, JsonParser
from src.utils.config import RAW_DATA_DIR, DATA_DIR


def main():
    # 1. 初始化收集器
    all_works = []
    all_sentences = []

    # 2. 加载 Parser
    csv_parser = CSVParser()
    json_parser = JsonParser()

    # 3. 批量处理唐诗 (CSV)

    for csv_file in Path(RAW_DATA_DIR / "Poetry").glob("唐.csv"):
        works, sents = csv_parser.parse_file(csv_file)
        all_works.extend(works)
        all_sentences.extend(sents)

    # 4. 批量处理宋词 (JSON)
    for json_file in Path(RAW_DATA_DIR / "chinese-poetry" / "宋词").glob(
        "ci.song.*.json"
    ):
        with open(json_file, encoding="utf-8") as f:
            works, sents = json_parser.parse_json(json.load(f))
            all_works.extend(works)
            all_sentences.extend(sents)

    # 5. 【核心治理逻辑】—— 放在这里！
    df_works = pd.DataFrame(all_works).drop_duplicates(subset=["work_id"])
    df_sents = pd.DataFrame(all_sentences)

    # 生成全局连续 ID，这是为了 FAISS 准备的
    df_sents = df_sents.reset_index().rename(columns={"index": "global_id"})

    # 6. 持久化
    df_works.to_csv(DATA_DIR / "unified_works.csv", index=False)
    df_sents.to_csv(DATA_DIR / "unified_sentences.csv", index=False)
    print("语料库合并完成！")


if __name__ == "__main__":
    main()
