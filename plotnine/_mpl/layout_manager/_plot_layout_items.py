from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING

from matplotlib.text import Text

from plotnine._utils import ha_as_float, side_artists, va_as_float
from plotnine.composition._compose import Compose
from plotnine.exceptions import PlotnineError

from ..utils import (
    ArtistGeometry,
    TextJustifier,
    bbox_in_axes_space,
    get_subplotspecs,
    rel_position,
    resize_footer_background,
    resize_footer_line,
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
    from matplotlib.figure import Figure
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle
    from matplotlib.transforms import Bbox, Transform

    from plotnine import ggplot
    from plotnine._mpl.offsetbox import FlexibleAnchoredOffsetbox
    from plotnine._mpl.text import StripText
    from plotnine.iapi import legend_artists
    from plotnine.themes.elements import margin as Margin
    from plotnine.themes.theme import theme
    from plotnine.typing import (
        StripPosition,
    )

    from ._composition_layout_items import CompositionLayoutItems
    from ._composition_side_space import CompositionSideSpaces
    from ._plot_side_space import PlotSideSpaces, _plot_side_space

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
class StripSizing:
    """
    Theme inputs that fix a strip background's size and offset
    """

    margin: Margin
    """Strip text margin with the units in lines"""

    strip_align: float
    """How far the background is offset from the panel edge"""

    bg_x: float
    """Left of the strip background in transAxes"""

    bg_y: float
    """Bottom of the strip background in transAxes"""

    bg_width: float
    """Width of the strip background in transAxes (top strips)"""

    bg_height: float
    """Height of the strip background in transAxes (right strips)"""


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
        self.axis_title_x_bottom: Text | None = get("axis_title_x_bottom")
        self.axis_title_x_top: Text | None = get("axis_title_x_top")
        self.axis_title_y_left: Text | None = get("axis_title_y_left")
        self.axis_title_y_right: Text | None = get("axis_title_y_right")

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

    def axis_text_x(self, ax: Axes, side: str) -> Iterator[Text]:
        """
        Return the visible x-axis labels on one side of an axes
        """
        major, minor = [], []

        if not self._is_blank("axis_text_x"):
            major = ax.xaxis.get_major_ticks()
            minor = ax.xaxis.get_minor_ticks()

        label_attr = side_artists(side)[1]
        return (
            getattr(tick, label_attr)
            for tick in chain(major, minor)
            if _text_is_visible(getattr(tick, label_attr))
        )

    def axis_text_y(self, ax: Axes, side: str) -> Iterator[Text]:
        """
        Return the visible y-axis labels on one side of an axes
        """
        major, minor = [], []

        if not self._is_blank("axis_text_y"):
            major = ax.yaxis.get_major_ticks()
            minor = ax.yaxis.get_minor_ticks()

        label_attr = side_artists(side)[1]
        return (
            getattr(tick, label_attr)
            for tick in chain(major, minor)
            if _text_is_visible(getattr(tick, label_attr))
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

    def _strip_sizing(self, position: StripPosition) -> StripSizing:
        """
        Theme inputs that fix one strip's background size and offset

        The keys read depend on the side the strip sits on.
        """
        theme = self.plot.theme
        if position == "top":
            return StripSizing(
                margin=theme.getp(("strip_text_x", "margin")).to("lines"),
                strip_align=theme.getp("strip_align_x"),
                bg_x=theme.getp(("strip_text_x", "x"), 0),
                bg_y=1,
                bg_width=theme.getp(("strip_background_x", "width"), 1),
                bg_height=0,
            )
        else:
            return StripSizing(
                margin=theme.getp(("strip_text_y", "margin")).to("lines"),
                strip_align=theme.getp("strip_align_y"),
                bg_x=1,
                bg_y=theme.getp(("strip_text_y", "y"), 0),
                bg_width=0,
                bg_height=theme.getp(("strip_background_y", "height"), 1),
            )

    def strip_patch_bbox(
        self, strip_text: StripText, scale: float = 1
    ) -> Bbox:
        """
        Figure-space bounding box of one strip's background patch

        The breadth (height for top strips, width for right strips) is
        scaled by `scale` so the layout manager can equalise strips in
        the same group.
        """
        from matplotlib.transforms import Bbox

        sizing = self._strip_sizing(strip_text.position)
        m = sizing.margin
        text_bbox = self.geometry.bbox(strip_text)
        ax_bbox = self.geometry.bbox(strip_text.ax)
        W, H = self.plot.figure.bbox.width, self.plot.figure.bbox.height
        line_height = strip_text._line_height(self.geometry.renderer)

        x0 = rel_position(sizing.bg_x, 0, ax_bbox.x0, ax_bbox.x1)
        y0 = rel_position(sizing.bg_y, 0, ax_bbox.y0, ax_bbox.y1)

        if strip_text.position == "top":
            margins = (m.b + m.t) * line_height / H
            width = ax_bbox.width * sizing.bg_width
            height = (text_bbox.height + margins) * scale
            y0 += height * sizing.strip_align
        else:
            margins = (m.l + m.r) * line_height / W
            height = ax_bbox.height * sizing.bg_height
            width = (text_bbox.width + margins) * scale
            x0 += width * sizing.strip_align
        return Bbox.from_bounds(x0, y0, width, height)

    def strip_text_x_extra_height(self, position: StripPosition) -> float:
        """
        Height taken up by the top strips that is outside the panels
        """
        if not self.strip_text_x:
            return 0

        heights = []
        for st in self.strip_text_x:
            if st.position != position:
                continue
            strip_align = self._strip_sizing(st.position).strip_align
            if st.patch.get_visible():
                # The patch bounds are not yet set, so derive its natural
                # height from the sizing inputs.
                h = self.strip_patch_bbox(st).height
            else:
                h = self.geometry.height(st)
            heights.append(max(h + h * strip_align, 0))

        return max(heights) if heights else 0

    def strip_text_y_extra_width(self, position: StripPosition) -> float:
        """
        Width taken up by the right strips that is outside the panels
        """
        if not self.strip_text_y:
            return 0

        widths = []
        for st in self.strip_text_y:
            if st.position != position:
                continue
            strip_align = self._strip_sizing(st.position).strip_align
            if st.patch.get_visible():
                # The patch bounds are not yet set, so derive its natural
                # width from the sizing inputs.
                w = self.strip_patch_bbox(st).width
            else:
                w = self.geometry.width(st)
            widths.append(max(w + w * strip_align, 0))

        return max(widths) if widths else 0

    def axis_ticks_x_max_height_at(
        self, location: AxesLocation, side: str
    ) -> float:
        """
        Return maximum height[figure space] of visible x ticks on a side
        """
        attr = side_artists(side)[0]
        heights = [
            self.geometry.tight_height(getattr(tick, attr))
            for ax in self._filter_axes(location)
            for tick in self.axis_ticks_x(ax)
            if getattr(tick, attr).get_visible()
        ]
        return max(heights) if len(heights) else 0

    def axis_text_x_max_height(self, ax: Axes, side: str) -> float:
        """
        Return maximum height[figure space] of x tick labels on a side
        """
        heights = [
            self.geometry.tight_height(label)
            for label in self.axis_text_x(ax, side)
        ]
        return max(heights) if len(heights) else 0

    def axis_text_x_max_height_at(
        self, location: AxesLocation, side: str
    ) -> float:
        """
        Return maximum height[figure space] of x tick labels on a side
        """
        heights = [
            self.axis_text_x_max_height(ax, side)
            for ax in self._filter_axes(location)
        ]
        return max(heights) if len(heights) else 0

    def axis_ticks_y_max_width_at(
        self, location: AxesLocation, side: str
    ) -> float:
        """
        Return maximum width[figure space] of visible y ticks on a side
        """
        attr = side_artists(side)[0]
        widths = [
            self.geometry.tight_width(getattr(tick, attr))
            for ax in self._filter_axes(location)
            for tick in self.axis_ticks_y(ax)
            if getattr(tick, attr).get_visible()
        ]
        return max(widths) if len(widths) else 0

    def axis_text_y_max_width(self, ax: Axes, side: str) -> float:
        """
        Return maximum width[figure space] of y tick labels on a side
        """
        widths = [
            self.geometry.tight_width(label)
            for label in self.axis_text_y(ax, side)
        ]
        return max(widths) if len(widths) else 0

    def axis_text_y_max_width_at(
        self, location: AxesLocation, side: str
    ) -> float:
        """
        Return maximum width[figure space] of y tick labels on a side
        """
        widths = [
            self.axis_text_y_max_width(ax, side)
            for ax in self._filter_axes(location)
        ]
        return max(widths) if len(widths) else 0

    # Side-scoped extents — each names a concrete edge (side picks the
    # artist, location picks the panels) and reads 0 when no axis is there.
    @property
    def axis_text_x_bottom(self) -> float:
        return self.axis_text_x_max_height_at("last_row", "bottom")

    @property
    def axis_text_x_top(self) -> float:
        return self.axis_text_x_max_height_at("first_row", "top")

    @property
    def axis_text_y_left(self) -> float:
        return self.axis_text_y_max_width_at("first_col", "left")

    @property
    def axis_text_y_right(self) -> float:
        return self.axis_text_y_max_width_at("last_col", "right")

    @property
    def axis_ticks_x_bottom(self) -> float:
        return self.axis_ticks_x_max_height_at("last_row", "bottom")

    @property
    def axis_ticks_x_top(self) -> float:
        return self.axis_ticks_x_max_height_at("first_row", "top")

    @property
    def axis_ticks_y_left(self) -> float:
        return self.axis_ticks_y_max_width_at("first_col", "left")

    @property
    def axis_ticks_y_right(self) -> float:
        return self.axis_ticks_y_max_width_at("last_col", "right")

    def axis_text_y_top_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum height[figure space] above the axes of y tick labels
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_top_y = self.geometry.top_y(ax)
            for side in ("left", "right"):
                for label in self.axis_text_y(ax, side):
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
            for side in ("left", "right"):
                for label in self.axis_text_y(ax, side):
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
            for side in ("bottom", "top"):
                for label in self.axis_text_x(ax, side):
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
            for side in ("bottom", "top"):
                for label in self.axis_text_x(ax, side):
                    label_right_x = self.geometry.right_x(label)
                    extras.append(max(0, label_right_x - ax_right_x))

        return max(extras) if len(extras) else 0

    def _move_artists(self, spaces: PlotSideSpaces):
        """
        Move the artists to their final positions
        """
        theme = self.plot.theme
        justify = _position_plot_labels(
            spaces.plot.figure, theme, spaces, self
        )

        if self.plot_tag:
            set_plot_tag_position(self.plot_tag, spaces)

        if self.axis_title_x_bottom:
            ha = theme.getp(("axis_title_x_bottom", "ha"), "center")
            self.axis_title_x_bottom.set_y(spaces.b.y1("axis_title_x"))
            justify.horizontally_about(self.axis_title_x_bottom, ha, "panel")

        if self.axis_title_x_top:
            ha = theme.getp(("axis_title_x_top", "ha"), "center")
            offset = spaces.t.strip_band_offset("axis")
            self.axis_title_x_top.set_y(spaces.t.y1("axis_title_x") + offset)
            justify.horizontally_about(self.axis_title_x_top, ha, "panel")

        if self.axis_title_y_left:
            va = theme.getp(("axis_title_y_left", "va"), "center")
            self.axis_title_y_left.set_x(spaces.l.x1("axis_title_y"))
            justify.vertically_about(self.axis_title_y_left, va, "panel")

        if self.axis_title_y_right:
            va = theme.getp(("axis_title_y_right", "va"), "center")
            offset = spaces.r.strip_band_offset("axis")
            self.axis_title_y_right.set_x(spaces.r.x1("axis_title_y") + offset)
            justify.vertically_about(self.axis_title_y_right, va, "panel")

        if self.legends:
            set_legends_position(self.legends, spaces)

        self._adjust_axis_text_x(justify, spaces)
        self._adjust_axis_text_y(justify, spaces)
        self._place_moved_axes(spaces)
        self._place_strip_backgrounds(spaces)

    def _adjust_axis_text_x(
        self, justify: TextJustifier, spaces: PlotSideSpaces
    ):
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

        # For strip_placement="inside", a top axis sharing its side with a
        # strip is pushed past the strip; zero otherwise.
        top_offset = spaces.t.strip_band_offset("axis")

        for side in ("bottom", "top"):
            va_default = "top" if side == "bottom" else "bottom"
            va = self.plot.theme.getp(
                (f"axis_text_x_{side}", "va"), va_default
            )
            for ax in self.plot.axs:
                texts = list(self.axis_text_x(ax, side))
                if not texts:
                    continue
                row_height = to_vertical_axis_dimensions(
                    self.axis_text_x_max_height(ax, side), ax
                )
                # bottom labels sit below the panel (axes y 0), top labels
                # above it (axes y 1)
                if side == "bottom":
                    low, high = (-row_height, 0)
                else:
                    offset = to_vertical_axis_dimensions(top_offset, ax)
                    low, high = (1 + offset, 1 + row_height + offset)
                for text in texts:
                    height = to_vertical_axis_dimensions(
                        self.geometry.tight_height(text), ax
                    )
                    justify.vertically(text, va, low, high, height=height)

    def _adjust_axis_text_y(
        self, justify: TextJustifier, spaces: PlotSideSpaces
    ):
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

        # For strip_placement="inside", a right axis sharing its side with a
        # strip is pushed past the strip; zero otherwise.
        right_offset = spaces.r.strip_band_offset("axis")

        for side in ("left", "right"):
            ha_default = "right" if side == "left" else "left"
            ha = self.plot.theme.getp(
                (f"axis_text_y_{side}", "ha"), ha_default
            )
            for ax in self.plot.axs:
                texts = list(self.axis_text_y(ax, side))
                if not texts:
                    continue
                col_width = to_horizontal_axis_dimensions(
                    self.axis_text_y_max_width(ax, side), ax
                )
                # left labels sit left of the panel (axes x 0), right labels
                # to the right of it (axes x 1)
                if side == "left":
                    low, high = (-col_width, 0)
                else:
                    offset = to_horizontal_axis_dimensions(right_offset, ax)
                    low, high = (1 + offset, 1 + col_width + offset)
                for text in texts:
                    width = to_horizontal_axis_dimensions(
                        self.geometry.tight_width(text), ax
                    )
                    justify.horizontally(text, ha, low, high, width=width)

    def _place_moved_axes(self, spaces: PlotSideSpaces):
        """
        Push a moved axis past the strip for strip_placement="inside"

        On a side where a moved axis and a facet strip would otherwise
        overlap, the spine and its tick marks shift outward by the strip's
        extent so the axis sits beyond the strip. Has no effect when the
        side has no shared strip/axis band.
        """
        fig = self.plot.figure
        to_points = 72 / fig.dpi
        top = spaces.t.strip_band_offset("axis") * fig.bbox.height * to_points
        right = spaces.r.strip_band_offset("axis") * fig.bbox.width * to_points
        for ax in self.plot.axs:
            if top:
                ax.spines["top"].set_position(("outward", top))
            if right:
                ax.spines["right"].set_position(("outward", right))

    def _strip_breadth_scales(
        self, group: list[StripText], breadth: Literal["height", "width"]
    ) -> list[float]:
        """
        Per-strip factor that equalises the breadth across a group

        Each strip's natural breadth is grown to match the largest in
        the group, so the backgrounds share a common height (top strips)
        or width (right strips).
        """
        natural = [getattr(self.strip_patch_bbox(st), breadth) for st in group]
        largest = max(natural)
        return [largest / b for b in natural]

    def _place_strip_backgrounds(self, spaces: PlotSideSpaces):
        """
        Fix each strip background at its final bounds and place its text

        When `strip_placement="outside"` and a moved axis shares the
        strip's side, the strip is shifted outward to clear the axis.
        """
        groups: tuple[
            tuple[
                list[StripText],
                Literal["height", "width"],
                _plot_side_space,
            ],
            ...,
        ] = (
            (self.strip_text_x or [], "height", spaces.t),
            (self.strip_text_y or [], "width", spaces.r),
        )
        for group, breadth, space in groups:
            if not group:
                continue
            offset = space.strip_band_offset("strip")
            scales = self._strip_breadth_scales(group, breadth)
            for st, scale in zip(group, scales):
                x0, y0, w, h = self.strip_patch_bbox(st, scale).bounds
                if st.position == "top":
                    y0 += offset
                else:
                    x0 += offset
                st.patch.set_bounds((x0, y0, w, h))
                st.patch.set_transform(self.plot.figure.transFigure)
                self._place_strip_text(st)

    def _place_strip_text(self, st: StripText):
        """
        Justify the strip text within its final background bounds
        """
        theme = self.plot.theme
        position = st.position
        ax = st.ax
        renderer = self.geometry.renderer
        sizing = self._strip_sizing(position)
        m = sizing.margin

        patch_bbox = bbox_in_axes_space(st.patch, ax, renderer)
        text_bbox = bbox_in_axes_space(st, ax, renderer)

        if position == "top":
            ha = theme.getp(("strip_text_x", "ha"), "center")
            va = theme.getp(("strip_text_x", "va"), "center")
            rel_x, rel_y = ha_as_float(ha), va_as_float(va)

            # line_height and margins in axes space
            line_height = st._line_height(renderer) / ax.bbox.height

            x = (
                # Justify horizontally within the strip_background
                rel_position(
                    rel_x,
                    text_bbox.width + (line_height * (m.l + m.r)),
                    patch_bbox.x0,
                    patch_bbox.x1,
                )
                + (m.l * line_height)
                + text_bbox.width / 2
            )
            # Setting the y position based on the bounding box is wrong
            y = (
                rel_position(
                    rel_y,
                    text_bbox.height,
                    patch_bbox.y0 + m.b * line_height,
                    patch_bbox.y1 - m.t * line_height,
                )
                + text_bbox.height / 2
            )
        else:  # "right"
            ha = theme.getp(("strip_text_y", "ha"), "center")
            va = theme.getp(("strip_text_y", "va"), "center")
            rel_x, rel_y = ha_as_float(ha), va_as_float(va)

            # line_height in axes space
            line_height = st._line_height(renderer) / ax.bbox.width

            x = (
                rel_position(
                    rel_x,
                    text_bbox.width,
                    patch_bbox.x0 + m.l * line_height,
                    patch_bbox.x1 - m.r * line_height,
                )
                + text_bbox.width / 2
            )
            y = (
                # Justify vertically within the strip_background
                rel_position(
                    rel_y,
                    text_bbox.height + ((m.b + m.t) * line_height),
                    patch_bbox.y0,
                    patch_bbox.y1,
                )
                + (m.b * line_height)
                + text_bbox.height / 2
            )

        st.set_position((x, y))


def _text_is_visible(text: Text) -> bool:
    """
    Return True if text is visible and is not empty
    """
    return text.get_visible() and text._text  # type: ignore


def _position_plot_labels(
    figure: Figure,
    theme: theme,
    spaces: PlotSideSpaces | CompositionSideSpaces,
    items: PlotLayoutItems | CompositionLayoutItems,
) -> TextJustifier:
    """
    Position title, subtitle, caption, footer, and footer decorations

    Returns the TextJustifier so the caller can reuse it for
    additional positioning (e.g. axis titles).
    """
    plot_title_position = theme.getp("plot_title_position", "panel")
    plot_caption_position = theme.getp("plot_caption_position", "panel")
    plot_footer_position = theme.getp("plot_footer_position", "plot")
    justify = TextJustifier.from_boundaries(
        figure,
        plot_left=spaces.plot_left,
        plot_right=spaces.plot_right,
        plot_bottom=spaces.plot_bottom,
        plot_top=spaces.plot_top,
        panel_left=spaces.panel_left,
        panel_right=spaces.panel_right,
        panel_bottom=spaces.panel_bottom,
        panel_top=spaces.panel_top,
    )

    if items.plot_title:
        ha = theme.getp(("plot_title", "ha"))
        items.plot_title.set_y(spaces.t.y2("plot_title"))
        justify.horizontally_about(items.plot_title, ha, plot_title_position)

    if items.plot_subtitle:
        ha = theme.getp(("plot_subtitle", "ha"))
        items.plot_subtitle.set_y(spaces.t.y2("plot_subtitle"))
        justify.horizontally_about(
            items.plot_subtitle, ha, plot_title_position
        )

    if items.plot_caption:
        ha = theme.getp(("plot_caption", "ha"), "right")
        items.plot_caption.set_y(spaces.b.y1("plot_caption"))
        justify.horizontally_about(
            items.plot_caption, ha, plot_caption_position
        )

    if items.plot_footer:
        ha = theme.getp(("plot_footer", "ha"), "left")
        items.plot_footer.set_y(spaces.b.y1("plot_footer"))
        justify.horizontally_about(items.plot_footer, ha, plot_footer_position)
        if items.plot_footer_background:
            resize_footer_background(
                items.plot_footer_background,
                x=spaces.l.offset,
                y=spaces.b.offset,
                height=spaces.b.footer_height,
                width=spaces.plot_width,
            )
        if items.plot_footer_line:
            resize_footer_line(
                items.plot_footer_line,
                x=spaces.l.offset,
                width=spaces.plot_width,
                y=spaces.b.offset + spaces.b.footer_height,
            )

    return justify


def set_legends_position(
    legends: legend_artists,
    spaces: PlotSideSpaces | CompositionSideSpaces,
):
    """
    Place legends on the figure, justifying each as required

    Works for both plot-level and composition-level legends. Both
    side-space hierarchies expose an `owner` property — a `ggplot`
    or `Compose` — which provides the `_sub_gridspec` to anchor
    against and the `figure` to transform onto.
    """
    panels_gs = spaces.owner._sub_gridspec
    params = panels_gs.get_subplot_params()
    transFigure = spaces.owner.figure.transFigure

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

    # Inside legends are placed using the panels coordinate system.
    # For a `Compose` owner with a `guide_area` host, the guides are
    # rendered in the guide_areas panel, so we need that gridspec
    if legends.inside:
        if isinstance(spaces.owner, Compose) and spaces.owner._guide_area:
            panels_gs = spaces.owner._guide_area._sub_gridspec

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

    justify = TextJustifier.from_boundaries(
        spaces.plot.figure,
        plot_left=spaces.l.plot_left,
        plot_right=spaces.r.plot_right,
        plot_bottom=spaces.b.plot_bottom,
        plot_top=spaces.t.plot_top,
        panel_left=spaces.l.panel_left,
        panel_right=spaces.r.panel_right,
        panel_bottom=spaces.b.panel_bottom,
        panel_top=spaces.t.panel_top,
    )
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
