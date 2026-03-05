"""
HIL Transcoder - 增强版：支持中文语义识别
HIL Transcoder - Enhanced: Chinese Semantic Recognition

基于 Gemini 建议改进的版本
Based on Gemini's suggestion
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict


@dataclass
class ParsedHIL:
    """解析后的 HIL 结构"""
    action_symbol: str
    object_symbol: str
    object_args: List[str]
    modifiers: List[str]
    limit: Optional[int]
    comparison: Optional[Dict] = None  # 新增：对比信息


class HILTranscoder:
    """HIL 编解码器 - 支持中英双语"""
    
    def __init__(self):
        # HIL 命令解析正则
        self._COMMAND_RE = re.compile(
            r'^\s*([?!>@])\s*:?\s*([\$@][\w\(\),\s]*)\s*(?:\{([^}]*)\})?\s*(?:\((\d+)\))?\s*$'
        )
        
        # 对比语法正则 @vs(A,B){dimensions}
        self._COMPARISON_RE = re.compile(
            r'@vs\(([\w\s,]+)\)\{([^}]+)\}'
        )
        
        # 中文动作词库
        self._ACTION_MAP = {
            "?": ["分析", "查看", "检查", "总结", "评估", "解释", "说明", "审查", 
                  "analyze", "check", "review", "summarize", "evaluate"],
            "!": ["创建", "写", "生成", "制作", "构建", "起草", "产出", "输出",
                  "create", "write", "generate", "make", "build", "draft"],
            ">": ["转换", "变成", "改为", "翻译", "改写", "重写", "转为", "转成",
                  "convert", "transform", "translate", "rewrite", "change"],
            "@": ["查询", "搜索", "查找", "获取", "检索", "找出", "定位",
                  "query", "search", "find", "lookup", "fetch"]
        }
        
        # 中文对比词库
        self._COMPARISON_KEYWORDS = [
            "对比", "比较", "区别", "不同", "差异", "vs", "pk", "versus"
        ]
        
        # 实体分隔符
        self._ENTITY_SEPARATORS = ["和", "与", "vs", "对比", "比较", "以及"]
    
    def parse(self, hil_cmd: str) -> ParsedHIL:
        """
        解析 HIL 命令
        Parse HIL command
        """
        # 检查是否为对比语法
        comparison_match = self._COMPARISON_RE.search(hil_cmd)
        if comparison_match:
            entities_str = comparison_match.group(1)
            dimensions_str = comparison_match.group(2)
            return ParsedHIL(
                action_symbol="@",
                object_symbol="@vs",
                object_args=[e.strip() for e in entities_str.split(",")],
                modifiers=[d.strip() for d in dimensions_str.split(",")],
                limit=None,
                comparison={
                    "entities": [e.strip() for e in entities_str.split(",")],
                    "dimensions": [d.strip() for d in dimensions_str.split(",")]
                }
            )
        
        # 标准语法解析
        match = self._COMMAND_RE.match(hil_cmd)
        if not match:
            raise ValueError(f"HIL 格式错误: {hil_cmd}")
        
        action = match.group(1)
        obj = match.group(2)
        mods_str = match.group(3) or ""
        limit_str = match.group(4)
        
        modifiers = [m.strip() for m in mods_str.split(",") if m.strip()]
        limit = int(limit_str) if limit_str else None
        
        return ParsedHIL(
            action_symbol=action,
            object_symbol=obj.split("(")[0].strip(),
            object_args=[a.strip() for a in obj.split("(")[1].replace(")", "").split(",") if a.strip()] if "(" in obj else [],
            modifiers=modifiers,
            limit=limit
        )
    
    def decode(self, hil_cmd: str, language: str = "zh") -> str:
        """
        HIL 解码为自然语言
        Decode HIL to natural language
        
        Args:
            hil_cmd: HIL 命令
            language: "zh" 中文或 "en" 英文
        """
        try:
            parsed = self.parse(hil_cmd)
        except ValueError:
            if language == "zh":
                return "执行指令中..."
            return "Executing command..."
        
        # 对比语法特殊处理
        if parsed.object_symbol == "@vs" and parsed.comparison:
            entities = ", ".join(parsed.comparison["entities"])
            dimensions = ", ".join(parsed.comparison["dimensions"])
            
            if language == "zh":
                return f"请对比分析 {entities} 在{dimensions}方面的异同点，并给出详细评价。"
            return f"Please compare and analyze the differences between {entities} in terms of {dimensions}."
        
        # 标准语法解码
        action_desc = self._decode_action(parsed.action_symbol, language)
        obj_desc = self._decode_object(parsed.object_symbol, language)
        mod_desc = self._decode_modifiers(parsed.modifiers, language)
        limit_desc = self._decode_limit(parsed.limit, language)
        
        if language == "zh":
            return f"{action_desc}{obj_desc}{mod_desc}{limit_desc}"
        return f"{action_desc} {obj_desc}{mod_desc}{limit_desc}"
    
    def reverse_translate(self, text: str) -> str:
        """
        自然语言 → HIL 编码（增强版中文语义识别）
        Natural language → HIL encoding
        """
        lowered = text.lower()
        
        # 1. 动作识别
        action = self._recognize_action(text)
        
        # 2. 检查是否为对比意图
        comparison = self._recognize_comparison(text)
        if comparison:
            entities = comparison["entities"]
            dimensions = comparison["dimensions"]
            
            # 构建 @vs() 语法
            entity_str = ", ".join(entities[:2])  # 最多两个实体
            dimension_str = ", ".join(dimensions) if dimensions else "features"
            object_part = f"@vs({entity_str}){{{dimension_str}}}"
        else:
            object_part = self._recognize_object(text)
        
        # 3. 修饰符识别
        modifiers = self._recognize_modifiers(text)
        
        # 4. 数量限制识别
        limit = self._recognize_limit(text)
        
        # 构建 HIL
        result = f"{action} : {object_part}"
        if modifiers:
            result += " {" + ", ".join(modifiers) + "}"
        if limit:
            result += f" ({limit})"
        
        return result
    
    def _recognize_action(self, text: str) -> str:
        """识别动作符号"""
        lowered = text.lower()
        
        for action, keywords in self._ACTION_MAP.items():
            for keyword in keywords:
                if keyword in lowered or keyword in text:
                    return action
        
        return "?"  # 默认分析
    
    def _recognize_comparison(self, text: str) -> Optional[Dict]:
        """
        识别对比意图
        支持：
        - "A和B的对比"
        - "A与B的区别"
        - "比较A和B"
        - "A vs B"
        """
        # 检查是否包含对比关键词
        has_comparison = any(kw in text.lower() or kw in text for kw in self._COMPARISON_KEYWORDS)
        
        if not has_comparison:
            return None
        
        # 提取实体
        entities = self._extract_entities(text)
        
        if len(entities) < 2:
            return None
        
        # 提取维度
        dimensions = self._extract_dimensions(text)
        
        return {
            "entities": entities[:2],
            "dimensions": dimensions if dimensions else ["features"]
        }
    
    def _extract_entities(self, text: str) -> List[str]:
        """从对比文本中提取实体"""
        # 步骤1: 清理文本，去除对比关键词
        clean_text = text
        for kw in ["对比", "比较", "区别", "不同"]:
            clean_text = clean_text.replace(kw, "")
        
        # 步骤2: 匹配 "实体A 和 实体B" 结构
        # 使用非贪婪匹配，提取最可能的实体对
        separators = r'和|与|vs|及|VS'
        
        # 找到连接词位置，分割实体
        for sep in ["和", "与", "vs", "及", "VS"]:
            if sep in clean_text:
                parts = clean_text.split(sep, 1)  # 只分割一次
                if len(parts) == 2:
                    entity1 = parts[0].strip()
                    entity2 = parts[1].strip()
                    
                    # 清理实体2（去除"的价格"等修饰）
                    entity2 = re.split(r'[的之]', entity2)[0].strip()
                    
                    # 提取有效部分（去除标点、停用词）
                    def clean_entity(e: str) -> str:
                        e = e.strip()
                        # 去除开头的停用词
                        e = re.sub(r'^(的|是|有|在|分析|比较|对比)', '', e).strip()
                        # 去除结尾的标点
                        e = re.sub(r'[，。！？.,!?之]$', '', e).strip()
                        return e
                    
                    entity1 = clean_entity(entity1)
                    entity2 = clean_entity(entity2)
                    
                    # 验证
                    if len(entity1) >= 2 and len(entity2) >= 2:
                        return [entity1, entity2]
        
        return []
    
    def _extract_dimensions(self, text: str) -> List[str]:
        """提取对比维度"""
        dimension_keywords = {
            "价格": "price",
            "价钱": "price",
            "成本": "price",
            "质量": "quality",
            "品质": "quality",
            "性能": "performance",
            "功能": "feature",
            "服务": "service",
            "速度": "speed",
            "效率": "efficiency",
            "外观": "appearance",
            "设计": "design"
        }
        
        dimensions = []
        for zh, en in dimension_keywords.items():
            if zh in text and en not in dimensions:
                dimensions.append(en)
        
        return dimensions
    
    def _recognize_object(self, text: str) -> str:
        """识别对象符号"""
        if any(k in text for k in ["知识", "数据", "信息", "资料", "database", "data"]):
            return "@"
        return "$"
    
    def _recognize_modifiers(self, text: str) -> List[str]:
        """识别修饰符"""
        modifiers = []
        
        if "中文" in text or "汉语" in text:
            modifiers.append("z")
        if "英文" in text or "英语" in text or "english" in text.lower():
            modifiers.append("e")
        if any(k in text for k in ["列表", "要点", "bullet", "list"]):
            modifiers.append("b")
        if any(k in text for k in ["json", "yaml", "xml", "格式", "schema"]):
            modifiers.append("s")
        if "表格" in text or "table" in text.lower():
            modifiers.append("t")
        
        return modifiers
    
    def _recognize_limit(self, text: str) -> Optional[int]:
        """识别数量限制"""
        match = re.search(r'(\d+)[个条点项份段]?', text)
        if match:
            return int(match.group(1))
        return None
    
    def _decode_action(self, action: str, language: str) -> str:
        """解码动作"""
        action_map = {
            "zh": {"?": "分析", "!": "创建", ">": "转换", "@": "查询"},
            "en": {"?": "Analyze", "!": "Create", ">": "Transform", "@": "Query"}
        }
        return action_map.get(language, action_map["zh"]).get(action, "处理")
    
    def _decode_object(self, obj: str, language: str) -> str:
        """解码对象"""
        obj_map = {
            "zh": {"$": "文档", "@": "知识库"},
            "en": {"$": "document", "@": "knowledge base"}
        }
        return obj_map.get(language, obj_map["zh"]).get(obj, "内容")
    
    def _decode_modifiers(self, modifiers: List[str], language: str) -> str:
        """解码修饰符"""
        if not modifiers:
            return ""
        
        mod_map = {
            "zh": {"z": "中文输出", "e": "英文输出", "b": "bullet格式", "s": "JSON格式", "t": "表格格式"},
            "en": {"z": "Chinese output", "e": "English output", "b": "bullet format", "s": "JSON format", "t": "table format"}
        }
        
        descs = [mod_map.get(language, mod_map["zh"]).get(m, m) for m in modifiers]
        
        if language == "zh":
            return "，使用 " + "、".join(descs)
        return " using " + ", ".join(descs)
    
    def _decode_limit(self, limit: Optional[int], language: str) -> str:
        """解码数量限制"""
        if not limit:
            return ""
        
        if language == "zh":
            return f"，限制 {limit} 个要点"
        return f", limit {limit} items"


# ============ 测试与演示 ============

def test_transcoder():
    """测试 HIL Transcoder"""
    print("=" * 60)
    print("HIL Transcoder 增强版测试")
    print("=" * 60)
    
    transcoder = HILTranscoder()
    
    # 测试 1: 对比语法
    print("\n【测试 1】对比语法识别")
    test_cases = [
        "对比立白和蓝月亮的价格和质量",
        "比较苹果和特斯拉的性能",
        "分析 A 与 B 的区别"
    ]
    
    for text in test_cases:
        hil = transcoder.reverse_translate(text)
        print(f"\n输入: {text}")
        print(f"HIL:  {hil}")
        
        # 解码回中文
        decoded = transcoder.decode(hil, language="zh")
        print(f"解码: {decoded}")
    
    # 测试 2: 标准语法
    print("\n" + "=" * 60)
    print("【测试 2】标准语法识别")
    
    standard_cases = [
        "分析这份文档，用中文输出，3个要点",
        "创建一份英文报告，bullet格式",
        "查询知识库关于机器学习的信息"
    ]
    
    for text in standard_cases:
        hil = transcoder.reverse_translate(text)
        print(f"\n输入: {text}")
        print(f"HIL:  {hil}")
    
    # 测试 3: 英文解码
    print("\n" + "=" * 60)
    print("【测试 3】英文解码")
    
    hil_examples = [
        "? : $ {z} (3)",
        "! : @ {e, b}",
        "@vs(productA,productB){price,quality}"
    ]
    
    for hil in hil_examples:
        decoded_zh = transcoder.decode(hil, "zh")
        decoded_en = transcoder.decode(hil, "en")
        print(f"\nHIL: {hil}")
        print(f"中文: {decoded_zh}")
        print(f"English: {decoded_en}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_transcoder()
