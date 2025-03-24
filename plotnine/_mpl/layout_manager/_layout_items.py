from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING, cast

from matplotlib.text import Text

from plotnine.exceptions import PlotnineError

from ..utils import (
    bbox_in_figure_space,
    get_subplotspecs,
    rel_position,
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
    from matplotlib.backend_bases import RendererBase
    from matplotlib.transforms import Bbox, Transform

    from plotnine import ggplot
    from plotnine._mpl.offsetbox import FlexibleAnchoredOffsetbox
    from plotnine._mpl.text import StripText
    from plotnine.iapi import legend_artists
    from plotnine.themes.elements import margin as Margin
    from plotnine.typing import StripPosition

    from ._spaces import LayoutSpaces

    AxesLocation: TypeAlias = Literal[
        "all", "first_row", "last_row", "first_col", "last_col"
    ]
    TagLocation: TypeAlias = Literal["margin", "plot", "panel"]
    TagPosition: TypeAlias = (
        Literal[
            "topleft",
            "top",
            "topright",
            "left",
            "right",
            "bottomleft",
            "bottom",
            "bottomright",
        ]
        | tuple[float, float]
    )


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
        self.renderer = cast("RendererBase", self.plot.figure._get_renderer())  # pyright: ignore

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
        self.plot_tag: Text | None = get("plot_tag")
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
            for spec, ax in zip(get_subplotspecs(axs), axs)
            if getattr(spec, pred_method)()
        ]

    def axis_text_x(self, ax: Axes) -> Iterator[Text]:
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

    def axis_text_y(self, ax: Axes) -> Iterator[Text]:
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

    def axis_text_x_margin(self, ax: Axes) -> Iterator[float]:
        """
        Return XTicks paddings
        """
        # In plotnine tick padding are specified as a margin to the
        # the axis_text.
        major, minor = [], []
        if not self._is_blank("axis_text_x"):
            h = self.plot.figure.bbox.height
            major = [
                (t.get_pad() or 0) / h for t in ax.xaxis.get_major_ticks()
            ]
            minor = [
                (t.get_pad() or 0) / h for t in ax.xaxis.get_minor_ticks()
            ]
        return chain(major, minor)

    def axis_text_y_margin(self, ax: Axes) -> Iterator[float]:
        """
        Return YTicks paddings
        """
        # In plotnine tick padding are specified as a margin to the
        # the axis_text.
        major, minor = [], []
        if not self._is_blank("axis_text_y"):
            w = self.plot.figure.bbox.width
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
                self.axis_text_x(ax), self.axis_text_x_margin(ax)
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
                self.axis_text_y(ax), self.axis_text_y_margin(ax)
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
            for label in self.axis_text_y(ax):
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
            for label in self.axis_text_y(ax):
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
            for label in self.axis_text_x(ax):
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
            for label in self.axis_text_x(ax):
                label_right_x = self.calc.right_x(label)
                extras.append(max(0, label_right_x - ax_right_x))

        return max(extras) if len(extras) else 0

    def _adjust_positions(self, spaces: LayoutSpaces):
        """
        Set the x,y position of the artists around the panels
        """
        theme = self.plot.theme
        plot_title_position = theme.getp("plot_title_position", "panel")
        plot_caption_position = theme.getp("plot_caption_position", "panel")

        if self.plot_tag:
            set_plot_tag_position(self.plot_tag, spaces)

        if self.plot_title:
            ha = theme.getp(("plot_title", "ha"))
            self.plot_title.set_y(spaces.t.y2("plot_title"))
            horizontally_align_text(
                self.plot_title, ha, spaces, plot_title_position
            )

        if self.plot_subtitle:
            ha = theme.getp(("plot_subtitle", "ha"))
            self.plot_subtitle.set_y(spaces.t.y2("plot_subtitle"))
            horizontally_align_text(
                self.plot_subtitle, ha, spaces, plot_title_position
            )

        if self.plot_caption:
            ha = theme.getp(("plot_caption", "ha"), "right")
            self.plot_caption.set_y(spaces.b.y1("plot_caption"))
            horizontally_align_text(
                self.plot_caption, ha, spaces, plot_caption_position
            )

        if self.axis_title_x:
            ha = theme.getp(("axis_title_x", "ha"), "center")
            self.axis_title_x.set_y(spaces.b.y1("axis_title_x"))
            horizontally_align_text(self.axis_title_x, ha, spaces)

        if self.axis_title_y:
            va = theme.getp(("axis_title_y", "va"), "center")
            self.axis_title_y.set_x(spaces.l.x1("axis_title_y"))
            vertically_align_text(self.axis_title_y, va, spaces)

        if self.legends:
            set_legends_position(self.legends, spaces)


