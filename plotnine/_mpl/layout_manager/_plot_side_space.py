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

from functools import cached_property
from typing import TYPE_CHECKING

from plotnine.exceptions import PlotnineError
from plotnine.facets import facet_grid, facet_null, facet_wrap

from ._plot_layout_items import PlotLayoutItems
from ._side_space import GridSpecParams, _side_space

if TYPE_CHECKING:
    from plotnine import ggplot
    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine.iapi import outside_legend


class _plot_side_space(_side_space):
    """
    Base class for the side space around a plot
    """

    def __init__(self, items: PlotLayoutItems):
        self.items = items
        self.gridspec = items.plot._gridspec
        self._calculate()

    @cached_property
    def _legend_size(self) -> tuple[float, float]:
        """
        Return size of legend in figure coordinates

        We need this to accurately justify the legend by proportional
        values e.g. 0.2, instead of just left, right, top,  bottom &
        center.
        """
        if not self.has_legend:
            return (0, 0)

        ol: outside_legend = getattr(self.items.legends, self.side)
        return self.items.geometry.size(ol.box)

    @cached_property
    def legend_width(self) -> float:
        """
        Return width of legend in figure coordinates
        """
        return self._legend_size[0]

    @cached_property
    def legend_height(self) -> float:
        """
        Return height of legend in figure coordinates
        """
        return self._legend_size[1]

    @property
    def has_tag(self) -> bool:
        """
        Return True if the space/margin to this side of the panel has a tag

        If it does, then it will be included in the layout
        """
        getp = self.items.plot.theme.getp
        return getp("plot_tag_location") == "margin" and self.side in getp(
            "plot_tag_position"
        )

    @property
    def has_legend(self) -> bool:
        """
        Return True if the space/margin to this side of the panel has a legend

        If it does, then it will be included in the layout
        """
        if not self.items.legends:
            return False
        return hasattr(self.items.legends, self.side)

    @property
    def tag_width(self) -> float:
        """
        The width of the tag including the margins

        The value is zero except if all these are true:
            - The tag is in the margin `theme(plot_tag_position = "margin")`
            - The tag at one one of the the following locations;
              left, right, topleft, topright, bottomleft or bottomright
        """
        return 0

    @property
    def tag_height(self) -> float:
        """
        The height of the tag including the margins

        The value is zero except if all these are true:
            - The tag is in the margin `theme(plot_tag_position = "margin")`
            - The tag at one one of the the following locations;
              top, bottom, topleft, topright, bottomleft or bottomright
        """
        return 0

    @property
    def axis_title_clearance(self) -> float:
        """
        The distance between the axis title and the panel

         Figure
         ----------------------------
        |         Panel              |
        |         -----------        |
        |        |           |       |
        |        |           |       |
        |  Y<--->|           |       |
        |        |           |       |
        |        |           |       |
        |         -----------        |
        |                            |
         ----------------------------

        We use this value to when aligning axis titles in a
        plot composition.
        """

        try:
            return self.total - self.sum_upto("axis_title_alignment")
        except AttributeError as err:
            # There is probably an error in in the layout manager
            raise PlotnineError("Side has no axis title") from err


