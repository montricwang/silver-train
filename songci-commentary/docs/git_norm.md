# 📝 Git 提交规范手册 (详细扩展版)

本项目遵循 Conventional Commits 规范，格式为：`<type>: <description>`。

---

## 1. feat (新功能 / Features)
适用于你为项目增加了新逻辑、新语料或新界面。
- `feat: 接入全宋词语料库，数据量扩充至 80 万条`
- `feat: 实现基于词牌名的过滤功能`
- `feat: 增加搜索结果的“相似度百分比”显示`
- `feat: 增加“全诗阅读”弹窗组件`
- `feat: 接入 jieba 分词实现关键词预处理`

## 2. fix (缺陷修复 / Bug Fixes)
适用于修复代码逻辑错误、显示异常或崩溃。
- `fix: 修复搜索结果中繁体字乱码问题`
- `fix: 解决向量加载时内存溢出 (OOM) 的崩溃错误`
- `fix: 修正 FAISS 检索结果索引偏移导致作者对不上的问题`
- `fix: 修复侧边栏滑动条无法调节 top_k 的 bug`
- `fix: 修复特定 query 下 BERT 编码返回空值的异常`

## 3. docs (文档变更 / Documentation)
适用于修改 README、Backlog 或注释，不涉及代码逻辑。
- `docs: 在 README 中增加环境安装步骤 (pip install)`
- `docs: 更新 backlog.md，标记 v0.1.0 任务已完成`
- `docs: 在代码中增加 FAISS 索引原理的详细中文注释`
- `docs: 建立 git_norm.md 规范文档`

## 4. refactor (代码重构 / Refactor)
适用于为了代码更美观、更易读而做的修改（功能不变）。
- `refactor: 将 data_process.py 中的冗长逻辑拆分为多个独立函数`
- `refactor: 将模型加载路径统一管理到 config.py`
- `refactor: 重构 Streamlit 布局代码，减少组件嵌套层级`
- `refactor: 统一变量命名风格，从驼峰式改为下划线式`

## 5. perf (性能优化 / Performance)
适用于提升运行速度、降低资源占用的改动。
- `perf: 开启多进程加速宋词语料的向量化处理`
- `perf: 使用 @st.cache_resource 缓存 FAISS 索引，搜索响应提升 200%`
- `perf: 优化 BERT 推理过程，开启 FP16 半精度加速`
- `perf: 将 CSV 读取逻辑改为分块读取，降低峰值内存损耗`

## 6. chore (杂务 / Chores)
适用于不影响源码的外部配置改动。
- `chore: 初始化 .gitignore 屏蔽大型索引文件`
- `chore: 更新 requirements.txt，增加 torch 和 transformers 依赖`
- `chore: 调整项目文件夹结构，新建 docs/ 目录`
- `chore: 配置 GitHub Action 自动构建任务`

## 7. style (格式调整 / Style)
不影响代码逻辑的样式微调（空格、缩进、CSS）。
- `style: 调整 Streamlit 卡片背景颜色为古风淡青`
- `style: 统一代码缩进为 4 个空格`
- `style: 修正 README 中的排版对齐问题`

---

## 💡 提交进阶技巧

1. **组合提交？** ❌ 严禁一次 commit 同时包含 `feat` 和 `fix`。如果加了功能又顺手修了个 bug，请分两次提交。
2. **描述长度**：标题（第一行）尽量控制在 50 字以内。如果需要详细解释，在标题后空一行写具体内容。
3. **频率建议**：每当你完成 Backlog 中的一个 **Checkbox**，就是一个完美的提交时机。