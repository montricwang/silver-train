import pandas as pd
import numpy as np
import torch
import faiss
from transformers import BertModel, BertTokenizer
from tqdm import tqdm
from pathlib import Path
from src.utils.config import DATA_DIR, MODEL_DIR

# --- 配置区 ---
MODEL_PATH = MODEL_DIR / "bert-ccpoem"
INPUT_CSV = DATA_DIR / "unified_sentences.csv"
OUTPUT_NPY = DATA_DIR / "unified_vectors.npy"
INDEX_PATH = DATA_DIR / "unified_sentences.index"

# 自动选择设备 (如果有英伟达显卡就用 GPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def encode_sentences(csv_path: Path, batch_size: int = 32):
    """
    将文本转换为向量
    Args:
        csv_path: 文本文件路径
        batch_size: 批量大小
    Returns:
        final_matrix: 向量矩阵
    """
    print(f"正在加载模型至 {DEVICE}...")
    tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
    model = BertModel.from_pretrained(MODEL_PATH).to(DEVICE)
    model.eval()

    df = pd.read_csv(csv_path)
    sentences = df["sentence"].tolist()
    all_vectors = []

    print(f"开始推理，共 {len(sentences)} 句...")
    with torch.no_grad():
        for i in tqdm(range(0, len(sentences), batch_size)):
            batch = sentences[i : i + batch_size]
            inputs = tokenizer(
                batch, return_tensors="pt", padding=True, truncation=True, max_length=64
            ).to(DEVICE)

            outputs = model(**inputs)
            # Mean Pooling: [batch, seq_len, dim] -> [batch, dim]
            embeddings = torch.mean(outputs.last_hidden_state, dim=1)
            all_vectors.append(embeddings.cpu().numpy())

    final_matrix = np.vstack(all_vectors).astype("float32")
    # 存一份 .npy 做备份
    np.save(OUTPUT_NPY, final_matrix)
    return final_matrix


def build_faiss_index(vectors: np.ndarray, save_path: Path, metric: str = "l2"):
    """
    将向量转换为 FAISS 索引
    Args:
        vectors: 向量数据
        save_path: 索引保存路径
        metric: 距离度量方式
    """
    dim = vectors.shape[1]
    print(f"正在构建索引，维度: {dim}, 度量: {metric}")

    if metric == "cosine":
        # 余弦相似度需要先对向量进行 L2 归一化
        faiss.normalize_L2(vectors)
        index = faiss.IndexFlatIP(dim)
    else:
        # 欧式距离直接使用
        index = faiss.IndexFlatL2(dim)

    index.add(vectors)
    faiss.write_index(index, str(save_path))
    print(f"🎉 索引构建完成: {save_path}")


if __name__ == "__main__":
    vectors = encode_sentences(INPUT_CSV)
    build_faiss_index(vectors, INDEX_PATH, metric="l2")
