import pandas as pd
import re
import hashlib
import opencc
from pathlib import Path
from typing import List, Dict


class BaseParser:
    def __init__(self):
        # 繁体转换为简体
        self.converter = opencc.OpenCC("t2s")
        # 统一切分规则
        self.split_pattern = re.compile(r"([^，。！？：；、\s]+)")

    def clean_text(self, text: str) -> str:
        """转换为简体并清理空格"""
        simplified = self.converter.convert(text.strip())
        return simplified

    def split_to_sentences(self, content: str) -> List[str]:
        """
        切分字符串，只留汉字，去掉标点
        """
        content = self.clean_text(content)
        # 提取所有非标点部分的文本
        parts = self.split_pattern.findall(content)
        return [p.strip() for p in parts if p.strip()]

    def generate_id(self, author: str, title: str, content: str) -> str:
        """
        为作品生成 MD5 指纹。
        """
        # 1. 预处理：转简体、去标点
        clean_author = self.clean_text(author)
        clean_title = self.clean_text(title)
        clean_content = re.sub(
            r"[，。！？：；、（）《》〈〉]", "", self.clean_text(content)
        )

        # 2. 拼接特征字符串
        fingerprint = f"{clean_author}{clean_title}{clean_content}"

        # 3. 生成 16 位哈希
        return hashlib.md5(fingerprint.encode("utf-8")).hexdigest()[:16]


class CSVParser(BaseParser):
    """适配 Poetry/*.csv 格式"""

    def parse_file(self, input_path: Path) -> List[Dict]:
        df = pd.read_csv(input_path)
        works, sentences = [], []
        for _, row in df.iterrows():
            title = str(row.get("题目", "题目缺失")) # 标题暂时不能去空格
            dynasty = self.clean_text(str(row.get("朝代", "朝代缺失")))
            author = self.clean_text(str(row.get("作者", "作者缺失")))
            content = str(row.get("内容", "内容缺失"))
            work_id = self.generate_id(author, title, content)

            works.append(
                {
                    "author": author,
                    "title": title,
                    "dynasty": dynasty,
                    "content": content,
                    "source": "Poetry",
                    # "genre": "诗",
                    "work_id": work_id,
                }
            )

            splitted_sentences = self.split_to_sentences(content)
            for sentence in splitted_sentences:
                sentences.append({"sentence": sentence, "work_id": work_id})

        return works, sentences


class JsonParser(BaseParser):
    """适配 chinese-poetry/*.json 格式"""

    def parse_json(self, json_data: List[Dict]) -> List[Dict]:
        works, sentences = [], []
        for entry in json_data:
            author = self.clean_text(entry["author"])
            rhythmic = self.clean_text(entry["rhythmic"])
            content = self.clean_text("".join(entry["paragraphs"]))
            work_id = self.generate_id(author, rhythmic, content)

            works.append(
                {
                    "author": author,
                    "rhythmic": rhythmic,
                    "content": content,
                    "dynasty": "宋",
                    "source": "chinese-poetry",
                    "genre": "词",
                    "work_id": work_id,
                }
            )

            splitted_sentences = self.split_to_sentences(content)
            for sentence in splitted_sentences:
                sentences.append({"sentence": sentence, "work_id": work_id})

        return works, sentences
