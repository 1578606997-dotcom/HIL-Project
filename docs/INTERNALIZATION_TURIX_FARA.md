# Turix & Fara 内化研究方案

## 项目分析

### Turix (TuriX-CUA)
- **核心**: 完整的开源 CUA 解决方案
- **特点**:
  - 68%+ OSWorld 测试通过率
  - OpenClaw Skill 支持 (!!!)
  - 多模型架构 (multi-agent)
  - 可恢复记忆压缩 (Recoverable Memory Compression)
  - Skills 系统（可复用的 markdown playbook）
  - 支持 Qwen3-VL
  - macOS + Windows 支持

### Fara-7B (Microsoft)
- **核心**: 7B 参数的超小型 Agentic Model
- **特点**:
  - 微软首个 SLM 级别的 CUA
  - 仅 7B 参数，可本地部署
  - 平均每任务 16 步（对比其他模型的 41 步）
  - 基于 Qwen2.5-VL-7B
  - 145K 合成数据训练
  - Magentic-One 框架
  - 直接预测坐标（无需 accessibility tree）

---

## 内化策略

### 第一阶段：学习借鉴（1-2 周）

#### 1.1 架构学习
- [ ] 深入研究 Turix 的多模型架构
- [ ] 分析 Fara-7B 的轻量级设计
- [ ] 对比我们的 Desktop Control Skill 架构

#### 1.2 关键技术点
**Turix 值得学习**:
- ✅ OpenClaw Skill 集成方式
- ✅ 多模型协作架构
- ✅ 可恢复记忆压缩
- ✅ Skills/Playbook 系统

**Fara-7B 值得学习**:
- ✅ 小模型高效推理（7B 参数）
- ✅ 直接坐标预测（无需 accessibility tree）
- ✅ 合成数据训练方法
- ✅ 步骤优化（16 vs 41 步）

---

### 第二阶段：差异化定位（2-3 周）

#### 2.1 我们的优势
| 维度 | Turix | Fara-7B | Desktop Control Skill |
|------|-------|---------|----------------------|
| 集成 | OpenClaw Skill ✅ | 独立 | OpenClaw Skill ✅ |
| 参数 | 未公开 | 7B (小) | 灵活（可接任意模型）|
| 开源 | ✅ 完全开源 | ✅ 开源 | ✅ 开源 |
| 浏览器扩展 | ❌ | ❌ | ✅ 我们有！ |
| HIL 语言 | ❌ | ❌ | ✅ 独特！ |
| 符号神经融合 | ❌ | ❌ | ✅ 研究中！ |

#### 2.2 差异化方向
1. **HIL + SNF 集成**：用符号压缩优化 CUA 性能（独特优势）
2. **浏览器扩展 v2.0**：Turix/Fara 没有浏览器扩展
3. **OpenClaw 生态**：Turix 也有，但我们可以更深入集成
4. **双语/本地化**：针对中文用户优化

---

### 第三阶段：技术内化（3-4 周）

#### 3.1 从 Turix 借鉴
```python
# 学习点 1: OpenClaw Skill 更紧密集成
# 当前我们的 Skill 是独立的，可以学习 Turix 的集成方式

# 学习点 2: Skills/Playbook 系统
# 创建可复用的任务模板（如：GitHub 运维模板）

# 学习点 3: 多模型架构
# 不依赖单一模型，多模型协作
```

#### 3.2 从 Fara-7B 借鉴
```python
# 学习点 1: 直接坐标预测
# 我们的 browser-extension 可以借鉴

# 学习点 2: 步骤优化
# 减少交互步骤，提高效率

# 学习点 3: 小模型适配
# 让 Desktop Control 也能用小模型高效运行
```

#### 3.3 独创性增强
```python
# 核心创新: HIL + CUA
# 将自然语言指令压缩为 HIL 符号
# 用符号驱动桌面/浏览器操作
# 减少 token 消耗，提高速度
```

---

### 第四阶段：项目整合（持续）

#### 4.1 代码层面
- [ ] 研究 Turix 源码（GitHub 克隆）
- [ ] 研究 Fara-7B 模型架构
- [ ] 提取可复用组件

#### 4.2 文档层面
- [ ] 在 SNF 项目中引用 Turix/Fara
- [ ] 撰写技术对比文章
- [ ] 明确差异化定位

#### 4.3 社区层面
- [ ] 向 Turix/Fara 项目学习社区运营
- [ ] 寻找合作机会（互补而非竞争）
- [ ] 参与他们的 Discord/GitHub Discussions

---

## 行动计划

### 立即执行
1. **克隆 Turix 源码**
   ```bash
   git clone https://github.com/TurixAI/TuriX-CUA.git
   ```

2. **研究 Fara-7B 论文**
   - 阅读：https://arxiv.org/abs/2511.19663
   - 了解训练方法和架构设计

3. **更新 Desktop Control Skill README**
   - 添加与 Turix/Fara 的对比
   - 突出我们的差异化优势

### 本周完成
- [ ] Turix 架构分析报告
- [ ] Fara-7B 技术要点总结
- [ ] 我们的差异化定位文档

### 本月完成
- [ ] 借鉴关键技术点（多模型、坐标预测等）
- [ ] 集成到 Desktop Control Skill v0.2.0
- [ ] 发布技术对比博客

---

## 关键洞察

**Turix 和 Fara 证明了 CUA 方向的价值**：
- Turix: 68%+ 成功率，活跃开发
- Fara: 微软大厂入局，7B 小模型可行

**我们的机会**：
1. **HIL + SNF**：这是独一无二的技术路线
2. **浏览器扩展**：Turix/Fara 没有
3. **OpenClaw 深度集成**：可以比 Turix 更深入

**不是竞争，是差异化共存**。
