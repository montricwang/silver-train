import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-fef335f3ddcd4adbae61d85c033facc7", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

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

# TEST_INPUT = "纵有魏珠照乘，未买得、流年住。争如盛饮流霞，醉偎琼树。"
# TEST_INPUT = "念往昔，繁华竞逐，叹门外楼头，悲恨相续。"
TEST_INPUT = "登临送目。正故国晚秋，天气初肃。千里澄江似练，翠峰如簇。征帆去棹残阳里，背西风酒旗斜矗。彩舟云淡，星河鹭起，画图难足。念往昔，繁华竞逐，叹门外楼头，悲恨相续。千古凭高对此，谩嗟荣辱。六朝旧事随流水，但寒烟衰草凝绿。至今商女，时时犹唱，后庭遗曲。"

response = client.chat.completions.create(
    model="qwen-max",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": TEST_INPUT},
    ],
    temperature=0.0,
)

raw = response.choices[0].message.content
print("原始返回：")
print(raw)


try:
    result = json.loads(raw)
    print("\n解析成功，找到典故：")
    for item in result:
        print(f"\n【{item['phrase']}】")
        print(f"  出处：{item['source']}")
        print(f"  原文：{item['original']}")
        print(f"  置信度：{item['confidence']}")
except json.JSONDecodeError:
    print("\nJSON解析失败，需要调整prompt")
