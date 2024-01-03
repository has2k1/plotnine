from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing import Any, Literal, Optional, Type

    from plotnine.typing import Theme

close_all_figures = False
"""
Development flag, e.g. set to `True` to prevent
the queuing up of figures when errors happen.
"""

current_theme: Optional[Theme | Type[Theme]] = None
"""Theme used when none is added to the ggplot object"""

base_family: str = "sans-serif"
"""
The base font family for all text that is part of the theme.
Default is sans-serif and one is choosen automatically from
rcParams["font.san-serif"]
"""

aspect_ratio: Literal["auto"] | float = "auto"
"""
Default aspect ratio used by the themes
"""

dpi: int = 100
"""
Default DPI used by the themes
"""

figure_size: tuple[float, float] = (640 / dpi, 480 / dpi)
"""
Default figure size inches
"""

base_margin: float = 0.01
"""
A size that is proportional of the figure width and
is used by some themes to determine other margins
"""


def get_option(name: str) -> Any:
    """
    Get package option

    Parameters
    ----------
    name :
        Name of the option
    """
    d = globals()

    if name in {"get_option", "set_option"} or name not in d:
        from .exceptions import PlotnineError

        raise PlotnineError(f"Unknown option {name}")

    return d[name]


def set_option(name: str, value: Any) -> Any:
    """
    Set package option

    Parameters
    ----------
    name :
        Name of the option
    value :
        New value of the option

    Returns
    -------
    :
        Old value of the option
    """
    d = globals()

    if name in {"get_option", "set_option"} or name not in d:
        from .exceptions import PlotnineError

        raise PlotnineError(f"Unknown option {name}")

    old = d[name]
    d[name] = value
    return old
