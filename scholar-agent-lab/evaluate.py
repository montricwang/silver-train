import json
import os
import sys
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv


# =========================
# 1. 读取环境变量
# =========================
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

if not API_KEY:
    raise ValueError("没有读取到 API_KEY，请检查 .env 文件。")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# =========================
# 2. 基本配置
# =========================
MODEL_NAME = "qwen-max"
NOTES_FILE = "王国维.json"

# 用法：
# python evaluate.py renjian_cihua_eval_v1_core.json
# python evaluate.py renjian_cihua_eval_v1_extend.json
if len(sys.argv) > 1:
    EVAL_FILE = sys.argv[1]
else:
    EVAL_FILE = "renjian_cihua_eval_v1_core.json"


# =========================
# 3. 读取《人间词话》知识上下文
# =========================
def load_notes_text(notes_file: str) -> str:
    with open(notes_file, "r", encoding="utf-8") as f:
        notes_data = json.load(f)

    notes = []
    for item in notes_data:
        # 兼容你当前的两种字段命名习惯
        if "content" in item:
            notes.append(item["content"])
        elif "text" in item:
            notes.append(item["text"])

    return "\n".join(notes)


# =========================
# 4. 读取评测集
# =========================
def load_eval_data(eval_file: str):
    with open(eval_file, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 5. 统一老格式 / 新格式
# =========================
def normalize_item(item: dict) -> dict:
    """
    统一成：
    {
        "id": ...,
        "text": ...,
        "task": ...,
        "gold": ...,
        "source": ...,
        "confidence": ...
    }
    """

    # 新格式：已经有 task / gold
    if "task" in item and "gold" in item:
        return {
            "id": item["id"],
            "text": item["text"],
            "task": item["task"],
            "gold": item["gold"],
            "source": item.get("source", ""),
            "confidence": item.get("confidence", None),
        }

    # 老格式：labels 里只有一个键值对
    if "labels" in item:
        labels = item["labels"]
        task = list(labels.keys())[0]
        gold = labels[task]
        return {
            "id": item["id"],
            "text": item["text"],
            "task": task,
            "gold": gold,
            "source": item.get("source", ""),
            "confidence": None,
        }

    raise ValueError(f"无法识别的数据格式: {item}")


# =========================
# 6. 构建 prompt
# =========================
def build_prompt(notes_text: str, text: str, task: str) -> str:
    if task == "type":
        question = """
请判断这句诗词属于“有我”还是“无我”。

只能返回下面两个词中的一个：
有我
无我
""".strip()

    elif task == "scale":
        question = """
请判断这句诗词属于“大”还是“小”的境界。

只能返回下面两个词中的一个：
大
小
""".strip()

    elif task == "气象":
        question = """
请判断这句诗词是否体现“气象”。

只能返回下面两个词中的一个：
有
无
""".strip()

    elif task == "ge_buge":
        question = """
请判断这句诗词属于“隔”还是“不隔”。

只能返回下面两个词中的一个：
隔
不隔
""".strip()

    else:
        question = """
请根据参考材料进行判断，只返回一个最合适的标签。
""".strip()

    prompt = f"""
下面是《人间词话》的原文：

{notes_text}

现在分析这句诗词：

{text}

要求：
1. 只能依据上面的材料来判断
2. 不要解释
3. 不要输出句子
4. 只返回一个词

{question}
""".strip()

    return prompt


# =========================
# 7. 调模型预测
# =========================
def predict_label(notes_text: str, text: str, task: str) -> str:
    prompt = build_prompt(notes_text, text, task)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    result = response.choices[0].message.content.strip()
    return normalize_prediction(result)


def normalize_prediction(pred: str) -> str:
    """
    做最轻量的清洗。
    防止模型返回：
    - 有我。
    - 这句属于无我
    """
    pred = pred.replace("。", "").replace("，", "").replace("：", "").strip()

    candidates = ["有我", "无我", "大", "小", "有", "无", "隔", "不隔"]
    for c in candidates:
        if pred == c:
            return c

    # 如果模型多说了一点话，就尝试包含匹配
    for c in candidates:
        if c in pred:
            return c

    return pred


# =========================
# 8. 运行评测
# =========================
def run_evaluation(notes_text: str, eval_data: list) -> dict:
    total_count = 0
    correct_count = 0
    stats = {}
    errors = []

    for raw_item in eval_data:
        item = normalize_item(raw_item)

        sample_id = item["id"]
        text = item["text"]
        task = item["task"]
        gold = item["gold"]

        pred = predict_label(notes_text, text, task)
        is_correct = pred == gold

        total_count += 1
        if is_correct:
            correct_count += 1

        if task not in stats:
            stats[task] = {"total": 0, "correct": 0}

        stats[task]["total"] += 1
        if is_correct:
            stats[task]["correct"] += 1

        if not is_correct:
            errors.append(
                {
                    "id": sample_id,
                    "task": task,
                    "gold": gold,
                    "pred": pred,
                    "text": text,
                }
            )

        print("-" * 60)
        print(f"id: {sample_id}")
        print(f"text: {text}")
        print(f"task: {task}")
        print(f"gold: {gold}")
        print(f"pred: {pred}")
        print(f"correct: {is_correct}")

    overall_accuracy = correct_count / total_count if total_count > 0 else 0.0

    per_task = {}
    for task, value in stats.items():
        acc = value["correct"] / value["total"] if value["total"] > 0 else 0.0
        per_task[task] = {
            "total": value["total"],
            "correct": value["correct"],
            "accuracy": acc,
        }

    result = {
        "model": MODEL_NAME,
        "dataset": EVAL_FILE,
        "total": total_count,
        "correct": correct_count,
        "accuracy": overall_accuracy,
        "per_task": per_task,
        "errors": errors,
    }

    return result


# =========================
# 9. 保存结果
# =========================
def save_results(result: dict):
    os.makedirs("results", exist_ok=True)

    dataset_name = os.path.splitext(os.path.basename(result["dataset"]))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    txt_path = os.path.join("results", f"{dataset_name}_{timestamp}.txt")
    json_path = os.path.join("results", f"{dataset_name}_{timestamp}.json")

    # 保存 txt
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"模型: {result['model']}\n")
        f.write(f"评测集: {result['dataset']}\n")
        f.write(f"总样本数: {result['total']}\n")
        f.write(f"总正确数: {result['correct']}\n")
        f.write(f"总体准确率: {result['accuracy']:.2%}\n\n")

        f.write("各任务准确率:\n")
        for task, value in result["per_task"].items():
            f.write(
                f"{task}: {value['correct']}/{value['total']} = {value['accuracy']:.2%}\n"
            )

        f.write("\n错误样例:\n")
        if len(result["errors"]) == 0:
            f.write("无\n")
        else:
            for err in result["errors"]:
                f.write(
                    f"id={err['id']} | task={err['task']} | gold={err['gold']} | pred={err['pred']} | text={err['text']}\n"
                )

    # 保存 json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return txt_path, json_path


# =========================
# 10. 主程序
# =========================
def main():
    notes_text = load_notes_text(NOTES_FILE)
    eval_data = load_eval_data(EVAL_FILE)

    result = run_evaluation(notes_text, eval_data)

    print("\n" + "=" * 60)
    print("评测完成")
    print("=" * 60)
    print(f"总样本数: {result['total']}")
    print(f"总正确数: {result['correct']}")
    print(f"总体准确率: {result['accuracy']:.2%}")

    print("\n各任务准确率：")
    for task, value in result["per_task"].items():
        print(f"{task}: {value['correct']}/{value['total']} = {value['accuracy']:.2%}")

    txt_path, json_path = save_results(result)

    print("\n结果已保存：")
    print(txt_path)
    print(json_path)


if __name__ == "__main__":
    main()
