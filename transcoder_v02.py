"""HIL Transcoder v0.2 - Enhanced with emotion and context support.

增强版 HIL 转码器，支持情感和语境维度识别
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from hil_spec_v02 import (
    HIL_V0_2, 
    detect_emotions, 
    detect_contexts,
    EMOTION_KEYWORDS,
    CONTEXT_KEYWORDS
)


@dataclass
class ParsedHIL:
    """Structured representation of a decoded HIL command."""

    action_symbol: str
    object_symbol: str
    object_args: List[str]
    modifiers: List[str]
    limit: Optional[int]
    emotions: List[str] = field(default_factory=list)  # NEW
    contexts: List[str] = field(default_factory=list)  # NEW


class HILTranscoderV2:
    """HIL v0.2 transcoder with emotion and context awareness.
    
    Enhanced grammar:
        <action> : <object> {<modifiers>} (<limit>) [<emotions>] [<contexts>]
    
    Examples:
        ? : $ {z, b} (3) [!urgent] [+continuation]
        → Analyze (urgently, continuing) the document in Chinese, bullet points, 3 items
        
        ! : @ {e} [+positive] [?polite]
        → Please create (positively, politely) the knowledge base in English
    """

    _ACTION_PATTERN = r"(?P<action>[?!>@])"
    _OBJECT_PATTERN = r"(?P<object>[\$@]\w*)"  # FIXED: 更严格的匹配，不包含括号
    _MODIFIERS_PATTERN = r"(?:\{(?P<modifiers>[^}]*)\})?"
    _LIMIT_PATTERN = r"(?:\((?P<limit>\d+)\))?"
    # FIXED: contexts 使用 <> 区别于 emotions 的 []
    _EMOTIONS_PATTERN = r"(?:\[(?P<emotions>[^\]]*)\])?"   # [!urgent,~negative]
    _CONTEXTS_PATTERN = r"(?:<(?P<contexts>[^>]*)>)?"       # <+continuation>

    _COMMAND_RE = re.compile(
        rf"^\s*{_ACTION_PATTERN}\s*:?\s*{_OBJECT_PATTERN}\s*"
        rf"{_MODIFIERS_PATTERN}\s*{_LIMIT_PATTERN}\s*"
        rf"{_EMOTIONS_PATTERN}\s*{_CONTEXTS_PATTERN}\s*$"
    )

    _OBJECT_WITH_ARGS_RE = re.compile(r"^(?P<base>[\$@]\w*)(?:\((?P<args>.*)\))?$")

    def _split_object(self, object_token: str) -> Tuple[str, List[str]]:
        token = object_token.strip()
        if token == "$":
            return "$", []

        match = self._OBJECT_WITH_ARGS_RE.match(token)
        if not match:
            raise ValueError(f"Invalid object token: {object_token!r}")

        base = match.group("base")
        args_raw = match.group("args")
        args = [arg.strip() for arg in args_raw.split(",") if arg.strip()] if args_raw else []
        return base, args

    def _parse_tags(self, tags_str: Optional[str]) -> List[str]:
        """Parse emotion/context tags like '!urgent,+positive'"""
        if not tags_str:
            return []
        return [tag.strip() for tag in tags_str.split(",") if tag.strip()]

    def parse(self, hil_cmd: str) -> ParsedHIL:
        """Parse HIL command into symbols, parameters, emotions, and contexts."""
        match = self._COMMAND_RE.match(hil_cmd)
        if not match:
            raise ValueError(f"Invalid HIL command format: {hil_cmd!r}")

        action_symbol = match.group("action")
        object_token = (match.group("object") or "").strip()
        object_symbol, object_args = self._split_object(object_token)
        raw_modifiers = match.group("modifiers") or ""
        limit_raw = match.group("limit")
        raw_emotions = match.group("emotions") or ""  # NEW
        raw_contexts = match.group("contexts") or ""   # NEW

        modifiers = [m.strip() for m in raw_modifiers.split(",") if m.strip()]
        emotions = self._parse_tags(raw_emotions)      # NEW
        contexts = self._parse_tags(raw_contexts)      # NEW

        # Validate symbols
        if object_symbol not in HIL_V0_2.objects:
            raise ValueError(
                f"Unsupported object symbol: {object_symbol!r}. "
                f"Supported: {sorted(HIL_V0_2.objects)}"
            )

        unsupported_mods = [m for m in modifiers if m not in HIL_V0_2.modifiers]
        if unsupported_mods:
            raise ValueError(f"Unsupported modifiers: {unsupported_mods}")

        # Validate emotions and contexts
        unsupported_emos = [e for e in emotions if e not in HIL_V0_2.emotions]
        if unsupported_emos:
            raise ValueError(f"Unsupported emotions: {unsupported_emos}")

        unsupported_ctxs = [c for c in contexts if c not in HIL_V0_2.contexts]
        if unsupported_ctxs:
            raise ValueError(f"Unsupported contexts: {unsupported_ctxs}")

        return ParsedHIL(
            action_symbol=action_symbol,
            object_symbol=object_symbol,
            object_args=object_args,
            modifiers=modifiers,
            limit=int(limit_raw) if limit_raw else None,
            emotions=emotions,
            contexts=contexts,
        )

    def decode(self, hil_cmd: str, language: str = "en") -> str:
        """Decode HIL command to natural language with emotion and context."""
        try:
            parsed = self.parse(hil_cmd)
        except ValueError as e:
            return f"[Decode Error: {e}]"

        parts = []

        # 1. Context (语境)
        for ctx in parsed.contexts:
            desc = HIL_V0_2.contexts.get(ctx, ctx)
            parts.append(desc)

        # 2. Emotion (情感)
        emotion_descs = []
        for emo in parsed.emotions:
            desc = HIL_V0_2.emotions.get(emo, emo)
            emotion_descs.append(desc)
        if emotion_descs:
            parts.append(" ".join(emotion_descs))

        # 3. Action (动作)
        action_desc = HIL_V0_2.actions.get(parsed.action_symbol, parsed.action_symbol)
        parts.append(action_desc)

        # 4. Object (对象)
        object_desc = HIL_V0_2.objects.get(parsed.object_symbol, parsed.object_symbol)
        if parsed.object_args:
            object_desc += " " + ", ".join(parsed.object_args)
        parts.append(object_desc)

        # 5. Modifiers (修饰符)
        for mod in parsed.modifiers:
            mod_desc = HIL_V0_2.modifiers.get(mod, mod)
            parts.append(mod_desc)

        # 6. Limit (限制)
        if parsed.limit:
            parts.append(f"limited to {parsed.limit} items")

        return " ".join(parts)

    def reverse_translate(self, text: str) -> str:
        """Natural language → HIL v0.2 with emotion/context detection."""
        # 1. Detect emotions and contexts FIRST (before cleaning)
        emotions = detect_emotions(text)
        contexts = detect_contexts(text)

        # 2. Clean text for basic parsing
        clean_text = text
        for keywords in list(EMOTION_KEYWORDS.values()) + list(CONTEXT_KEYWORDS.values()):
            for kw in keywords:
                clean_text = clean_text.replace(kw, "")

        # 3. Recognize action
        action = self._recognize_action(clean_text)

        # 4. Recognize object
        object_sym = self._recognize_object(clean_text)

        # 5. Recognize modifiers
        modifiers = self._recognize_modifiers(clean_text)

        # 6. Recognize limit
        limit = self._recognize_limit(clean_text)

        # 7. Build HIL (FIXED: contexts 使用 <> 格式)
        parts = [action, ":", object_sym]
        if modifiers:
            parts.append("{" + ",".join(modifiers) + "}")
        if limit:
            parts.append(f"({limit})")
        if emotions:
            parts.append("[" + ",".join(emotions) + "]")
        if contexts:
            parts.append("<" + ",".join(contexts) + ">")  # FIXED: <> 格式

        return " ".join(parts)

    def _recognize_action(self, text: str) -> str:
        """Recognize action symbol from text."""
        text_lower = text.lower()
        for action, keywords in [
            ("!", ["创建", "create", "写", "write", "生成", "generate"]),
            (">", ["转换", "transform", "翻译", "translate", "改写"]),
            ("@", ["查询", "query", "搜索", "search", "查找", "find"]),
        ]:
            if any(kw in text or kw in text_lower for kw in keywords):
                return action
        return "?"  # Default: analyze

    def _recognize_object(self, text: str) -> str:
        """Recognize object symbol from text."""
        if any(kw in text for kw in ["知识", "knowledge", "数据", "data", "库", "base"]):
            return "@"
        return "$"

    def _recognize_modifiers(self, text: str) -> List[str]:
        """Recognize modifiers from text."""
        mods = []
        if "中文" in text or "chinese" in text.lower():
            mods.append("z")
        if "英文" in text or "english" in text.lower():
            mods.append("e")
        if any(kw in text for kw in ["列表", "bullet", "要点", "points"]):
            mods.append("b")
        if "json" in text.lower() or "schema" in text.lower():
            mods.append("s")
        return mods

    def _recognize_limit(self, text: str) -> Optional[int]:
        """Recognize limit number from text."""
        match = re.search(r'(\d+)\s*(?:个|items?|points?)?', text)
        if match:
            return int(match.group(1))
        return None


# ============ 测试 ============

def test_v2():
    """Test HIL Transcoder v0.2"""
    print("=" * 60)
    print("HIL Transcoder v0.2 - 情感/语境支持测试")
    print("=" * 60)

    tc = HILTranscoderV2()

    # 测试 1: 基础 + 情感 + 语境
    print("\n【测试 1】情感 + 语境识别")
    test_cases = [
        "请立即分析这份文档，继续之前的分析",  # !urgent +continuation
        "必须尽快生成报告，这个很关键",        # !critical
        "糟糕，这份报告有问题，请纠正",         # ~negative +correction
        "很好，继续优化这份方案",              # +positive +continuation
        "请帮忙查询一下，我不明白这个问题",     # ?polite ?confused
    ]

    for text in test_cases:
        hil = tc.reverse_translate(text)
        decoded = tc.decode(hil)
        print(f"\n输入: {text}")
        print(f"HIL:  {hil}")
        print(f"解码: {decoded}")

    # 测试 2: 手动构造 HIL (FIXED: contexts 使用 <> 格式)
    print("\n" + "=" * 60)
    print("【测试 2】手动构造 HIL 解码")
    hil_cases = [
        "? : $ {z, b} (3) [!urgent] <+continuation>",  # FIXED: <> for contexts
        "! : @ {e} [+positive] [?polite]",
        "> : $ [~negative] <+correction>",  # FIXED: <> for contexts
    ]

    for hil in hil_cases:
        decoded = tc.decode(hil)
        print(f"\nHIL: {hil}")
        print(f"解码: {decoded}")

    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_v2()
