# Reader 前端数据流

Reader 是一个 Streamlit 前端。它不直接访问数据库，也不直接调用 LLM 或 CNKGraph；它通过 FastAPI 获得数据。

## 1. 页面启动时发生什么

```text
main()
  -> st.set_page_config()
  -> install_styles()
  -> fetch_poems()
  -> initialize_state()
  -> render_poem_directory()
  -> fetch_poem()
  -> render_poem()
  -> render_tools()
```

对应文件：

- `apps/reader_app.py`：页面入口和渲染函数。
- `apps/reader/api_client.py`：所有 HTTP 请求。
- `apps/reader/state.py`：跨 rerun 的页面状态。

## 2. 左侧目录

```text
render_poem_directory(poems)
  -> 根据筛选文本过滤 poems
  -> 根据 DIRECTORY_PAGE_SIZE 分页
  -> fetch_opening_lines() 补无标题作品的起句
  -> 点击某首词时调用 choose_poem()
```

`choose_poem()` 在 `apps/reader/state.py` 中。它会清空上一首词的选句、阅读辅助结果、AI 候选和领读状态。

## 3. 正文阅读区

正文阅读区由 `render_poem()` 分发四种模式：

| 模式 | 函数 | 说明 |
|---|---|---|
| 通读 | `render_overview_mode()` | 居中展示原始 poem_line |
| 慢读 | `render_slow_mode()` | 按标点拆成 breathing fragments 并缩进 |
| 转轮 | `render_focus_reader()` | 一次突出一句，上下句低透明显示 |
| 领读 | `render_guided_mode()` | 在转轮基础上按速度自动推进 |

慢读模式的核心纯函数在 `apps/reader/text.py`：

```text
build_breathing_fragments(sections)
```

它只改变展示文本 `display_text`，不会修改原文 `text`，也不会把缩进带入 selected_text 或 API 请求。

## 4. 点击一句词时发生什么

```text
正文按钮点击
  -> choose_line(line_no, text)
  -> 写入 st.session_state.selected_text
  -> 写入 st.session_state.selected_line_no
  -> 右侧表单自动显示选中文本
```

`choose_line()` 不调用后端。它只是更新页面状态。

## 5. 手动阅读辅助

```text
render_tools()
  -> 用户输入 selected_text 或点击正文回填
  -> 选择工具 pills
  -> 提交表单
  -> fetch_reading_aids()
  -> POST /api/poems/{poem_id}/reading-aids
  -> render_reading_results()
```

手动阅读辅助不调用 LLM。它让后端调用 CNKGraph 的字词、典故、出处、韵部和词谱工具。

## 6. AI 候选证据审阅

```text
点击“AI 审阅候选证据并生成短注”
  -> fetch_allusion_candidates()
  -> POST /api/poems/{poem_id}/allusion-candidates/with-review
  -> render_allusion_evidence_preview()
```

这个按钮会触发完整后端链路：

```text
LLM 候选识别
  -> CNKGraph 候选证据检索
  -> LLM Evidence Review
```

Reader 只负责展示返回结果，不在前端判断典故是否成立。

## 7. 为什么有这么多 HTML 辅助函数

Streamlit 原生组件不总能满足证据卡片、短注、长引文折叠的展示需求，所以项目用少量 HTML 片段展示证据。

相关纯函数在：

```text
apps/reader/evidence.py
```

这些函数会先做 HTML 转义，避免 CNKGraph 或 LLM 文本污染页面。

## 8. 本地代理问题

Reader 访问本机 FastAPI 时使用：

```python
trust_env=False
```

这表示忽略 Clash、系统代理或终端代理变量。原因是 Reader 请求的是本机：

```text
http://127.0.0.1:8000
```

本机请求不应该绕到代理里。