class left_space(_plot_side_space):
    """
    Space in the figure for artists on the left of the panel area

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    tag_alignment: float = 0
    """
    Space added to align the tag in this plot with others in a composition

    This value is calculated during the layout process, and it ensures that
    all tags on this side of the plot take up the same amount of space in
    the margin. e.g. from

         ------------------------------------
        | plot_margin | tag | artists        |
        |------------------------------------|
        | plot_margin | A long tag | artists |
         ------------------------------------

    to

         ------------------------------------
        | plot_margin |     tag    | artists |
        |------------------------------------|
        | plot_margin | A long tag | artists |
         ------------------------------------

    And the tag is justified within that space e.g if ha="left" we get

         ------------------------------------
        | plot_margin | tag        | artists |
        |------------------------------------|
        | plot_margin | A long tag | artists |
         ------------------------------------

    So, contrary to the order in which the space items are laid out, the 
    tag_alignment does not necessarily come before the plot_tag.
    """
    plot_tag_margin_left: float = 0
    plot_tag: float = 0
    plot_tag_margin_right: float = 0
    margin_alignment: float = 0
    """
    Space added to align this plot with others in a composition

    This value is calculated during the layout process in a tree structure
    that has convenient access to the sides/edges of the panels in the
    composition.
    """
    legend: float = 0
    legend_box_spacing: float = 0
    axis_title_y_margin_left: float = 0
    axis_title_y: float = 0
    axis_title_y_margin_right: float = 0
    axis_title_alignment: float = 0
    """
    Space added to align the axis title with others in a composition

    This value is calculated during the layout process. The amount is
    the difference between the largest and smallest axis_title_clearance
    among the items in the composition.
    """
    axis_text_y_margin_left: float = 0
    axis_text_y: float = 0
    axis_text_y_margin_right: float = 0
    axis_ticks_y: float = 0

    def _calculate(self):
        theme = self.items.plot.theme
        geometry = self.items.geometry
        items = self.items

        self.plot_margin = theme.getp("plot_margin_left")

        if self.has_tag and items.plot_tag:
            m = theme.get_margin("plot_tag").fig
            self.plot_tag_margin_left = m.l
            self.plot_tag = geometry.width(items.plot_tag)
            self.plot_tag_margin_right = m.r

        if items.legends and items.legends.left:
            self.legend = self.legend_width
            self.legend_box_spacing = theme.getp("legend_box_spacing")

        if items.axis_title_y:
            m = theme.get_margin("axis_title_y").fig
            self.axis_title_y_margin_left = m.l
            self.axis_title_y = geometry.width(items.axis_title_y)
            self.axis_title_y_margin_right = m.r

        # Account for the space consumed by the axis
        self.axis_text_y = items.axis_text_y_max_width_at("first_col")
        if self.axis_text_y:
            m = theme.get_margin("axis_text_y").fig
            self.axis_text_y_margin_left = m.l
            self.axis_text_y_margin_right = m.r

        self.axis_ticks_y = items.axis_ticks_y_max_width_at("first_col")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = items.axis_text_x_left_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @property
    def offset(self) -> float:
        """
        Distance from left of the figure to the left of the plot gridspec

              ----------------(1, 1)
             |      ----      |
             |  dx |    |     |
             |<--->|    |     |
             |     |    |     |
             |      ----      |
        (0, 0)----------------

        """
        return self.gridspec.bbox_relative.x0

    def x1(self, item: str) -> float:
        """
        Lower x-coordinate in figure space of the item
        """
        return self.to_figure_space(self.sum_upto(item))

    def x2(self, item: str) -> float:
        """
        Higher x-coordinate in figure space of the item
        """
        return self.to_figure_space(self.sum_incl(item))

    @property
    def panel_left_relative(self):
        """
        Left (relative to the gridspec) of the panels in figure dimensions
        """
        return self.total

    @property
    def panel_left(self):
        """
        Left of the panels in figure space
        """
        return self.to_figure_space(self.panel_left_relative)

    @property
    def plot_left(self):
        """
        Distance up to the left-most artist in figure space
        """
        return self.x1("legend")

    @property
    def tag_width(self):
        """
        The width of the tag including the margins
        """
        return (
            self.plot_tag_margin_left
            + self.plot_tag
            + self.plot_tag_margin_right
        )


class right_space(_plot_side_space):
    """
    Space in the figure for artists on the right of the panel area

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    tag_alignment: float = 0
    plot_tag_margin_right: float = 0
    plot_tag: float = 0
    plot_tag_margin_left: float = 0
    margin_alignment: float = 0
    legend: float = 0
    legend_box_spacing: float = 0
    strip_text_y_extra_width: float = 0

    def _calculate(self):
        items = self.items
        theme = self.items.plot.theme
        geometry = self.items.geometry

        self.plot_margin = theme.getp("plot_margin_right")

        if self.has_tag and items.plot_tag:
            m = theme.get_margin("plot_tag").fig
            self.plot_tag_margin_right = m.r
            self.plot_tag = geometry.width(items.plot_tag)
            self.plot_tag_margin_left = m.l

        if items.legends and items.legends.right:
            self.legend = self.legend_width
            self.legend_box_spacing = theme.getp("legend_box_spacing")

        self.strip_text_y_extra_width = items.strip_text_y_extra_width("right")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = items.axis_text_x_right_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @property
    def offset(self):
        """
        Distance from right of the figure to the right of the plot gridspec

              ---------------(1, 1)
             |     ----      |
             |    |    | -dx |
             |    |    |<--->|
             |    |    |     |
             |     ----      |
        (0, 0)---------------

        """
        return self.gridspec.bbox_relative.x1 - 1

    def x1(self, item: str) -> float:
        """
        Lower x-coordinate in figure space of the item
        """
        return self.to_figure_space(1 - self.sum_incl(item))

    def x2(self, item: str) -> float:
        """
        Higher x-coordinate in figure space of the item
        """
        return self.to_figure_space(1 - self.sum_upto(item))

    @property
    def panel_right_relative(self):
        """
        Right (relative to the gridspec) of the panels in figure dimensions
        """
        return 1 - self.total

    @property
    def panel_right(self):
        """
        Right of the panels in figure space
        """
        return self.to_figure_space(self.panel_right_relative)

    @property
    def plot_right(self):
        """
        Distance up to the right-most artist in figure space
        """
        return self.x2("legend")

    @property
    def tag_width(self):
        """
        The width of the tag including the margins
        """
        return (
            self.plot_tag_margin_right
            + self.plot_tag
            + self.plot_tag_margin_left
        )


