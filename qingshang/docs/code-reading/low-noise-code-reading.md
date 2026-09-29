# 低噪声代码翻译法

这套方法用于阅读陌生 Python / 后端 / 框架代码。目标不是把代码讲成教程，而是快速回答三个问题：**这是什么实体、这是什么写法、它在这里做什么**。

默认只做第一层解释。解释中允许保留少量稳定术语，例如 ORM、泛型、依赖注入、构造调用。遇到真正卡住的术语，再单独追问第二层概念；如果第二层仍不够，再追问第三层机制。不要在每一行代码里把所有背景知识都展开。

## 一、基本原则

### 1. 按人的认知顺序解释，不机械从左到右翻译

解释一段代码时，优先遵循人的理解顺序：

1. 这整体是在声明、调用还是配置什么？
2. 关键名字是什么，用来表示什么？
3. 它在 Python / ORM / 框架层是什么类型或角色？
4. 它在数据库、HTTP、文件或外部服务层有什么效果？
5. 关键参数分别改变了什么规则？
6. 最后用一句话说明整段代码的效果。

### 2. 关键实体第一次出现时，紧跟实体分类

格式为：

```text
实体名【实体分类】
```

实体分类可以有双重身份，优先写成：

```text
名称【语法身份 / 工程身份】
```

例如：

```text
id【类属性 / ORM 字段】
PoemModel【类 / ORM 模型】
get_db【函数 / FastAPI 依赖函数】
db【函数参数 / 数据库会话】
```

这样既保留 Python 语法层，也保留框架工程层。

### 3. 分类词要短，不在【】里写解释

【】中只放短标签，不放长解释。常用标签包括：

```text
模块、类、函数、方法、变量、类属性、函数参数、关键字参数、属性、异常类
导入语句、函数调用、构造调用、方法调用、装饰器调用
类型标注、泛型类型标注、联合类型、异步函数、异步等待、元组、单元素元组语法
ORM 模型、ORM 字段、Pydantic 模型、数据库列、数据库约束、数据库会话、路由函数、依赖函数、响应模型、请求模型、配置项、服务函数、CRUD 函数
```

标签不是越多越好。只标当前理解代码所必需的关键实体。

### 4. 用短句解释“是什么 + 做什么”

推荐句式：

```text
XXX【实体分类】表示……
XXX【实体分类】声明……
XXX【实体分类】创建……
XXX=True【关键字参数】表示……
```

避免写成百科式说明。不要用“非常重要”“从底层机制看”“从框架设计角度看”这类过渡句，除非正在专门解释机制。

### 5. 函数名和函数调用合并解释

不要重复写：

```text
mapped_column 是一个函数。
mapped_column(...) 是一次函数调用。
```

直接写：

```text
mapped_column【函数】创建这个字段的列声明。
```

需要强调类被调用时，再区分：

```text
UniqueConstraint【类】表示唯一约束。
UniqueConstraint(...)【构造调用】创建一个唯一约束对象。
```

这种区分很重要：类不一定都意味着复杂业务对象。很多框架类的构造调用只是创建一份配置对象、规则对象或异常对象，交给框架之后读取。

### 6. 参数只解释最终效果

不要重复解释“参数名是什么”和“参数赋值是什么”。直接解释参数赋值的效果。

```text
primary_key=True【关键字参数】表示这一列是主键。
autoincrement=True【关键字参数】表示这一列自动递增。
nullable=True【关键字参数】表示这一列允许为空。
```

### 7. 特殊语法要指出名称，但不展开历史和底层机制

例如：

```text
Mapped[int]【泛型类型标注】表示这个 ORM 字段在 Python 层按 int 使用。
str | None【联合类型】表示字符串或空值。
await xxx【异步等待】表示等待异步操作完成。
(...)【元组】承载一组配置。
末尾逗号【单元素元组语法】保证只有一个元素时仍然是元组。
```

### 8. 框架特殊对象轻度解释，基础类型通常不解释

`Mapped`、`mapped_column`、`relationship`、`AsyncSession`、`Depends`、`BaseModel`、`Field`、`select`、`selectinload`、`HTTPException` 这类框架对象需要轻度说明。

