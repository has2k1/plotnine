from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING, cast

from matplotlib.text import Text

from plotnine._mpl.patches import StripTextPatch
from plotnine._utils import ha_as_float, va_as_float
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
    from plotnine.typing import (
        HorizontalJustification,
        StripPosition,
        VerticalJustification,
    )

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

    def strip_text_x_extra_height(self, position: StripPosition) -> float:
        """
        Height taken up by the top strips that is outside the panels
        """
        if not self.strip_text_x:
            return 0

        artists = [
            st.patch if st.patch.get_visible() else st
            for st in self.strip_text_x
            if st.patch.position == position
        ]

        heights = []

        for a in artists:
            info = (
                a.text.draw_info
                if isinstance(a, StripTextPatch)
                else a.draw_info
            )
            h = self.calc.height(a)
            heights.append(max(h + h * info.strip_align, 0))

        return max(heights)

    def strip_text_y_extra_width(self, position: StripPosition) -> float:
        """
        Width taken up by the top strips that is outside the panels
        """
        if not self.strip_text_y:
            return 0

        artists = [
            st.patch if st.patch.get_visible() else st
            for st in self.strip_text_y
            if st.patch.position == position
        ]

        widths = []

        for a in artists:
            info = (
                a.text.draw_info
                if isinstance(a, StripTextPatch)
                else a.draw_info
            )
            w = self.calc.width(a)
            widths.append(max(w + w * info.strip_align, 0))

        return max(widths)

    def axis_ticks_x_max_height_at(self, location: AxesLocation) -> float:
        """
        Return maximum height[figure space] of x ticks
        """
        heights = [
            self.calc.tight_height(tick.tick1line)
            for ax in self._filter_axes(location)
            for tick in self.axis_ticks_x(ax)
        ]
        return max(heights) if len(heights) else 0

    def axis_text_x_max_height(self, ax: Axes) -> float:
        """
        Return maximum height[figure space] of x tick labels
        """
        heights = [
            self.calc.tight_height(label) for label in self.axis_text_x(ax)
        ]
        return max(heights) if len(heights) else 0

    def axis_text_x_max_height_at(self, location: AxesLocation) -> float:
        """
        Return maximum height[figure space] of x tick labels
        """
        heights = [
            self.axis_text_x_max_height(ax)
            for ax in self._filter_axes(location)
        ]
        return max(heights) if len(heights) else 0

    def axis_ticks_y_max_width_at(self, location: AxesLocation) -> float:
        """
        Return maximum width[figure space] of y ticks
        """
        widths = [
            self.calc.tight_width(tick.tick1line)
            for ax in self._filter_axes(location)
            for tick in self.axis_ticks_y(ax)
        ]
        return max(widths) if len(widths) else 0

    def axis_text_y_max_width(self, ax: Axes) -> float:
        """
        Return maximum width[figure space] of y tick labels
        """
        widths = [
            self.calc.tight_width(label) for label in self.axis_text_y(ax)
        ]
        return max(widths) if len(widths) else 0

    def axis_text_y_max_width_at(self, location: AxesLocation) -> float:
        """
        Return maximum width[figure space] of y tick labels
        """
        widths = [
            self.axis_text_y_max_width(ax)
            for ax in self._filter_axes(location)
        ]
        return max(widths) if len(widths) else 0

    def axis_text_y_top_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum height[figure space] above the axes of y tick labels
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
        Return maximum height[figure space] below the axes of y tick labels
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
        Return maximum width[figure space] left of the axes of x tick labels
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
        Return maximum width[figure space] right of the axes of y tick labels
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
        justify = TextJustifier(spaces)

        if self.plot_tag:
            set_plot_tag_position(self.plot_tag, spaces)

        if self.plot_title:
            ha = theme.getp(("plot_title", "ha"))
            self.plot_title.set_y(spaces.t.y2("plot_title"))
            justify.horizontally_about(
                self.plot_title, ha, plot_title_position
            )

        if self.plot_subtitle:
            ha = theme.getp(("plot_subtitle", "ha"))
            self.plot_subtitle.set_y(spaces.t.y2("plot_subtitle"))
            justify.horizontally_about(
                self.plot_subtitle, ha, plot_title_position
            )

        if self.plot_caption:
            ha = theme.getp(("plot_caption", "ha"), "right")
            self.plot_caption.set_y(spaces.b.y1("plot_caption"))
            justify.horizontally_about(
                self.plot_caption, ha, plot_caption_position
            )

        if self.axis_title_x:
            ha = theme.getp(("axis_title_x", "ha"), "center")
            self.axis_title_x.set_y(spaces.b.y1("axis_title_x"))
            justify.horizontally_about(self.axis_title_x, ha, "panel")

        if self.axis_title_y:
            va = theme.getp(("axis_title_y", "va"), "center")
            self.axis_title_y.set_x(spaces.l.x1("axis_title_y"))
            justify.vertically_about(self.axis_title_y, va, "panel")

        if self.legends:
            set_legends_position(self.legends, spaces)

        self._adjust_axis_text_x(justify)
        self._adjust_axis_text_y(justify)
        self._strip_text_x_background_equal_heights()
        self._strip_text_y_background_equal_widths()

    def _adjust_axis_text_x(self, justify: TextJustifier):
        """
        Adjust x-axis text, justifying vertically as necessary
        """

        def to_vertical_axis_dimensions(value: float, ax: Axes) -> float:
            """
            Convert value in figure dimensions to axis dimensions
            """
            _, H = self.plot.figure.bbox.size
            h = ax.get_window_extent().height
            return value * H / h

        if self._is_blank("axis_text_x"):
            return

        va = self.plot.theme.getp(("axis_text_x", "va"), "top")

        for ax in self.plot.axs:
            texts = list(self.axis_text_x(ax))
            axis_text_row_height = to_vertical_axis_dimensions(
                self.axis_text_x_max_height(ax), ax
            )
            for text in texts:
                height = to_vertical_axis_dimensions(
                    self.calc.tight_height(text), ax
                )
                justify.vertically(
                    text, va, -axis_text_row_height, 0, height=height
                )

    def _adjust_axis_text_y(self, justify: TextJustifier):
        """
        Adjust x-axis text, justifying horizontally as necessary
        """

        def to_horizontal_axis_dimensions(value: float, ax: Axes) -> float:
            """
            Convert value in figure dimensions to axis dimensions

            Matplotlib expects x position of y-axis text is in transAxes,
            but all our layout measurements are in transFigure.

               ---------------------
              |                     |
              |     -----------     |
              |  X |           |    |
              |  X |           |    |
              |  X |           |    |
              |  X |           |    |
              |  X |           |    |
              |  X |           |    |
              |    0-----------1    |
              |        axes         |
              |                     |
              0---------------------1
                       figure

            We do not set the transform to transFigure because, then we need
            to calculate the position in transFigure; accounting for all the
            space wherever the panel may be.
            """
            W, _ = self.plot.figure.bbox.size
            w = ax.get_window_extent().width
            return value * W / w

        if self._is_blank("axis_text_y"):
            return

        ha = self.plot.theme.getp(("axis_text_y", "ha"), "right")

        for ax in self.plot.axs:
            texts = list(self.axis_text_y(ax))
            axis_text_col_width = to_horizontal_axis_dimensions(
                self.axis_text_y_max_width(ax), ax
            )
            for text in texts:
                width = to_horizontal_axis_dimensions(
                    self.calc.tight_width(text), ax
                )
                justify.horizontally(
                    text, ha, -axis_text_col_width, 0, width=width
                )

    def _strip_text_x_background_equal_heights(self):
        """
        Make the strip_text_x_backgrounds have equal heights

        The smaller heights are expanded to match the largest height
        """
        if not self.strip_text_x:
            return

        heights = [self.calc.bbox(t.patch).height for t in self.strip_text_x]
        max_height = max(heights)
        relative_heights = [max_height / h for h in heights]
        for text, scale in zip(self.strip_text_x, relative_heights):
            text.patch.expand = scale

    def _strip_text_y_background_equal_widths(self):
        """
        Make the strip_text_y_backgrounds have equal widths

        The smaller widths are expanded to match the largest width
        """
        if not self.strip_text_y:
            return

        widths = [self.calc.bbox(t.patch).width for t in self.strip_text_y]
        max_width = max(widths)
        relative_widths = [max_width / w for w in widths]
        for text, scale in zip(self.strip_text_y, relative_widths):
            text.patch.expand = scale


