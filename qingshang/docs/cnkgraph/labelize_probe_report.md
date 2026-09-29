# CNKGraph 自动笺注专项复测报告

> 测试时间：2026-06-20  
> 专项脚本：`scripts/probes/probe_cnkgraph_labelize.py`  
> 原始结果：`data/generated/cnkgraph_labelize_probe_20260620_134704.json`

## 1. 结论

**当前公开接口下，CNKGraph 自动笺注不能进入清商主线依赖。**

本轮没有发现可用的 labelize 调用方式：53 次总请求中，31 次为实际 labelize 请求，返回 2xx 的数量为 0。用于确认作品有效性的 4 次搜索、4 次作者作品列表和 12 次作品详情全部返回 200，因此不能把失败简单归因于无效 `writingId`。

最符合现有证据的判断是：

> `POST /api/tool/labelize` 的公开路由高度疑似已移除或迁移；`GET /api/writing/{writingId}/labelize` 的专用路由高度疑似不存在，当前请求可能落入了通用作品浏览路由。

这仍不是服务端代码层面的最终证明。存在未公开新路径、私有 host 或网关规则的可能，但继续盲猜路径的收益已经很低。除非 CNKGraph 提供方给出新文档，否则建议保持“暂缓”，同时推进多个稳定小接口组成的清商版半自动笺注。

## 2. 测试约束

- 总请求上限：80；实际请求：53。
- 每次请求完成后至少等待 0.5 秒，未做并发和压力测试。
- 只使用读取、搜索和文本分析请求，没有修改远端数据。
- 未修改 FastAPI 业务代码、数据库结构或 poems 数据契约。
- 测试 host：`https://api.cnkgraph.com`、`https://open.cnkgraph.com`。
- 响应证据完整保存在时间戳 JSON；单条响应最多保存 20,000 字符。

## 3. 结果总览

| 测试类别 | 请求数 | 结果 | 说明 |
|---|---:|---|---|
| Postman 原始请求 | 1 | 1 个 404 | JSON、北齐史传原文 |
| 路径与大小写变体 | 7 | 7 个 404 | 包含 `tools`、`Labelize`、`labels`、`annotations` |
| 备用 host | 2 | 2 个 404 | 两个 host 表现一致 |
| Content-Type | 2 | 2 个 404 | form-urlencoded、text/plain |
| JSON 字段别名 | 3 | 3 个 404 | `text`、`dynastyName`、`author` |
| 文本类型 | 4 | 4 个 404 | 短词组、单句、整首词、现代夹古文 |
| OPTIONS | 2 | 1 个 404、1 个 405 | writing 路径返回 `Allow: GET` |
| 作品搜索 | 4 | 4 个 200 | 杜甫、苏轼、周邦彦、李白 |
| 作者作品列表 | 4 | 4 个 200 | 为每位作者取得真实作品 ID |
| 作品详情确认 | 12 | 12 个 200 | 每位作者 3 首 |
| 真实作品 labelize | 12 | 12 个 404 | 全部返回“作者不存在” |

实际 labelize 请求合计 31 次，**0/31 返回 2xx**。其余 22 次用于 OPTIONS、发现作品和确认作品有效性。

## 4. 路径、方法与认证判断

### `POST /api/tool/labelize`

以下形式均返回 IIS 空 404：

- `POST /api/tool/labelize`
- `POST /Api/Tool/Labelize`
- `POST /api/tools/labelize`
- `POST /api/tool/Labelize`
- `OPTIONS /api/tool/labelize`

更换 JSON、form-urlencoded、text/plain，或更换字段和文本内容，都没有进入 400/415/422 等参数校验阶段。这表明服务端很可能没有匹配到公开路由，而不是请求体字段写错。

两个 host 的 canonical POST 都返回相同风格的 IIS 404，没有出现 401、403、`WWW-Authenticate`、token 或 permission 提示。因此本轮**没有证据支持“需要认证”**，但不能排除另有未公开的认证网关。

