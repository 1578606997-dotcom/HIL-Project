"""HIL v0.2 syntax specification with emotion and context support.

HIL v0.2 语法规范，支持情感和语境维度

Enhancements based on user feedback to improve information accuracy
after natural language symbolization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional


@dataclass(frozen=True)
class HILSpec:
    """Container for HIL symbol mappings."""

    actions: Dict[str, str]
    objects: Dict[str, str]
    modifiers: Dict[str, str]
    emotions: Dict[str, str]  # NEW: 情感维度
    contexts: Dict[str, str]  # NEW: 语境维度


# HIL v0.2 规范
HIL_V0_2 = HILSpec(
    # 基础动作
    actions={
        "?": "analyze",
        "!": "create",
        ">": "transform",
        "@": "query",
    },
    
    # 对象
    objects={
        "$": "the provided document",
        "@": "the knowledge base (RAG context)",
        "@vs": "a compare-and-contrast analysis across competitors",
        "@top": "the top competitive advantages from the knowledge base",
    },
    
    # 修饰符（语言/格式）
    modifiers={
        "z": "in Chinese",
        "e": "in English",
        "b": "using bullet points",
        "s": "as a JSON schema",
        "t": "as a table",
    },
    
    # NEW: 情感维度 [!symbol]
    # 使用 ! 前缀表示紧急/强烈情感
    # 使用 ~ 前缀表示负面情感
    # 使用 + 前缀表示积极情感
    # 使用 ? 前缀表示疑问/礼貌
    emotions={
        "!urgent": "urgently",           # [!urgent] 紧急
        "!critical": "critically",       # [!critical] 关键
        "~negative": "with concern about", # [~negative] 负面/担忧
        "~angry": "frustrated by",       # [~angry] 愤怒
        "+positive": "optimistically",   # [+positive] 积极
        "+excited": "enthusiastically",  # [+excited] 兴奋
        "?polite": "please",             # [?polite] 礼貌
        "?confused": "unclear about",    # [?confused] 困惑
    },
    
    # NEW: 语境维度 [symbol]
    # 表示对话的上下文关系
    contexts={
        "+continuation": "continuing to",     # [+continuation] 继续
        "+correction": "correcting",          # [+correction] 纠正
        "+example": "providing examples of",  # [+example] 举例
        "+condition": "if applicable",        # [+condition] 条件
        "-stop": "stopping",                  # [-stop] 停止
        "-skip": "skipping",                  # [-skip] 跳过
    },
)


# 情感识别关键词映射
EMOTION_KEYWORDS: Dict[str, List[str]] = {
    "!urgent": ["必须", "立即", "紧急", "尽快", "马上", "urgent", "immediately", "asap"],
    "!critical": ["关键", "重要", "critical", "crucial", "vital"],
    "~negative": ["糟糕", "差", "失败", "问题", "错误", "bad", "terrible", "wrong"],
    "~angry": ["生气", "愤怒", "讨厌", "angry", "mad", "frustrated"],
    "+positive": ["好", "优秀", "棒", "成功", "不错", "good", "great", "excellent"],
    "+excited": ["兴奋", "期待", "激动", "excited", "looking forward"],
    "?polite": ["请", "麻烦", "能否", "是否可以", "please", "could you"],
    "?confused": ["不懂", "不明白", "困惑", "confused", "unclear"],
}


# 语境识别关键词映射
CONTEXT_KEYWORDS: Dict[str, List[str]] = {
    "+continuation": ["再", "继续", "接着", "然后", "继续", "continue", "next", "then"],
    "+correction": ["不对", "错了", "应该", "改为", "不对", "wrong", "should be", "correct"],
    "+example": ["比如", "例如", "像", "举例", "example", "such as", "like"],
    "+condition": ["如果", "假如", "除非", "条件", "if", "unless", "condition"],
    "-stop": ["停止", "结束", "算了", "stop", "end", "quit"],
    "-skip": ["跳过", "忽略", "不管", "skip", "ignore"],
}


def supported_symbols() -> Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
    """Return all supported action/object/modifier symbols."""
    return (
        tuple(HIL_V0_2.actions.keys()),
        tuple(HIL_V0_2.objects.keys()),
        tuple(HIL_V0_2.modifiers.keys()),
    )


def supported_emotions() -> Tuple[str, ...]:
    """Return all supported emotion symbols."""
    return tuple(HIL_V0_2.emotions.keys())


def supported_contexts() -> Tuple[str, ...]:
    """Return all supported context symbols."""
    return tuple(HIL_V0_2.contexts.keys())


def detect_emotions(text: str) -> List[str]:
    """Detect emotions from natural language text.
    
    Args:
        text: Natural language input
        
    Returns:
        List of detected emotion symbols
    """
    detected = []
    text_lower = text.lower()
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text or keyword in text_lower:
                detected.append(emotion)
                break
    
    return detected


def detect_contexts(text: str) -> List[str]:
    """Detect contexts from natural language text.
    
    Args:
        text: Natural language input
        
    Returns:
        List of detected context symbols
    """
    detected = []
    text_lower = text.lower()
    
    for context, keywords in CONTEXT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text or keyword in text_lower:
                detected.append(context)
                break
    
    return detected


# 向后兼容：保留 v0.1 接口
HIL_V0_1 = HILSpec(
    actions=HIL_V0_2.actions,
    objects=HIL_V0_2.objects,
    modifiers=HIL_V0_2.modifiers,
    emotions={},
    contexts={},
)
