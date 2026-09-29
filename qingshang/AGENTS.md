# AGENTS.md

## 项目角色

本仓库是“清商”项目：一个围绕结构化宋词数据、FastAPI API、PostgreSQL / SQLAlchemy 数据层和 LLM 辅助分析构建的宋词阅读与赏析应用。

## 工作约定

- 每轮只围绕用户当前任务修改，避免顺手重构无关文件。
- 不要因为某些代码“看起来可以优化”就主动改动；发现技术债时，可以记录到同步文档或 TODO。
- 未经明确要求，不要修改数据库 schema、API 返回结构、生成数据路径和核心 poem / section / line 数据契约。
- 优先产出小而可 review 的 diff。
- 非平凡改动完成后，更新 `docs/sync/latest.md`，说明本轮改了什么、验证了什么、哪些没有验证、下一步建议是什么。

## 开始任务前先读

在进行较大改动、回答项目现状、判断下一步、或生成同步说明之前，先阅读：

- `docs/sync/latest.md`

这个文件是项目当前状态的同步摘要。它应被视为最新架构、可用接口、已验证功能、已知问题和近期优先级的入口文档。

## 代码解释与阅读文档

当解释代码、添加学习型注释、或生成代码阅读文档时，遵守以下两份规则：

- `docs/code-reading/low-noise-code-reading.md`
- `docs/code-reading/python-file-reading.md`

两者分工如下：

- `low-noise-code-reading.md` 用于解释一行代码或一小段代码。
- `python-file-reading.md` 用于解释一个 `.py` 文件、一个类、一个函数的整体职责、调用关系和项目位置。

核心要求：

- 使用低噪声解释，不要把每个术语都展开成教程。
- 关键实体后面要标注简短分类，例如：`Mapped【ORM 类型标注工具】`、`get_db【函数 / FastAPI 依赖函数】`、`UniqueConstraint(...)【构造调用】`。
- 按人的认知顺序解释代码，而不是机械地从左到右翻译。
- 第一层解释保持简洁：说明“这是什么、用来做什么、最终效果是什么”。
- 解释文件、类、函数时，优先说明职责、所属层级、上游调用、下游依赖、输入、输出和容易误解的点。
- 遇到框架代码和控制反转时，要简短说明框架之后会自动读取、注册、调用或注入什么。
- 详细学习说明优先写入 `docs/code-reading/*.md`，不要在源码里堆大量行内注释。
- 源码注释只补充少量关键点，例如“框架偷偷做什么”“为什么这里不能省略”“容易误解的边界”。
- 不要为了补注释而重写已经正常工作的代码。

## 验证要求

改动后运行与本轮任务最相关的最小检查。后端代码改动通常至少运行：

```bash
python -m compileall app scripts
```

如果改动影响 API 行为，需要说明哪些接口已经或尚未手动验证，例如：

- `GET /health`
- `GET /api/poems`
- `GET /api/poems/{poem_id}`
- `POST /api/poems/{poem_id}/analyze`

如果没有真实连接 PostgreSQL、没有真实调用 LLM、没有真实调用外部 API，要在 `docs/sync/latest.md` 里明确说明“未验证”。
