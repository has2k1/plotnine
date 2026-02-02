from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

from matplotlib.text import Text

from plotnine._mpl.patches import StripTextPatch
from plotnine.exceptions import PlotnineError

from ..utils import (
    ArtistGeometry,
    JustifyBoundaries,
    TextJustifier,
    get_subplotspecs,
    rel_position,
)

if TYPE_CHECKING:
    from typing import (
        Any,
        Iterator,
        Literal,
        TypeAlias,
    )

    from matplotlib.axes import Axes
    from matplotlib.axis import Tick
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle
    from matplotlib.transforms import Transform

    from plotnine import ggplot
    from plotnine._mpl.offsetbox import FlexibleAnchoredOffsetbox
    from plotnine._mpl.text import StripText
    from plotnine.iapi import legend_artists
    from plotnine.themes.elements import margin as Margin
    from plotnine.typing import (
        StripPosition,
    )

    from ._plot_side_space import PlotSideSpaces

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


class PlotLayoutItems:
    """
    Objects required to compute the layout
    """

    def __init__(self, plot: ggplot):
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

        self.plot = plot
        self.geometry = ArtistGeometry(self.plot.figure)

        self.axis_title_x: Text | None = get("axis_title_x")
        self.axis_title_y: Text | None = get("axis_title_y")

        # # The legends references the structure that contains the
        # # AnchoredOffsetboxes (groups of legends)
        self.legends: legend_artists | None = get("legends")
        self.plot_caption: Text | None = get("plot_caption")
        self.plot_footer: Text | None = get("plot_footer")
        self.plot_subtitle: Text | None = get("plot_subtitle")
        self.plot_title: Text | None = get("plot_title")
        self.plot_tag: Text | None = get("plot_tag")
        self.strip_text_x: list[StripText] | None = get("strip_text_x")
        self.strip_text_y: list[StripText] | None = get("strip_text_y")

        self.plot_footer_background: Rectangle | None = get(
            "plot_footer_background"
        )
        self.plot_footer_line: Line2D | None = get("plot_footer_line")

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
            h = self.geometry.height(a)
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
            w = self.geometry.width(a)
            widths.append(max(w + w * info.strip_align, 0))

        return max(widths)

    def axis_ticks_x_max_height_at(self, location: AxesLocation) -> float:
        """
        Return maximum height[figure space] of x ticks
        """
        heights = [
            self.geometry.tight_height(tick.tick1line)
            for ax in self._filter_axes(location)
            for tick in self.axis_ticks_x(ax)
        ]
        return max(heights) if len(heights) else 0

    def axis_text_x_max_height(self, ax: Axes) -> float:
        """
        Return maximum height[figure space] of x tick labels
        """
        heights = [
            self.geometry.tight_height(label) for label in self.axis_text_x(ax)
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
            self.geometry.tight_width(tick.tick1line)
            for ax in self._filter_axes(location)
            for tick in self.axis_ticks_y(ax)
        ]
        return max(widths) if len(widths) else 0

    def axis_text_y_max_width(self, ax: Axes) -> float:
        """
        Return maximum width[figure space] of y tick labels
        """
        widths = [
            self.geometry.tight_width(label) for label in self.axis_text_y(ax)
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
            ax_top_y = self.geometry.top_y(ax)
            for label in self.axis_text_y(ax):
                label_top_y = self.geometry.top_y(label)
                extras.append(max(0, label_top_y - ax_top_y))

        return max(extras) if len(extras) else 0

    def axis_text_y_bottom_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum height[figure space] below the axes of y tick labels
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_bottom_y = self.geometry.bottom_y(ax)
            for label in self.axis_text_y(ax):
                label_bottom_y = self.geometry.bottom_y(label)
                protrusion = abs(min(label_bottom_y - ax_bottom_y, 0))
                extras.append(protrusion)

        return max(extras) if len(extras) else 0

    def axis_text_x_left_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum width[figure space] left of the axes of x tick labels
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_left_x = self.geometry.left_x(ax)
            for label in self.axis_text_x(ax):
                label_left_x = self.geometry.left_x(label)
                protrusion = abs(min(label_left_x - ax_left_x, 0))
                extras.append(protrusion)

        return max(extras) if len(extras) else 0

    def axis_text_x_right_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum width[figure space] right of the axes of y tick labels
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_right_x = self.geometry.right_x(ax)
            for label in self.axis_text_x(ax):
                label_right_x = self.geometry.right_x(label)
                extras.append(max(0, label_right_x - ax_right_x))

        return max(extras) if len(extras) else 0

    def _move_artists(self, spaces: PlotSideSpaces):
        """
        Move the artists to their final positions
        """
        theme = self.plot.theme
        plot_title_position = theme.getp("plot_title_position", "panel")
        plot_caption_position = theme.getp("plot_caption_position", "panel")
        plot_footer_position = theme.getp("plot_footer_position", "plot")
        justify = PlotTextJustifier(spaces)

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

        if self.plot_footer:
            ha = theme.getp(("plot_footer", "ha"), "left")
            self.plot_footer.set_y(spaces.b.y1("plot_footer"))
            justify.horizontally_about(
                self.plot_footer, ha, plot_footer_position
            )
            self._resize_plot_footer_background(spaces)
            self._resize_plot_footer_line(spaces)

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

    def _adjust_axis_text_x(self, justify: PlotTextJustifier):
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
                    self.geometry.tight_height(text), ax
                )
                justify.vertically(
                    text, va, -axis_text_row_height, 0, height=height
                )

    def _adjust_axis_text_y(self, justify: PlotTextJustifier):
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
                    self.geometry.tight_width(text), ax
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

        heights = [
            self.geometry.bbox(t.patch).height for t in self.strip_text_x
        ]
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

        widths = [self.geometry.bbox(t.patch).width for t in self.strip_text_y]
        max_width = max(widths)
        relative_widths = [max_width / w for w in widths]
        for text, scale in zip(self.strip_text_y, relative_widths):
            text.patch.expand = scale

    def _resize_plot_footer_background(self, spaces: PlotSideSpaces):
        """
        Resize the plot footer to the size of the footer
        """
        if not self.plot_footer_background:
            return

        self.plot_footer_background.set_x(spaces.l.offset)
        self.plot_footer_background.set_y(spaces.b.offset)
        self.plot_footer_background.set_height(spaces.b.footer_height)
        self.plot_footer_background.set_width(spaces.plot_width)

    def _resize_plot_footer_line(self, spaces: PlotSideSpaces):
        """
        Resize the footer line to be a border above the footer
        """
        if not self.plot_footer_line:
            return

        x1 = spaces.l.offset
        x2 = x1 + spaces.plot_width
        y1 = y2 = spaces.b.offset + spaces.b.footer_height
        self.plot_footer_line.set_xdata([x1, x2])
        self.plot_footer_line.set_ydata([y1, y2])


