from openai import OpenAI
import streamlit as st
from skills.extract import extract_allusions
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 页面配置
st.set_page_config(page_title="宋词典故解析", page_icon="🏮")

st.title("宋词典故解析")
st.subheader("诗词典故自动化抽取")

# 输入区
with st.container():
    test_default = "念往昔，繁华竞逐，叹门外楼头，悲恨相续。"
    poem_input = st.text_area("请输入文本：", value=test_default, height=150)
    analyze_btn = st.button("开始拆解", type="primary")

# 结果逻辑
if analyze_btn:
    if not poem_input.strip():
        st.warning("请输入内容后点击解析。")
    else:
        with st.spinner("正在分析，请稍候..."):
            results = extract_allusions(poem_input, client).get("extracted_allusions")

            if not results:
                st.info("未发现明显典故。")
            else:
                st.success(f"解析完成，共发现 {len(results)} 处引用。")

                # 循环渲染卡片
                for idx, item in enumerate(results):
                    with st.expander(
                        f"「{item.get('phrase')}」{item.get('confidence')}",
                        expanded=True,
                    ):
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.write("**出处**")
                            st.code(item.get("source", "未知"))
                        with col2:
                            st.write("**相关原文**")
                            st.info(item.get("original", "无原文记录"))


# 侧边栏说明
with st.sidebar:
    st.markdown("### 🛠️ 工程状态")
    st.info("当前模式：Single-Node Extraction")
    st.warning("注意：目前尚未接入 Validator 节点，考据结果可能存在 LLM 幻觉。")
    st.divider()
    st.markdown("Designed by 言哉")
