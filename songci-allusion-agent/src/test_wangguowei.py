# test_wangguowei.py
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen-max")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ========= 路径 =========
SKILL_PATH = Path("skills/wang_guowei/skills.md")
SCHEMA_PATH = Path("skills/wang_guowei/schema.json")

# ========= 测试输入 =========
INPUT_TEXT = "寂寞亭基野渡边，春流平岸草芊芊。一川晚照人闲立，满袖杨花听杜鹃"
TITLE = "溪桥晚兴"
AUTHOR = "郑协"


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def load_json_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def extract_json(text: str) -> dict:
    text = text.strip()

    # 兼容 ```json ... ``` 这种返回
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and start < end:
            candidate = text[start : end + 1]
            return json.loads(candidate)
        raise


def validate_result(result: dict, schema: dict) -> list[str]:
    """
    这里做一个最小手工校验，避免你还要额外装 jsonschema。
    """
    errors = []

    required_fields = schema.get("required", [])
    properties = schema.get("properties", {})

    for field in required_fields:
        if field not in result:
            errors.append(f"缺少必填字段: {field}")

    if errors:
        return errors

    for field, rule in properties.items():
        if field not in result:
            continue

        value = result[field]
        field_type = rule.get("type")

        if field_type == "boolean" and not isinstance(value, bool):
            errors.append(f"{field} 应为 boolean，实际为 {type(value).__name__}")

        elif field_type == "string" and not isinstance(value, str):
            errors.append(f"{field} 应为 string，实际为 {type(value).__name__}")

        elif field_type == "number" and not isinstance(value, (int, float)):
            errors.append(f"{field} 应为 number，实际为 {type(value).__name__}")

        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{field} 不在允许枚举中: {value}")

        if field_type == "number":
            if "minimum" in rule and value < rule["minimum"]:
                errors.append(f"{field} 小于最小值 {rule['minimum']}")
            if "maximum" in rule and value > rule["maximum"]:
                errors.append(f"{field} 大于最大值 {rule['maximum']}")

    return errors


def build_messages(skill_text: str, schema: dict, title: str, author: str, text: str):
    system_prompt = (
        "你是一个严格遵循技能说明的诗词分析助手。\n"
        "你必须根据提供的 skill 文档进行分析，并严格按照 schema 返回 JSON。\n"
        "不要输出 markdown，不要输出代码块，不要附加任何解释。"
    )

    user_prompt = f"""
以下是技能说明（skill）：

{skill_text}

以下是输出 schema：

{json.dumps(schema, ensure_ascii=False, indent=2)}

现在请分析下面这首词：

title: {title}
author: {author}
text: {text}

只返回一个 JSON 对象。
""".strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def main():
    print("=" * 80)
    print(f"【0】待赏析内容\n原文：{INPUT_TEXT}\n题目：{TITLE}\n作者：{AUTHOR}")
    print("=" * 80)
    print("=" * 80)
    print("【1】读取 skill 与 schema")
    print("=" * 80)

    try:
        skill_text = load_text_file(SKILL_PATH)
        schema = load_json_file(SCHEMA_PATH)
    except Exception as e:
        print(f"读取文件失败：{e}")
        return

    print(f"Skill 文件：{SKILL_PATH}")
    print(f"Schema 文件：{SCHEMA_PATH}")
    print("读取成功。")

    print("\n" + "=" * 80)
    print("【2】发送模型请求")
    print("=" * 80)

    messages = build_messages(
        skill_text=skill_text,
        schema=schema,
        title=TITLE,
        author=AUTHOR,
        text=INPUT_TEXT,
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.2,
            messages=messages,
        )
        raw_output = response.choices[0].message.content or ""
    except Exception as e:
        print(f"模型调用失败：{e}")
        return

    print("模型原始返回：")
    print("-" * 80)
    print(raw_output)
    print("-" * 80)

    print("\n" + "=" * 80)
    print("【3】解析 JSON")
    print("=" * 80)

    try:
        parsed = extract_json(raw_output)
    except Exception as e:
        print(f"JSON 解析失败：{e}")
        return

    print("JSON 解析成功。")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)
    print("【4】Schema 校验")
    print("=" * 80)

    errors = validate_result(parsed, schema)
    if errors:
        print("校验失败：")
        for err in errors:
            print(f"- {err}")
        return

    print("Schema 校验通过。")

    print("\n" + "=" * 80)
    print("【5】结果摘要")
    print("=" * 80)

    print(f"是否有境界：{parsed.get('has_jingjie')}")
    print(f"境界类型：{parsed.get('realm_type')}")
    print(f"造境/写境：{parsed.get('creation_mode')}")
    print(f"不隔程度：{parsed.get('transparency')}")
    print(f"真切程度：{parsed.get('sincerity')}")
    print(f"分析说明：{parsed.get('explanation')}")

    print("\n测试完成。")


if __name__ == "__main__":
    main()
