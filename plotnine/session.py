"""
Session state for plotnine
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plotnine.composition._compose import Compose
    from plotnine.ggplot import ggplot

__all__ = ("last_plot",)

LAST_PLOT: ggplot | Compose | None = None


def last_plot() -> ggplot | Compose | None:
    """
    Return the specification of the last plot drawn in this session

    Returns
    -------
    ggplot | Compose | None
        The plot specification captured before `draw()`, `save()`, or notebook
        display builds it. Returns `None` before the session draws a plot.
    """
    return LAST_PLOT


def set_last_plot(plot: ggplot | Compose) -> None:
    """
    Save the last plot rendered in this session
    """
    global LAST_PLOT
    LAST_PLOT = plot


def reset_last_plot() -> None:
    """
    Clear the last plot rendered in this session
    """
    global LAST_PLOT
    LAST_PLOT = None
