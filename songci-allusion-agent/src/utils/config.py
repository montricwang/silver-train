# config.py
from pathlib import Path

# --- 基础路径定位 ---
# 自动定位项目根目录 (config.py 在 ./src/utils 目录下)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# --- 数据与模型路径 ---
RAW_DATA_DIR = ROOT_DIR / "raw_data"
DATA_DIR = ROOT_DIR / "data"
MODEL_DIR = ROOT_DIR / "models"

# 具体文件路径
PROCESSED_CSV = DATA_DIR / "unified_poetry.csv"
FAISS_INDEX = DATA_DIR / "unified_poetry.index"

# 语义模型路径
BERT_MODEL_PATH = MODEL_DIR / "bert-ccpoem"

# --- 业务配置 ---
# V0.3.0 语料白名单
INCLUDE_DYNASTIES = ["唐", "宋_1", "宋_2", "宋_3", "宋_4"]

# 搜索设置
DEFAULT_TOP_K = 5
