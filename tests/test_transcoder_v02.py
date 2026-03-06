"""Tests for HIL Transcoder v0.2

Test coverage for emotion and context support.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from transcoder_v02 import HILTranscoderV2, ParsedHIL


class TestHILTranscoderV2:
    """Test suite for HILTranscoderV2"""
    
    @classmethod
    def setup_class(cls):
        cls.tc = HILTranscoderV2()
    
    # ========== Basic Parsing Tests ==========
    
    def test_parse_basic_command(self):
        """Test parsing basic HIL command"""
        parsed = self.tc.parse("? : $")
        assert parsed.action_symbol == "?"
        assert parsed.object_symbol == "$"
        assert parsed.modifiers == []
        assert parsed.limit is None
        assert parsed.emotions == []
        assert parsed.contexts == []
    
    def test_parse_with_modifiers(self):
        """Test parsing with modifiers"""
        parsed = self.tc.parse("? : $ {z, b}")
        assert parsed.modifiers == ["z", "b"]
    
    def test_parse_with_limit(self):
        """Test parsing with limit"""
        parsed = self.tc.parse("? : $ (3)")
        assert parsed.limit == 3
    
    def test_parse_full_command(self):
        """Test parsing full command with all components"""
        parsed = self.tc.parse("? : $ {z, b} (3) [!urgent] <+continuation>")
        assert parsed.action_symbol == "?"
        assert parsed.object_symbol == "$"
        assert parsed.modifiers == ["z", "b"]
        assert parsed.limit == 3
        assert parsed.emotions == ["!urgent"]
        assert parsed.contexts == ["+continuation"]
    
    # ========== Emotion Tests ==========
    
    def test_parse_emotion_urgent(self):
        """Test parsing urgent emotion"""
        parsed = self.tc.parse("? : $ [!urgent]")
        assert "!urgent" in parsed.emotions
    
    def test_parse_emotion_positive(self):
        """Test parsing positive emotion"""
        parsed = self.tc.parse("? : $ [+positive]")
        assert "+positive" in parsed.emotions
    
    def test_parse_emotion_negative(self):
        """Test parsing negative emotion"""
        parsed = self.tc.parse("? : $ [~negative]")
        assert "~negative" in parsed.emotions
    
    def test_parse_multiple_emotions(self):
        """Test parsing multiple emotions"""
        parsed = self.tc.parse("? : $ [!urgent,+positive,?polite]")
        assert parsed.emotions == ["!urgent", "+positive", "?polite"]
    
    def test_parse_no_emotion(self):
        """Test parsing without emotion"""
        parsed = self.tc.parse("? : $")
        assert parsed.emotions == []
    
    # ========== Context Tests ==========
    
    def test_parse_context_continuation(self):
        """Test parsing continuation context"""
        parsed = self.tc.parse("? : $ <+continuation>")
        assert "+continuation" in parsed.contexts
    
    def test_parse_context_correction(self):
        """Test parsing correction context"""
        parsed = self.tc.parse("? : $ <+correction>")
        assert "+correction" in parsed.contexts
    
    def test_parse_context_example(self):
        """Test parsing example context"""
        parsed = self.tc.parse("? : $ <+example>")
        assert "+example" in parsed.contexts
    
    def test_parse_multiple_contexts(self):
        """Test parsing multiple contexts"""
        parsed = self.tc.parse("? : $ <+continuation,+correction>")
        assert parsed.contexts == ["+continuation", "+correction"]
    
    def test_parse_no_context(self):
        """Test parsing without context"""
        parsed = self.tc.parse("? : $")
        assert parsed.contexts == []
    
    # ========== Combined Tests ==========
    
    def test_parse_emotion_and_context(self):
        """Test parsing both emotion and context"""
        parsed = self.tc.parse("? : $ [!urgent] <+continuation>")
        assert parsed.emotions == ["!urgent"]
        assert parsed.contexts == ["+continuation"]
    
    def test_parse_complex_command(self):
        """Test parsing complex command with everything"""
        cmd = "! : @ {e, b} (5) [!urgent,+positive] <+continuation,+example>"
        parsed = self.tc.parse(cmd)
        assert parsed.action_symbol == "!"
        assert parsed.object_symbol == "@"
        assert parsed.modifiers == ["e", "b"]
        assert parsed.limit == 5
        assert parsed.emotions == ["!urgent", "+positive"]
        assert parsed.contexts == ["+continuation", "+example"]
    
    # ========== Reverse Translation Tests ==========
    
    def test_reverse_translate_basic(self):
        """Test basic reverse translation"""
        hil = self.tc.reverse_translate("分析文档")
        assert ":" in hil
        assert "$" in hil
    
    def test_reverse_translate_with_emotion(self):
        """Test reverse translation with emotion detection"""
        hil = self.tc.reverse_translate("必须立即分析")
        assert "[!urgent" in hil or "[!critical" in hil
    
    def test_reverse_translate_with_context(self):
        """Test reverse translation with context detection"""
        hil = self.tc.reverse_translate("继续分析")
        assert "<+continuation>" in hil
    
    def test_reverse_translate_chinese(self):
        """Test reverse translation with Chinese modifiers"""
        hil = self.tc.reverse_translate("用中文分析")
        assert "{z}" in hil or "z" in hil
    
    # ========== Decode Tests ==========
    
    def test_decode_basic(self):
        """Test basic decode"""
        result = self.tc.decode("? : $")
        assert "analyze" in result.lower()
    
    def test_decode_with_emotion(self):
        """Test decode with emotion"""
        result = self.tc.decode("? : $ [!urgent]")
        assert "urgent" in result.lower()
    
    def test_decode_with_context(self):
        """Test decode with context"""
        result = self.tc.decode("? : $ <+continuation>")
        assert "continuing" in result.lower()
    
    def test_decode_full(self):
        """Test decode full command"""
        result = self.tc.decode("? : $ {z, b} (3) [!urgent] <+continuation>")
        assert "analyze" in result.lower()
        assert "Chinese" in result or "中文" in result
        assert "bullet" in result.lower()
        assert "urgent" in result.lower()
        assert "continuing" in result.lower()


def run_tests():
    """Run all tests"""
    test_class = TestHILTranscoderV2()
    test_class.setup_class()
    
    methods = [m for m in dir(test_class) if m.startswith("test_")]
    passed = 0
    failed = 0
    
    print("=" * 60)
    print("HIL Transcoder v0.2 单元测试")
    print("=" * 60)
    
    for method_name in methods:
        try:
            getattr(test_class, method_name)()
            print(f"✅ {method_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {method_name}: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
