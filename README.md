# HIL (Human-Interaction Language)

HIL 是一种用于 AI 指令的**结构化中间语言**，目标是以极简符号替代冗余自然语言，降低企业级 AI 部署中的 Token 成本与响应延迟。

## 愿景

推动人机交互从“自然语言冗余模式”进化为“结构化高效模式”。

## HIL v0.1 语法

- **Action**: `?` Analyze, `!` Create, `>` Transform
- **Object**: `$` Document/Context, `@` RAG/Knowledge Base
- **Modifier**: `{z}` 中文输出, `{b}` 列表输出, `{s}` JSON Schema 输出
- **Param**: `(n)` 限制输出条目数量

示例：

```text
? : $ {z, b} (3)
```

解码后：

```text
Please analyze the provided document and in Chinese and using bullet points and limited to 3 points.
```

## 价值与优势（SWOT 摘要）

- **技术前沿性**：结构化提示可在任务控制上提升一致性，研究结论显示可带来约 **10.7% 的准确性提升**。
- **市场需求明确**：企业 AI 落地面临高成本痛点，Token 成本严重度 **85/100**，延迟问题严重度 **70/100**。
- **可扩展性强**：语法可持续扩展，支持更多动作、对象与参数组合。

## 项目状态

- 当前阶段：**阶段 1：MVP 开发（0-6 个月）**

## 商业模式

- **开源核心 + SaaS 增值服务** 混合模式
  - 开源：基础语法、转码器、社区扩展
  - SaaS：团队协作、策略管理、观测分析、成本优化报表

## 快速开始

```bash
python transcoder.py
python benchmark.py
```

> 运行 `benchmark.py` 需要先安装 `tiktoken`：

```bash
pip install tiktoken
```
