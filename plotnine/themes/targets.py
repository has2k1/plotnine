from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

    from matplotlib.collections import LineCollection
    from matplotlib.patches import Rectangle
    from matplotlib.text import Text

    from plotnine._mpl.offsetbox import ColoredDrawingArea
    from plotnine._mpl.patches import StripTextPatch
    from plotnine._mpl.text import StripText
    from plotnine.iapi import legend_artists


@dataclass
class ThemeTargets:
    """
    Artists that will be themed

    This includes only artist that cannot be accessed easily from
    the figure or the axes.
    """

    axis_title_x: Optional[Text] = None
    axis_title_y: Optional[Text] = None
    legend_frame: Optional[Rectangle] = None
    legend_key: list[ColoredDrawingArea] = field(default_factory=list)
    legends: Optional[legend_artists] = None
    legend_text_colorbar: list[Text] = field(default_factory=list)
    legend_text_legend: list[Text] = field(default_factory=list)
    legend_ticks: Optional[LineCollection] = None
    legend_title: Optional[Text] = None
    panel_border: list[Rectangle] = field(default_factory=list)
    plot_caption: Optional[Text] = None
    plot_subtitle: Optional[Text] = None
    plot_title: Optional[Text] = None
    strip_background_x: list[StripTextPatch] = field(default_factory=list)
    strip_background_y: list[StripTextPatch] = field(default_factory=list)
    strip_text_x: list[StripText] = field(default_factory=list)
    strip_text_y: list[StripText] = field(default_factory=list)