def _text_is_visible(text: Text) -> bool:
    """
    Return True if text is visible and is not empty
    """
    return text.get_visible() and text._text  # type: ignore


def horizontally_align_text(
    text: Text,
    ha: str | float,
    spaces: LayoutSpaces,
    how: Literal["panel", "plot"] = "panel",
):
    """
    Horizontal justification

    Reinterpret horizontal alignment to be justification about the panels or
    the plot (depending on the how parameter)
    """
    if isinstance(ha, str):
        lookup = {
            "left": 0.0,
            "center": 0.5,
            "right": 1.0,
        }
        rel = lookup[ha]
    else:
        rel = ha

    if how == "panel":
        left = spaces.l.left
        right = spaces.r.right
    else:
        left = spaces.l.plot_left
        right = spaces.r.plot_right

    width = spaces.items.calc.width(text)
    x = rel_position(rel, width, left, right)
    text.set_x(x)
    text.set_horizontalalignment("left")


def vertically_align_text(
    text: Text,
    va: str | float,
    spaces: LayoutSpaces,
    how: Literal["panel", "plot"] = "panel",
):
    """
    Vertical justification

    Reinterpret vertical alignment to be justification about the panels or
    the plot (depending on the how parameter).
    """
    if isinstance(va, str):
        lookup = {
            "top": 1.0,
            "center": 0.5,
            "baseline": 0.5,
            "center_baseline": 0.5,
            "bottom": 0.0,
        }
        rel = lookup[va]
    else:
        rel = va

    if how == "panel":
        top = spaces.t.top
        bottom = spaces.b.bottom
    else:
        top = spaces.t.plot_top
        bottom = spaces.b.plot_bottom

    height = spaces.items.calc.height(text)
    y = rel_position(rel, height, bottom, top)
    text.set_y(y)
    text.set_verticalalignment("bottom")


