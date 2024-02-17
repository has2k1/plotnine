from __future__ import annotations

from typing import Optional


def get_plotnine_all(use_clipboard=True) -> Optional[str]:
    """
    Generate package level * (star) imports for plotnine

    The contents of __all__ in plotnine/__init__.py
    """
    from importlib import import_module
    from textwrap import indent

    modules = (
        "coords",
        "facets",
        "geoms",
        "ggplot",
        "guides",
        "labels",
        "mapping",
        "positions",
        "qplot",
        "scales",
        "stats",
        "themes",
        "themes.elements",
        "watermark",
    )

    comma_join = ",\n".join

    def get_all_from_module(name):
        """
        Module level imports
        """
        qname = f"plotnine.{name}"
        comment = f"# {qname}\n"
        m = import_module(qname)
        return comment + comma_join(f'"{x}"' for x in sorted(m.__all__))

    _imports = "\n".join(f"from .{name} import *" for name in modules)
    lst = indent(
        comma_join(get_all_from_module(name) for name in modules), " " * 4
    )
    _all = f"__all__ = (\n{lst},\n)"
    content = f"{_imports}\n\n{_all}"
    if use_clipboard:
        from pandas.io import clipboard

        clipboard.copy(content)  # pyright: ignore
    else:
        return content
