from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from matplotlib.backend_bases import RendererBase
from matplotlib.text import Text

from plotnine import ggplot

if TYPE_CHECKING:
    from plotnine._mpl.text import StripText
    from plotnine.iapi import legend_artists


@dataclass
class LayoutPack:
    """
    Objects required to compute the layout
    """

    plot: ggplot

    def __post_init__(self):
        def get(name: str) -> Any:
            """
            Return themeable target or None
            """
            if self.theme.T.is_blank(name):
                return None
            else:
                t = getattr(self.theme.targets, name)
                if isinstance(t, Text) and t.get_text() == "":
                    return None
                return t

        self.axs = self.plot.axs
        self.theme = self.plot.theme
        self.figure = self.plot.figure
        self.facet = self.plot.facet
        self.renderer = cast(RendererBase, self.plot.figure._get_renderer())  # pyright: ignore

        self.axis_title_x: Text | None = get("axis_title_x")
        self.axis_title_y: Text | None = get("axis_title_y")

        # # The legends references the structure that contains the
        # # AnchoredOffsetboxes (groups of legends)
        self.legends: legend_artists | None = get("legends")
        self.plot_caption: Text | None = get("plot_caption")
        self.plot_subtitle: Text | None = get("plot_subtitle")
        self.plot_title: Text | None = get("plot_title")
        self.strip_text_x: list[StripText] | None = get("strip_text_x")
        self.strip_text_y: list[StripText] | None = get("strip_text_y")
