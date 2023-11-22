from __future__ import annotations

from typing import Literal, TypeAlias

DisplayNameFormat: TypeAlias = Literal[
    "full", "name", "short", "relative", "canonical"
]
DocObjectKind: TypeAlias = Literal[
    "module", "class", "method", "function", "attribute", "alias"
]
