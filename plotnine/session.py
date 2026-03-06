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
    Retrieve the last plot rendered in this session

    Returns
    -------
    ggplot | Compose | None
        The last plot that was rendered via `draw()`, `save()`,
        or notebook display. Returns `None` if no plot has been
        rendered yet.
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
