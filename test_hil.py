"""Tests for HIL transcoder."""

import pytest
from transcoder import HILTranscoder


class TestHILTranscoder:
    """Test suite for HILTranscoder."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transcoder = HILTranscoder()

    def test_decode_analyze_document(self):
        """Test decoding analyze document command."""
        hil = "? : $ {z, b} (3)"
        result = self.transcoder.decode(hil)
        assert "分析" in result or "analyze" in result.lower()
        assert "3" in result

    def test_decode_compare(self):
        """Test decoding compare command."""
        hil = "? : @vs(Apple, Tesla) {b} (5)"
        result = self.transcoder.decode(hil)
        assert "compare" in result.lower() or "对比" in result
        assert "Apple" in result
        assert "Tesla" in result

    def test_decode_transform(self):
        """Test decoding transform command."""
        hil = "> : @ {s}"
        result = self.transcoder.decode(hil)
        assert result  # Should not be empty

    def test_invalid_command(self):
        """Test handling of invalid command."""
        with pytest.raises(Exception):
            self.transcoder.decode("invalid command")


class TestHILSpec:
    """Test HIL specification constants."""

    def test_action_symbols(self):
        """Test action symbols are defined."""
        from hil_spec import HIL_V0_1
        assert "?" in HIL_V0_1["actions"]
        assert "!" in HIL_V0_1["actions"]
        assert ">" in HIL_V0_1["actions"]

    def test_object_symbols(self):
        """Test object symbols are defined."""
        from hil_spec import HIL_V0_1
        assert "$" in HIL_V0_1["objects"]
        assert "@" in HIL_V0_1["objects"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