`int`、`str`、`bool`、`list`、`dict`、`True`、`None` 这类基础类型通常不解释，除非当前代码正好卡在类型组合上。

### 9. 每段最后给一句“整段意思”

最后一句用于形成口述版：

```text
整段意思是：……
```

这句话应尽量短，帮助快速记住代码的实际作用。

### 10. 导入语句也要翻译，但只翻译“引入了什么工具”

导入语句通常不需要深挖模块内部，只需要说明：从哪个模块引入了哪些名称，这些名称在当前文件里大致用来做什么。

推荐顺序：

```text
1. 先说明 from ... import ... 是导入语句。
2. 说明模块名是什么。
3. 逐个说明被导入的类、函数或工具。
4. 最后说明整段导入是为了什么。
```

例如：

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
```

可以翻译为：

```text
from ... import ...【导入语句】表示从指定模块中引入名称。

sqlalchemy.orm【模块】提供 SQLAlchemy 的 ORM 相关工具。

Mapped【ORM 类型标注工具】用来标注 ORM 字段的 Python 类型。

mapped_column【函数】用来声明数据库表中的列。

relationship【函数】用来声明 ORM 对象之间的关系，例如 poem.sections。

整段意思是：从 SQLAlchemy 的 ORM 模块里引入字段类型标注、列声明和对象关系声明工具。
```

导入语句的解释不要写成“这个库很重要”“这个模块功能很多”。当前文件用到什么，就解释什么。

### 11. 遇到框架调用，要说明“框架接手后做了什么”

普通 Python 代码通常是你自己调用函数、自己传变量；框架代码常常相反：你先写声明，框架之后读取这些声明并自动调用函数、准备参数或生成响应。这就是阅读框架代码时最容易不安的地方。

因此，遇到 FastAPI、SQLAlchemy、Pydantic 这类框架调用时，第一层解释里要补一句“框架会偷偷做什么”，但仍然保持克制。

推荐句式：

```text
框架会在……时读取这个声明。
框架会根据这个配置自动……
这个函数不是你手动调用，而是由框架在……时调用。
这里先登记规则，真正执行发生在……之后。
```

例如：

```python
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

可以补一句：

```text
@app.get("/health")【装饰器调用】把 health_check 注册成 GET /health 的处理函数。
框架会在收到 GET /health 请求时自动调用 health_check，不是代码启动时立刻执行它。
```

再例如：

```python
db: AsyncSession = Depends(get_db)
```

可以补一句：

```text
Depends(get_db)【函数调用】声明 db 由 get_db 提供。
FastAPI 会在请求进入路由函数前自动调用 get_db，把得到的 session 传给 db。
```

框架背后动作只解释到“什么时候读、自动做什么”为止，不在第一层展开控制反转、依赖注入系统或 ORM 内部机制。

## 二、分层追问规则

第一层：低噪声代码翻译。只解释这是什么实体、是什么写法、当前做什么。

第二层：概念解释。只在卡住某个术语时追问，例如“构造调用是什么？”“泛型类型标注是什么？”

第三层：机制解释。只在确实需要理解背后原理时追问，例如“为什么类可以作为配置对象？”“FastAPI 为什么能自动调用 get_db？”

默认停在第一层，不主动展开第二层和第三层。

## 三、样例

### 样例 1：ORM 字段声明

代码：

```python
id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
```

翻译：

```text
id【类属性 / ORM 字段】声明一个名为 id 的字段，对应数据库表中的一列。

Mapped【ORM 类型标注工具】表示这个属性受 SQLAlchemy ORM 管理。

Mapped[int]【泛型类型标注】表示这个 ORM 字段在 Python 层按 int 整型使用。

mapped_column【函数】创建 id 字段的列声明。

primary_key=True【关键字参数】表示这一列是主键。

autoincrement=True【关键字参数】表示这一列自动递增。

整段意思是：声明一个名为 id 的 ORM 字段；它在 Python 里是 int，在数据库里是自增主键列。
```

### 样例 2：可为空的朝代字段

代码：

```python
dynasty: Mapped[str | None] = mapped_column(
    String(50),
    index=True,
    nullable=True,
    comment="朝代，例如唐、南唐、宋",
)
```

