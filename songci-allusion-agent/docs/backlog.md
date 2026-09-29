# 🏮 古诗词语义搜索项目待办清单 (Project Backlog)

## 🔴 P0 核心能力 (Core & Data Engine)
*目标：打破“唐诗”局限，构建百万级全意象向量库。*

- [ ] **异构数据 ETL Pipeline**
    - [ ] 解析 `chinese-poetry` 宋词 JSON，提取 `author`, `title`, `paragraphs`。
    - [ ] **数据清洗**：剔除带有 `[ ]` 等损坏字符的诗句，统一简繁体（BERT 模型通常对简体更友好）。
    - [ ] **格式对齐**：构建统一的 Schema (id, sentence, author, title, genre, dynasty)。
- [ ] **语义颗粒度升级 (Chunking Strategy)**
    - [ ] 实验“单句”与“联（上下句）”的 Embedding 效果差异。
    - [ ] 重新生成百万级 `vectors.npy` (预计 1GB+)。
- [ ] **高性能索引重建**
    - [ ] 重建 FAISS 索引，对比 `IndexFlatL2` 与 `IndexIVFFlat`（若数据量超过 100 万，需考虑内存压力）。
- [ ] **基准测试集 (Golden Dataset V1)**
    - [ ] 手动整理 50 条“必中”词句，建立自动评估脚本计算 Hit@5。

---

## 🟡 P1 检索质量与算法调优 (Search Science)
*目标：解决“搜不准”和“语义偏移”的隐性问题。*

- [ ] **Bad Case 诊断记录**
    - [ ] 记录“小山”、“红蜡”、“断鸿”等特定意向的检索排名。
    - [ ] 分析 BERT 预训练偏见（现代汉语 vs 古汉语意象）。
- [ ] **混合检索架构 (Hybrid Search)**
    - [ ] **集成 BM25 算法**：实现关键词硬匹配。
    - [ ] **得分融合 (Rank Fusion)**：将向量相似度与关键词得分按比例加权。
- [ ] **策略决策实验**
    - [ ] 实验不同 `top_k` 对用户体验的影响。
    - [ ] 评估是否引入 **Cross-Encoder** 进行小规模 Rerank。

---

## 🟢 P2 功能增强与产品深度 (Feature Depth)
*目标：从“搜索框”进化为“文化工具”。*

- [ ] **上下文全息展示**
    - [ ] 在 CSV 中增加 `full_text` 字段，实现 UI 端“查看全诗”。
    - [ ] 增加朝代 (Dynasty) 和体裁 (Genre) 的侧边栏 Filter。
- [ ] **多句连续匹配逻辑**
    - [ ] 优化 Query 处理，支持“门外楼头”这种跨句意象的联合检索。
- [ ] **UI 交互美化**
    - [ ] 使用 Streamlit 的 `st.expander` 或 `st.columns` 优化布局。
    - [ ] 增加搜索结果的相似度热力条显示。

---

## 🟣 P3 研究、探索与交付 (R&D & Delivery)
*目标：技术前瞻性研究与云端落地。*

- [ ] **典故知识图谱接入**
    - [ ] 尝试爬取或整理典故词表，实现结果中的“典故自动高亮”。
- [ ] **LLM-as-Judge 评估体系**
    - [ ] 编写 Prompt，让 LLM 评估检索结果与 Query 的“意境重合度”。
- [ ] **工程化云端部署**
    - [ ] 优化模型与向量库体积（量化压缩），部署至 Hugging Face 或个人服务器。
    - [ ] **CI/CD**：接入版本信息自动同步至 UI 界面。

---

## ✅ 已完成 (Done)
- [x] v0.1.0-alpha: 跑通唐诗 50 万数据语义检索闭环。
- [x] v0.2.0-aplha: 支持全宋词语料。