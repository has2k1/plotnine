from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Sequence, TypeAlias

    from matplotlib.collections import LineCollection
    from matplotlib.offsetbox import AnchoredOffsetbox
    from matplotlib.patches import Rectangle
    from matplotlib.text import Text

    from plotnine._mpl.offsetbox import ColoredDrawingArea
    from plotnine._mpl.patches import FancyBboxPatch
    from plotnine._mpl.text import SText
    from plotnine.iapi import grouped_legends

    FancyPatches: TypeAlias = list[FancyBboxPatch]
    ColoredAreas: TypeAlias = list[ColoredDrawingArea]
    STexts: TypeAlias = list[SText]


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
    legend_key: Optional[ColoredAreas] = field(default_factory=list)
    legends: Optional[grouped_legends] = None
    legend_text_colorbar: Sequence[Text] = field(default_factory=list)
    legend_text_legend: Sequence[Text] = field(default_factory=list)
    legend_ticks: Optional[LineCollection] = None
    legend_title: Optional[Text] = None
    plot_caption: Optional[Text] = None
    plot_subtitle: Optional[Text] = None
    plot_title: Optional[Text] = None
    strip_background_x: FancyPatches = field(default_factory=list)
    strip_background_y: FancyPatches = field(default_factory=list)
    strip_text_x: STexts = field(default_factory=list)
    strip_text_y: STexts = field(default_factory=list)
