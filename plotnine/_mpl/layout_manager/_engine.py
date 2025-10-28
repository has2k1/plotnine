from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.layout_engine import LayoutEngine

from ._composition_side_space import CompositionSideSpaces
from ._plot_side_space import PlotSideSpaces

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from plotnine import ggplot
    from plotnine.composition import Compose


class PlotnineLayoutEngine(LayoutEngine):
    """
    Geometry management for plotnine plots

    It works for both singular plots (ggplot) and compositions (Compose).
    For plots, it adjusts the position of objects around the panels and/or
    resizes the plot to the desired aspect-ratio. For compositions, it
    adjusts the position of objects (the annotations of the top-level
    composition) around the plots, and also the artists around the panels
    in all the contained plots.
    """

    _adjust_compatible = True
    _colorbar_gridspec = False

    def __init__(self, item: ggplot | Compose):
        self.item = item

    def execute(self, fig: Figure):
        from contextlib import nullcontext

        from plotnine import ggplot

        item = self.item
        renderer = fig._get_renderer()  # pyright: ignore[reportAttributeAccessIssue]

        with getattr(renderer, "_draw_disabled", nullcontext)():
            if isinstance(item, ggplot):
                item._sidespaces = PlotSideSpaces(item)
            else:
                item._sidespaces = CompositionSideSpaces(item)
            item._sidespaces.arrange()