def set_legends_position(legends: legend_artists, spaces: LayoutSpaces):
    """
    Place legend on the figure and justify is a required
    """
    panels_gs = spaces.plot.facet._panels_gridspec
    params = panels_gs.get_subplot_params()
    transFigure = spaces.plot.figure.transFigure

    def set_position(
        aob: FlexibleAnchoredOffsetbox,
        anchor_point: tuple[float, float],
        xy_loc: tuple[float, float],
        transform: Transform = transFigure,
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

    if legends.right:
        y = rel_position(
            legends.right.justification,
            spaces.r._legend_height,
            params.bottom,
            params.top,
        )
        x = spaces.r.x2("legend")
        set_position(legends.right.box, (x, y), (1, 0))

    if legends.left:
        y = rel_position(
            legends.left.justification,
            spaces.l._legend_height,
            params.bottom,
            params.top,
        )
        x = spaces.l.x1("legend")
        set_position(legends.left.box, (x, y), (0, 0))

    if legends.top:
        x = rel_position(
            legends.top.justification,
            spaces.t._legend_width,
            params.left,
            params.right,
        )
        y = spaces.t.y2("legend")
        set_position(legends.top.box, (x, y), (0, 1))

    if legends.bottom:
        x = rel_position(
            legends.bottom.justification,
            spaces.b._legend_width,
            params.left,
            params.right,
        )
        y = spaces.b.y1("legend")
        set_position(legends.bottom.box, (x, y), (0, 0))

    # Inside legends are placed using the panels coordinate system
    if legends.inside:
        transPanels = panels_gs.to_transform()
        for l in legends.inside:
            set_position(l.box, l.position, l.justification, transPanels)


def set_plot_tag_position(tag: Text, spaces: LayoutSpaces):
    """
    Set the postion of the plot_tag
    """
    theme = spaces.plot.theme
    panels_gs = spaces.plot.facet._panels_gridspec
    location: TagLocation = theme.getp("plot_tag_location")
    position: TagPosition = theme.getp("plot_tag_position")
    margin = theme.get_margin("plot_tag")

    if location == "margin":
        return set_plot_tag_position_in_margin(tag, spaces)

    lookup: dict[str, tuple[float, float]] = {
        "topleft": (0, 1),
        "top": (0.5, 1),
        "topright": (1, 1),
        "left": (0, 0.5),
        "right": (1, 0.5),
        "bottomleft": (0, 0),
        "bottom": (0.5, 0),
        "bottomright": (1, 0),
    }

    if isinstance(position, str):
        # Coordinates of the space in which to place the tag
        if location == "plot":
            (x1, y1), (x2, y2) = spaces.plot_area_coordinates
        else:
            (x1, y1), (x2, y2) = spaces.panel_area_coordinates

        # Calculate the position when the tag has no margins
        rel_x, rel_y = lookup[position]
        width, height = spaces.items.calc.size(tag)
        x = rel_position(rel_x, width, x1, x2)
        y = rel_position(rel_y, height, y1, y2)

        # Adjust the position to account for the margins
        # When the units for the margin are in the figure coordinates,
        # the adjustment is proportional to the size of the space.
        # For points, inches and lines, the adjustment is absolute.
        mx, my = _plot_tag_margin_adjustment(margin, position)
        if margin.unit == "fig":
            panel_width, panel_height = (x2 - x1), (y2 - y1)
        else:
            panel_width, panel_height = 1, 1

        x += panel_width * mx
        y += panel_height * my

        position = (x, y)
        tag.set_horizontalalignment("left")
        tag.set_verticalalignment("bottom")
    else:
        if location == "panel":
            transPanels = panels_gs.to_transform()
            tag.set_transform(transPanels)

    tag.set_position(position)


def set_plot_tag_position_in_margin(tag: Text, spaces: LayoutSpaces):
    """
    Place the tag in the margin around the plot
    """
    position: TagPosition = spaces.plot.theme.getp("plot_tag_position")
    if not isinstance(position, str):
        raise PlotnineError(
            f"Cannot have plot_tag_location='margin' if "
            f"plot_tag_position={position!r}."
        )

    tag.set_position(spaces.to_figure_space((0.5, 0.5)))
    if "top" in position:
        tag.set_y(spaces.t.y2("plot_tag"))
        tag.set_verticalalignment("top")
    if "bottom" in position:
        tag.set_y(spaces.b.y1("plot_tag"))
        tag.set_verticalalignment("bottom")
    if "left" in position:
        tag.set_x(spaces.l.x1("plot_tag"))
        tag.set_horizontalalignment("left")
    if "right" in position:
        tag.set_x(spaces.r.x2("plot_tag"))
        tag.set_horizontalalignment("right")


def _plot_tag_margin_adjustment(
    margin: Margin, position: str
) -> tuple[float, float]:
    """
    How to adjust the plot_tag to account for the margin
    """
    m = margin.fig
    dx, dy = 0, 0

    if "top" in position:
        dy = -m.t
    elif "bottom" in position:
        dy = m.b

    if "left" in position:
        dx = m.l
    elif "right" in position:
        dx = -m.r

    return (dx, dy)
