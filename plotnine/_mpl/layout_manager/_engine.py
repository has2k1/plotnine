from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from matplotlib.layout_engine import LayoutEngine

from ._spaces import LayoutSpaces

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from plotnine import ggplot


class PlotnineLayoutEngine(LayoutEngine):
    """
    Implement geometry management for plotnine plots

    This layout manager automatically adjusts the location of
    objects placed around the plot panels and the subplot
    spacing parameters so that the plot fits cleanly within
    the figure area.
    """

    _adjust_compatible = True
    _colorbar_gridspec = False

    def __init__(self, plot: ggplot):
        self.plot = plot
        self.theme = plot.theme

    def execute(self, fig: Figure):
        from contextlib import nullcontext

        renderer = fig._get_renderer()  # pyright: ignore[reportAttributeAccessIssue]

        with getattr(renderer, "_draw_disabled", nullcontext)():
            spaces = LayoutSpaces(self.plot)

        self.plot.facet._panels_gridspec.update(**asdict(spaces.gsparams))
        spaces.items._adjust_positions(spaces)
