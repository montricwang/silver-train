import json
import streamlit as st
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
INPUT_DIR = PROJECT_ROOT / "inputs"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "skill_tests"


def list_cases():
    return sorted(
        [
            path.name.replace("_synthesis.md", "")
            for path in OUTPUT_DIR.glob("*_synthesis.md")
        ]
    )


def load_text(path: Path):
    return path.read_text(encoding="utf-8")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


st.set_page_config(
    page_title="宋词赏析展示器",
    layout="wide",
)

st.title("宋词赏析展示器")
st.caption("展示已经生成的综合赏析与结构化分析结果。")

cases = list_cases()

case_name = st.sidebar.selectbox("选择案例", cases)

poem_path = INPUT_DIR / f"{case_name}.txt"
synthesis_path = OUTPUT_DIR / f"{case_name}_synthesis.md"
imagery_path = OUTPUT_DIR / f"{case_name}_imagery.json"
spacetime_path = OUTPUT_DIR / f"{case_name}_spacetime.json"
composition_path = OUTPUT_DIR / f"{case_name}_composition.json"

st.divider()
st.subheader("作品")
st.text(load_text(poem_path))
st.divider()
st.subheader("综合赏析")
st.markdown(load_text(synthesis_path))

st.subheader("意象分析 JSON")
st.json(load_json(imagery_path), expanded=False)

st.subheader("时空结构 JSON")
st.json(load_json(spacetime_path), expanded=False)

st.subheader("章法写法 JSON")
st.json(load_json(composition_path), expanded=False)

st.divider()

st.subheader("文件路径")
st.code(str(synthesis_path))
st.code(str(imagery_path))
st.code(str(spacetime_path))
st.code(str(composition_path))
