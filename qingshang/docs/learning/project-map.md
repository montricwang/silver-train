# 清商项目阅读地图

这份文档用于第一次重新进入项目时快速定位：哪个文件负责什么、谁调用谁、哪里会真的访问数据库、哪里会真的调用 LLM 或外部 API。

## 1. 先记住三条主线

### 本地词作读取主线

```text
Reader / 浏览器
  -> FastAPI GET /api/poems
  -> app/api/routes/poems.py
  -> app/crud/poem.py
  -> app/models/poem.py
  -> PostgreSQL
```

这条线只读本地数据库，不调用 LLM，也不调用 CNKGraph。

### 手动阅读辅助主线

```text
Reader 选中文本
  -> POST /api/poems/{poem_id}/reading-aids
  -> app/api/routes/poems.py
  -> app/services/cnkgraph_tools.py
  -> app/services/cnkgraph_client.py
  -> CNKGraph
```

这条线调用外部 CNKGraph，但不调用 LLM。

### AI 候选与证据审阅主线

```text
Reader 点击 AI 审阅按钮
  -> POST /api/poems/{poem_id}/allusion-candidates/with-review
  -> 候选识别 LLM
  -> CNKGraph 证据检索
  -> Evidence Reviewer LLM
  -> Reader 展示审阅短注
```

这条线同时调用 LLM 和 CNKGraph，是当前最复杂的功能。

## 2. 模块分层

| 层级 | 中文名 | 主要文件 | 作用 |
|---|---|---|---|
| Frontend | Reader 前端 | `apps/reader_app.py`、`apps/reader/*` | 展示词作、阅读模式、阅读辅助和证据审阅结果 |
| API | 路由层 | `app/api/routes/*.py` | 接收 HTTP 请求，校验参数，调用服务层 |
| Schema | 数据契约层 | `app/schemas/*.py` | 定义请求和响应的稳定结构 |
| Service | 业务服务层 | `app/services/*.py` | 调用 LLM、CNKGraph，编排候选和证据审阅 |
| CRUD | 数据读取层 | `app/crud/poem.py` | 封装数据库查询 |
| ORM | 数据模型层 | `app/models/poem.py` | 定义 poems/sections/lines 三层表结构 |
| DB | 数据库基础设施 | `app/db/*.py` | 创建 engine、session 和初始化表 |
| Scripts | 数据脚本 | `scripts/*.py` | 清洗、导入、probe 外部 API |

## 3. Reader 拆分后的阅读顺序

先看这些文件：

1. `apps/reader_app.py`
   - 只看 `main()`、`render_poem()`、`render_tools()`。
   - 目标：知道页面分成左侧目录、正文、右侧阅读辅助。

2. `apps/reader/api_client.py`
   - 看 `fetch_poems()`、`fetch_poem()`、`fetch_reading_aids()`、`fetch_allusion_candidates()`。
   - 目标：知道前端如何访问 FastAPI。

3. `apps/reader/state.py`
   - 看 `choose_poem()`、`choose_line()`、`initialize_state()`。
   - 目标：理解 Streamlit 的 `session_state` 保存了哪些页面状态。

4. `apps/reader/text.py`
   - 看 `build_breathing_fragments()`。
   - 目标：理解慢读模式如何只在展示层加缩进，不改原文。

5. `apps/reader/evidence.py`
   - 看 `card_html()`、`evidence_preview_html()`、`review_result_html()`。
   - 目标：理解外部证据如何被转义、截断和折叠展示。

6. `apps/reader/config.py`
   - 最后看。
   - 目标：查中文标签、颜色、超时、阅读模式等常量。

## 4. 后端主链路阅读顺序

1. `app/main.py`
   - 看 FastAPI app 如何创建和注册路由。

2. `app/api/routes/__init__.py`
   - 看总 router 如何聚合 poems/cnkgraph 等子路由。

3. `app/api/routes/poems.py`
   - 看所有以 `/api/poems` 开头的接口。

4. `app/crud/poem.py`
   - 看数据库读取函数。

5. `app/models/poem.py`
   - 看三张核心表：`poems`、`poem_sections`、`poem_lines`。

6. `app/schemas/poem.py`
   - 看 API 返回给前端的词作结构。

## 5. LLM 和 CNKGraph 阅读顺序

1. `app/services/llm_client.py`
   - 统一 LLM HTTP 客户端。

2. `app/services/allusion_candidate_extractor.py`
   - LLM 只做候选识别，不生成证据。

3. `app/services/cnkgraph_client.py`
   - 只负责真实 HTTP 请求。

4. `app/services/cnkgraph_tools.py`
   - 把 CNKGraph raw response 转成清商窄模型。

5. `app/services/allusion_evidence.py`
   - 用 query variants 自动查询候选证据。

6. `app/services/allusion_evidence_reviewer.py`
   - 受控 LLM Reviewer 审阅已有证据。

## 6. 哪些地方会真的产生副作用

| 文件 | 副作用 |
|---|---|
| `apps/reader/api_client.py` | 从前端发 HTTP 请求到本地 FastAPI |
| `app/db/session.py` | 创建数据库连接池和 session |
| `app/crud/poem.py` | 执行数据库查询 |
| `app/services/llm_client.py` | 调用外部 LLM API |
| `app/services/cnkgraph_client.py` | 调用外部 CNKGraph API |
| `scripts/import_zhoubangyan_poems.py` | 写入 PostgreSQL |

其他大部分 `schemas`、`config`、`text`、`evidence` 文件主要是结构定义或纯函数。

## 7. 框架会自动接手的地方

| 写法 | 框架偷偷做什么 |
|---|---|
| `@router.get(...)` / `@router.post(...)` | FastAPI 收到匹配请求时自动调用路由函数 |
| `Depends(get_db)` | FastAPI 在请求进入路由前自动创建数据库 session |
| `BaseModel` 子类 | Pydantic 自动校验输入/输出结构 |
| `Mapped[...] = mapped_column(...)` | SQLAlchemy 读取声明并映射到数据库列 |
| `relationship(...)` | SQLAlchemy 管理 ORM 对象关系 |
| `@st.cache_data(...)` | Streamlit 缓存函数返回值，减少重复请求 |
| `st.session_state` | Streamlit 在页面 rerun 之间保存交互状态 |