class top_space(_plot_side_space):
    """
    Space in the figure for artists above the panel area

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    tag_alignment: float = 0
    plot_tag_margin_top: float = 0
    plot_tag: float = 0
    plot_tag_margin_bottom: float = 0
    margin_alignment: float = 0
    plot_title_margin_top: float = 0
    plot_title: float = 0
    plot_title_margin_bottom: float = 0
    plot_subtitle_margin_top: float = 0
    plot_subtitle: float = 0
    plot_subtitle_margin_bottom: float = 0
    legend: float = 0
    legend_box_spacing: float = 0
    strip_text_x_extra_height: float = 0

    def _calculate(self):
        items = self.items
        theme = self.items.plot.theme
        geometry = self.items.geometry
        W, H = theme.getp("figure_size")
        F = W / H

        self.plot_margin = theme.getp("plot_margin_top") * F

        if self.has_tag and items.plot_tag:
            m = theme.get_margin("plot_tag").fig
            self.plot_tag_margin_top = m.t
            self.plot_tag = geometry.height(items.plot_tag)
            self.plot_tag_margin_bottom = m.b

        if items.plot_title:
            m = theme.get_margin("plot_title").fig
            self.plot_title_margin_top = m.t * F
            self.plot_title = geometry.height(items.plot_title)
            self.plot_title_margin_bottom = m.b * F

        if items.plot_subtitle:
            m = theme.get_margin("plot_subtitle").fig
            self.plot_subtitle_margin_top = m.t * F
            self.plot_subtitle = geometry.height(items.plot_subtitle)
            self.plot_subtitle_margin_bottom = m.b * F

        if items.legends and items.legends.top:
            self.legend = self.legend_height
            self.legend_box_spacing = theme.getp("legend_box_spacing") * F

        self.strip_text_x_extra_height = items.strip_text_x_extra_height("top")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = items.axis_text_y_top_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @property
    def offset(self) -> float:
        """
        Distance from top of the figure to the top of the plot gridspec

              ----------------(1, 1)
             |       ^        |
             |       |-dy     |
             |       v        |
             |      ----      |
             |     |    |     |
             |     |    |     |
             |     |    |     |
             |      ----      |
             |                |
        (0, 0)----------------
        """
        return self.gridspec.bbox_relative.y1 - 1

    def y1(self, item: str) -> float:
        """
        Lower y-coordinate in figure space of the item
        """
        return self.to_figure_space(1 - self.sum_incl(item))

    def y2(self, item: str) -> float:
        """
        Higher y-coordinate in figure space of the item
        """
        return self.to_figure_space(1 - self.sum_upto(item))

    @property
    def panel_top_relative(self):
        """
        Top (relative to the gridspec) of the panels in figure dimensions
        """
        return 1 - self.total

    @property
    def panel_top(self):
        """
        Top of the panels in figure space
        """
        return self.to_figure_space(self.panel_top_relative)

    @property
    def plot_top(self):
        """
        Distance up to the top-most artist in figure space
        """
        return self.y2("legend")

    @property
    def tag_height(self):
        """
        The height of the tag including the margins
        """
        return (
            self.plot_tag_margin_top
            + self.plot_tag
            + self.plot_tag_margin_bottom
        )


class bottom_space(_plot_side_space):
    """
    Space in the figure for artists below the panel area

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    tag_alignment: float = 0
    plot_tag_margin_bottom: float = 0
    plot_tag: float = 0
    plot_tag_margin_top: float = 0
    margin_alignment: float = 0
    plot_caption_margin_bottom: float = 0
    plot_caption: float = 0
    plot_caption_margin_top: float = 0
    legend: float = 0
    legend_box_spacing: float = 0
    axis_title_x_margin_bottom: float = 0
    axis_title_x: float = 0
    axis_title_x_margin_top: float = 0
    axis_title_alignment: float = 0
    """
    Space added to align the axis title with others in a composition

    This value is calculated during the layout process in a tree structure
    that has convenient access to the sides/edges of the panels in the
    composition. It's amount is the difference in height between this axis
    text (and it's margins) and the tallest axis text (and it's margin).
    """
    axis_text_x_margin_bottom: float = 0
    axis_text_x: float = 0
    axis_text_x_margin_top: float = 0
    axis_ticks_x: float = 0

    def _calculate(self):
        items = self.items
        theme = self.items.plot.theme
        geometry = self.items.geometry
        W, H = theme.getp("figure_size")
        F = W / H

        self.plot_margin = theme.getp("plot_margin_bottom") * F

        if self.has_tag and items.plot_tag:
            m = theme.get_margin("plot_tag").fig
            self.plot_tag_margin_bottom = m.b
            self.plot_tag = geometry.height(items.plot_tag)
            self.plot_tag_margin_top = m.t

        if items.plot_caption:
            m = theme.get_margin("plot_caption").fig
            self.plot_caption_margin_bottom = m.b * F
            self.plot_caption = geometry.height(items.plot_caption)
            self.plot_caption_margin_top = m.t * F

        if items.legends and items.legends.bottom:
            self.legend = self.legend_height
            self.legend_box_spacing = theme.getp("legend_box_spacing") * F

        if items.axis_title_x:
            m = theme.get_margin("axis_title_x").fig
            self.axis_title_x_margin_bottom = m.b * F
            self.axis_title_x = geometry.height(items.axis_title_x)
            self.axis_title_x_margin_top = m.t * F

        # Account for the space consumed by the axis
        self.axis_text_x = items.axis_text_x_max_height_at("last_row")
        if self.axis_text_x:
            m = theme.get_margin("axis_text_x").fig
            self.axis_text_x_margin_bottom = m.b
            self.axis_text_x_margin_top = m.t
        self.axis_ticks_x = items.axis_ticks_x_max_height_at("last_row")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = items.axis_text_y_bottom_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @property
    def offset(self) -> float:
        """
        Distance from bottom of the figure to the bottom of the plot gridspec

              ----------------(1, 1)
             |                |
             |      ----      |
             |     |    |     |
             |     |    |     |
             |     |    |     |
             |      ----      |
             |       ^        |
             |       |dy      |
             |       v        |
        (0, 0)----------------
        """
        return self.gridspec.bbox_relative.y0

    def y1(self, item: str) -> float:
        """
        Lower y-coordinate in figure space of the item
        """
        return self.to_figure_space(self.sum_upto(item))

    def y2(self, item: str) -> float:
        """
        Higher y-coordinate in figure space of the item
        """
        return self.to_figure_space(self.sum_incl(item))

    @property
    def panel_bottom_relative(self):
        """
        Bottom (relative to the gridspec) of the panels in figure dimensions
        """
        return self.total

    @property
    def panel_bottom(self):
        """
        Bottom of the panels in figure space
        """
        return self.to_figure_space(self.panel_bottom_relative)

    @property
    def plot_bottom(self):
        """
        Distance up to the bottom-most artist in figure space
        """
        return self.y1("legend")

    @property
    def tag_height(self):
        """
        The height of the tag including the margins
        """
        return (
            self.plot_tag_margin_bottom
            + self.plot_tag
            + self.plot_tag_margin_top
        )