def _text_is_visible(text: Text) -> bool:
    """
    Return True if text is visible and is not empty
    """
    return text.get_visible() and text._text  # type: ignore


@dataclass
class TextJustifier:
    """
    Justify Text

    The justification methods reinterpret alignment values to be justification
    about a span.
    """

    spaces: LayoutSpaces

    def horizontally(
        self,
        text: Text,
        ha: HorizontalJustification | float,
        left: float,
        right: float,
        width: float | None = None,
    ):
        """
        Horizontally Justify text between left and right
        """
        rel = ha_as_float(ha)
        if width is None:
            width = self.spaces.items.calc.width(text)
        x = rel_position(rel, width, left, right)
        text.set_x(x)
        text.set_horizontalalignment("left")

    def vertically(
        self,
        text: Text,
        va: VerticalJustification | float,
        bottom: float,
        top: float,
        height: float | None = None,
    ):
        """
        Vertically Justify text between bottom and top
        """
        rel = va_as_float(va)

        if height is None:
            height = self.spaces.items.calc.height(text)
        y = rel_position(rel, height, bottom, top)
        text.set_y(y)
        text.set_verticalalignment("bottom")

    def horizontally_across_panel(
        self, text: Text, ha: HorizontalJustification | float
    ):
        """
        Horizontally Justify text accross the panel(s) width
        """
        self.horizontally(
            text, ha, self.spaces.l.panel_left, self.spaces.r.panel_right
        )

    def horizontally_across_plot(
        self, text: Text, ha: HorizontalJustification | float
    ):
        """
        Horizontally Justify text across the plot's width
        """
        self.horizontally(
            text, ha, self.spaces.l.plot_left, self.spaces.r.plot_right
        )

    def vertically_along_panel(
        self, text: Text, va: VerticalJustification | float
    ):
        """
        Horizontally Justify text along the panel(s) height
        """
        self.vertically(
            text, va, self.spaces.b.panel_bottom, self.spaces.t.panel_top
        )

    def vertically_along_plot(
        self, text: Text, va: VerticalJustification | float
    ):
        """
        Vertically Justify text along the plot's height
        """
        self.vertically(
            text, va, self.spaces.b.plot_bottom, self.spaces.t.plot_top
        )

    def horizontally_about(
        self, text: Text, ratio: float, how: Literal["panel", "plot"]
    ):
        """
        Horizontally Justify text across the panel or plot
        """
        if how == "panel":
            self.horizontally_across_panel(text, ratio)
        else:
            self.horizontally_across_plot(text, ratio)

    def vertically_about(
        self, text: Text, ratio: float, how: Literal["panel", "plot"]
    ):
        """
        Vertically Justify text along the panel or plot
        """
        if how == "panel":
            self.vertically_along_panel(text, ratio)
        else:
            self.vertically_along_plot(text, ratio)


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
            spaces.r.legend_height,
            params.bottom,
            params.top,
        )
        x = spaces.r.x2("legend")
        set_position(legends.right.box, (x, y), (1, 0))

    if legends.left:
        y = rel_position(
            legends.left.justification,
            spaces.l.legend_height,
            params.bottom,
            params.top,
        )
        x = spaces.l.x1("legend")
        set_position(legends.left.box, (x, y), (0, 0))

    if legends.top:
        x = rel_position(
            legends.top.justification,
            spaces.t.legend_width,
            params.left,
            params.right,
        )
        y = spaces.t.y2("legend")
        set_position(legends.top.box, (x, y), (0, 1))

    if legends.bottom:
        x = rel_position(
            legends.bottom.justification,
            spaces.b.legend_width,
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
    Place the tag in an inner margin around the plot

    The panel_margin remains outside the tag. For compositions, the
    tag is placed and within the tag_alignment space.
    """
    position: TagPosition = spaces.plot.theme.getp("plot_tag_position")
    if not isinstance(position, str):
        raise PlotnineError(
            f"Cannot have plot_tag_location='margin' if "
            f"plot_tag_position={position!r}."
        )

    tag.set_position(spaces.to_figure_space((0.5, 0.5)))
    ha = spaces.plot.theme.get_ha("plot_tag")
    va = spaces.plot.theme.get_va("plot_tag")
    if "left" in position:  # left, topleft, bottomleft
        space = spaces.l.tag_alignment
        x = spaces.l.x1("plot_tag") - (1 - ha) * space
        tag.set_x(x)
        tag.set_horizontalalignment("left")
    if "right" in position:  # right, topright, bottomright
        space = spaces.r.tag_alignment
        x = spaces.r.x1("plot_tag") + ha * space
        tag.set_x(x)
        tag.set_horizontalalignment("left")
    if "bottom" in position:  # bottom, bottomleft, bottomright
        space = spaces.b.tag_alignment
        y = spaces.b.y1("plot_tag") + (1 - va) * space
        tag.set_y(y)
        tag.set_verticalalignment("bottom")
    if "top" in position:  # top, topleft, topright
        space = spaces.t.tag_alignment
        y = spaces.t.y1("plot_tag") + va * space
        tag.set_y(y)
        tag.set_verticalalignment("bottom")

    justify = TextJustifier(spaces)
    if position in ("left", "right"):
        justify.vertically_along_plot(tag, va)
    elif position in ("top", "bottom"):
        justify.horizontally_across_plot(tag, ha)


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
