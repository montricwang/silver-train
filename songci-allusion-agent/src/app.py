import streamlit as st
import faiss
import pandas as pd
import torch
from transformers import BertModel, BertTokenizer
from utils.config import MODEL_DIR, DATA_DIR

# --- 1. 页面配置 ---
st.set_page_config(page_title="唐诗宋词语义搜索引擎", page_icon="", layout="wide")

st.title("唐诗宋词语义搜索引擎")
st.markdown("基于 `BERT-ccpoem` 深度语义匹配与 `FAISS` 高性能检索")

# --- 2. 路径配置 ---
MODEL_PATH = MODEL_DIR / "bert-ccpoem"
SENTS_CSV_PATH = DATA_DIR / "unified_sentences.csv"
WORKS_CSV_PATH = DATA_DIR / "unified_works.csv"
INDEX_PATH = DATA_DIR / "unified_sentences.index"


# --- 3. 核心资源加载 (带缓存优化) ---
@st.cache_resource
def load_resources():
    with st.status("正在初始化搜索引擎...", expanded=True) as status:
        st.write("加载 BERT 语义模型...")
        tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
        model = BertModel.from_pretrained(MODEL_PATH)

        # 自动适配计算设备
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        model.eval()

        st.write("加载 `FAISS` 向量索引...")
        index = faiss.read_index(str(INDEX_PATH))

        st.write("读取句子库...")
        df_sents = pd.read_csv(SENTS_CSV_PATH)

        st.write("读取作品库并构建关联索引...")
        df_works = pd.read_csv(WORKS_CSV_PATH)
        # 强制确保 work_id 是字符串格式，避免匹配失败
        df_works["work_id"] = df_works["work_id"].astype(str)
        # 将 work_id 设为索引，实现 O(1) 极速查找
        df_works = df_works.set_index("work_id")

        status.update(
            label="系统就绪", state="complete", expanded=False
        )

    return tokenizer, model, index, df_sents, df_works, device


# 执行加载逻辑
tokenizer, model, index, df_sents, df_works, device = load_resources()


# --- 4. 向量化函数 ---
def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(
        device
    )
    with torch.no_grad():
        outputs = model(**inputs)
        # Mean Pooling: 取所有 token 的平均向量
        return (
            torch.mean(outputs.last_hidden_state, dim=1).cpu().numpy().astype("float32")
        )


# --- 5. 侧边栏设置 ---
with st.sidebar:
    st.header("搜索设置")
    top_k = st.slider("展现结果数量", 1, 30, 10)
    st.divider()
    st.write(f"当前索引容量: {len(df_sents):,} 句")
    st.write(f"关联作品数量: {len(df_works):,} 篇")
    st.caption("提示：距离得分越小，语义越接近。")

# --- 6. 主界面交互 ---
query = st.text_input(
    "输入您想查询的意境、诗句或心情：", placeholder="例如：月落乌啼、金戈铁马、思念故乡"
)

if query:
    # A. 执行检索
    query_vec = get_embedding(query)
    distances, indices = index.search(query_vec, k=top_k)

    st.subheader(f"语义匹配结果：『{query}』")

    # B. 展示结果
    for dist, idx in zip(distances[0], indices[0]):
        if idx >= len(df_sents):
            continue

        # 获取当前命中的句子行
        sent_row = df_sents.iloc[idx]
        # 强制转换为字符串，确保能匹配上 df_works 的索引
        work_id = str(sent_row["work_id"])

        # --- C. 核心关联逻辑：从 works 表提取元数据 ---
        try:
            work_info = df_works.loc[work_id]
            # 兼容多种可能的字段名
            author = work_info.get("author", "佚名")

            t, r = work_info.get("title"), work_info.get("rhythmic")
            title = t if pd.notna(t) else r  # 标题与词牌目前不会同时出现

            dynasty = work_info.get("dynasty", "未知")
            full_content = work_info.get("content", "内容缺失")
        except KeyError:
            # 如果索引中没找到（通常是数据清洗时的遗漏）
            author = "未知"
            title = "作品已下架"
            dynasty = "未知"
            full_content = "未能在作品库中找到关联全文"

        # D. 渲染 UI 卡片
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.metric("距离得分", f"{dist:.2f}")
            with col2:
                # 突出显示搜到的金句
                st.markdown(f"### {sent_row['sentence']}")
                # 组合显示元数据：【朝代】作者 《作品名》
                st.caption(f"【{dynasty}】{author}《{title}》")

                # 交互折叠框：显示全文
                with st.expander("查看作品全篇"):
                    # 简单清洗内容显示格式
                    formatted_content = (
                        str(full_content).replace("\\n", "\n").replace("|", "\n")
                    )
                    st.text(formatted_content)
                    st.divider()
                    st.caption(f"作品指纹  `{work_id}`")

            st.divider()
