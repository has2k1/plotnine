from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

    from plotnine import ggplot

__all__ = ("get_aesthetic_limits",)


def get_aesthetic_limits(
    plot: ggplot,
    ae: str,
) -> (
    tuple[float, float]
    | Sequence[str]
    | list[tuple[float]]
    | list[Sequence[str]]
):
    """
    Get the limits of an aesthetic

    These are the limits before they are expanded.

    Parameters
    ----------
    plot :
        ggplot object

    ae :
        Name of aesthetic

    Returns
    -------
    out :
        The limits of the aesthetic. If the plot is facetted, (has many
        panels), it is a sequence of limits, one for each panel.
    """
    plot = deepcopy(plot)
    plot._build()
    limits = [
        getattr(panel, ae).limits
        for panel in plot._build_objs.layout.panel_params
    ]

    return limits[0] if len(limits) == 1 else limits
