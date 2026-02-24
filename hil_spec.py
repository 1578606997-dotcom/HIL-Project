"""HIL v0.1 syntax specification.

This module centralizes symbol-to-semantics mappings so parser/decoder logic
can stay lightweight and maintainable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class HILSpec:
    """Container for HIL v0.1 symbol mappings."""

    actions: Dict[str, str]
    objects: Dict[str, str]
    modifiers: Dict[str, str]


HIL_V0_1 = HILSpec(
    actions={
        "?": "analyze",
        "!": "create",
        ">": "transform",
    },
    objects={
        "$": "the provided document",
        "@": "the knowledge base (RAG context)",
        "@vs": "a compare-and-contrast analysis across competitors",
        "@top": "the top competitive advantages from the knowledge base",
    },
    modifiers={
        "z": "in Chinese",
        "b": "using bullet points",
        "s": "as a JSON schema",
    },
)


def supported_symbols() -> Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
    """Return all supported action/object/modifier symbols."""

    return (
        tuple(HIL_V0_1.actions.keys()),
        tuple(HIL_V0_1.objects.keys()),
        tuple(HIL_V0_1.modifiers.keys()),
    )
