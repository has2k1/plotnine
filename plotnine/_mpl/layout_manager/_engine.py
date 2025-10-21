from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

from matplotlib.layout_engine import LayoutEngine

from ...exceptions import PlotnineWarning
from ._composition_side_space import CompositionLayoutSpaces
from ._layout_tree import LayoutTree
from ._plot_side_space import PlotLayoutSpaces

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
            spaces = PlotLayoutSpaces(self.plot)

        gsparams = spaces.get_gridspec_params()
        self.plot.facet._gridspec.update_params_and_artists(gsparams)
        spaces.items._adjust_positions(spaces)


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
        cmp = self.composition

        # Caculate the space taken up by all plot artists
        lookup_spaces: dict[ggplot, PlotLayoutSpaces] = {}
        with getattr(renderer, "_draw_disabled", nullcontext)():
            cmp_spaces = CompositionLayoutSpaces(cmp)
            gsparams = cmp_spaces.get_gridspec_params()
            cmp.items._gridspec.update_params_and_artists(gsparams)
            cmp_spaces.items._adjust_positions(cmp_spaces)

            for ps in self.composition.plotspecs:
                lookup_spaces[ps.plot] = PlotLayoutSpaces(ps.plot)

        # Adjust the size and placements of the plots
        tree = LayoutTree.create(self.composition, lookup_spaces)
        tree.harmonise()

        # Set the final positions of the artists in each plot
        for plot, spaces in lookup_spaces.items():
            gsparams = spaces.get_gridspec_params()
            if not gsparams.valid:
                warn(
                    "The layout manager failed, the figure size is too small "
                    "to contain all the plots. Use theme() increase the "
                    "figure size and/or reduce the size of the texts.",
                    PlotnineWarning,
                )
                break
            plot.facet._gridspec.update_params_and_artists(gsparams)
            spaces.items._adjust_positions(spaces)
