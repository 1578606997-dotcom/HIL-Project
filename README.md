# HIL (Human-Interaction Language)

HIL 是一种用于 AI 指令的**结构化中间语言**，目标是以极简符号替代冗余自然语言，降低企业级 AI 部署中的 Token 成本与响应延迟。

## 愿景

推动人机交互从"自然语言冗余模式"进化为"结构化高效模式"。

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

## 项目结构

```
HIL-Project/
├── partial_hil_transcoder.py  # 局部符号化转码器（最新）
├── hil_spec_v02.py            # HIL v0.2 规范定义
├── auto_debug.py              # 自动调试工具
├── benchmark.py               # 性能基准测试
├── tests/
│   └── test_transcoder_v02.py # 单元测试
├── docs/                      # 设计文档
│   ├── OPS_PLAN.md
│   ├── BIDIRECTIONAL_HIL_DESIGN.md
│   └── ...
├── archive/                   # 归档的旧版本
│   ├── transcoder.py          # v0.1
│   ├── transcoder_v02.py      # v0.2 旧版
│   └── ...
└── README.md
```

## 快速开始

### 使用局部符号化转码器（推荐）

```python
from partial_hil_transcoder import PartialHILTranscoder

tc = PartialHILTranscoder()

# 编码：自然语言 → HIL
result = tc.transcode("请分析苹果公司财报，用中文输出，列出3个要点")
print(result.to_hil())  # 输出: ? "苹果公司财报" {z, b} (3)

# 解码：HIL → 自然语言
decoded = tc.decode("? \"苹果公司财报\" {z, b} (3)")
print(decoded)  # 输出: 分析"苹果公司财报"，中文，列表，限制3条
```

### 运行测试

```bash
# 运行单元测试
python tests/test_transcoder_v02.py

# 运行基准测试
python benchmark.py
```

> 运行 `benchmark.py` 需要先安装 `tiktoken`：

```bash
pip install tiktoken
```

## 版本历史

| 版本 | 文件 | 说明 |
|------|------|------|
| v0.3 | `partial_hil_transcoder.py` | 局部符号化（当前） |
| v0.2 | `archive/transcoder_v02.py` | 情感/语境支持 |
| v0.1 | `archive/transcoder.py` | 基础功能 |

## 项目状态

- 当前阶段：**MVP 开发**

## 商业模式

- **开源核心 + SaaS 增值服务** 混合模式
  - 开源：基础语法、转码器、社区扩展
  - SaaS：团队协作、策略管理、观测分析、成本优化报表
