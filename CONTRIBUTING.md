# Contributing to HIL-Gateway

感谢你对 HIL-Gateway 的兴趣！以下是参与项目的指南。

## 如何贡献

### 报告问题
- 使用 GitHub Issues 报告 bug
- 描述问题时请提供：
  - 复现步骤
  - 预期行为 vs 实际行为
  - 环境信息（Python 版本、操作系统）

### 提交代码
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 代码风格
- 行长度不超过 100 字符
- 为新功能添加测试
- 确保所有测试通过

## 开发环境

```bash
# 克隆仓库
git clone https://github.com/1578606997-dotcom/HIL-Project.git
cd HIL-Project

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install pytest  # 测试依赖

# 运行测试
pytest test_hil.py -v
```

## 项目结构

- `transcoder.py` - HIL 转码器核心
- `benchmark.py` - 性能测试工具
- `hil_spec.py` - HIL 语法规范
- `test_hil.py` - 测试文件

## 联系方式

如有问题，欢迎通过 GitHub Issues 讨论。
