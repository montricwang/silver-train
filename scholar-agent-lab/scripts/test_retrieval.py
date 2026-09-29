from __future__ import annotations

import chromadb
from pathlib import Path

from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore


PERSIST_DIR = Path("data/vector_store/chroma_db")
COLLECTION_NAME = "renjian_commentary_v1"
EMBED_MODEL_NAME = "models/bge-small-zh-v1.5"


def load_index() -> VectorStoreIndex:
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

    chroma_client = chromadb.PersistentClient(path=str(PERSIST_DIR))
    chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
    )
    return index


def main() -> None:
    index = load_index()

    retriever = index.as_retriever(similarity_top_k=5)

    query = "王国维如何解释有我之境和无我之境？"
    nodes = retriever.retrieve(query)

    print("=" * 60)
    print(f"Query: {query}")
    print("=" * 60)

    for i, node in enumerate(nodes, start=1):
        print(f"\n--- Top {i} ---")
        print("Score:", getattr(node, "score", None))
        print("Metadata:", node.metadata)
        print("Text:", node.text[:500])


if __name__ == "__main__":
    main()