class PlotSideSpaces:
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

    W: float
    """Figure Width [inches]"""

    H: float
    """Figure Height [inches]"""

    w: float
    """Axes width w.r.t figure in [0, 1]"""

    h: float
    """Axes height w.r.t figure in [0, 1]"""

    sh: float
    """horizontal spacing btn panels w.r.t figure"""

    sw: float
    """vertical spacing btn panels w.r.t figure"""

    gsparams: GridSpecParams
    """Grid spacing btn panels w.r.t figure"""

    def __init__(self, plot: ggplot):
        self.plot = plot
        self.items = PlotLayoutItems(plot)

        self.l = left_space(self.items)
        """All subspaces to the left of the panels"""

        self.r = right_space(self.items)
        """All subspaces to the right of the panels"""

        self.t = top_space(self.items)
        """All subspaces above the top of the panels"""

        self.b = bottom_space(self.items)
        """All subspaces below the bottom of the panels"""

        self.W, self.H = plot.theme.getp("figure_size")

    def get_gridspec_params(self) -> GridSpecParams:
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

        return self.gsparams

    @property
    def plot_width(self) -> float:
        """
        Width [figure dimensions] of the whole plot
        """
        return float(self.plot._gridspec.width)

    @property
    def plot_height(self) -> float:
        """
        Height [figure dimensions] of the whole plot
        """
        return float(self.plot._gridspec.height)

    @property
    def panel_width(self) -> float:
        """
        Width [figure dimensions] of panels
        """
        return self.r.panel_right - self.l.panel_left

    @property
    def panel_height(self) -> float:
        """
        Height [figure dimensions] of panels
        """
        return self.t.panel_top - self.b.panel_bottom

    @property
    def horizontal_space(self) -> float:
        """
        Horizontal non-panel space [figure dimensions]
        """
        # The same as plot_width - panel_width
        return self.l.total + self.r.total

    @property
    def vertical_space(self) -> float:
        """
        Vertical non-panel space [figure dimensions]
        """
        # The same as plot_height - panel_height
        return self.t.total + self.b.total

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

    @property
    def plot_area_coordinates(
        self,
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        Lower-left and upper-right coordinates of the plot area

        This is the area surrounded by the plot_margin.
        """
        x1, x2 = self.l.x2("plot_margin"), self.r.x1("plot_margin")
        y1, y2 = self.b.y2("plot_margin"), self.t.y1("plot_margin")
        return ((x1, y1), (x2, y2))

    @property
    def panel_area_coordinates(
        self,
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        Lower-left and upper-right coordinates of the panel area

        This is the area in which the panels are drawn.
        """
        x1, x2 = self.l.panel_left, self.r.panel_right
        y1, y2 = self.b.panel_bottom, self.t.panel_top
        return ((x1, y1), (x2, y2))

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
            self.l.panel_left_relative,
            self.r.panel_right_relative,
            self.t.panel_top_relative,
            self.b.panel_bottom_relative,
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
        self.w = (self.panel_width - self.sw * (ncol - 1)) / ncol
        self.h = (self.panel_height - self.sh * (nrow - 1)) / nrow

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
            self.sh += self.t.strip_text_x_extra_height * (1 + strip_align_x)

        if facet.free["x"]:
            self.sh += self.items.axis_text_x_max_height_at(
                "all"
            ) + self.items.axis_ticks_x_max_height_at("all")
        if facet.free["y"]:
            self.sw += self.items.axis_text_y_max_width_at(
                "all"
            ) + self.items.axis_ticks_y_max_width_at("all")

        # width and height of axes as fraction of figure width & height
        self.w = (self.panel_width - self.sw * (ncol - 1)) / ncol
        self.h = (self.panel_height - self.sh * (nrow - 1)) / nrow

        # Spacing as fraction of axes width & height
        wspace = self.sw / self.w
        hspace = self.sh / self.h
        return (wspace, hspace)

    def _calculate_panel_spacing_facet_null(self) -> tuple[float, float]:
        """
        Calculate spacing parts for facet_null
        """
        self.w = self.panel_width
        self.h = self.panel_height
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

    @cached_property
    def gs(self) -> p9GridSpec:
        """
        The gridspec
        """
        return self.plot._gridspec

    def to_figure_space(
        self,
        position: tuple[float, float],
    ) -> tuple[float, float]:
        """
        Convert position from gridspec space to figure space
        """
        _x, _y = position
        x = self.l.plot_left + (self.r.plot_right - self.l.plot_left) * _x
        y = self.b.plot_bottom + (self.t.plot_top - self.b.plot_bottom) * _y
        return (x, y)
