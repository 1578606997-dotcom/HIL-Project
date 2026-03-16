"""
Partial HIL Transcoder - 局部符号化转码器

核心思想：
- 高频、低信息密度的词 → 符号化（节省 token）
- 关键、高信息密度的词 → 保留原文（保证准确度）

语法格式：
    <action> "<target>" {modifiers} (limit) [emotions] <contexts>

示例：
    输入: "请分析苹果公司财报，用中文输出，列出3个要点"
    输出: ? "苹果公司财报" {z, b} (3)
    
    输入: "把这段文字翻译成英文"
    输出: > "这段文字" {e}
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from hil_spec_v02 import (
    HIL_V0_2,
    detect_emotions,
    detect_contexts,
    EMOTION_KEYWORDS,
    CONTEXT_KEYWORDS,
)


@dataclass
class PartialHIL:
    action: str
    target: str
    modifiers: List[str] = field(default_factory=list)
    limit: Optional[int] = None
    emotions: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)

    def to_hil(self) -> str:
        parts = [self.action]
        if self.target:
            parts.append(f'"{self.target}"')
        if self.modifiers:
            parts.append("{" + ",".join(self.modifiers) + "}")
        if self.limit:
            parts.append(f"({self.limit})")
        if self.emotions:
            parts.append("[" + ",".join(self.emotions) + "]")
        if self.contexts:
            parts.append("<" + ",".join(self.contexts) + ">")
        return " ".join(parts)


class PartialHILTranscoder:
    ACTION_MAP = {
        "?": "分析",
        "!": "创建",
        ">": "转换",
        "@": "查询",
    }
    
    ACTION_REVERSE = {v: k for k, v in ACTION_MAP.items()}
    
    MODIFIER_MAP = {
        "z": "中文输出",
        "e": "英文输出",
        "b": "列表格式",
        "s": "JSON格式",
        "t": "表格格式",
    }
    
    ACTION_KEYWORDS = {
        "?": ["分析", "查看", "检查", "比较", "评估", "analyze", "check", "review"],
        "!": ["创建", "生成", "写", "制作", "创建", "create", "write", "generate"],
        ">": ["转换", "翻译", "改写", "变成", "transform", "translate"],
        "@": ["查询", "搜索", "查找", "找", "query", "search", "find"],
    }
    
    MODIFIER_KEYWORDS = {
        "z": ["中文", "汉语", "简体", "chinese"],
        "e": ["英文", "英语", "english"],
        "b": ["列表", "要点", "bullet", "点"],
        "s": ["json", "schema", "结构化"],
        "t": ["表格", "table", "矩阵"],
    }
    
    _HIL_PATTERN = re.compile(
        r'^(?P<action>[?!>@])\s*'
        r'"(?P<target>[^"]*)"\s*'
        r'(?:\{(?P<modifiers>[^}]*)\})?\s*'
        r'(?:\((?P<limit>\d+)\))?\s*'
        r'(?:\[(?P<emotions>[^\]]*)\])?\s*'
        r'(?:<(?P<contexts>[^>]*)>)?\s*$'
    )
    
    _HIL_PATTERN_NO_TARGET = re.compile(
        r'^(?P<action>[?!>@])\s*'
        r'(?:\{(?P<modifiers>[^}]*)\})?\s*'
        r'(?:\((?P<limit>\d+)\))?\s*'
        r'(?:\[(?P<emotions>[^\]]*)\])?\s*'
        r'(?:<(?P<contexts>[^>]*)>)?\s*$'
    )

    def encode(self, text: str) -> str:
        hil = self._parse_natural_language(text)
        return hil.to_hil()

    def decode(self, hil_str: str) -> str:
        match = self._HIL_PATTERN.match(hil_str.strip())
        if not match:
            match = self._HIL_PATTERN_NO_TARGET.match(hil_str.strip())
        
        if not match:
            return f"[解码错误: 格式不正确] {hil_str}"
        
        action = match.group("action")
        target = match.groupdict().get("target") or ""
        modifiers_str = match.groupdict().get("modifiers") or ""
        limit_str = match.groupdict().get("limit")
        emotions_str = match.groupdict().get("emotions") or ""
        contexts_str = match.groupdict().get("contexts") or ""
        
        modifiers = [m.strip() for m in modifiers_str.split(",") if m.strip()]
        limit = int(limit_str) if limit_str else None
        emotions = [e.strip() for e in emotions_str.split(",") if e.strip()]
        contexts = [c.strip() for c in contexts_str.split(",") if c.strip()]
        
        parts = []
        
        for ctx in contexts:
            ctx_desc = HIL_V0_2.contexts.get(ctx, ctx)
            parts.append(ctx_desc)
        
        for emo in emotions:
            emo_desc = HIL_V0_2.emotions.get(emo, emo)
            parts.append(emo_desc)
        
        action_desc = self.ACTION_MAP.get(action, action)
        parts.append(action_desc)
        
        if target:
            parts.append(f'"{target}"')
        
        for mod in modifiers:
            mod_desc = self.MODIFIER_MAP.get(mod, mod)
            parts.append(mod_desc)
        
        if limit:
            parts.append(f"限制{limit}条")
        
        return " ".join(parts)

    def _parse_natural_language(self, text: str) -> PartialHIL:
        emotions = detect_emotions(text)
        contexts = detect_contexts(text)
        
        clean_text = text
        for keywords in list(EMOTION_KEYWORDS.values()) + list(CONTEXT_KEYWORDS.values()):
            for kw in keywords:
                clean_text = clean_text.replace(kw, " ")
        
        action = self._detect_action(clean_text)
        
        target = self._extract_target(clean_text, action)
        
        modifiers = self._detect_modifiers(clean_text)
        
        limit = self._detect_limit(clean_text)
        
        return PartialHIL(
            action=action,
            target=target,
            modifiers=modifiers,
            limit=limit,
            emotions=emotions,
            contexts=contexts,
        )

    def _detect_action(self, text: str) -> str:
        text_lower = text.lower()
        for action, keywords in self.ACTION_KEYWORDS.items():
            for kw in keywords:
                if kw in text or kw in text_lower:
                    return action
        return "?"

    def _extract_target(self, text: str, action: str) -> str:
        quoted_match = re.search(r'["""]([^"""]+)["""]', text)
        if quoted_match:
            return quoted_match.group(1).strip()
        
        action_patterns = {
            "?": [
                r'分析[一下]?\s*([^，。！？,\n]{2,30})',
                r'比较\s*([^，。！？,\n]{2,30})',
                r'检查\s*([^，。！？,\n]{2,30})',
                r'评估\s*([^，。！？,\n]{2,30})',
            ],
            "!": [
                r'创建\s*([^，。！？,\n]{2,30})',
                r'生成\s*([^，。！？,\n]{2,30})',
                r'写\s*([^，。！？,\n]{2,30})',
            ],
            ">": [
                r'[把将]\s*([^，。！？,\n]{2,30}?)(?=[翻译转换成])',
                r'翻译\s*([^，。！？,\n]{2,30})',
                r'转换\s*([^，。！？,\n]{2,30})',
            ],
            "@": [
                r'查询\s*([^，。！？,\n]{2,30})',
                r'搜索\s*([^，。！？,\n]{2,30})',
                r'查找\s*([^，。！？,\n]{2,30})',
            ],
        }
        
        patterns = action_patterns.get(action, [])
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                target = match.group(1).strip()
                target = self._clean_target(target)
                if target and len(target) >= 2:
                    return target
        
        return ""

    def _clean_target(self, target: str) -> str:
        target = re.sub(r'^(一份|份|关于)', '', target)
        target = re.sub(r'的$', '', target)
        target = re.sub(r'(翻译|转换|成英文|成中文)$', '', target)
        
        stopwords = [
            "这份", "这个", "那个", "一下", "关于",
            "用", "以", "给", "在", "输出", "格式",
            "中文", "英文", "列表", "json", "JSON", "表格",
            "展示", "中", "知识库",
        ]
        for sw in stopwords:
            target = target.replace(sw, "")
        
        target = re.sub(r'[，。！？、]$', '', target)
        return target.strip()

    def _detect_modifiers(self, text: str) -> List[str]:
        mods = []
        text_lower = text.lower()
        for mod, keywords in self.MODIFIER_KEYWORDS.items():
            for kw in keywords:
                if kw in text or kw in text_lower:
                    mods.append(mod)
                    break
        return mods

    def _detect_limit(self, text: str) -> Optional[int]:
        patterns = [
            r'(\d+)\s*[个条点项]',
            r'限制\s*(\d+)',
            r'limit\s*(?:to\s*)?(\d+)',
            r'(\d+)\s*items?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def roundtrip(self, text: str) -> dict:
        hil = self.encode(text)
        decoded = self.decode(hil)
        
        original_len = len(text)
        hil_len = len(hil)
        compression_ratio = hil_len / original_len if original_len > 0 else 0
        token_saving = 1 - compression_ratio
        
        return {
            "original": text,
            "hil": hil,
            "decoded": decoded,
            "original_len": original_len,
            "hil_len": hil_len,
            "compression_ratio": round(compression_ratio, 2),
            "token_saving": f"{round(token_saving * 100, 1)}%",
        }


def run_demo():
    print("=" * 70)
    print("Partial HIL Transcoder - 局部符号化演示")
    print("=" * 70)
    
    tc = PartialHILTranscoder()
    
    test_cases = [
        "请分析苹果公司财报，用中文输出，列出3个要点",
        "把这段文字翻译成英文",
        "创建一份关于人工智能的报告，用列表格式",
        "查询知识库中关于机器学习的信息",
        "立即分析这份合同，继续之前的分析",
        "比较特斯拉和比亚迪的竞争优势，用表格展示",
    ]
    
    print("\n【编码测试：自然语言 → 局部符号化 HIL】\n")
    
    for i, text in enumerate(test_cases, 1):
        result = tc.roundtrip(text)
        print(f"测试 {i}:")
        print(f"  原文: {result['original']}")
        print(f"  HIL:  {result['hil']}")
        print(f"  解码: {result['decoded']}")
        print(f"  压缩: {result['original_len']} → {result['hil_len']} 字符 (节省 {result['token_saving']})")
        print()
    
    print("=" * 70)
    print("【解码测试：HIL → 自然语言】\n")
    
    hil_cases = [
        '? "苹果公司Q3财报" {z, b} (5)',
        '! "市场分析报告" {e, t}',
        '> "用户反馈内容" {e}',
        '? "竞品数据" {z, s} [!urgent] <+continuation>',
    ]
    
    for hil in hil_cases:
        decoded = tc.decode(hil)
        print(f"  HIL: {hil}")
        print(f"  →   {decoded}")
        print()
    
    print("=" * 70)
    print("✅ 演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