def _text_is_visible(text: Text) -> bool:
    """
    Return True if text is visible and is not empty
    """
    return text.get_visible() and text._text  # type: ignore


class PlotTextJustifier(TextJustifier):
    """
    Justify Text about a plot or it's panels
    """

    def __init__(self, spaces: PlotSideSpaces):
        boundaries = JustifyBoundaries(
            plot_left=spaces.l.plot_left,
            plot_right=spaces.r.plot_right,
            plot_bottom=spaces.b.plot_bottom,
            plot_top=spaces.t.plot_top,
            panel_left=spaces.l.panel_left,
            panel_right=spaces.r.panel_right,
            panel_bottom=spaces.b.panel_bottom,
            panel_top=spaces.t.panel_top,
        )
        super().__init__(spaces.plot.figure, boundaries)


def set_legends_position(legends: legend_artists, spaces: PlotSideSpaces):
    """
    Place legend on the figure and justify is a required
    """
    panels_gs = spaces.plot._sub_gridspec
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


def set_plot_tag_position(tag: Text, spaces: PlotSideSpaces):
    """
    Set the postion of the plot_tag
    """
    theme = spaces.plot.theme
    panels_gs = spaces.plot._sub_gridspec
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
        width, height = spaces.items.geometry.size(tag)
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


def set_plot_tag_position_in_margin(tag: Text, spaces: PlotSideSpaces):
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

    justify = PlotTextJustifier(spaces)
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
