#!/usr/bin/env python

"""
Print annotated `plotnine.themes.theme.__init__` themeable params from
`themeable` docstrings.

Note that the resulting output requires some manual deduplication.
"""

import inspect
import re

from plotnine.themes.theme import theme
from plotnine.themes.themeable import themeable

_ELEMENTS = frozenset({"element_text", "element_line", "element_rect"})
_SKIP = frozenset({"self", "complete", "kwargs"})
_PATTERN = re.compile(r"^\s*theme_element : (.+?)$", re.MULTILINE)


def _doc_type(tp: type) -> str | None:
    for klass in tp.__mro__:
        if m := _PATTERN.search(klass.__doc__ or ""):
            break
    else:
        return None

    s = re.sub(r"\s+", " ", m[1])
    s = re.sub(r",\s*default\s*=.*$", "", s).strip()
    if s in _ELEMENTS:
        s = f"{s} | element_blank"
    return s


def _param_type(name: str) -> str | None:
    # e.g. axis_line_x_bottom -> axis_line_x -> axis_line
    registry = themeable.registry()
    parts = name.split("_")
    while parts:
        if (tp := registry.get("_".join(parts))) and (s := _doc_type(tp)):
            return s
        parts.pop()
    return None


def main():
    for name in inspect.signature(theme.__init__).parameters:
        if name in _SKIP:
            continue
        if (ann := _param_type(name)) is None:
            print(f"        {name}=None,  # FIXME")
        else:
            if not re.search(r"\bNone$", ann):
                ann = f"{ann} | None"
            print(f"        {name}: {ann} = None,")


if __name__ == "__main__":
    main()
