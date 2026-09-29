# LLM 与证据工作流

清商当前最重要的设计边界是：LLM 不是事实来源。LLM 只在受控位置工作，事实证据来自已接入的 CNKGraph 工具。

## 1. 三种 LLM 用法

### 旧整首赏析

```text
POST /api/poems/{poem_id}/analyze
```

这条链路直接让 LLM 生成结构化赏析。它是早期能力，不是当前证据优先主线。

### 候选识别

```text
POST /api/poems/{poem_id}/allusion-candidates
```

LLM 只负责指出“哪些原文短语值得查证”，例如典故、文献化用、礼俗制度、历史地名、固定文学传统。

它不能输出已确认出处，不能把普通意象当典故。

### 证据审阅

```text
POST /api/poems/{poem_id}/allusion-candidates/with-review
```

Reviewer 只审阅后端已经查到的 CNKGraph evidence，不允许 Web Search，不允许凭记忆补充新出处。

## 2. 候选识别流程

```text
app/api/routes/poems.py
  -> read_allusion_candidates()
  -> app/services/allusion_candidate_extractor.py
  -> build_allusion_candidate_prompt()
  -> chat_completion()
  -> filter_allusion_candidates()
```

关键规则：

- `anchor_text` 必须原样出现在对应 `line_text` 中。
- 每句最多 2 个候选。
- 全词最多 10 个候选。
- `query_variants` 是查询提示，不是解释结论。
- 服务端会把模型自由 reason 归一成谨慎模板。

## 3. 完整可查单位

候选识别强调“完整可查单位”，意思是不要把会造成歧义的短语截得太短。

例子：

```text
燕台句 -> 不能截成 燕台
榆火 -> 不能截成 火
折柔条 -> 不能截成 柔条
前度刘郎 -> 不能截成 刘郎
```

这是为了让后续 CNKGraph 查询更接近当前词境。

## 4. 候选证据检索

```text
app/services/allusion_evidence.py
  -> 对每个候选取前 3 个 query_variants
  -> 调用 cnkgraph_tools 的典故和 reference 工具
  -> 每个 query/source 返回 hit/no_result/error
```

这里不调用 LLM。

CNKGraph 返回的 raw response 不直接展示给 Reader，而是被 `app/services/cnkgraph_tools.py` 转换为清商自己的窄字段。

## 5. Evidence Reviewer

```text
app/services/allusion_evidence_reviewer.py
  -> 输入候选 + evidence_results
  -> 调用 Evidence Reviewer LLM
  -> 校验模型引用的 evidence_id 是否存在
  -> 过滤不合规 best_evidence
  -> 返回审阅短注或证据不足
```

Reviewer 的角色分类：

| role | 中文 |
|---|---|
| `prior_source` | 前代来源 |
| `current_work_self_hit` | 当前作品自命中 |
| `later_reuse` | 后代沿用 |
| `weak_related` | 弱相关 |
| `irrelevant` | 无关或误命中 |
| `unknown` | 关系不明 |

## 6. 为什么当前作品自命中要降权

如果 CNKGraph 查到的结果就是当前周邦彦这首词，不能用它证明它自己。

所以程序会把这类证据标成：

```text
current_work_self_hit
```

它可以展示，但不能进入最佳证据。

## 7. 什么时候可以生成短注

只有在有合格 `best_evidence` 时，Reviewer 才能生成 1-2 句审阅短注。

如果证据不足，应该返回：

```text
insufficient_evidence
```

如果证据方向冲突或无法判断，应该返回：

```text
ambiguous
```

## 8. 当前没有做什么

当前没有接入：

- Web Search
- 本地 Poetry RAG
- CCPoem-Bert
- LangGraph / Agent
- 知人论世资料库
- 审阅结果数据库持久化

这些边界很重要。它们说明当前系统是“封闭证据集审阅”，不是开放式搜索智能体。

