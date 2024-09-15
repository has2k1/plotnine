from __future__ import annotations

from typing import Optional


def get_plotnine_all(use_clipboard=True) -> Optional[str]:
    """
    Generate package level * (star) imports for plotnine

    The contents of __all__ in plotnine/__init__.py
    """
    from importlib import import_module

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

    def get_all_from_module(name, quote=False):
        """
        Module level imports
        """
        qname = f"plotnine.{name}"
        m = import_module(qname)
        fmt = ('"{}",' if quote else "{},").format
        return "\n    ".join(fmt(x) for x in sorted(m.__all__))

    _imports = "\n".join(
        f"from .{name} import (\n    {get_all_from_module(name)}\n)"
        for name in modules
    )
    _all = "\n".join(
        [
            "__all__ = (",
            "\n".join(
                f"    {get_all_from_module(name, True)}" for name in modules
            ),
            ")",
        ]
    )
    content = f"{_imports}\n\n{_all}"
    if use_clipboard:
        from pandas.io import clipboard

        clipboard.copy(content)  # pyright: ignore
    else:
        return content
