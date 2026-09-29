---
name: spatiotemporal_analysis
description: 分析一首中国古典诗词中的时间安排与空间组织。当用户提供一首词或诗，需要识别其中的时间序列（现在/过去/想象的未来）、空间移动（近处/远处、内/外、人间/天上）、虚实关系（实景/虚境）、视角变换时使用。此 skill 关注作品的"时空骨架"——作者用了哪些时间空间的跳接与对照来组织材料。不分析单个意象的语义（属于意象 skill），不做整体章法判断（属于章法 skill）。
---

# 时空结构分析

## 任务定义

输入：一首中国古典诗词的完整文本。

输出：该作品的时空骨架分析，包括时间序列、空间序列、虚实安排、视角分布。

## 分析范围

**做：**
- 标注每一句（或每个意象群）所处的时间维度（现在/过去/未来/无时态）
- 标注每一句的空间位置（具体的地理或方位标识）
- 识别时间跳接与空间跳接的发生位置
- 识别虚境（回忆、想象、梦境、假设）与实境（眼前所见）的分布
- 识别叙述视角的位置与切换

**不做：**
- 不分析意象本身的文化联想（属于意象 skill）
- 不分析整体章法、起承转合（属于章法 skill）
- 不分析声律、句法、字法
- 不评价时空安排的"高明程度"

## 分析步骤

### 步骤 1：句序切分

将全词按句切分（以句号、问号、感叹号为界，或词牌定义的句读）。每句给一个序号，如 L1、L2、L3...

### 步骤 2：时间标注

对每一句，判断其时间属性：

- `present`：当下、眼前
- `past`：过去、回忆
- `future`：将来、想象的未来
- `atemporal`：无明确时态（咏物的静态描写、永恒陈述）
- `dream`：梦境、幻境

如果一句内部含多个时态，标主要时态并在 note 中说明。

### 步骤 3：空间标注

对每一句，判断其空间属性：

- `location`：尽可能具体的空间标识（如"楼上"、"江边"、"塞外"、"室内"）
- `distance`：相对位置（近 / 中 / 远 / 极远）
- `interior_exterior`：室内 / 室外 / 无明显区分

如果一句内部含空间跳接（如"楼上→远江"），标注主要空间并说明跳接。

### 步骤 4：虚实标注

对每一句，判断虚实属性：

- `real`：实景，眼前所见所闻
- `virtual_memory`：虚境，回忆
- `virtual_imagination`：虚境，想象（包括对他处他人的设想）
- `virtual_hypothesis`：虚境，假设（"若是"、"何时"等条件）

### 步骤 5：视角分析

判断全词的叙述视角：

- `perspective_type`：第一人称 / 代言体 / 第三人称 / 对话体 / 不明
- `is_switched`：视角在词中是否切换
- 如果切换，标注切换发生的句序与切换方向

### 步骤 6：跳接识别

识别全词中的关键时空跳接点：

- 时间跳接：从一个时间维度切换到另一个的位置（如 L3 是 present，L4 是 past）
- 空间跳接：从一个空间切换到另一个的位置
- 虚实跳接：实/虚之间的切换位置

对每个跳接，标注：发生位置（哪两句之间）、跳接类型、跳接方向。

## 输出格式

严格按以下 JSON schema 输出，不要在 JSON 外加任何文字：

{
  "poem_title": "词牌·题目",
  "line_analysis": [
    {
      "line_id": "L1",
      "text": "原文句",
      "time": "present | past | future | atemporal | dream",
      "space": {
        "location": "具体空间标识",
        "distance": "near | middle | far | extreme",
        "interior_exterior": "interior | exterior | unclear"
      },
      "reality": "real | virtual_memory | virtual_imagination | virtual_hypothesis",
      "note": "如有跳接或多重属性，在此说明（30 字内）"
    }
  ],
  "perspective": {
    "type": "first_person | persona | third_person | dialogue | unclear",
    "is_switched": true,
    "switch_points": [
      {
        "between_lines": "L4-L5",
        "direction": "从代言体切换到第一人称"
      }
    ]
  },
  "transitions": [
    {
      "between_lines": "L3-L4",
      "type": "time | space | reality",
      "direction": "present→past（描述切换方向）",
      "note": "简短说明"
    }
  ],
  "summary": {
    "dominant_time_organization": "linear_present | flashback | parallel | atemporal_static | dream_woven",
    "dominant_space_organization": "static | outward_expansion | inward_contraction | parallel_layout | concentric",
    "virtual_real_pattern": "all_real | all_virtual | real_to_virtual | virtual_to_real | interwoven"
  }
}


## 边界与诚实原则

- 如果一句的时间属性确实模糊，标 `atemporal` 并在 note 中说明
- 如果空间没有明确标识（如纯写情感），`location` 字段填 "unspecified"
- 视角分析不要过度推断——如果全词都是景物描写没有"我"出现，标 `unclear` 而不是强行猜测
- summary 中的"主导时间组织"等高层判断要基于 line_analysis 的实际分布，不要直接套用模板