from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING, cast

from matplotlib._tight_layout import get_subplotspec_list
from matplotlib.backend_bases import RendererBase
from matplotlib.text import Text

from ..utils import (
    bbox_in_figure_space,
    get_transPanels,
    tight_bbox_in_figure_space,
)

if TYPE_CHECKING:
    from typing import (
        Any,
        Iterator,
        Literal,
        Sequence,
        TypeAlias,
    )

    from matplotlib.artist import Artist
    from matplotlib.axes import Axes
    from matplotlib.axis import Tick
    from matplotlib.transforms import Bbox, Transform

    from plotnine import ggplot
    from plotnine._mpl.offsetbox import FlexibleAnchoredOffsetbox
    from plotnine._mpl.text import StripText
    from plotnine.iapi import legend_artists
    from plotnine.typing import StripPosition

    from ._spaces import LayoutSpaces

    AxesLocation: TypeAlias = Literal[
        "all", "first_row", "last_row", "first_col", "last_col"
    ]


@dataclass
class Calc:
    """
    Calculate space taken up by an artist
    """

    # fig: Figure
    # renderer: RendererBase
    plot: ggplot

    def __post_init__(self):
        self.figure = self.plot.figure
        self.renderer = cast(RendererBase, self.plot.figure._get_renderer())  # pyright: ignore

    def bbox(self, artist: Artist) -> Bbox:
        """
        Bounding box of artist in figure coordinates
        """
        return bbox_in_figure_space(artist, self.figure, self.renderer)

    def tight_bbox(self, artist: Artist) -> Bbox:
        """
        Bounding box of artist and its children in figure coordinates
        """
        return tight_bbox_in_figure_space(artist, self.figure, self.renderer)

    def width(self, artist: Artist) -> float:
        """
        Width of artist in figure space
        """
        return self.bbox(artist).width

    def tight_width(self, artist: Artist) -> float:
        """
        Width of artist and its children in figure space
        """
        return self.tight_bbox(artist).width

    def height(self, artist: Artist) -> float:
        """
        Height of artist in figure space
        """
        return self.bbox(artist).height

    def tight_height(self, artist: Artist) -> float:
        """
        Height of artist and its children in figure space
        """
        return self.tight_bbox(artist).height

    def size(self, artist: Artist) -> tuple[float, float]:
        """
        (width, height) of artist in figure space
        """
        bbox = self.bbox(artist)
        return (bbox.width, bbox.height)

    def tight_size(self, artist: Artist) -> tuple[float, float]:
        """
        (width, height) of artist and its children in figure space
        """
        bbox = self.tight_bbox(artist)
        return (bbox.width, bbox.height)

    def left_x(self, artist: Artist) -> float:
        """
        x value of the left edge of the artist

         ---
        x   |
         ---
        """
        return self.bbox(artist).min[0]

    def right_x(self, artist: Artist) -> float:
        """
        x value of the left edge of the artist

         ---
        |   x
         ---
        """
        return self.bbox(artist).max[0]

    def top_y(self, artist: Artist) -> float:
        """
        y value of the top edge of the artist

         -y-
        |   |
         ---
        """
        return self.bbox(artist).max[1]

    def bottom_y(self, artist: Artist) -> float:
        """
        y value of the bottom edge of the artist

         ---
        |   |
         -y-
        """
        return self.bbox(artist).min[1]

    def max_width(self, artists: Sequence[Artist]) -> float:
        """
        Return the maximum width of list of artists
        """
        widths = [
            bbox_in_figure_space(a, self.figure, self.renderer).width
            for a in artists
        ]
        return max(widths) if len(widths) else 0

    def max_height(self, artists: Sequence[Artist]) -> float:
        """
        Return the maximum height of list of artists
        """
        heights = [
            bbox_in_figure_space(a, self.figure, self.renderer).height
            for a in artists
        ]
        return max(heights) if len(heights) else 0


