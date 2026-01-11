# 语言学分析工作流与资源指南 (基于 Antigravity 平台)

本指南旨在总结本次“综合国力” (Comprehensive National Power) 翻译研究中的方法论，为后续以 AI 辅助编码为主要手段的语言学分析提供参考。

## 1. 核心资源库 (Resource Inventory)

我们的分析主要依赖三大核心数据源，分别对应不同的分析维度。

### 1.1 中国政治语料库 (Chinese Political Corpora)
*   **类型**: 本地数据库 (Local DuckDB)
*   **位置**: `/app/dev/chinese-political-corpora/corpus.duckdb`
*   **内容**: 
    *   历届党代会报告 (中文 & 英文译本)
    *   政府工作报告 (1954-至今)
*   **用途**: 
    *   **历时分析 (Diachronic Analysis)**: 追踪特定术语（如“综合国力”）在不同年份的使用频率。
    *   **译法演变 (Translation Evolution)**: 比如发现从 "Overall National Strength" 到 "Comprehensive National Power" 的转变。
    *   **上下文检索 (KWIC)**: 提取术语的搭配词 (Collocations) 和语境。

### 1.2 美国总统语料库 (US Presidential Corpus)
*   **类型**: 远程 API 服务 (Corpus Service)
*   **访问方式**: 
    *   MCP Tool (`search_corpus`, `search_phrases`)
    *   Direct API (`curl` to `https://corpus-production.up.railway.app`)
*   **内容**: 全量美国总统公开演说、文告、辩论记录。
*   **用途**: 
    *   **本族语验证 (Nativeness Verification)**: 验证某个译法（如 "Composite Power"）是否存在于英语母语政治话语中。
    *   **概念对齐 (Conceptual Alignment)**: 寻找中式概念（如“综合”）在美式英语中的实际对应词（如 "National Power" + "all elements of"）。
    *   **修饰语分析 (Modifier Analysis)**: 检查 "Composite", "Comprehensive" 等词的真实搭配习惯（如 composite 搭配 materials）。

### 1.3 MCP 词典服务 (Dictionary Service)
*   **类型**: MCP Tool (`define_word`)
*   **内容**: 集成 Chambers, EC Dict (英汉大词典), Rightword 等多本权威词典。
*   **用途**: 
    *   **语义辨析 (Semantic Discrimination)**: 区分近义词的细微差别（如 Comprehensive 侧重 *Scope*, Composite 侧重 *Parts*）。
    *   **术语确认**: 检查某个短语是否已被词典收录。

---

## 2. 技术手段与工具 (Technical Methods)

在 Antigravity 平台上，我们通过编写和执行代码来“驱动”这些语料库。

### 2.1 Python 脚本分析 (Local Analysis)
适用于处理本地 DuckDB 数据。
*   **关键库**: `duckdb`, `pandas`, `re`
*   **典型脚本**: `/app/dev/chinese-political-corpora/analyze_english_evolution.py`
*   **工作流**:
    1.  连接 DuckDB。
    2.  编写 SQL 查询提取包含目标词的文本。
    3.  使用 Pandas 或 Regex 进行频率统计和关键词提取。
    4.  输出上下文片段以供人工审核。

### 2.2 Node.js / Curl 远程调用 (Remote Analysis)
适用于访问 MCP 或外部 API，特别是当需要快速验证或 MCP 接口不稳定时。
*   **关键工具**: `curl`, `node`
*   **典型命令**:
    ```bash
    # 查找 "composite" 作为修饰语的搭配
    curl -s -X POST https://corpus-production.up.railway.app/query/collocations \
    -H "Content-Type: application/json" \
    -d '{"word": "composite", "role": "modifier", "limit": 50}'
    ```
*   **优势**: 速度快，直接绕过中间层，便于获取原始 JSON 数据进行清洗。

### 2.3 网络验证 (Web Verification)
*   **工具**: `search_web`, `read_url_content`
*   **用途**: 当语料库数据滞后时（如“最近几年”的趋势），使用网络搜索验证最新的官方文件（如最新发布的白皮书或 MFA 半官方译文）。

---

## 3. AI 辅助分析的最佳实践 (Best Practices)

基于本次经验，进行语言学分析时建议遵循以下 **Agentic Workflow**：

1.  **假设驱动 (Hypothesis Driven)**:
    *   不要只问“这个词怎么翻”，而要建立假设：“官方译法可能随时间改变了”或“这个词在美式英语中可能不自然”。
    
2.  **三角验证 (Triangulation)**:
    *   **内部验证**: 查本地语料库（历史演变）。
    *   **外部验证**: 查目标语语料库（自然度）。
    *   **词典验证**: 查定义（理论依据）。
    *   只有三者结合，才能得出如“Composite 是学术精准但政治失语”这样的深度结论。

3.  **批判性编码 (Critical Coding)**:
    *   编写脚本时，要考虑到数据可能不存在的情况（处理 Empty Result）。
    *   如果在 API 中查不到（如 "Comprehensive Power" 为 0），不要轻易放弃，尝试搜索其近义词 ("National Power") 或反向搜索（搜索该词修饰了什么）。

4.  **动态更新 (Iterative Refinement)**:
    *   将分析结果实时回填到文档（如 Blog Post）中。
    *   如果发现新证据（如用户提供的外部链接），立即编写新脚本（如 `verify_composite_trend.py`）进行定向爆破查证。

---

*此文档可作为后续进行类似术语分析（如 "New Quality Productive Forces / 新质生产力"）的操作手册。*
