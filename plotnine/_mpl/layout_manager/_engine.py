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

        self.plot._sidespaces.apply()
        self.plot._sidespaces.adjust_artist_positions()


class PlotnineCompositionLayoutEngine(LayoutEngine):
    """
    Layout Manager for Plotnine Composition
    """

    _adjust_compatible = True
    _colorbar_gridspec = False

    def __init__(self, composition: Compose):
        self.composition = composition

    def execute(self, fig: Figure):
        from contextlib import nullcontext

        renderer = fig._get_renderer()  # pyright: ignore[reportAttributeAccessIssue]

        # Calculate the all sidespaces (recursively)
        # For the compositions, we have to also update (.apply)
        # the gridspec so that LayoutTree has the right information
        # to arrange the plots and resize them (.harmonise).
        def _calculate_sidespaces(cmp: Compose):
            cmp._sidespaces = CompositionSideSpaces(cmp)
            cmp._sidespaces.apply()

            for plot in cmp.iter_plots():
                plot._sidespaces = PlotSideSpaces(plot)

            for sub_cmp in cmp.iter_sub_compositions():
                _calculate_sidespaces(sub_cmp)

        # Caculate the space taken up by all plot artists
        with getattr(renderer, "_draw_disabled", nullcontext)():
            _calculate_sidespaces(self.composition)

        # Adjust the size and placements of the plots
        tree = LayoutTree.create(self.composition)
        tree.harmonise()

        # Recursively place the artists in both the compositions
        # and plots in their final position.
        # First we update (.apply) the plot gridspecs as LayoutTree
        # has adjusted the sidespaces to their final values.
        def _adjust_artist_positions(cmp: Compose):
            cmp._sidespaces.adjust_artist_positions()

            for plot in cmp.iter_plots():
                plot._sidespaces.apply()
                plot._sidespaces.adjust_artist_positions()

            for sub_cmp in cmp.iter_sub_compositions():
                _adjust_artist_positions(sub_cmp)

        _adjust_artist_positions(self.composition)