@dataclass
class LayoutItems:
    """
    Objects required to compute the layout
    """

    plot: ggplot

    def __post_init__(self):
        def get(name: str) -> Any:
            """
            Return themeable target or None
            """
            if self._is_blank(name):
                return None
            else:
                t = getattr(self.plot.theme.targets, name)
                if isinstance(t, Text) and t.get_text() == "":
                    return None
                return t

        self.calc = Calc(self.plot)

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

    def _is_blank(self, name: str) -> bool:
        return self.plot.theme.T.is_blank(name)

    def _filter_axes(self, location: AxesLocation = "all") -> list[Axes]:
        """
        Return subset of axes
        """
        axs = self.plot.axs

        if location == "all":
            return axs

        # e.g. is_first_row, is_last_row, ..
        pred_method = f"is_{location}"
        return [
            ax
            for spec, ax in zip(get_subplotspec_list(axs), axs)
            if getattr(spec, pred_method)()
        ]

    def axis_labels_x(self, ax: Axes) -> Iterator[Text]:
        """
        Return all x-axis labels for an axes that will be shown
        """
        major, minor = [], []

        if not self._is_blank("axis_text_x"):
            major = ax.xaxis.get_major_ticks()
            minor = ax.xaxis.get_minor_ticks()

        return (
            tick.label1
            for tick in chain(major, minor)
            if _text_is_visible(tick.label1)
        )

    def axis_labels_y(self, ax: Axes) -> Iterator[Text]:
        """
        Return all y-axis labels for an axes that will be shown
        """
        major, minor = [], []

        if not self._is_blank("axis_text_y"):
            major = ax.yaxis.get_major_ticks()
            minor = ax.yaxis.get_minor_ticks()

        return (
            tick.label1
            for tick in chain(major, minor)
            if _text_is_visible(tick.label1)
        )

    def axis_ticks_x(self, ax: Axes) -> Iterator[Tick]:
        """
        Return all XTicks that will be shown
        """
        major, minor = [], []

        if not self._is_blank("axis_ticks_major_x"):
            major = ax.xaxis.get_major_ticks()

        if not self._is_blank("axis_ticks_minor_x"):
            minor = ax.xaxis.get_minor_ticks()

        return chain(major, minor)

    def axis_ticks_y(self, ax: Axes) -> Iterator[Tick]:
        """
        Return all YTicks that will be shown
        """
        major, minor = [], []

        if not self._is_blank("axis_ticks_major_y"):
            major = ax.yaxis.get_major_ticks()

        if not self._is_blank("axis_ticks_minor_y"):
            minor = ax.yaxis.get_minor_ticks()

        return chain(major, minor)

    def axis_ticks_pad_x(self, ax: Axes) -> Iterator[float]:
        """
        Return XTicks paddings
        """
        # In plotnine tick padding are specified as a margin to the
        # the axis_text.
        major, minor = [], []
        if not self._is_blank("axis_text_x"):
            h = self.plot.figure.get_figheight() * 72
            major = [
                (t.get_pad() or 0) / h for t in ax.xaxis.get_major_ticks()
            ]
            minor = [
                (t.get_pad() or 0) / h for t in ax.xaxis.get_minor_ticks()
            ]
        return chain(major, minor)

    def axis_ticks_pad_y(self, ax: Axes) -> Iterator[float]:
        """
        Return YTicks paddings
        """
        # In plotnine tick padding are specified as a margin to the
        # the axis_text.
        major, minor = [], []
        if not self._is_blank("axis_text_y"):
            w = self.plot.figure.get_figwidth() * 72
            major = [
                (t.get_pad() or 0) / w for t in ax.yaxis.get_major_ticks()
            ]
            minor = [
                (t.get_pad() or 0) / w for t in ax.yaxis.get_minor_ticks()
            ]
        return chain(major, minor)

    def strip_text_x_height(self, position: StripPosition) -> float:
        """
        Height taken up by the top strips
        """
        if not self.strip_text_x:
            return 0

        artists = [
            st.patch if st.patch.get_visible() else st
            for st in self.strip_text_x
            if st.patch.position == position
        ]
        return self.calc.max_height(artists)

    def strip_text_y_width(self, position: StripPosition) -> float:
        """
        Width taken up by the right strips
        """
        if not self.strip_text_y:
            return 0

        artists = [
            st.patch if st.patch.get_visible() else st
            for st in self.strip_text_y
            if st.patch.position == position
        ]
        return self.calc.max_width(artists)

    def axis_ticks_x_max_height(self, location: AxesLocation) -> float:
        """
        Return maximum height[inches] of x ticks
        """
        heights = [
            self.calc.tight_height(tick.tick1line)
            for ax in self._filter_axes(location)
            for tick in self.axis_ticks_x(ax)
        ]
        return max(heights) if len(heights) else 0

    def axis_text_x_max_height(self, location: AxesLocation) -> float:
        """
        Return maximum height[inches] of x tick labels
        """
        heights = [
            self.calc.tight_height(label) + pad
            for ax in self._filter_axes(location)
            for label, pad in zip(
                self.axis_labels_x(ax), self.axis_ticks_pad_x(ax)
            )
        ]
        return max(heights) if len(heights) else 0

    def axis_ticks_y_max_width(self, location: AxesLocation) -> float:
        """
        Return maximum width[inches] of y ticks
        """
        widths = [
            self.calc.tight_width(tick.tick1line)
            for ax in self._filter_axes(location)
            for tick in self.axis_ticks_y(ax)
        ]
        return max(widths) if len(widths) else 0

    def axis_text_y_max_width(self, location: AxesLocation) -> float:
        """
        Return maximum width[inches] of y tick labels
        """
        widths = [
            self.calc.tight_width(label) + pad
            for ax in self._filter_axes(location)
            for label, pad in zip(
                self.axis_labels_y(ax), self.axis_ticks_pad_y(ax)
            )
        ]
        return max(widths) if len(widths) else 0

    def axis_text_y_top_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum height[inches] above the axes of y tick labels
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_top_y = self.calc.top_y(ax)
            for label in self.axis_labels_y(ax):
                label_top_y = self.calc.top_y(label)
                extras.append(max(0, label_top_y - ax_top_y))

        return max(extras) if len(extras) else 0

    def axis_text_y_bottom_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum height[inches] below the axes of y tick labels
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_bottom_y = self.calc.bottom_y(ax)
            for label in self.axis_labels_y(ax):
                label_bottom_y = self.calc.bottom_y(label)
                protrusion = abs(min(label_bottom_y - ax_bottom_y, 0))
                extras.append(protrusion)

        return max(extras) if len(extras) else 0

    def axis_text_x_left_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum width[inches] of x tick labels to the left of the axes
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_left_x = self.calc.left_x(ax)
            for label in self.axis_labels_x(ax):
                label_left_x = self.calc.left_x(label)
                protrusion = abs(min(label_left_x - ax_left_x, 0))
                extras.append(protrusion)

        return max(extras) if len(extras) else 0

    def axis_text_x_right_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum width[inches] of x tick labels to the right of the axes
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_right_x = self.calc.right_x(ax)
            for label in self.axis_labels_x(ax):
                label_right_x = self.calc.right_x(label)
                extras.append(max(0, label_right_x - ax_right_x))

        return max(extras) if len(extras) else 0

    def _adjust_positions(self, spaces: LayoutSpaces):
        """
        Set the x,y position of the artists around the panels
        """
        theme = self.plot.theme

        if self.plot_title:
            ha = theme.getp(("plot_title", "ha"))
            self.plot_title.set_y(spaces.t.edge("plot_title"))
            horizontally_align_text_with_panels(self.plot_title, ha, spaces)

        if self.plot_subtitle:
            ha = theme.getp(("plot_subtitle", "ha"))
            self.plot_subtitle.set_y(spaces.t.edge("plot_subtitle"))
            horizontally_align_text_with_panels(self.plot_subtitle, ha, spaces)

        if self.plot_caption:
            ha = theme.getp(("plot_caption", "ha"), "right")
            self.plot_caption.set_y(spaces.b.edge("plot_caption"))
            horizontally_align_text_with_panels(self.plot_caption, ha, spaces)

        if self.axis_title_x:
            ha = theme.getp(("axis_title_x", "ha"), "center")
            self.axis_title_x.set_y(spaces.b.edge("axis_title_x"))
            horizontally_align_text_with_panels(self.axis_title_x, ha, spaces)

        if self.axis_title_y:
            va = theme.getp(("axis_title_y", "va"), "center")
            self.axis_title_y.set_x(spaces.l.edge("axis_title_y"))
            vertically_align_text_with_panels(self.axis_title_y, va, spaces)

        if self.legends:
            set_legends_position(self.legends, spaces)


