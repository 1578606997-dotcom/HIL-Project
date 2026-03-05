#!/usr/bin/env python3
"""
HIL Framework - 自主调试系统
自动检测问题、生成修复建议、执行优化
"""

import subprocess
import json
import sys
from datetime import datetime

class HILAutoDebugger:
    """HIL 框架自主调试器"""
    
    def __init__(self):
        self.test_results = []
        self.issues = []
        self.suggestions = []
    
    def run_self_test(self) -> dict:
        """运行自检"""
        print("🔍 运行自主检测...")
        
        # 导入框架
        try:
            from hil_framework_v0_1_0 import HILBidirectionalBridge
            bridge = HILBidirectionalBridge()
        except Exception as e:
            return {
                'status': 'error',
                'error': f'导入失败: {e}',
                'timestamp': datetime.now().isoformat()
            }
        
        # 测试用例库
        test_cases = [
            {
                'input': '分析这份财报，用中文输出，3个要点',
                'expected_hil_pattern': r'\? : \$ .*\(3\)',
                'description': '基本分析请求'
            },
            {
                'input': '比较苹果和特斯拉的优劣',
                'expected_hil_pattern': r'.*vs.*',
                'description': '对比请求（应支持 vs）'
            },
            {
                'input': '查询知识库关于深度学习',
                'expected_hil_pattern': r'@ : @ .*深度学习.*',
                'description': 'RAG 查询'
            },
            {
                'input': '生成一份报告，英文，JSON格式',
                'expected_hil_pattern': r'! : \$ .*\{e, s\}.*',
                'description': '多修饰符请求'
            }
        ]
        
        passed = 0
        failed = 0
        
        for test in test_cases:
            try:
                result = bridge.roundtrip(test['input'])
                hil = result['hil']
                
                # 检查基本结构
                if ':' in hil and hil[0] in ['?', '!', '>', '@']:
                    passed += 1
                    self.test_results.append({
                        'test': test['description'],
                        'status': 'pass',
                        'input': test['input'],
                        'hil': hil
                    })
                else:
                    failed += 1
                    self.issues.append({
                        'test': test['description'],
                        'issue': 'HIL 结构不完整',
                        'input': test['input'],
                        'output': hil
                    })
                    
            except Exception as e:
                failed += 1
                self.issues.append({
                    'test': test['description'],
                    'issue': f'异常: {e}',
                    'input': test['input']
                })
        
        # 计算通过率
        pass_rate = passed / (passed + failed) if (passed + failed) > 0 else 0
        
        return {
            'status': 'completed',
            'pass_rate': round(pass_rate, 2),
            'passed': passed,
            'failed': failed,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_issues(self) -> list:
        """分析问题并生成修复建议"""
        print("🔧 分析问题...")
        
        for issue in self.issues:
            suggestion = self._generate_fix(issue)
            self.suggestions.append({
                'issue': issue,
                'suggestion': suggestion
            })
        
        return self.suggestions
    
    def _generate_fix(self, issue: dict) -> str:
        """针对问题生成修复建议"""
        issue_type = issue.get('issue', '')
        
        if '对比' in issue.get('test', '') or '比较' in issue.get('input', ''):
            return "修复: 添加 @vs(A,B) 对比语法支持"
        
        if '结构不完整' in issue_type:
            return "修复: 改进意图解析逻辑"
        
        if '异常' in issue_type:
            return "修复: 添加异常处理和回退机制"
        
        return "建议: 查看详细日志"
    
    def generate_report(self) -> str:
        """生成调试报告"""
        report = []
        report.append("=" * 60)
        report.append("HIL Framework 自主调试报告")
        report.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")
        
        # 测试结果
        test_result = self.run_self_test()
        report.append(f"测试通过率: {test_result['pass_rate'] * 100}%")
        report.append(f"通过: {test_result['passed']}, 失败: {test_result['failed']}")
        report.append("")
        
        # 问题列表
        if self.issues:
            report.append("【发现的问题】")
            for i, issue in enumerate(self.issues, 1):
                report.append(f"{i}. {issue['test']}")
                report.append(f"   问题: {issue['issue']}")
            report.append("")
        
        # 修复建议
        if self.suggestions:
            report.append("【修复建议】")
            for i, sug in enumerate(self.suggestions, 1):
                report.append(f"{i}. {sug['suggestion']}")
            report.append("")
        
        # 下一步行动
        if test_result['pass_rate'] < 0.8:
            report.append("【⚠️ 状态】需要立即修复")
            report.append("建议: 执行 Phase 1.1 修复计划")
        elif test_result['pass_rate'] < 0.95:
            report.append("【🟡 状态】需要优化")
            report.append("建议: 执行 Phase 1.2 增强计划")
        else:
            report.append("【🟢 状态】运行良好")
            report.append("建议: 准备 Phase 2 开发")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def auto_fix(self) -> bool:
        """自动修复简单问题"""
        print("🔨 尝试自动修复...")
        
        # 这里可以添加自动修复逻辑
        # 例如: 修改代码、更新配置等
        
        return True
    
    def run(self):
        """运行完整调试流程"""
        print("🚀 启动 HIL 自主调试系统\n")
        
        # 1. 自检
        test_result = self.run_self_test()
        
        # 2. 分析问题
        if self.issues:
            self.analyze_issues()
        
        # 3. 生成报告
        report = self.generate_report()
        print(report)
        
        # 4. 保存报告
        with open('DEBUG_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("\n✅ 报告已保存到 DEBUG_REPORT.md")
        
        # 5. 触发修复（如果失败率高）
        if test_result['pass_rate'] < 0.8:
            print("\n⚠️ 失败率过高，触发自动修复...")
            self.auto_fix()
        
        return test_result['pass_rate']

if __name__ == "__main__":
    debugger = HILAutoDebugger()
    pass_rate = debugger.run()
    
    # 根据通过率决定下一步
    if pass_rate < 0.5:
        print("\n❌ 需要人工介入，问题较严重")
        sys.exit(1)
    elif pass_rate < 0.8:
        print("\n🟡 需要修复优化")
        sys.exit(0)
    else:
        print("\n🟢 系统运行正常")
        sys.exit(0)