翻译：

```text
dynasty【类属性 / ORM 字段】声明“朝代”字段，对应数据库表中的一列。

这个字段用来保存作品所属朝代，例如“唐”“南唐”“宋”。

Mapped[str | None]【泛型类型标注】表示这个字段在 Python/ORM 层可以是字符串，也可以是空值。

str | None【联合类型】表示“字符串或空值”。

mapped_column【函数】创建 dynasty 字段的列声明。

String(50)【构造调用】表示数据库中这一列是长度约 50 的字符串列。

nullable=True【关键字参数】表示这一列允许为空。

index=True【关键字参数】表示给这一列建立索引，方便按朝代筛选查询。

comment=...【关键字参数】给这一列添加数据库注释。

整段意思是：在模型类里声明一个 dynasty 类属性；它作为 ORM 字段映射到数据库中的朝代列，可为空、可索引，并带有注释。
```

### 样例 3：导入 ORM 工具

代码：

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
```

翻译：

```text
sqlalchemy.orm【模块】提供 SQLAlchemy 的 ORM 相关工具。

Mapped【ORM 类型标注工具】用来标注 ORM 字段的 Python 类型。

mapped_column【函数】用来声明数据库表中的列。

relationship【函数】用来声明 ORM 对象之间的关系，比如 poem.sections。

from ... import ...【导入语句】表示从指定模块中引入这些名称。

整段意思是：从 SQLAlchemy 的 ORM 模块里引入字段类型标注、列声明和对象关系声明工具。
```

### 样例 4：表级唯一约束

代码：

```python
__table_args__ = (
    UniqueConstraint(
        "author",
        "author_order",
        name="uq_poems_author_author_order",
    ),
)
```

翻译：

```text
__table_args__【类属性】声明 SQLAlchemy 表级配置。

UniqueConstraint【类】表示唯一约束。

UniqueConstraint(...)【构造调用】创建一个唯一约束对象。

"author"【字符串参数】和 "author_order"【字符串参数】指定参与唯一约束的两个列名。

name="uq_poems_author_author_order"【关键字参数】给这个约束命名。

(...)【元组】承载这组表级配置。

末尾逗号【单元素元组语法】保证这里是只有一个元素的元组。

整段意思是：在这张表中，author 和 author_order 的组合不能重复。
```

### 样例 5：FastAPI 依赖注入

代码：

```python
db: AsyncSession = Depends(get_db)
```

翻译：

```text
db【函数参数 / 数据库会话变量】表示路由函数中使用的数据库会话。

AsyncSession【类 / 类型标注】表示这是一个异步数据库会话。

Depends【函数】告诉 FastAPI：这个参数不是用户直接传的，而是由依赖函数提供。

get_db【函数 / 依赖函数】负责创建并交出数据库 session。

Depends(get_db)【函数调用】表示让 FastAPI 调用 get_db 来准备 db。

FastAPI 会在请求进入路由函数前自动调用 get_db，把得到的 session 传给 db。

整段意思是：这个路由函数需要一个异步数据库 session，FastAPI 会在处理请求时通过 get_db 自动提供。
```

### 样例 6：异步数据库查询

代码：

```python
result = await db.execute(stmt)
```

翻译：

```text
result【变量】接收数据库执行结果。

await【异步等待】表示这里要等待异步操作完成。

db【变量 / 数据库会话】是一个 AsyncSession。

execute【方法】执行 SQLAlchemy 查询语句。

stmt【变量 / 查询对象】是前面构造好的查询。

整段意思是：用 db 执行 stmt 这条查询，并等待数据库返回结果。
```

## 四、使用边界

这套方法适合解释项目主链路中的关键代码，例如 ORM 模型、FastAPI 路由、Pydantic schema、数据库查询、LLM client 和分析器。

它不适合把每个 import、每个基础类型、每个框架内部调用都展开。解释的目标是降低阅读摩擦，而不是把每行代码变成一篇教程。

推荐使用方式：先用低噪声翻译读通主链路；遇到反复出现且真正碍事的术语，再单独追问概念；最后只对核心机制做深挖。
