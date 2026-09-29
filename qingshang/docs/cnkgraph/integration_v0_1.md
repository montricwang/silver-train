# CNKGraph Tool Layer v0.1

## 1. 本轮边界

本轮把已实测可访问的近期 CNKGraph 接口封装为清商自己的只读工具层。目标是为单首词阅读提供典故、出处、字典、词谱和韵典候选，不建设完整知识库，也不做 Agent 或 LLM 综合解释。

没有修改 `poems`、`poem_sections`、`poem_lines` 三张表，没有新增 ORM 模型或数据库迁移，也没有把 CNKGraph ID 写入本地核心数据。

## 2. 接入的外部接口

`CNKGraphClient` 当前封装：

| CNKGraph 接口 | 用途 |
|---|---|
| `GET /api/char/{char}` | 单字信息 |
| `POST /api/glossary/典故/find` | 典故候选 |
| `GET /api/glossary/{kind}/{id}` | 词典、典故或佛典详情 |
| `POST /api/ciTune/find` | 词牌搜索 |
| `GET /api/ciTune/{id}` | 词谱详情 |
| `POST /api/ciTune/pattern` | 平仄片段匹配 |
| `POST /api/rhyme/find` | 单字韵书信息 |
| `POST /api/tool/reference` | 出处与化用候选 |
| `GET /api/writing/{id}` | 外部作品详情 |
| `GET /api/writing/{id}/tones` | 作品平仄 |
| `GET /api/writing/{id}/bookLinks` | 古籍出处与引用 |

客户端公开方法均通过 `_request_json()` 发送请求。网络错误、超时、非 2xx 和 JSON 解析错误统一转换为 `CNKGraphClientError`。

## 3. 暂不接入的接口

### 自动笺注

不接入：

- `POST /api/tool/labelize`
- `GET /api/writing/{writingId}/labelize`

专项复测中 31 次 labelize 调用没有一次返回 2xx，12 个已确认有效的作品也全部返回 404。详见 `docs/cnkgraph/labelize_probe_report.md`。

### 中远期领域

人物、地理、年历、古籍、类书和曲谱暂不正式接入。它们需要实体消歧、版本与来源管理或跨文体产品设计，不属于单首宋词阅读的最小闭环。

## 4. 清商窄响应模型

清商 API 不直接返回第三方完整结构，而使用：

- `EvidenceItem`：具体落点、判断、证据文本、来源和匹配状态。
- `AllusionCandidate`：典故关键词、解释、出处和原文候选。
- `ProsodyAid`：词牌名、声律信息和韵典证据。
- `ReadingAidResponse`：一首词、选中文本、工具结果与局部错误的聚合结果。

`raw` 只用于调试、溯源和后续适配。前端应读取清商字段，不依赖 `raw` 内的 CNKGraph 字段；外部字段变化时，修改适配层即可，不应改变清商 API 的主要契约。

## 5. 清商接口

### 直接工具接口

| Method | Path | 返回 |
|---|---|---|
| `GET` | `/api/cnkgraph/char/{char}` | `EvidenceItem[]` |
| `GET` | `/api/cnkgraph/allusions?key=...` | `AllusionCandidate[]` |
| `POST` | `/api/cnkgraph/reference` | `EvidenceItem[]` |
| `GET` | `/api/cnkgraph/ci-tunes?key=...` | `EvidenceItem[]` |
| `POST` | `/api/cnkgraph/rhyme` | `EvidenceItem[]` |

直接工具接口的上游错误返回 HTTP 502，便于 Swagger 调试时区分清商参数错误和外部服务错误。

### 阅读器聚合接口

`POST /api/poems/{poem_id}/reading-aids`

```json
{
  "selected_text": "前度刘郎",
  "line_no": 13,
  "include": ["allusion", "reference", "char", "ci_tune", "rhyme"]
}
```

接口先读取本地诗词。`line_no` 存在时会验证对应词句；`selected_text` 优先，否则使用该句正文。它只调用 `include` 指定的工具，不调用 LLM。

字典与韵典按选中文本中的不重复文字查询，单次聚合最多取 30 个字符，避免一次阅读请求产生无界外部调用。

## 6. 失败降级

reading-aids 对每个工具独立捕获 `CNKGraphClientError`：

- 已成功的其他工具结果照常返回。
- 失败工具返回空结果。
- 错误写入 `ReadingAidResponse.errors`。
- 本地词作不存在仍返回 404；`line_no` 不存在或没有可用文本返回 400。

因此 CNKGraph 断网、超时或返回错误状态不会让整页阅读失败。v0.1 尚未实现缓存、重试或熔断；这些应在确认调用许可和频率限制后加入。

## 7. 配置与验证

环境变量：

```env
CNKGRAPH_BASE_URL=https://api.cnkgraph.com
CNKGRAPH_TIMEOUT_SECONDS=10
```

验证命令：

```powershell
.venv\Scripts\python.exe -m compileall app scripts tests
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m pytest
```

测试使用 `httpx.MockTransport` 和异步 mock，不请求真实 CNKGraph。真实接口只用于独立冒烟验证，不作为自动测试的一部分。

## 8. 后续方向

下一轮可在不改变现有窄模型的前提下增加缓存和契约样本测试，再把多个证据候选交给规则或 LLM 做筛选与解释。LLM 综合解释、Agent 编排、持久化注评和中远期领域接口均不在 v0.1 范围内。
