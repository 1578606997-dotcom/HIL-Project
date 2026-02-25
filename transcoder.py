"""HIL transcoder for decoding compact HIL commands to natural-language prompts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from hil_spec import HIL_V0_1


@dataclass
class ParsedHIL:
    """Structured representation of a decoded HIL command."""

    action_symbol: str
    object_symbol: str
    object_args: List[str]
    modifiers: List[str]
    limit: Optional[int]


class HILTranscoder:
    """Decode HIL v0.1 commands into concise natural-language prompts.

    Supported grammar (spaces optional):
        <action> : <object> {<modifier>[, <modifier> ...]} (<n>)

    Example:
        ? : $ {z, b} (3)
        ? : @vs(Apple, Tesla) {b}
    """

    _ACTION_PATTERN = r"(?P<action>[?!>])"
    _OBJECT_PATTERN = r"(?P<object>[\$@][\w\(\),\s]*)"
    _MODIFIERS_PATTERN = r"(?:\{(?P<modifiers>[^}]*)\})?"
    _LIMIT_PATTERN = r"(?:\((?P<limit>\d+)\))?"

    _COMMAND_RE = re.compile(
        rf"^\s*{_ACTION_PATTERN}\s*:?"
        rf"\s*{_OBJECT_PATTERN}"
        rf"\s*{_MODIFIERS_PATTERN}"
        rf"\s*{_LIMIT_PATTERN}\s*$"
    )

    _OBJECT_WITH_ARGS_RE = re.compile(
        r"^(?P<base>[\$@]\w*)(?:\((?P<args>.*)\))?$"
    )

    def _split_object(self, object_token: str) -> Tuple[str, List[str]]:
        token = object_token.strip()
        if token == "$":
            return "$", []

        match = self._OBJECT_WITH_ARGS_RE.match(token)
        if not match:
            raise ValueError(f"Invalid object token: {object_token!r}")

        base = match.group("base")
        args_raw = match.group("args")
        if args_raw:
            args = [arg.strip() for arg in args_raw.split(",") if arg.strip()]
        else:
            args = []
        return base, args

    def parse(self, hil_cmd: str) -> ParsedHIL:
        """Parse HIL command into symbols and parameters."""

        match = self._COMMAND_RE.match(hil_cmd)
        if not match:
            raise ValueError(f"Invalid HIL command format: {hil_cmd!r}")

        action_symbol = match.group("action")
        object_token = (match.group("object") or "").strip()
        object_symbol, object_args = self._split_object(object_token)
        raw_modifiers = match.group("modifiers") or ""
        limit_raw = match.group("limit")

        modifiers = [m.strip() for m in raw_modifiers.split(",") if m.strip()]

        if object_symbol not in HIL_V0_1.objects:
            raise ValueError(
                f"Unsupported object symbol: {object_symbol!r}. "
                f"Supported: {sorted(HIL_V0_1.objects)}"
            )

        unsupported_mods = [m for m in modifiers if m not in HIL_V0_1.modifiers]
        if unsupported_mods:
            raise ValueError(
                f"Unsupported modifier(s): {unsupported_mods}. "
                f"Supported: {sorted(HIL_V0_1.modifiers)}"
            )

        limit = int(limit_raw) if limit_raw else None
        return ParsedHIL(
            action_symbol=action_symbol,
            object_symbol=object_symbol,
            object_args=object_args,
            modifiers=modifiers,
            limit=limit,
        )

    def decode(self, hil_cmd: str) -> str:
        """Decode HIL command into a natural-language prompt."""

        parsed = self.parse(hil_cmd)

        action_phrase = HIL_V0_1.actions[parsed.action_symbol]
        object_phrase = HIL_V0_1.objects[parsed.object_symbol]

        if parsed.object_symbol == "@vs" and parsed.object_args:
            joined = ", ".join(parsed.object_args)
            object_phrase = (
                "a compare-and-contrast analysis between "
                f"{joined}"
            )

        parts = [f"Please {action_phrase} {object_phrase}"]

        if parsed.modifiers:
            modifier_phrase = " and ".join(
                HIL_V0_1.modifiers[m] for m in parsed.modifiers
            )
            parts.append(modifier_phrase)

        if parsed.limit is not None:
            parts.append(f"limited to {parsed.limit} points")

        sentence = " and ".join(parts) + "."
        return sentence[0].upper() + sentence[1:]

    def reverse_translate(
        self,
        natural_language: str,
        llm_client: Optional[Any] = None,
        model: str = "gpt-4o-mini",
    ) -> str:
        """Translate natural language to HIL with rules + optional LLM refinement."""

        text = natural_language.strip()
        lowered = text.lower()

        # Rule-based fallback (fast, deterministic)
        action = "?"
        if any(k in lowered for k in ("create", "write", "generate", "生成", "写")):
            action = "!"
        elif any(
            k in lowered
            for k in ("transform", "convert", "rewrite", "改写", "转换")
        ):
            action = ">"

        object_part = "$"
        if "top" in lowered and any(
            k in lowered for k in ("advantage", "优势", "竞争")
        ):
            object_part = "@top"
        elif any(k in lowered for k in ("compare", "versus", "vs", "对比", "竞品")):
            pair = re.findall(r"([A-Z][A-Za-z0-9\-_]+)", text)
            if len(pair) >= 2:
                object_part = f"@vs({pair[0]}, {pair[1]})"
            else:
                object_part = "@vs"
        elif any(k in lowered for k in ("knowledge base", "rag", "知识库", "检索")):
            object_part = "@"

        modifiers: List[str] = []
        if any(k in lowered for k in ("中文", "chinese")):
            modifiers.append("z")
        if any(k in lowered for k in ("bullet", "要点", "列表")):
            modifiers.append("b")
        if "json" in lowered:
            modifiers.append("s")

        count_match = re.search(
            r"(?:\b|第)(\d{1,3})(?:\s*(?:points?|条|项))?",
            lowered,
        )
        limit = int(count_match.group(1)) if count_match else None

        hil = f"{action} : {object_part}"
        if modifiers:
            hil += " {" + ", ".join(modifiers) + "}"
        if limit is not None:
            hil += f" ({limit})"

        # Optional LLM refinement
        if llm_client is not None:
            try:
                system_prompt = (
                    "You convert natural-language requests into one-line HIL commands. "
                    "Allowed actions: ?, !, >. Allowed objects: $, @, @vs, @top. "
                    "Allowed modifiers: z,b,s. Output only HIL."
                )
                user_prompt = (
                    f"Text: {text}\n"
                    f"Draft HIL: {hil}\n"
                    "Return final HIL only."
                )

                if hasattr(llm_client, "responses"):
                    rsp = llm_client.responses.create(
                        model=model,
                        input=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                    )
                    candidate = getattr(rsp, "output_text", "").strip()
                elif (
                    hasattr(llm_client, "chat")
                    and hasattr(llm_client.chat, "completions")
                ):
                    rsp = llm_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                    )
                    candidate = rsp.choices[0].message.content.strip()
                else:
                    candidate = ""

                if candidate:
                    self.parse(candidate)
                    hil = candidate
            except Exception:
                pass

        # Final validation
        self.parse(hil)
        return hil


if __name__ == "__main__":
    transcoder = HILTranscoder()

    demo = "? : $ {z, b} (3)"
    print("Decode demo:", demo)
    print(transcoder.decode(demo))

    vs_demo = "? : @vs(Apple, Tesla) {b} (5)"
    print("\nCompare demo:", vs_demo)
    print(transcoder.decode(vs_demo))

    reverse_demo = "总结这份文档"
    print("\nReverse demo:", reverse_demo)
    print(transcoder.reverse_translate(reverse_demo))
