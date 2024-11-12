"""
Routines to adjust subplot params so that subplots are
nicely fit in the figure. In doing so, only axis labels, tick labels, axes
titles and offsetboxes that are anchored to axes are currently considered.

Internally, this module assumes that the margins (left margin, etc.) which are
differences between `Axes.get_tightbbox` and `Axes.bbox` are independent of
Axes position. This may fail if `Axes.adjustable` is `datalim` as well as
such cases as when left or right margin are affected by xlabel.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field, fields
from functools import cached_property
from typing import TYPE_CHECKING

from plotnine.facets import facet_grid, facet_null, facet_wrap

from ._layout_items import LayoutItems

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Generator

    from plotnine import ggplot


# Note
# Margins around the plot are specified in figure coordinates
# We interpret that value to be a fraction of the width. So along
# the vertical direction we multiply by W/H to get equal space
# in both directions


@dataclass
class GridSpecParams:
    """
    Gridspec Parameters
    """

    left: float
    right: float
    top: float
    bottom: float
    wspace: float
    hspace: float


@dataclass
class _side_spaces(ABC):
    """
    Base class to for spaces

    A *_space class should track the size taken up by all the objects that
    may fall on that side of the panel. The same name may appear in multiple
    side classes (e.g. legend).
    """

    items: LayoutItems

    def __post_init__(self):
        self._calculate()

    def _calculate(self):
        """
        Calculate the space taken up by each artist
        """

    @property
    def total(self) -> float:
        """
        Total space
        """
        return sum(getattr(self, f.name) for f in fields(self)[1:])

    def sum_upto(self, item: str) -> float:
        """
        Sum of space upto but not including item

        Sums starting at the edge of the figure i.e. the "plot_margin".
        """

        def _fields_upto(item: str) -> Generator[Field, None, None]:
            for f in fields(self)[1:]:
                if f.name == item:
                    break
                yield f

        return sum(getattr(self, f.name) for f in _fields_upto(item))

    @cached_property
    def _legend_size(self) -> tuple[float, float]:
        """
        Return size of legend in figure coordinates

        We need this to accurately justify the legend by proportional
        values e.g. 0.2, instead of just left, right, top,  bottom &
        center.
        """
        return (0, 0)

    @cached_property
    def _legend_width(self) -> float:
        """
        Return width of legend in figure coordinates
        """
        return self._legend_size[0]

    @cached_property
    def _legend_height(self) -> float:
        """
        Return height of legend in figure coordinates
        """
        return self._legend_size[1]


@dataclass
class left_spaces(_side_spaces):
    """
    Space in the figure for artists on the left of the panel area

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    legend: float = 0
    legend_box_spacing: float = 0
    axis_title_y: float = 0
    axis_title_y_margin_right: float = 0
    axis_text_y: float = 0
    axis_ticks_y: float = 0

    def _calculate(self):
        theme = self.items.plot.theme
        calc = self.items.calc
        items = self.items

        self.plot_margin = theme.getp("plot_margin_left")
        if items.legends and items.legends.left:
            self.legend = self._legend_width
            self.legend_box_spacing = theme.getp("legend_box_spacing")

        if items.axis_title_y:
            self.axis_title_y_margin_right = theme.getp(
                ("axis_title_y", "margin")
            ).get_as("r", "fig")
            self.axis_title_y = calc.width(items.axis_title_y)

        # Account for the space consumed by the axis
        self.axis_text_y = items.axis_text_y_max_width("first_col")
        self.axis_ticks_y = items.axis_ticks_y_max_width("first_col")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = items.axis_text_x_left_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @cached_property
    def _legend_size(self) -> tuple[float, float]:
        if not (self.items.legends and self.items.legends.left):
            return (0, 0)

        return self.items.calc.size(self.items.legends.left.box)

    def edge(self, item: str) -> float:
        """
        Distance w.r.t figure width from the left edge of the figure
        """
        return self.sum_upto(item)

    @property
    def left(self):
        """
        Left of the panels in figure space
        """
        return self.total

    @property
    def plot_left(self):
        """
        Distance in figure space from left edge upto where artists start
        """
        return self.edge("legend")


