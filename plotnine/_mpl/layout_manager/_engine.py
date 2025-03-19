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
    from plotnine.plot_composition import Compose


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

        gsparams = spaces.get_gridspec_params()
        self.plot.facet._panels_gridspec.update(**asdict(gsparams))
        spaces.items._adjust_positions(spaces)


class PlotnineCompositionLayoutEngine(LayoutEngine):
    """
    Layout Manager for Plotnine Composition
    """

    _adjust_compatible = True
    _colorbar_gridspec = False

    def __init__(self, composition: Compose):
        self.composition = composition
        self.lookup_spaces: dict[ggplot, LayoutSpaces] = {}

    def execute(self, fig: Figure):
        from contextlib import nullcontext

        renderer = fig._get_renderer()  # pyright: ignore[reportAttributeAccessIssue]

        def get_spaces(plot):
            with getattr(renderer, "_draw_disabled", nullcontext)():
                return LayoutSpaces(plot)

        for ps in self.composition.plotspecs:
            spaces = get_spaces(ps.plot)
            self.lookup_spaces[ps.plot] = spaces

        self.align()

        for plot, spaces in self.lookup_spaces.items():
            gsparams = spaces.get_gridspec_params()
            if not gsparams.valid:
                warn(
                    "The layout manager failed, the figure size is too small "
                    "to contain all the plots. Use theme() increase the "
                    "figure size and/or reduce the size of the texts.",
                    PlotnineWarning,
                )
                break
            plot.facet._panels_gridspec.update(**asdict(gsparams))
            spaces.items._adjust_positions(spaces)

    def align(self):
        from ._layout_tree import LayoutTree

        tree = LayoutTree.create(self.composition, self.lookup_spaces)
        tree.align()
