from __future__ import annotations

import typing
from dataclasses import asdict, dataclass

from matplotlib.layout_engine import LayoutEngine
from matplotlib.text import Text

if typing.TYPE_CHECKING:
    from typing import Optional

    from matplotlib.backend_bases import RendererBase
    from matplotlib.offsetbox import AnchoredOffsetbox

    from plotnine.typing import (
        Any,
        Axes,
        Facet,
        Figure,
        Ggplot,
        LegendPosition,
        Theme,
    )


@dataclass
class LayoutPack:
    """
    Objects required to compute the layout
    """

    axs: list[Axes]
    figure: Figure
    renderer: RendererBase
    theme: Theme
    facet: Facet
    axis_title_x: Optional[Text] = None
    axis_title_y: Optional[Text] = None
    # The legend references the legend_background. That is the
    # AnchoredOffsetbox that contains all the legends.
    legend: Optional[AnchoredOffsetbox] = None
    legend_position: Optional[LegendPosition] = None
    plot_caption: Optional[Text] = None
    plot_subtitle: Optional[Text] = None
    plot_title: Optional[Text] = None


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

    plot: Ggplot
    _theme_targets: dict[str, Any]

    def __init__(self, plot: Ggplot):
        self.plot = plot
        self._theme_targets = plot.theme._targets

    def execute(self, fig: Figure):
        from contextlib import nullcontext

        from ._plotnine_tight_layout import (
            get_plotnine_tight_layout,
            set_figure_artist_positions,
        )

        pack = self.pack_information()

        with getattr(pack.renderer, "_draw_disabled", nullcontext)():
            tparams = get_plotnine_tight_layout(pack)

        set_figure_artist_positions(pack, tparams)
        fig.subplots_adjust(**asdict(tparams.grid))

    def pack_information(self) -> LayoutPack:
        """
        Put together objects required to do the layout
        """
        _property = self.plot.theme.themeables.property
        is_blank = self.plot.theme.themeables.is_blank
        get_target = self._theme_targets.get

        def get(th: str) -> Any:
            """
            Return themeable target or None
            """
            if is_blank(th):
                return None
            else:
                t = get_target(th, None)
                if isinstance(t, Text) and t.get_text() == "":
                    return None
                return t

        legend_position = _property("legend_position")
        if legend_position in ("none", "None"):
            legend_position = None

        return LayoutPack(
            axs=self.plot.axs,
            figure=self.plot.figure,
            renderer=self.plot.figure._get_renderer(),  # pyright: ignore
            theme=self.plot.theme,
            facet=self.plot.facet,
            axis_title_x=get("axis_title_x"),
            axis_title_y=get("axis_title_y"),
            legend=get_target("legend_background"),
            legend_position=legend_position,
            plot_caption=get("plot_caption"),
            plot_subtitle=get("plot_subtitle"),
            plot_title=get("plot_title"),
        )
