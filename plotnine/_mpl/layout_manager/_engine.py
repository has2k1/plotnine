from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING
from warnings import warn

from matplotlib.layout_engine import LayoutEngine

from ...exceptions import PlotnineWarning
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


class PlotnineCompositionLayoutEngine(LayoutEngine):
    """
    Layout Manager for Plotnine Composition
    """

    _adjust_compatible = True
    _colorbar_gridspec = False

    def __init__(self, plots: list[ggplot]):
        self.plots = plots

    def execute(self, fig: Figure):
        from contextlib import nullcontext

        renderer = fig._get_renderer()  # pyright: ignore[reportAttributeAccessIssue]

        def get_spaces(plot):
            with getattr(renderer, "_draw_disabled", nullcontext)():
                return LayoutSpaces(plot)

        for plot in self.plots:
            spaces = get_spaces(plot)
            if not spaces.gsparams.valid:
                warn(
                    "The layout manager failed, the figure size is too small "
                    "to contain all the plots. Use theme() increase the "
                    "figure size and/or reduce the size of the texts.",
                    PlotnineWarning,
                )
                break

            plot.facet._panels_gridspec.update(**asdict(spaces.gsparams))
            spaces.items._adjust_positions(spaces)
