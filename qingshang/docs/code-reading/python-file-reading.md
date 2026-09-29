# 低噪声 Python 文件阅读法

这份规则用于阅读一个 `.py` 文件、一个类、一个函数的整体职责。它和 `low-noise-code-reading.md` 分工不同：

- `low-noise-code-reading.md`：解释一行代码或一小段代码。
- `python-file-reading.md`：解释一个文件、类、函数在项目里的位置、职责和调用关系。

目标不是把代码讲成教程，而是帮助读者快速建立项目地图：这个文件为什么存在，这个类代表什么，这个函数被谁调用、处理什么、输出什么。

---

## 1. 总原则

阅读顺序优先按人的认知逻辑，而不是按源码从上到下机械解释。

推荐顺序是：

1. 这个文件在项目里属于哪一层？
2. 它负责什么？
3. 它对外提供哪些主要类或函数？
4. 谁会调用它？
5. 它又依赖谁？
6. 输入从哪里来？
7. 输出到哪里去？
8. 框架是否会自动读取、注册或调用其中的内容？
9. 它最容易误解的点是什么？

解释时保持低噪声：只说明当前理解代码所必需的信息。不要展开成长教程，不要解释基础 Python 类型，不要把每个 import 都百科化。

---

## 2. 文件级阅读格式

一个 `.py` 文件优先按这个格式解释：

```text
文件：app/services/poem_analyzer.py

职责：
把数据库中的词作转换成 LLM prompt，调用模型，并把返回内容校验成结构化分析结果。

所属层级：
Service 层 / LLM 分析层。

主要入口：
analyze_poem【函数 / 服务函数】。

上游调用：
app/api/routes/poems.py 中的分析接口。

下游依赖：
chat_completion【函数 / LLM 客户端函数】。
PoemAnalysis【Pydantic 模型 / 响应数据结构】。
PoemModel【ORM 模型】。

输入：
一首已经从数据库查出的 PoemModel，通常包含 sections 和 lines。

输出：
PoemAnalysis，表示结构化分析结果。

框架接手后做什么：
这个文件本身不会被框架直接当作路由调用；它由路由函数主动调用。

注意点：
LLM 可能返回非严格 JSON，所以需要 extract_json 做兜底解析。
```

文件级说明不要逐行解释 import。只需要说明重要依赖和它们在本文件中的作用。

---

## 3. 类级阅读格式

解释类时，先说它代表什么，再说字段、方法、关系。不要一开始逐字段铺开。

推荐格式：

```text
PoemModel【类 / ORM 模型】表示 poems 表中的一首词。

主要职责：
保存词作的元信息和正文缓存，例如作者、词牌、题名、宫调、full_text。

主要字段：
poem_id【类属性 / ORM 字段】是业务稳定编号，例如 zhoubangyan-0001。
author_order【类属性 / ORM 字段】表示该作者内部的作品排序。
full_text【类属性 / ORM 字段】保存整首词正文缓存。

对象关系：
sections【类属性 / ORM 关系】表示这首词包含的片段列表。

框架接手后做什么：
SQLAlchemy 会读取这个类中的字段声明和关系声明，把它映射到数据库表 poems。

注意点：
id 是数据库内部主键；poem_id 是面向业务和 API 的稳定编号，两者不是一回事。
```

类级解释要区分两类身份：

```text
PoemModel【类 / ORM 模型】
poem_id【类属性 / ORM 字段】
sections【类属性 / ORM 关系】
UniqueConstraint【类 / 约束声明工具】
```

如果一个类只是配置、约束、异常或 schema，也要说明它的角色，不要默认把所有类都理解成“复杂业务对象”。

---

## 4. 函数级阅读格式

函数级说明只回答“被谁调用、输入什么、处理什么、输出什么”。

推荐格式：

```text
get_poem_by_poem_id【函数 / CRUD 函数】

被谁调用：
诗词详情接口和分析接口。

输入：
db【函数参数 / 数据库会话】：用于执行数据库查询。
poem_id【函数参数】：词作业务编号。

处理：
构造查询语句。
按 poem_id 查询 poems 表。
使用 selectinload 预先加载 sections 和 lines。

输出：
找到时返回 PoemModel。
找不到时返回 None。

可能失败：
数据库连接失败、表不存在、字段名不匹配。

框架接手后做什么：
这个函数不是 FastAPI 自动调用的路由函数，而是被路由函数主动调用。
```

函数级说明中，如果是框架函数，要特别说明框架何时自动调用它。

例如：

```text
get_db【函数 / FastAPI 依赖函数】

被谁调用：
由 FastAPI 在处理带有 Depends(get_db) 的路由时自动调用。

输入：
无显式参数。

处理：
创建一个 AsyncSession。
通过 yield 把 session 交给路由函数。
请求结束后自动关闭 session。

输出：
一次请求期间可用的数据库 session。

框架接手后做什么：
FastAPI 会在请求进入路由函数前推进 get_db，把 yield 出来的 session 传给路由参数；请求结束后再继续执行 yield 后面的清理流程。
```

---

## 5. 框架接手行为必须说明

