from __future__ import annotations

from pathlib import Path

import chromadb
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from openai import OpenAI
import os
from dotenv import load_dotenv

PERSIST_DIR = Path("data/vector_store/chroma_db")
COLLECTION_NAME = "renjian_commentary_v1"
EMBED_MODEL_NAME = "models/bge-small-zh-v1.5"


load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SKILL_PATH = Path("skills/wangguowei_skill_v1.md")


def load_skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def load_index() -> VectorStoreIndex:
    Settings.embed_model = HuggingFaceEmbedding(model_name=str(EMBED_MODEL_NAME))

    chroma_client = chromadb.PersistentClient(path=str(PERSIST_DIR))
    chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
    )

    return index


def build_context(nodes) -> str:
    texts = []

    for i, node in enumerate(nodes, start=1):
        texts.append(f"[资料{i}]\n{node.text}")

    return "\n\n".join(texts)


def ask_llm(user_text: str, context: str):
    skill = load_skill()

    system_prompt = f"""
    {skill}
    """

    user_prompt = f"""
    请根据以上 skill 和参考资料，对下面这句词进行赏析。

    【参考资料】
    {context}

    【待分析文本】
    {user_text}

    请严格按照 skill 规定的输出结构回答。
    """

    resp = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content


def main():

    index = load_index()
    retriever = index.as_retriever(similarity_top_k=10)

    query = "一川晚照人闲立，满袖杨花听杜鹃"

    nodes = retriever.retrieve(query)

    context = build_context(nodes)

    print("=" * 60)
    print("检索到的资料：")
    print("=" * 60)
    print(context[:2000])

    print("\n\n")

    answer = ask_llm(query, context)

    print("=" * 60)
    print("RAG回答：")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()
