from __future__ import annotations

import typing
from dataclasses import asdict, dataclass

from matplotlib.layout_engine import LayoutEngine
from matplotlib.text import Text

if typing.TYPE_CHECKING:
    from typing import Any, Optional

    from matplotlib.axes import Axes
    from matplotlib.backend_bases import RendererBase
    from matplotlib.figure import Figure

    from plotnine import ggplot, theme
    from plotnine._mpl.text import StripText
    from plotnine.facets.facet import facet
    from plotnine.iapi import legend_artists


@dataclass
class LayoutPack:
    """
    Objects required to compute the layout
    """

    axs: list[Axes]
    figure: Figure
    renderer: RendererBase
    theme: theme
    facet: facet
    axis_title_x: Optional[Text] = None
    axis_title_y: Optional[Text] = None
    # The legends references the structure that contains the
    # AnchoredOffsetboxes (groups of legends)
    legends: Optional[legend_artists] = None
    plot_caption: Optional[Text] = None
    plot_subtitle: Optional[Text] = None
    plot_title: Optional[Text] = None
    strip_text_x: Optional[list[StripText]] = None
    strip_text_y: Optional[list[StripText]] = None


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

        pack = self.setup()

        with getattr(pack.renderer, "_draw_disabled", nullcontext)():
            tparams = get_plotnine_tight_layout(pack)

        fig.subplots_adjust(**asdict(tparams.params))
        set_figure_artist_positions(pack, tparams)

    def setup(self) -> LayoutPack:
        """
        Put together objects required to do the layout
        """
        targets = self.theme.targets

        def get_target(name: str) -> Any:
            """
            Return themeable target or None
            """
            if self.theme.T.is_blank(name):
                return None
            else:
                t = getattr(targets, name)
                if isinstance(t, Text) and t.get_text() == "":
                    return None
                return t

        return LayoutPack(
            axs=self.plot.axs,
            figure=self.plot.figure,
            renderer=self.plot.figure._get_renderer(),  # pyright: ignore
            theme=self.theme,
            facet=self.plot.facet,
            axis_title_x=get_target("axis_title_x"),
            axis_title_y=get_target("axis_title_y"),
            legends=get_target("legends"),
            plot_caption=get_target("plot_caption"),
            plot_subtitle=get_target("plot_subtitle"),
            plot_title=get_target("plot_title"),
            strip_text_x=get_target("strip_text_x"),
            strip_text_y=get_target("strip_text_y"),
        )