@dataclass
class right_spaces(_side_spaces):
    """
    Space in the figure for artists on the right of the panel area

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    legend: float = 0
    legend_box_spacing: float = 0
    strip_text_y_width_right: float = 0

    def _calculate(self):
        items = self.items
        theme = self.items.plot.theme

        self.plot_margin = theme.getp("plot_margin_right")
        if items.legends and items.legends.right:
            self.legend = self._legend_width
            self.legend_box_spacing = theme.getp("legend_box_spacing")

        self.strip_text_y_width_right = items.strip_text_y_width("right")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = items.axis_text_x_right_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @cached_property
    def _legend_size(self) -> tuple[float, float]:
        if not (self.items.legends and self.items.legends.right):
            return (0, 0)

        return self.items.calc.size(self.items.legends.right.box)

    def edge(self, item: str) -> float:
        """
        Distance w.r.t figure width from the right edge of the figure
        """
        return 1 - self.sum_upto(item)

    @property
    def right(self):
        """
        Right of the panels in figure space
        """
        return 1 - self.total

    @property
    def plot_right(self):
        """
        Distance in figure space from right edge upto where artists start
        """
        return self.edge("legend")


@dataclass
class top_spaces(_side_spaces):
    """
    Space in the figure for artists above the panel area

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    plot_title: float = 0
    plot_title_margin_bottom: float = 0
    plot_subtitle: float = 0
    plot_subtitle_margin_bottom: float = 0
    legend: float = 0
    legend_box_spacing: float = 0
    strip_text_x_height_top: float = 0

    def _calculate(self):
        items = self.items
        theme = self.items.plot.theme
        calc = self.items.calc
        W, H = theme.getp("figure_size")
        F = W / H

        self.plot_margin = theme.getp("plot_margin_top") * F
        if items.plot_title:
            self.plot_title = calc.height(items.plot_title)
            self.plot_title_margin_bottom = (
                theme.getp(("plot_title", "margin")).get_as("b", "fig") * F
            )

        if items.plot_subtitle:
            self.plot_subtitle = calc.height(items.plot_subtitle)
            self.plot_subtitle_margin_bottom = (
                theme.getp(("plot_subtitle", "margin")).get_as("b", "fig") * F
            )

        if items.legends and items.legends.top:
            self.legend = self._legend_height
            self.legend_box_spacing = theme.getp("legend_box_spacing") * F

        self.strip_text_x_height_top = items.strip_text_x_height("top")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = items.axis_text_y_top_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @cached_property
    def _legend_size(self) -> tuple[float, float]:
        if not (self.items.legends and self.items.legends.top):
            return (0, 0)

        return self.items.calc.size(self.items.legends.top.box)

    def edge(self, item: str) -> float:
        """
        Distance w.r.t figure height from the top edge of the figure
        """
        return 1 - self.sum_upto(item)

    @property
    def top(self):
        """
        Top of the panels in figure space
        """
        return 1 - self.total

    @property
    def plot_top(self):
        """
        Distance in figure space from top edge upto where artists start
        """
        return self.edge("legend")


