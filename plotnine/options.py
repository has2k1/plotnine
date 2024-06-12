from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Literal, Optional, Type

    from plotnine import theme
    from plotnine.typing import FigureFormat

close_all_figures = False
"""
Development flag, e.g. set to `True` to prevent
the queuing up of figures when errors happen.
"""

current_theme: Optional[theme | Type[theme]] = None
"""Theme used when none is added to the ggplot object"""

base_family: str = "sans-serif"
"""
The base font family for all text that is part of the theme.
Default is sans-serif and one is chosen automatically from
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

figure_format: Optional[FigureFormat] = None
"""
The format for the inline figures outputted by the jupyter kernel.

If `None`, it is the value of

    %config InlineBackend.figure_format

If that has not been set, the default is "retina".
You can set it explicitly with:

    %config InlineBackend.figure_format = "retina"
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


# Quarto sets environment variables for the figure dpi, size and format
# for the project or document.
#
# https://quarto.org/docs/computations/execution-options.html#figure-options
#
# If we are in quarto, we read those and make them the default values for
# the options.
# Note that, reading the variables and setting them in a context manager
# cannot not work since the option values would be set after the original
# defaults have been used by the theme.
if "QUARTO_FIG_WIDTH" in os.environ:

    def _set_options_from_quarto():
        """
        Set options from quarto
        """
        global dpi, figure_size, figure_format

        dpi = int(os.environ["QUARTO_FIG_DPI"])
        figure_size = (
            float(os.environ["QUARTO_FIG_WIDTH"]),
            float(os.environ["QUARTO_FIG_HEIGHT"]),
        )

        # quarto verifies the format
        # If is retina, it doubles the original dpi and changes the
        # format to png
        figure_format = os.environ["QUARTO_FIG_FORMAT"]  # pyright: ignore

    _set_options_from_quarto()
