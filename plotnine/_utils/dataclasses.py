from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Iterable


def non_none_init_items(obj) -> Iterable[tuple[str, Any]]:
    """
    Yield (name, value) pairs of dataclass fields of `obj` that:

      1. Have `init=True` in their definition
      2. Have a value that is not `None`

    This function is shallow and does not recursively yield nested
    dataclasses.
    """
    return (
        (f.name, value)
        for f in fields(obj)
        if f.init and (value := getattr(obj, f.name)) is not None
    )
