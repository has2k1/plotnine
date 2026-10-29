from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.collections import LineCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import FancyBboxPatch, Rectangle
    from matplotlib.text import Text

    from plotnine._mpl.offsetbox import ColoredDrawingArea
    from plotnine._mpl.text import StripText
    from plotnine.iapi import legend_artists


@dataclass
class ThemeTargets:
    """
    Artists that will be themed

    This includes only artist that cannot be easily accessed from
    the figure or the axes.
    """

    axis_title_x_top: Text | None = None
    axis_title_x_bottom: Text | None = None
    axis_title_y_left: Text | None = None
    axis_title_y_right: Text | None = None
    legend_frame: Rectangle | None = None
    legend_key: list[ColoredDrawingArea] = field(default_factory=list)
    legends: legend_artists | None = None
    legend_text_colorbar: list[Text] = field(default_factory=list)
    legend_text_legend: list[Text] = field(default_factory=list)
    legend_axis_line: LineCollection | None = None
    legend_ticks: LineCollection | None = None
    legend_title: Text | None = None
    panel_border: list[Rectangle] = field(default_factory=list)
    plot_caption: Text | None = None
    plot_subtitle: Text | None = None
    plot_footer: Text | None = None
    plot_tag: Text | None = None
    plot_title: Text | None = None
    plot_background: Rectangle | None = None
    plot_footer_background: Rectangle | None = None
    plot_footer_line: Line2D | None = None
    strip_background_x: list[FancyBboxPatch] = field(default_factory=list)
    strip_background_y: list[FancyBboxPatch] = field(default_factory=list)
    strip_text_x_top: list[StripText] = field(default_factory=list)
    strip_text_x_bottom: list[StripText] = field(default_factory=list)
    strip_text_y_left: list[StripText] = field(default_factory=list)
    strip_text_y_right: list[StripText] = field(default_factory=list)
