# schema.py
from typing import List, TypedDict, Optional


class Allusion(TypedDict):
    phrase: str
    source: str
    original: str 
    confidence: str  # "high" / "medium" / "low"


class ValidationResult(TypedDict):
    phrase: str
    matched_sentence: str  # FAISS 找到的最相似句子
    matched_author: str
    matched_title: str
    similarity_score: float
    validated: bool  # 是否通过验证


class AgentState(TypedDict):
    input_text: str
    extracted_allusions: List[Allusion]  # LLM 抽取结果
    validation_results: List[ValidationResult]  # FAISS 验证结果
    final_report: Optional[str]  # 最终输出，初始为 None
    error: Optional[str]  # 出错时记录，方便调试
