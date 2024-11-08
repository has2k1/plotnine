from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from matplotlib.layout_engine import LayoutEngine

from ._layout_pack import LayoutPack

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

        from ._plotnine_tight_layout import (
            get_plotnine_tight_layout,
            set_figure_artist_positions,
        )

        pack = LayoutPack(self.plot)

        with getattr(pack.renderer, "_draw_disabled", nullcontext)():
            tparams = get_plotnine_tight_layout(pack)

        fig.subplots_adjust(**asdict(tparams.params))
        set_figure_artist_positions(pack, tparams)
