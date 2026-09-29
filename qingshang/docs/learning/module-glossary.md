# 模块中文名速查

## Reader 前端

| 文件 | 中文名 | 读它时关注什么 |
|---|---|---|
| `apps/reader_app.py` | Reader 页面入口 | 页面布局、渲染顺序、用户交互入口 |
| `apps/reader/config.py` | Reader 配置与标签 | 常量、中文标签、主题颜色、超时 |
| `apps/reader/api_client.py` | Reader API 客户端 | 前端如何请求 FastAPI |
| `apps/reader/state.py` | Reader 页面状态 | `st.session_state` 如何保存选句、词作、阅读模式 |
| `apps/reader/text.py` | Reader 文本展示处理 | 慢读拆句、缩进、行定位 |
| `apps/reader/evidence.py` | Reader 证据展示整理 | HTML 转义、证据卡片、审阅短注、长引文截断 |

## FastAPI 后端

| 文件 | 中文名 | 读它时关注什么 |
|---|---|---|
| `app/main.py` | FastAPI 应用入口 | app 创建、路由注册、健康检查 |
| `app/api/routes/__init__.py` | 总路由聚合 | 哪些子路由被注册 |
| `app/api/routes/poems.py` | 词作路由 | poem 相关 API 的入口 |
| `app/api/routes/cnkgraph.py` | CNKGraph 工具路由 | 直接工具接口 |

## 数据层

| 文件 | 中文名 | 读它时关注什么 |
|---|---|---|
| `app/models/poem.py` | 诗词 ORM 模型 | 三张表和对象关系 |
| `app/crud/poem.py` | 诗词查询函数 | 列表和详情如何查询 |
| `app/db/session.py` | 数据库会话 | FastAPI 如何自动注入 session |
| `app/db/init_db.py` | 数据库初始化 | `create_all()` 只创建缺失表，不做迁移 |

## Schema 层

| 文件 | 中文名 | 读它时关注什么 |
|---|---|---|
| `app/schemas/poem.py` | 词作响应结构 | Reader 拿到的 poem/section/line 格式 |
| `app/schemas/cnkgraph.py` | CNKGraph 窄模型 | 外部证据如何被收窄 |
| `app/schemas/allusion.py` | 典故候选与审阅结构 | 候选、证据结果、Review 结果 |
| `app/schemas/analysis.py` | 整首赏析结构 | 旧 analyze 接口的结构化输出 |

## Service 层

| 文件 | 中文名 | 读它时关注什么 |
|---|---|---|
| `app/services/llm_client.py` | LLM HTTP 客户端 | 如何调用兼容 OpenAI 协议的模型 |
| `app/services/poem_analyzer.py` | 整首赏析服务 | 旧结构化赏析链路 |
| `app/services/allusion_candidate_extractor.py` | 典故候选提取器 | LLM 如何只提候选，不生成证据 |
| `app/services/cnkgraph_client.py` | CNKGraph HTTP 客户端 | 外部 API 请求和错误包装 |
| `app/services/cnkgraph_tools.py` | CNKGraph 工具适配器 | raw response 如何变成 EvidenceItem |
| `app/services/allusion_evidence.py` | 候选证据检索器 | query_variants 如何自动查 CNKGraph |
| `app/services/allusion_evidence_reviewer.py` | 证据审阅器 | LLM 如何审阅已有证据 |

## 常见词

| 词 | 项目里的意思 |
|---|---|
| Reader | Streamlit 前端阅读器 |
| poem_id | 对外稳定作品编号，例如 `zhoubangyan-0001` |
| line_no | 全词中的句号，用于定位选句 |
| selected_text | 用户手动输入或点击正文回填的查询文本 |
| anchor_text | LLM 识别出的原文候选锚点 |
| query_variants | 给 CNKGraph 用的查询变体，不是解释结论 |
| evidence_results | CNKGraph 对某个候选的查询结果 |
| review_result | LLM Reviewer 对已有证据的审阅结果 |
| raw | 外部 API 原始响应，调试用，不作为 Reader 主展示字段 |

