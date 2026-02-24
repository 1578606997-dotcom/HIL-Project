# HIL Gateway
### Neuro-compression Gateway for SLM→LLM Cascades

> **HIL (Human Interaction Language) is now positioned as a Neuro-compression Gateway**: a lightweight, structured instruction layer where small models (SLMs) pre-compress user intent before handing off to large models (LLMs).

---

## Vision

Natural-language prompting is expressive but often redundant for production AI systems.
HIL Gateway introduces a compact symbolic protocol that allows:

- **SLM-first intent compression** (edge-side / gateway-side)
- **LLM-side high-fidelity execution** with fewer tokens
- **Deterministic control surfaces** for enterprise workflows

In short: **SLMs compress, LLMs reason, HIL orchestrates.**

---

## Enterprise Value Proposition

HIL Gateway is purpose-built for two critical enterprise pain points:

- **Token Cost Pressure: 85/100 severity**
- **Response Latency Pressure: 70/100 severity**

By replacing verbose prompts with structured HIL commands, teams can reduce prompt overhead while improving predictability, routing, and observability in SLM-LLM cascade architectures.

---

## Measured Impact (RAG Competitive Analysis Scenario)

The following benchmark snapshot demonstrates production-style savings when a long competitive-analysis request is compressed into HIL before LLM execution.

| Scenario | Traditional Prompt Tokens | HIL Command Tokens | Tokens Saved | Saving Rate |
|---|---:|---:|---:|---:|
| RAG competitor analysis (observed best case) | 210 | 80 | 130 | **62%** |
| RAG competitor analysis (observed range) | 155–210 | 58–90 | 60–130 | **35%–62%** |

**Result:** In RAG competitor-analysis workflows, token savings have reached **62%** in measured runs.

---

## Why HIL for SLM→LLM Cascades

- **Compression before reasoning**: Push symbolic compression to SLM/gateway layer.
- **Lower marginal inference cost**: Fewer input tokens per LLM call.
- **Faster turn-around**: Reduced prompt size helps cut latency in multi-hop chains.
- **Better governance**: Symbolic grammar is auditable and easier to enforce with policy.

---

## HIL v0.1 Grammar

- **Action**: `?` Analyze, `!` Create, `>` Transform
- **Object**: `$` Document/Context, `@` RAG/Knowledge Base, `@vs` Compare & Contrast, `@top` Top Competitive Advantages
- **Modifier**: `{z}` Chinese output, `{b}` Bullet points, `{s}` JSON schema
- **Param**: `(n)` Limit to `n` points

Example:

```text
? : @vs(Apple, Tesla) {b} (5)
```

Interpreted as:

```text
Please analyze a compare-and-contrast analysis between Apple, Tesla and using bullet points and limited to 5 points.
```

---

## Project Stage

- **Stage 1: MVP Development (0–6 months)**

---

## Business Model

- **Open-core + SaaS augmentation**
  - Open source core: grammar spec, transcoder, benchmark, ecosystem extensions
  - SaaS layer: team policy, routing strategy, telemetry, cost and latency optimization dashboards

---

## Quick Start

```bash
python transcoder.py
python benchmark.py
```

> `benchmark.py` requires `tiktoken`.

```bash
pip install tiktoken
```

---

## 中文简介（简版）

HIL Gateway 正在从“人机交互语言”升级为“面向 SLM-LLM 级联架构的 Token 优化网关”。
核心思想是：让小模型先做结构化压缩，再把高密度指令交给大模型推理执行。
在 RAG 竞品分析场景中，实测 Token 节省率可达到 **62%**。