### `GET /api/writing/{writingId}/labelize`

`OPTIONS /api/writing/10000/labelize` 返回 405，并带有 `Allow: GET`；GET 则返回 404“作者不存在”。这并不能证明 labelize action 存在。

同样的“作者不存在”也出现在：

- `/api/writing/10000/labels`
- `/api/writing/10000/annotations`
- 路径大小写变体

因此更合理的解释是：这些三段路径被通用的 writing/author 路由接收，然后把 `labelize`、`labels` 或 `annotations` 当成作者相关参数处理。若专用 labelize 路由仍存在，它至少没有在这些公开路径上优先匹配。

## 5. 真实作品交叉验证

以下 12 个作品均先通过 `GET /api/writing/{id}` 返回 200，再测试 labelize：

| 作者 | 作品 ID | 题名 | 详情 | labelize |
|---|---:|---|---:|---:|
| 杜甫 | 30790 | 李监宅 | 200 | 404 |
| 杜甫 | 31012 | 重题郑氏东亭 | 200 | 404 |
| 杜甫 | 31242 | 题张氏隐居二首 | 200 | 404 |
| 苏轼 | 358256 | 句 | 200 | 404 |
| 苏轼 | 136925 | 沁园春 | 200 | 404 |
| 苏轼 | 137166 | 醉落魄 述怀 | 200 | 404 |
| 周邦彦 | 165609 | 瑞龙吟 大石 | 200 | 404 |
| 周邦彦 | 474659 | 烛影摇红 | 200 | 404 |
| 周邦彦 | 165594 | 锁窗寒/琐寒窗 越调 | 200 | 404 |
| 李白 | 25812 | 赠孟浩然 | 200 | 404 |
| 李白 | 25691 | 见京兆韦参军量移东阳二首 | 200 | 404 |
| 李白 | 25820 | 赠薛校书 | 200 | 404 |

四位作者、诗与词、唐与北宋都得到相同结果，不符合“只支持部分作品”的特征。

## 6. 按预设标准判定

| 判定 | 结论 | 依据 |
|---|---|---|
| A. 可用 | 否 | 31 次 labelize 请求无一返回 2xx |
| B. 疑似需要认证 | 证据不足 | 没有 401/403 或认证相关响应头、错误信息 |
| C. 疑似路径废弃 | **是，当前最符合证据** | tool 路径在方法、载荷、host 变化下持续空 404；writing action 疑似被通用路由吞掉 |
| D. 疑似参数错误 | 否 | 没有进入 400/415/422 字段或格式校验阶段 |
| E. 疑似只支持部分作品 | 否 | 12 个已确认有效作品全部一致失败 |
| F. 不建议近期使用 | **是** | 当前没有成功调用方式，也没有稳定响应 schema 可供集成 |

## 7. 对清商的决策

### 近期

不等待 labelize，也不为它修改现有 API 或数据库。采用稳定的小接口构建候选链路：

```text
词句或用户选中文本
  -> glossary 词汇/典故候选
  -> reference 出处与化用
  -> char 单字信息
  -> ciTune / tones / rhyme 格律信息
  -> 清商内部 AnnotationCandidate
  -> 规则筛选与 LLM 综合解释
```

`AnnotationCandidate` 应是清商自己的窄模型，至少包含原文范围、候选类型、外部 ID、标题、摘要、来源和确认状态。CNKGraph 的完整响应不应直接成为前端契约。

### 后续复核条件

只有出现以下任一新证据时，才值得再次专项测试：

1. CNKGraph 提供方发布新的路径、认证或请求示例。
2. 搜韵前端出现可观察到的自动笺注网络请求。
3. Postman collection 更新了 labelize 定义。
4. 提供方确认当前 404 是临时故障。

在没有新证据时继续猜路径，只会增加远端请求而不会提高结论质量。