普通 Python 代码通常是“我调用函数，函数立刻执行”。框架代码经常是“我写声明，框架稍后读取这个声明并自动做事”。

遇到下面这些情况，要补一句“框架接手后做什么”：

```text
@app.get(...)
@router.post(...)
Depends(get_db)
BaseModel 子类
ORM 模型类
relationship(...)
__table_args__
Settings()
```

示例：

```python
@router.get("/{poem_id}")
async def read_poem_detail(...):
    ...
```

低噪声解释：

```text
@router.get("/{poem_id}")【装饰器调用】把 read_poem_detail 注册成 GET /api/poems/{poem_id} 的处理函数。

read_poem_detail【异步函数 / 路由函数】负责处理单首词作详情请求。

框架接手后做什么：
FastAPI 在收到匹配路径的 HTTP 请求时，会自动调用 read_poem_detail，并把路径参数、查询参数和依赖参数准备好。
```

这类说明的目的，是解决“控制反转”带来的不安感：代码不是没有执行，而是由框架在合适的时机自动执行。

---

## 6. 源码内注释与文档说明的边界

不要把所有解释都塞进源码注释。优先把完整阅读说明写到 `docs/code-reading/*.md`。

源码内只适合补三类注释：

1. 框架偷偷做了什么。
2. 这行为什么不能省略。
3. 很容易误解的边界。

适合放进源码的注释：

```python
# FastAPI 会在请求进入路由函数前调用 get_db，
# 并把 yield 出来的 session 传给路由参数 db。
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

不适合放进源码的注释：

```python
# 导入 FastAPI
from fastapi import FastAPI
```

这种注释对理解项目帮助很小，反而会让代码变吵。

---

## 7. 不要解释到哪种程度

文件级、类级、函数级阅读不是教程。默认不要展开：

```text
SQLAlchemy 内部状态机
FastAPI 依赖注入源码
asyncpg 连接池内部实现
Pydantic 校验器底层机制
Python 元类或描述符机制
```

第一层只需要能回答：

```text
它是什么？
它负责什么？
谁调用它？
它调用谁？
输入是什么？
输出是什么？
框架是否自动接手？
```

如果某个术语或机制仍然卡住，再单独进入第二层追问。

---

## 8. 与低噪声代码翻译法的配合

阅读一个文件时，先用本方法建立整体地图：文件、类、函数的职责和调用关系。

遇到某一行具体代码看不懂时，再使用 `low-noise-code-reading.md` 中的行级翻译法。

推荐顺序：

```text
文件级：这个文件负责什么。
类级：这个类代表什么。
函数级：这个函数输入、处理、输出什么。
行级：关键语句是什么写法，在这里做什么。
```

不要反过来一上来逐行分析。逐行分析容易让人陷入 import、参数、语法细节，反而看不见项目主链路。

---

## 9. 样例：session.py

```text
文件：app/db/session.py

职责：
创建数据库连接入口和数据库会话工厂，并提供 FastAPI 路由使用的数据库依赖函数。

所属层级：
数据库基础设施层。

主要入口：
get_db【函数 / FastAPI 依赖函数】。

上游调用：
app/api/routes/poems.py 中使用 Depends(get_db) 的路由函数。

下游依赖：
settings.database_url【配置项】提供数据库连接字符串。
create_async_engine【函数】创建异步数据库引擎。
async_sessionmaker【函数】创建异步 session 工厂。

输入：
没有直接业务输入；数据库地址来自配置。

输出：
engine【变量 / 数据库引擎】。
AsyncSessionLocal【变量 / 数据库会话工厂】。
get_db【函数 / FastAPI 依赖函数】。

框架接手后做什么：
FastAPI 在路由参数中看到 Depends(get_db) 时，会自动调用 get_db，为本次请求准备数据库 session。

注意点：
engine 不是一次具体查询；AsyncSessionLocal 也不是 session 本身，而是创建 session 的工厂。
```

---

## 10. 样例：poems.py 路由文件

```text
文件：app/api/routes/poems.py

职责：
定义诗词相关 HTTP API，包括词作列表、词作详情和词作分析。

所属层级：
API 路由层。

主要入口：
read_poem_list【异步函数 / 路由函数】。
read_poem_detail【异步函数 / 路由函数】。
analyze_poem_detail【异步函数 / 路由函数】。

上游调用：
FastAPI 根据 HTTP 请求路径和方法自动调用对应路由函数。

下游依赖：
get_db【函数 / FastAPI 依赖函数】提供数据库 session。
list_poems【函数 / CRUD 函数】查询词作列表。
get_poem_by_poem_id【函数 / CRUD 函数】查询单首词作。
analyze_poem【函数 / 服务函数】调用 LLM 分析词作。

输入：
HTTP 路径参数、查询参数，以及 FastAPI 自动注入的数据库 session。

输出：
Pydantic 响应模型或结构化 JSON。

框架接手后做什么：
FastAPI 会根据路由装饰器注册表匹配请求，自动解析参数、调用依赖函数、执行路由函数，并把返回值序列化为 HTTP 响应。

注意点：
路由文件不应该直接堆大量数据库查询细节；查询逻辑应放在 CRUD 层，LLM 分析逻辑应放在 service 层。
```

