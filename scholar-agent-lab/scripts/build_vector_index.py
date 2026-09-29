from __future__ import annotations

import json
from pathlib import Path

import chromadb
from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore


INPUT_FILE = Path("data/processed/commentary_chunks_v1.jsonl")
PERSIST_DIR = Path("data/vector_store/chroma_db")
COLLECTION_NAME = "renjian_commentary_v1"

# 第一版先用一个稳妥的中文 embedding 模型
# 你也可以后面换成更适合中文检索的模型
EMBED_MODEL_NAME = "models/bge-small-zh-v1.5"


def load_chunk_records(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"未找到输入文件: {path}")

    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def convert_to_documents(records: list[dict]) -> list[Document]:
    documents = []

    for record in records:
        text = record["text"]

        metadata = {
            "chunk_id": record["chunk_id"],
            "book": record["book"],
            "file": record["file"],
            "chunk_index": record["chunk_index"],
        }

        doc = Document(
            text=text,
            metadata=metadata,
        )
        documents.append(doc)

    return documents


def build_index(documents: list[Document]) -> VectorStoreIndex:
    # 1. 设置 embedding 模型
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

    # 2. 初始化 Chroma 持久化数据库
    PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=str(PERSIST_DIR))
    chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

    # 3. 包装成 LlamaIndex 的 vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 4. 建索引
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )
    return index


def main() -> None:
    print("=" * 60)
    print("开始构建向量索引")
    print("=" * 60)

    records = load_chunk_records(INPUT_FILE)
    print(f"读取 chunk 数量: {len(records)}")

    documents = convert_to_documents(records)
    print(f"转换为 Document 数量: {len(documents)}")

    _ = build_index(documents)

    print("\n向量索引构建完成")
    print(f"Chroma 持久化目录: {PERSIST_DIR}")
    print(f"Collection 名称: {COLLECTION_NAME}")
    print(f"Embedding 模型: {EMBED_MODEL_NAME}")


if __name__ == "__main__":
    main()
