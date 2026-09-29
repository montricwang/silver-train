from pathlib import Path
import json

from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    """
    基础文本清洗。

    当前阶段故意不做复杂处理，只做最基础的三件事：
    1. 去掉首尾空白
    2. 把连续空白压成单个空格
    3. 保留原始文字顺序

    这样做的原因：
    你现在最重要的是先把“结构”抽出来，而不是急着做精细清洗。
    """
    return " ".join(text.split()).strip()


def text_without_superscript_refs(p_tag, parser: str = "lxml") -> str:
    """
    从一个 <p> 标签中提取正文文本，并删掉脚注引用上标。

    例如原文可能是：
        有有我之境……“泪眼问花花不语”[1]、“可堪……”[2]……

    我们希望得到：
        有有我之境……“泪眼问花花不语”、“可堪……”……

    做法：
    - 先复制一份临时 HTML
    - 把里面所有 <a> 标签删除
    - 再提取纯文本

    这里之所以不直接改原始 p_tag，是为了避免影响后续遍历。
    """
    temp = BeautifulSoup(str(p_tag), parser)

    for a in temp.find_all("a"):
        a.decompose()

    return clean_text(temp.get_text(" ", strip=True))


def parse_xhtml_file(input_file: Path, parser: str = "lxml") -> dict:
    """
    解析单个 XHTML 文件，返回结构化结果 dict。

    输出结构固定为：
    {
      "source_file": 文件名,
      "section_id": 条目标号,
      "original_text": 原文,
      "notes": 注释列表,
      "translation": 译文,
      "commentary": 评析
    }

    这个函数是整个脚本的核心。
    以后无论你是：
    - 调试单个文件
    - 批量清洗目录
    - 做后续 AI 提炼
    都应该从这个函数开始复用。
    """
    # 1. 读取 XHTML 原文
    html = input_file.read_text(encoding="utf-8")

    # 2. 解析为 BeautifulSoup 标签树
    soup = BeautifulSoup(html, parser)

    # 3. 定位正文区域
    body = soup.body

    # 4. 取出正文中所有 h1 和 p 标签，按文档顺序遍历
    elements = body.find_all(["h1", "p"])

    # 5. 初始化输出骨架
    result = {
        "source_file": input_file.name,
        "section_id": None,
        "original_text": "",
        "notes": [],
        "translation": "",
        "commentary": "",
    }

    # 6. current_section 用来记录当前遍历到哪个区域
    #    一开始还没进入任何区域，所以设为 None
    current_section = None

    # 7. 顺序遍历整个文档
    for elem in elements:
        # ----------------------------
        # 处理 h1：通常是条目标号，例如“三”
        # ----------------------------
        if elem.name == "h1":
            result["section_id"] = clean_text(elem.get_text())
            continue

        # 从这里往下，elem 一定是 <p>
        full_text = clean_text(elem.get_text(" ", strip=True))

        # ----------------------------
        # 如果是区域标题，就切换当前状态
        # ----------------------------
        if full_text == "【注释】":
            current_section = "notes"
            continue

        if full_text == "【译文】":
            current_section = "translation"
            continue

        if full_text == "【评析】":
            current_section = "commentary"
            continue

        # ----------------------------
        # 还没进入【注释】之前的第一段正文，就是原文
        # ----------------------------
        if current_section is None:
            result["original_text"] = text_without_superscript_refs(elem, parser=parser)
            current_section = "original"
            continue

        # ----------------------------
        # 注释区域
        # ----------------------------
        if current_section == "notes":
            # 注释通常长这样：
            # [1] “泪眼”二句：出自南唐词人冯延巳……
            #
            # 这里做一个非常朴素的切分：
            #   label   -> [1]
            #   content -> 后面的注释正文
            note_text = full_text
            close_bracket_index = note_text.find("]")

            # 如果没找到右中括号，说明这一段可能不是标准注释格式
            # 当前阶段不做复杂异常处理，直接把整段都塞进 content
            if close_bracket_index == -1:
                result["notes"].append({"label": "", "content": note_text})
            else:
                label = note_text[: close_bracket_index + 1]
                content = note_text[close_bracket_index + 1 :].strip()

                result["notes"].append({"label": label, "content": content})
            continue

        # ----------------------------
        # 译文区域：允许多段拼接
        # ----------------------------
        if current_section == "translation":
            if result["translation"]:
                result["translation"] += "\n" + full_text
            else:
                result["translation"] = full_text
            continue

        # ----------------------------
        # 评析区域：允许多段拼接
        # ----------------------------
        if current_section == "commentary":
            if result["commentary"]:
                result["commentary"] += "\n" + full_text
            else:
                result["commentary"] = full_text
            continue

    return result


def save_result_to_json(result: dict, output_file: Path) -> None:
    """
    把单个解析结果写入 JSON 文件。
    """
    output_file.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def parse_directory(
    input_dir: Path, output_dir: Path, pattern: str = "*.html", parser: str = "lxml"
) -> None:
    """
    批量解析一个目录下的所有 HTML / XHTML 文件。

    参数说明：
    - input_dir: 原始 XHTML 文件所在目录
    - output_dir: 输出 JSON 文件所在目录
    - pattern: 文件匹配模式，默认 *.html
               如果你的文件是 .xhtml，就改成 *.xhtml
    - parser: BeautifulSoup 使用的解析器，默认 lxml

    处理流程：
    1. 找到目录下所有符合 pattern 的文件
    2. 对每个文件调用 parse_xhtml_file()
    3. 把结果写到 output_dir 中
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(input_dir.glob(pattern))

    print(f"找到文件数：{len(files)}")
    print(f"输入目录：{input_dir}")
    print(f"输出目录：{output_dir}")
    print("-" * 80)

    for file_path in files:
        result = parse_xhtml_file(file_path, parser=parser)

        # 输出文件名：原文件名去掉后缀，加 .json
        output_file = output_dir / f"{file_path.stem}.json"
        save_result_to_json(result, output_file)

        print(f"已解析：{file_path.name}")
        print(f"  section_id: {result['section_id']}")
        print(f"  notes_count: {len(result['notes'])}")
        print(f"  output: {output_file.name}")
        print("-" * 80)

def merge_json_files(input_dir: Path, output_file: Path):
    """
    把一个目录下的所有 JSON 文件合并成一个列表。

    输入：
        input_dir/
            text00001.json
            text00002.json
            text00003.json

    输出：
        merged.json

    merged.json 的结构：

    [
        {...},
        {...},
        {...}
    ]
    """

    merged = []

    # 找到目录下所有 json
    for file in sorted(input_dir.glob("*.json")):

        data = json.loads(file.read_text(encoding="utf-8"))

        merged.append(data)

    # 保存
    output_file.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"合并完成，共 {len(merged)} 条")

if __name__ == "__main__":
    # =============================
    # 这里改成你自己的目录
    # =============================

    # 你的 XHTML/HTML 文件所在目录
    input_dir = Path("D:\Documents\Code\songci-allusion-agent\\raw_data\人间词话（彭玉平译注）\OEBPS")

    # 解析后的 JSON 输出目录
    output_dir = Path("parsed_json")

    # 如果你的文件后缀是 .xhtml，就改成 "*.xhtml"
    parse_directory(
        input_dir=input_dir, output_dir=output_dir, pattern="*.html", parser="lxml"
    )
    merge_json_files(output_dir, Path("renjian_cihua_corpus.json"))