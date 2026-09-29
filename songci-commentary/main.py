import os
import json
import argparse
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()
PROJECT_ROOT = Path(__file__).parent

SKILL_MAP = {
    "imagery": "skills/imagery_analysis/SKILL.md",
    "spacetime": "skills/spatiotemporal_analysis/SKILL.md",
    "composition": "skills/composition_method/SKILL.md",
    # "synthesis": "skills/synthesis_commentary/SKILL.md",
}


def load_text(path):
    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{path}")
    return path.read_text(encoding="utf-8")


@traceable(name="build_prompt")
def build_prompt(skill_text, poem_text):
    system_prompt = f"""你是一个宋词分析系统。你需要严格按照下面的 SKILL.md 执行任务。
        注意：
        1. 优先遵守 SKILL.md 中的分析范围、步骤和输出格式。
        2. 不要输出 SKILL.md 要求之外的解释。
        3. 如果 SKILL.md 要求 JSON 输出，则只输出合法 JSON，不要在 JSON 外添加说明文字。

        下面是 SKILL.md 内容：
        {skill_text}
        """
    user_prompt = f"""请分析下面这首词：
        {poem_text}
        """

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


@traceable(name="call_llm")
def call_llm(messages):

    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL")
    model_name = os.getenv("DEEPSEEK_MODEL_NAME")

    if not api_key:
        raise RuntimeError("缺少 API_KEY，请检查 .env")
    if not base_url:
        raise RuntimeError("缺少 BASE_URL，请检查 .env")
    if not model_name:
        raise RuntimeError("缺少 MODEL_NAME，请检查 .env")

    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        # 不同 skill 可以尝试不同温度
        # 意象 skill 用 temperature=0（提取性任务）
        # 时空 skill 用 temperature=0（标注性任务）
        # 章法 skill 用 temperature=0.3 或 0.5（综合判断任务）
        temperature=0,
    )

    return response.choices[0].message.content


def save_output(skill_name, input_path, content):
    out_dir = PROJECT_ROOT / "outputs" / "skill_tests"
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = input_path.stem
    save_path = out_dir / f"{stem}_{skill_name}.json"

    try:
        if skill_name != "synthesis":
            data = json.loads(content)
            save_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        else:
            # synthesis 技能通常返回的是 Markdown 文本，无需 JSON 序列化
            # 直接将原始 content 写入文件即可
            # 确保 save_path 的后缀在传入前已经处理为 .md
            save_path.write_text(content, encoding="utf-8")
        return save_path
    except json.JSONDecodeError as e:
        raw_save_path = save_path.with_suffix(".raw.txt")
        raw_save_path.write_text(content, encoding="utf-8")
        raise ValueError(
            f"模型输出格式错误，原始输出已保存到 {raw_save_path} 。错误：{e.msg}"
        ) from e


@traceable(name="run_one_skill")
def run_one_skill(skill_name: str, input_file_name: str):
    if skill_name not in SKILL_MAP:
        raise KeyError(f"未知 skill: {skill_name}，可选: {list(SKILL_MAP.keys())}")

    skill_path = PROJECT_ROOT / SKILL_MAP[skill_name]
    input_path = PROJECT_ROOT / "inputs" / f"{input_file_name}.txt"

    if Path(f"outputs/skill_tests/{input_file_name}_{skill_name}.json").exists():
        print(f"文件 {input_file_name}_{skill_name}.json 已存在，不再调用大模型生成")
        return {
            "skill_name": skill_name,
            "input_file": input_path,
            "output_path": f"outputs/skill_tests/{input_file_name}_{skill_name}.json",
        }

    skill_text = load_text(skill_path)
    poem_text = load_text(input_path)

    print(f"开始调用 skill： {skill_name}")
    result = call_llm(messages=build_prompt(skill_text, poem_text))

    output_path = save_output(skill_name, input_path, result)
    print(f"{skill_name} 输出已保存到: {output_path}")

    return {
        "skill_name": skill_name,
        "input_file": input_path,
        "output_path": str(output_path),
    }


@traceable(name="run_synthesis")
def run_synthesis(input_file_name: str):
    input_path = PROJECT_ROOT / "inputs" / f"{input_file_name}.txt"
    poem_text = load_text(input_path)
    base_dir = PROJECT_ROOT / "outputs" / "skill_tests"

    def load_json(dimension: str):
        path = base_dir / f"{input_file_name}_{dimension}.json"
        if not path.exists():
            raise FileNotFoundError(
                "缺少 {dimension} 结果，请先运行该 skill 生成相应 json 文件"
            )
        return json.loads(path.read_text(encoding="utf-8"))

    imagery_text = json.dumps(
        obj=load_json("imagery"),
        ensure_ascii=False,
        indent=2,
    )
    spacetime_text = json.dumps(
        obj=load_json("spacetime"),
        ensure_ascii=False,
        indent=2,
    )
    composition_text = json.dumps(
        obj=load_json("composition"),
        ensure_ascii=False,
        indent=2,
    )

    skill_path = PROJECT_ROOT / "skills" / "synthesis_commentary" / "SKILL.md"
    system_prompt = load_text(skill_path)

    user_prompt = f"""
        原词如下：
        {poem_text}

        意象分析：
        {imagery_text}

        时空分析：
        {spacetime_text}

        章法分析：
        {composition_text}

        请基于以上信息写一篇完整赏析。
        """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    result = call_llm(messages=messages)

    out_dir = PROJECT_ROOT / "outputs" / "skill_tests"
    out_dir.mkdir(parents=True, exist_ok=True)

    save_path = out_dir / f"{input_file_name}_synthesis.md"
    save_path.write_text(result, encoding="utf-8")
    print(f"synthesis 输出已保存到: {save_path}")

    return save_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skill",
        required=True,
        choices=["imagery", "spacetime", "composition", "all"],
        help="要运行的 skill",
    )
    parser.add_argument(
        "--synthesize",
        action="store_true",
        help="是否生成综合赏析",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="输入词作文件名称，例如 genglouzi",
    )

    args = parser.parse_args()

    if args.skill == "all":
        for skill_name in SKILL_MAP:
            if skill_name != "synthesis":
                run_one_skill(skill_name, args.input)
        if args.synthesize is True:
            run_synthesis(args.input)
    else:
        run_one_skill(args.skill, args.input)


if __name__ == "__main__":
    main()
