import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

with open("王国维.json", "r", encoding="utf-8") as f:
    data = json.load(f)

notes = []
for item in data:
    notes.append(item["content"])

notes_text = "\n".join(notes)
text = "采菊东篱下，悠然见南山"


prompt = f"""
下面是《人间词话》的前若干则：

{notes_text}

现在请你参考这些内容，对下面这首词句做一个简短点评：

{text}

要求：
1. 判断是否存在境界
2. 如果存在境界，是造境还是写境
3. 如果存在境界，是有我之境还是无我之境
4. 如果存在境界，是大的境界还是小的境界
5. 判断是否存在气象
6. 以上判断均要给出理由
7. 分析必须仅依据以上材料中的概念，不要加入材料中没有出现的文学解释。
"""

# print(f"提示词：{prompt}")

response = client.chat.completions.create(
    model="qwen-max", messages=[{"role": "user", "content": prompt}]
)

print("返回结果如下")
print(response.choices[0].message.content)