@dataclass
class bottom_spaces(_side_spaces):
    """
    Space in the figure for artists below the panel area

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    plot_caption: float = 0
    plot_caption_margin_top: float = 0
    legend: float = 0
    legend_box_spacing: float = 0
    axis_title_x: float = 0
    axis_title_x_margin_top: float = 0
    axis_text_x: float = 0
    axis_ticks_x: float = 0

    def _calculate(self):
        items = self.items
        theme = self.items.plot.theme
        calc = self.items.calc
        W, H = theme.getp("figure_size")
        F = W / H

        self.plot_margin = theme.getp("plot_margin_bottom") * F

        if items.plot_caption:
            self.plot_caption = calc.height(items.plot_caption)
            self.plot_caption_margin_top = (
                theme.getp(("plot_caption", "margin")).get_as("t", "fig") * F
            )

        if items.legends and items.legends.bottom:
            self.legend = self._legend_height
            self.legend_box_spacing = theme.getp("legend_box_spacing") * F

        if items.axis_title_x:
            self.axis_title_x = calc.height(items.axis_title_x)
            self.axis_title_x_margin_top = (
                theme.getp(("axis_title_x", "margin")).get_as("t", "fig") * F
            )

        # Account for the space consumed by the axis
        self.axis_ticks_x = items.axis_ticks_x_max_height("last_row")
        self.axis_text_x = items.axis_text_x_max_height("last_row")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = items.axis_text_y_bottom_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @cached_property
    def _legend_size(self) -> tuple[float, float]:
        if not (self.items.legends and self.items.legends.bottom):
            return (0, 0)

        return self.items.calc.size(self.items.legends.bottom.box)

    def edge(self, item: str) -> float:
        """
        Distance w.r.t figure height from the bottom edge of the figure
        """
        return self.sum_upto(item)

    @property
    def bottom(self):
        """
        Bottom of the panels in figure space
        """
        return self.total

    @property
    def plot_bottom(self):
        """
        Distance in figure space from bottom edge upto where artists start
        """
        return self.edge("legend")


@dataclass
class LayoutSpaces:
    """
    Compute the all the spaces required in the layout

    These are:

    1. The space of each artist between the panel and the edge of the
       figure.
    2. The space in-between the panels

    From these values, we put together the grid-spec parameters required
    by matplotblib to position the axes. We also use the values to adjust
    the coordinates of all the artists that occupy these spaces, placing
    them in their final positions.
    """

    plot: ggplot

    l: left_spaces = field(init=False)
    """All subspaces to the left of the panels"""

    r: right_spaces = field(init=False)
    """All subspaces to the right of the panels"""

    t: top_spaces = field(init=False)
    """All subspaces above the top of the panels"""

    b: bottom_spaces = field(init=False)
    """All subspaces below the bottom of the panels"""

    W: float = field(init=False)
    """Figure Width [inches]"""

    H: float = field(init=False)
    """Figure Height [inches]"""

    w: float = field(init=False)
    """Axes width w.r.t figure in [0, 1]"""

    h: float = field(init=False)
    """Axes height w.r.t figure in [0, 1]"""

    sw: float = field(init=False)
    """horizontal spacing btn panels w.r.t figure"""

    sh: float = field(init=False)
    """vertical spacing btn panels w.r.t figure"""

    gsparams: GridSpecParams = field(init=False)
    """Grid spacing btn panels w.r.t figure"""

    def __post_init__(self):
        self.items = LayoutItems(self.plot)
        self.W, self.H = self.plot.theme.getp("figure_size")

        # Calculate the spacing along the edges of the panel area
        # (spacing required by plotnine)
        self.l = left_spaces(self.items)
        self.r = right_spaces(self.items)
        self.t = top_spaces(self.items)
        self.b = bottom_spaces(self.items)

        # Calculate the gridspec params
        # (spacing required by mpl)
        self.gsparams = self._calculate_panel_spacing()

        # Adjust the spacing parameters for the desired aspect ratio
        # It is simpler to adjust for the aspect ratio than to calculate
        # the final parameters that are true to the aspect ratio in
        # one-short
        if (ratio := self.plot.facet._aspect_ratio()) is not None:
            current_ratio = self.aspect_ratio
            if ratio > current_ratio:
                # Increase aspect ratio, taller panels
                self._reduce_width(ratio)
            elif ratio < current_ratio:
                # Increase aspect ratio, wider panels
                self._reduce_height(ratio)

    def increase_horizontal_plot_margin(self, dw: float):
        """
        Increase the plot_margin to the right & left of the panels
        """
        self.l.plot_margin += dw
        self.r.plot_margin += dw

    def increase_vertical_plot_margin(self, dh: float):
        """
        Increase the plot_margin to the above & below of the panels
        """
        self.t.plot_margin += dh
        self.b.plot_margin += dh

    def _calculate_panel_spacing(self) -> GridSpecParams:
        """
        Spacing between the panels (wspace & hspace)

        Both spaces are calculated from a fraction of the width.
        This ensures that the same fraction gives equals space
        in both directions.
        """
        if isinstance(self.plot.facet, facet_wrap):
            wspace, hspace = self._calculate_panel_spacing_facet_wrap()
        elif isinstance(self.plot.facet, facet_grid):
            wspace, hspace = self._calculate_panel_spacing_facet_grid()
        elif isinstance(self.plot.facet, facet_null):
            wspace, hspace = self._calculate_panel_spacing_facet_null()
        else:
            raise TypeError(f"Unknown type of facet: {type(self.plot.facet)}")

        return GridSpecParams(
            self.l.left,
            self.r.right,
            self.t.top,
            self.b.bottom,
            wspace,
            hspace,
        )

    def _calculate_panel_spacing_facet_grid(self) -> tuple[float, float]:
        """
        Calculate spacing parts for facet_grid
        """
        theme = self.plot.theme

        ncol = self.plot.facet.ncol
        nrow = self.plot.facet.nrow

        # Both spacings are specified as fractions of the figure width
        # Multiply the vertical by (W/H) so that the gullies along both
        # directions are equally spaced.
        self.sw = theme.getp("panel_spacing_x")
        self.sh = theme.getp("panel_spacing_y") * self.W / self.H

        # width and height of axes as fraction of figure width & height
        self.w = ((self.r.right - self.l.left) - self.sw * (ncol - 1)) / ncol
        self.h = ((self.t.top - self.b.bottom) - self.sh * (nrow - 1)) / nrow

        # Spacing as fraction of axes width & height
        wspace = self.sw / self.w
        hspace = self.sh / self.h
        return (wspace, hspace)

    def _calculate_panel_spacing_facet_wrap(self) -> tuple[float, float]:
        """
        Calculate spacing parts for facet_wrap
        """
        facet = self.plot.facet
        theme = self.plot.theme

        ncol = facet.ncol
        nrow = facet.nrow

        # Both spacings are specified as fractions of the figure width
        self.sw = theme.getp("panel_spacing_x")
        self.sh = theme.getp("panel_spacing_y") * self.W / self.H

        # A fraction of the strip height
        # Effectively slides the strip
        #   +ve: Away from the panel
        #    0:  Top of the panel
        #   -ve: Into the panel
        # Where values <= -1, put the strip completely into
        # the panel. We do not worry about larger -ves.
        strip_align_x = theme.getp("strip_align_x")

        # Only interested in the proportion of the strip that
        # does not overlap with the panel
        if strip_align_x > -1:
            self.sh += self.t.strip_text_x_height_top * (1 + strip_align_x)

        if facet.free["x"]:
            self.sh += self.items.axis_text_x_max_height(
                "all"
            ) + self.items.axis_ticks_x_max_height("all")
        if facet.free["y"]:
            self.sw += self.items.axis_text_y_max_width(
                "all"
            ) + self.items.axis_ticks_y_max_width("all")

        # width and height of axes as fraction of figure width & height
        self.w = ((self.r.right - self.l.left) - self.sw * (ncol - 1)) / ncol
        self.h = ((self.t.top - self.b.bottom) - self.sh * (nrow - 1)) / nrow

        # Spacing as fraction of axes width & height
        wspace = self.sw / self.w
        hspace = self.sh / self.h
        return (wspace, hspace)

    def _calculate_panel_spacing_facet_null(self) -> tuple[float, float]:
        """
        Calculate spacing parts for facet_null
        """
        self.w = self.r.right - self.l.left
        self.h = self.t.top - self.b.bottom
        self.sw = 0
        self.sh = 0
        return 0, 0

    def _reduce_height(self, ratio: float):
        """
        Reduce the height of axes to get the aspect ratio
        """
        # New height w.r.t figure height
        h1 = ratio * self.w * (self.W / self.H)

        # Half of the total vertical reduction w.r.t figure height
        dh = (self.h - h1) * self.plot.facet.nrow / 2

        # Reduce plot area height
        self.gsparams.top -= dh
        self.gsparams.bottom += dh
        self.gsparams.hspace = self.sh / h1

        # Add more vertical plot margin
        self.increase_vertical_plot_margin(dh)

    def _reduce_width(self, ratio: float):
        """
        Reduce the width of axes to get the aspect ratio
        """
        # New width w.r.t figure width
        w1 = (self.h * self.H) / (ratio * self.W)

        # Half of the total horizontal reduction w.r.t figure width
        dw = (self.w - w1) * self.plot.facet.ncol / 2

        # Reduce width
        self.gsparams.left += dw
        self.gsparams.right -= dw
        self.gsparams.wspace = self.sw / w1

        # Add more horizontal margin
        self.increase_horizontal_plot_margin(dw)

    @property
    def aspect_ratio(self) -> float:
        """
        Default aspect ratio of the panels
        """
        return (self.h * self.H) / (self.w * self.W)
