from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.layout_engine import LayoutEngine

from ._composition_side_space import CompositionSideSpaces
from ._layout_tree import LayoutTree
from ._plot_side_space import PlotSideSpaces

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from plotnine import ggplot
    from plotnine.composition import Compose


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
            self.plot._sidespaces = PlotSideSpaces(self.plot)

        self.plot._sidespaces.resize_gridspec()
        self.plot._sidespaces.place_artists()


class PlotnineCompositionLayoutEngine(LayoutEngine):
    """
    Layout Manager for Plotnine Composition
    """

    _adjust_compatible = True
    _colorbar_gridspec = False

    def __init__(self, composition: Compose):
        self.composition = composition
        """
        Top level composition
        """

    def execute(self, fig: Figure):
        from contextlib import nullcontext

        renderer = fig._get_renderer()  # pyright: ignore[reportAttributeAccessIssue]
        cmp = self.composition

        # Calculate the sidespaces of:
        #   1. The top composition
        #   2. All the contained plots (recurvively)
        with getattr(renderer, "_draw_disabled", nullcontext)():
            # We have to apply the spaces of the composition before
            # executing the LayoutTree because it expects the
            # ._sub_gridspec of the composition to have its final
            # position and total area.
            cmp._sidespaces = CompositionSideSpaces(cmp)
            cmp._sidespaces.resize_gridspec()

            for plot in cmp.iter_plots_all():
                plot._sidespaces = PlotSideSpaces(plot)

        # Adjust the numbers that align the plots, and resize them.
        tree = LayoutTree.create(cmp)
        tree.arrange_layout()

        # At this point, the compositions > plots > panels have been
        # placed in their final positions and have the desired sizes.
        # We place the artists around them into their final positions.
        cmp._sidespaces.place_artists()
        for plot in cmp.iter_plots_all():
            plot._sidespaces.resize_gridspec()
            plot._sidespaces.place_artists()
