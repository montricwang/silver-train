import json
from openai import OpenAI
from schema import AgentState, Allusion

SYSTEM_PROMPT = """你是一位精通中国古典文学的学者，专门研究诗词用典。
用户会输入一句或一首宋词，请找出其中可能涉及的典故，并以JSON格式返回。

返回格式如下，只返回JSON，不要有任何其他文字：
[
  {
    "phrase": "词中的典故词语",
    "source": "出处（书名或作者作品）",
    "original": "原文相关句子",
    "confidence": "high/medium/low"
  }
]

如果没有找到典故，返回空数组：[]"""


def extract_allusions(input_text: str, client: OpenAI) -> AgentState:
    """
    调用LLM从输入词文中抽取典故。
    """
    response = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": input_text},
        ],
        temperature=0.3,
    )
    raw = response.choices[0].message.content
    extracted: list[Allusion] = json.loads(raw)

    return {"extracted_allusions": extracted, "error": None}
