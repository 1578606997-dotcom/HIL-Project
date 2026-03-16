#!/usr/bin/env python3
"""
HIL Framework v0.1.0 - Phase 1 Prototype
自然语言 → HIL 双向编解码框架

作者: CJ + OpenClaw AI
状态: 原型开发中
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# HIL 语法规范 V0.1
HIL_SPEC = {
    "actions": {
        "?": "analyze",
        "!": "create", 
        ">": "transform",
        "@": "rag_query"
    },
    "objects": {
        "$": "document",
        "@": "rag_object"
    },
    "modifiers": {
        "z": "chinese_output",
        "e": "english_output",
        "b": "bullet_format",
        "s": "json_schema",
        "t": "table_format"
    }
}

@dataclass
class HILIntent:
    """意图结构"""
    action: str
    object: str
    target: Optional[str] = None
    modifiers: Dict[str, any] = None
    constraints: Dict[str, any] = None
    
    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = {}
        if self.constraints is None:
            self.constraints = {}

class NaturalLanguageEncoder:
    """自然语言 → HIL 编码器 (Phase 1 原型)"""
    
    def __init__(self):
        self.action_keywords = {
            "分析": "?", "查看": "?", "检查": "?", "比较": "?",
            "创建": "!", "生成": "!", "写": "!", "制作": "!",
            "转换": ">", "转成": ">", "变为": ">",
            "查询": "@", "搜索": "@", "找": "@"
        }
        
        self.object_keywords = {
            "文档": "$", "文件": "$", "报告": "$",
            "知识": "@", "信息": "@", "数据": "@"
        }
        
        self.language_patterns = {
            r"中文|汉语|简体": "z",
            r"英文|英语|English": "e"
        }
        
        self.format_patterns = {
            r"bullet|要点|列表|点": "b",
            r"json|JSON|格式|schema": "s",
            r"表格|table|矩阵": "t"
        }
    
    def encode(self, text: str) -> str:
        """
        自然语言 → HIL 符号
        
        Args:
            text: 自然语言输入
            
        Returns:
            HIL 符号字符串
        """
        # Step 1: 解析意图
        intent = self._parse_intent(text)
        
        # Step 2: 构建 HIL
        hil = self._build_hil(intent)
        
        return hil
    
    def _parse_intent(self, text: str) -> HILIntent:
        """解析自然语言意图"""
        intent = HILIntent(
            action="?",  # 默认分析
            object="$",  # 默认文档
            modifiers={},
            constraints={}
        )
        
        # 识别动作
        for keyword, symbol in self.action_keywords.items():
            if keyword in text:
                intent.action = symbol
                break
        
        # 识别对象
        for keyword, symbol in self.object_keywords.items():
            if keyword in text:
                intent.object = symbol
                break
        
        # 识别目标 (括号内的内容)
        target_match = re.search(r'["""]([^"""]+)["""]', text)
        if target_match:
            intent.target = target_match.group(1)
        
        # 识别语言
        for pattern, code in self.language_patterns.items():
            if re.search(pattern, text):
                intent.modifiers['language'] = code
                break
        
        # 识别格式
        for pattern, code in self.format_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                intent.modifiers['format'] = code
                break
        
        # 识别数量限制
        num_match = re.search(r'(\d+)[个条点项]', text)
        if num_match:
            intent.constraints['limit'] = int(num_match.group(1))
        
        return intent
    
    def _build_hil(self, intent: HILIntent) -> str:
        """构建 HIL 符号"""
        parts = [intent.action, ":", intent.object]
        
        # 添加目标
        if intent.target:
            parts.append(f'"{intent.target}"')
        
        # 添加修饰符
        modifiers = []
        if 'language' in intent.modifiers:
            modifiers.append(intent.modifiers['language'])
        if 'format' in intent.modifiers:
            modifiers.append(intent.modifiers['format'])
        
        if modifiers:
            parts.append(f"{{{', '.join(modifiers)}}}")
        
        # 添加约束
        if 'limit' in intent.constraints:
            parts.append(f"({intent.constraints['limit']})")
        
        return " ".join(parts)

class HILDecoder:
    """HIL → 自然语言解码器 (已有功能增强)"""
    
    def decode(self, hil: str) -> str:
        """
        HIL 符号 → 自然语言
        
        Args:
            hil: HIL 符号字符串
            
        Returns:
            自然语言描述
        """
        try:
            parts = self._tokenize(hil)
            return self._reconstruct(parts)
        except Exception as e:
            return f"[解码错误: {e}]"
    
    def _tokenize(self, hil: str) -> Dict:
        """解析 HIL 符号"""
        tokens = {
            'action': '',
            'object': '',
            'target': '',
            'modifiers': [],
            'constraints': {}
        }
        
        # 动作 (第一个字符)
        action_match = re.match(r'^([?!>@])', hil)
        if action_match:
            tokens['action'] = action_match.group(1)
        
        # 对象
        obj_match = re.search(r':\s*([$@])', hil)
        if obj_match:
            tokens['object'] = obj_match.group(1)
        
        # 目标
        target_match = re.search(r'"([^"]+)"', hil)
        if target_match:
            tokens['target'] = target_match.group(1)
        
        # 修饰符
        mod_match = re.search(r'\{([^}]+)\}', hil)
        if mod_match:
            tokens['modifiers'] = [m.strip() for m in mod_match.group(1).split(',')]
        
        # 约束
        cons_match = re.search(r'\((\d+)\)', hil)
        if cons_match:
            tokens['constraints']['limit'] = int(cons_match.group(1))
        
        return tokens
    
    def _reconstruct(self, tokens: Dict) -> str:
        """重建自然语言"""
        action_map = {
            "?": "分析",
            "!": "创建",
            ">": "转换",
            "@": "查询"
        }
        
        object_map = {
            "$": "文档",
            "@": "知识库"
        }
        
        modifier_map = {
            "z": "中文",
            "e": "英文",
            "b": "bullet 格式",
            "s": "JSON 格式",
            "t": "表格"
        }
        
        parts = []
        
        # 动作
        action = action_map.get(tokens['action'], '处理')
        parts.append(action)
        
        # 目标
        if tokens['target']:
            parts.append(f"「{tokens['target']}」")
        
        # 对象
        obj = object_map.get(tokens['object'], '内容')
        if not tokens['target']:
            parts.append(obj)
        
        # 修饰符
        mods = []
        for mod in tokens['modifiers']:
            if mod in modifier_map:
                mods.append(modifier_map[mod])
        
        if mods:
            parts.append(f"，使用 {'，'.join(mods)}")
        
        # 约束
        if 'limit' in tokens['constraints']:
            parts.append(f"，限制 {tokens['constraints']['limit']} 个要点")
        
        return "".join(parts)

class HILBidirectionalBridge:
    """HIL 双向桥接 - 核心框架"""
    
    def __init__(self):
        self.encoder = NaturalLanguageEncoder()
        self.decoder = HILDecoder()
    
    def encode(self, natural: str) -> str:
        """自然语言 → HIL"""
        return self.encoder.encode(natural)
    
    def decode(self, hil: str) -> str:
        """HIL → 自然语言"""
        return self.decoder.decode(hil)
    
    def roundtrip(self, natural: str) -> Dict:
        """往返测试"""
        hil = self.encode(natural)
        reconstructed = self.decode(hil)
        
        # 计算压缩率
        compression = len(hil) / len(natural) if len(natural) > 0 else 0
        
        return {
            'original': natural,
            'hil': hil,
            'reconstructed': reconstructed,
            'compression_ratio': round(compression, 2),
            'original_length': len(natural),
            'hil_length': len(hil)
        }

# ============ 调试/测试模块 ============

def run_tests():
    """运行基础测试"""
    print("=" * 60)
    print("HIL Framework v0.1.0 - Phase 1 测试")
    print("=" * 60)
    
    bridge = HILBidirectionalBridge()
    
    test_cases = [
        "分析这份财报，用中文输出，3个要点",
        "创建一份报告，bullet格式",
        "比较苹果和特斯拉的优劣，英文输出",
        "查询知识库关于机器学习的信息"
    ]
    
    print("\n【编码测试】")
    for i, text in enumerate(test_cases, 1):
        result = bridge.roundtrip(text)
        print(f"\n测试 {i}:")
        print(f"  输入: {result['original']}")
        print(f"  HIL:  {result['hil']}")
        print(f"  还原: {result['reconstructed']}")
        print(f"  压缩率: {result['compression_ratio']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
