"""HIL transcoder for decoding compact HIL commands to natural-language prompts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from hil_spec import HIL_V0_1


@dataclass
class ParsedHIL:
    """Structured representation of a decoded HIL command."""

    action_symbol: str
    object_symbol: str
    modifiers: List[str]
    limit: Optional[int]


class HILTranscoder:
    """Decode HIL v0.1 commands into concise natural-language prompts.

    Supported grammar (spaces optional):
        <action> : <object> {<modifier>[, <modifier> ...]} (<n>)

    Example:
        ? : $ {z, b} (3)
    """

    _ACTION_PATTERN = r"(?P<action>[?!>])"
    _OBJECT_PATTERN = r"(?P<object>[$@])"
    _MODIFIERS_PATTERN = r"(?:\{(?P<modifiers>[^}]*)\})?"
    _LIMIT_PATTERN = r"(?:\((?P<limit>\d+)\))?"

    _COMMAND_RE = re.compile(
        rf"^\s*{_ACTION_PATTERN}\s*:?\s*{_OBJECT_PATTERN}\s*{_MODIFIERS_PATTERN}\s*{_LIMIT_PATTERN}\s*$"
    )

    def parse(self, hil_cmd: str) -> ParsedHIL:
        """Parse HIL command into symbols and parameters."""

        match = self._COMMAND_RE.match(hil_cmd)
        if not match:
            raise ValueError(f"Invalid HIL command format: {hil_cmd!r}")

        action_symbol = match.group("action")
        object_symbol = match.group("object")
        raw_modifiers = match.group("modifiers") or ""
        limit_raw = match.group("limit")

        modifiers = [m.strip() for m in raw_modifiers.split(",") if m.strip()]

        unsupported = [m for m in modifiers if m not in HIL_V0_1.modifiers]
        if unsupported:
            raise ValueError(
                f"Unsupported modifier(s): {unsupported}. "
                f"Supported: {sorted(HIL_V0_1.modifiers)}"
            )

        limit = int(limit_raw) if limit_raw else None
        return ParsedHIL(
            action_symbol=action_symbol,
            object_symbol=object_symbol,
            modifiers=modifiers,
            limit=limit,
        )

    def decode(self, hil_cmd: str) -> str:
        """Decode HIL command into a natural-language prompt."""

        parsed = self.parse(hil_cmd)

        action_phrase = HIL_V0_1.actions[parsed.action_symbol]
        object_phrase = HIL_V0_1.objects[parsed.object_symbol]

        parts = [f"Please {action_phrase} {object_phrase}"]

        if parsed.modifiers:
            modifier_phrase = " and ".join(HIL_V0_1.modifiers[m] for m in parsed.modifiers)
            parts.append(modifier_phrase)

        if parsed.limit is not None:
            parts.append(f"limited to {parsed.limit} points")

        sentence = " and ".join(parts) + "."
        return sentence[0].upper() + sentence[1:]


if __name__ == "__main__":
    demo = "? : $ {z, b} (3)"
    print(HILTranscoder().decode(demo))
