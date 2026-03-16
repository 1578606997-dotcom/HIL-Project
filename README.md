# HIL (Human-Interaction Language)

HIL 是一种用于 AI 指令的**结构化中间语言**，目标是以极简符号替代冗余自然语言，降低企业级 AI 部署中的 Token 成本与响应延迟。

## 愿景

推动人机交互从“自然语言冗余模式”进化为“结构化高效模式”。

## HIL 语法版本

### HIL v0.2（最新）- 支持情感与语境

- **Action**: `?` Analyze, `!` Create, `>` Transform, `@` Query
- **Object**: `$` Document, `@` Knowledge Base
- **Modifier**: `{z}` 中文, `{b}` 列表, `{s}` JSON, `{e}` 英文
- **Param**: `(n)` 限制条目数
- **Emotion**: `[!urgent]` 紧急, `[+positive]` 积极, `[~negative]` 负面, `[?polite]` 礼貌
- **Context**: `<+continuation>` 继续, `<+correction>` 纠正, `<+example>` 举例

**v0.2 示例**：

```text
? : $ {z, b} (3) [!urgent] <+continuation>
```

解码后：

```text
Continuing to urgently analyze the provided document in Chinese using bullet points limited to 3 items.
```

### HIL v0.1（基础）

- **Action**: `?` Analyze, `!` Create, `>` Transform
- **Object**: `$` Document/Context, `@` RAG/Knowledge Base
- **Modifier**: `{z}` 中文输出, `{b}` 列表输出, `{s}` JSON Schema 输出
- **Param**: `(n)` 限制输出条目数量

**v0.1 示例**：

```text
? : $ {z, b} (3)
```

## 价值与优势（SWOT 摘要）

- **技术前沿性**：结构化提示可在任务控制上提升一致性，研究结论显示可带来约 **10.7% 的准确性提升**。
- **市场需求明确**：企业 AI 落地面临高成本痛点，Token 成本严重度 **85/100**，延迟问题严重度 **70/100**。
- **可扩展性强**：语法可持续扩展，支持更多动作、对象与参数组合。

## 项目结构

```
HIL-Project/
├── hil_spec.py              # HIL v0.1 规范定义
├── hil_spec_v02.py          # HIL v0.2 规范定义（含情感/语境）
├── transcoder.py            # v0.1 转码器
├── transcoder_v02.py        # v0.2 增强转码器
├── benchmark.py             # 性能基准测试
├── tests/
│   └── test_transcoder_v02.py  # v0.2 单元测试
├── OPS_PLAN.md              # 运维计划
└── README.md                # 项目文档
```

## 项目状态

- 当前阶段：**阶段 1：MVP 开发（0-6 个月）**

## 商业模式

- **开源核心 + SaaS 增值服务** 混合模式
  - 开源：基础语法、转码器、社区扩展
  - SaaS：团队协作、策略管理、观测分析、成本优化报表

## 快速开始

### 基础使用 (v0.1)

```bash
python transcoder.py
```

### 增强版使用 (v0.2) - 支持情感与语境

```bash
python transcoder_v02.py
```

**v0.2 使用示例**：

```python
from transcoder_v02 import HILTranscoderV2

tc = HILTranscoderV2()

# 编码：自然语言 → HIL
hil = tc.reverse_translate("请立即分析这份文档，继续之前的分析")
print(hil)  # 输出: ? : $ [!urgent,?polite] <+continuation>

# 解码：HIL → 自然语言
decoded = tc.decode("? : $ {z} [!urgent] <+continuation>")
print(decoded)  # 输出: continuing to urgently analyze the provided document in Chinese
```

### 运行测试

```bash
# 运行 v0.2 单元测试
python tests/test_transcoder_v02.py

# 运行基准测试
python benchmark.py
```

> 运行 `benchmark.py` 需要先安装 `tiktoken`：

```bash
pip install tiktoken
```