def _text_is_visible(text: Text) -> bool:
    """
    Return True if text is visible and is not empty
    """
    return text.get_visible() and text._text  # type: ignore


def horizontally_align_text_with_panels(
    text: Text, ha: str | float, spaces: LayoutSpaces
):
    """
    Horizontal justification

    Reinterpret horizontal alignment to be justification about the panels.
    """
    if isinstance(ha, str):
        lookup = {
            "left": 0.0,
            "center": 0.5,
            "right": 1.0,
        }
        f = lookup[ha]
    else:
        f = ha

    params = spaces.gsparams
    width = spaces.items.calc.width(text)
    x = params.left * (1 - f) + (params.right - width) * f
    text.set_x(x)
    text.set_horizontalalignment("left")


def vertically_align_text_with_panels(
    text: Text, va: str | float, spaces: LayoutSpaces
):
    """
    Vertical justification

    Reinterpret vertical alignment to be justification about the panels.
    """
    if isinstance(va, str):
        lookup = {
            "top": 1.0,
            "center": 0.5,
            "baseline": 0.5,
            "center_baseline": 0.5,
            "bottom": 0.0,
        }
        f = lookup[va]
    else:
        f = va

    params = spaces.gsparams
    height = spaces.items.calc.height(text)
    y = params.bottom * (1 - f) + (params.top - height) * f
    text.set_y(y)
    text.set_verticalalignment("bottom")


