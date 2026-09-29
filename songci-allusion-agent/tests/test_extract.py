# test_extract.py
from openai import OpenAI
from src.schema import AgentState
from src.skills import extract_allusions
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

state: AgentState = {
    "input_text": "新样靓妆，艳溢香融，羞杀蕊珠宫女。",
    "extracted_allusions": [],
    "validation_results": [],
    "final_report": None,
    "error": None,
}

result = extract_allusions(state, client)

print(f"错误：{result['error']}")
print(f"找到典故数：{len(result['extracted_allusions'])}")
for a in result["extracted_allusions"]:
    print(f"\n【{a['phrase']}】{a['source']}")
    print(f"  {a['original'][:50]}...")