def set_legends_position(legends: legend_artists, spaces: LayoutSpaces):
    """
    Place legend on the figure and justify is a required
    """
    figure = spaces.plot.figure
    params = figure.subplotpars

    def set_position(
        aob: FlexibleAnchoredOffsetbox,
        anchor_point: tuple[float, float],
        xy_loc: tuple[float, float],
        transform: Transform = figure.transFigure,
    ):
        """
        Place box (by the anchor point) at given xy location

        Parameters
        ----------
        aob :
           Offsetbox to place
        anchor_point :
            Point on the Offsefbox.
        xy_loc :
            Point where to place the offsetbox.
        transform :
            Transformation
        """
        aob.xy_loc = xy_loc
        aob.set_bbox_to_anchor(anchor_point, transform)  # type: ignore

    def func(a, b, length, f):
        return a * (1 - f) + (b - length) * f

    if legends.right:
        j = legends.right.justification
        y = (
            params.bottom * (1 - j)
            + (params.top - spaces.r._legend_height) * j
        )
        x = spaces.r.edge("legend")
        set_position(legends.right.box, (x, y), (1, 0))

    if legends.left:
        j = legends.left.justification
        y = (
            params.bottom * (1 - j)
            + (params.top - spaces.l._legend_height) * j
        )
        x = spaces.l.edge("legend")
        set_position(legends.left.box, (x, y), (0, 0))

    if legends.top:
        j = legends.top.justification
        x = params.left * (1 - j) + (params.right - spaces.t._legend_width) * j
        y = spaces.t.edge("legend")
        set_position(legends.top.box, (x, y), (0, 1))

    if legends.bottom:
        j = legends.bottom.justification
        x = params.left * (1 - j) + (params.right - spaces.b._legend_width) * j
        y = spaces.b.edge("legend")
        set_position(legends.bottom.box, (x, y), (0, 0))

    # Inside legends are placed using the panels coordinate system
    if legends.inside:
        transPanels = get_transPanels(figure)
        for l in legends.inside:
            set_position(l.box, l.position, l.justification, transPanels)
