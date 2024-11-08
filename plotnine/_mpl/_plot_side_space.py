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
from dataclasses import dataclass, fields
from functools import cached_property
from typing import TYPE_CHECKING, cast

from ..facets import facet_grid, facet_null, facet_wrap
from .utils import bbox_in_figure_space

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Generator

    from ._layout_pack import LayoutPack


# Note
# Margins around the plot are specified in figure coordinates
# We interpret that value to be a fraction of the width. So along
# the vertical direction we multiply by W/H to get equal space
# in both directions


@dataclass
class WHSpaceParts:
    """
    Width-Height Spaces

    We need these in one places for easy access
    """

    W: float  # Figure width
    H: float  # Figure height
    w: float  # Axes width w.r.t figure in [0, 1]
    h: float  # Axes height w.r.t figure in [0, 1]
    sw: float  # horizontal spacing btn panels w.r.t figure
    sh: float  # vertical spacing btn panels w.r.t figure
    wspace: float  # mpl.subplotpars.wspace
    hspace: float  # mpl.subplotpars.hspace

    @property
    def aspect_ratio(self) -> float:
        """
        Aspect ratio of the panels
        """
        return (self.h * self.H) / (self.w * self.W)


@dataclass
class _side_spaces(ABC):
    """
    Base class to for spaces

    A *_space class should track the size taken up by all the objects that
    may fall on that side of the panel. The same name may appear in multiple
    side classes (e.g. legend).
    """

    pack: LayoutPack

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
    Space in the figure for artists on the left of the panels

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
        theme = self.pack.theme
        pack = self.pack

        self.plot_margin = theme.getp("plot_margin_left")
        if pack.legends and pack.legends.left:
            self.legend = self._legend_width
            self.legend_box_spacing = theme.getp("legend_box_spacing")

        if pack.axis_title_y:
            self.axis_title_y_margin_right = theme.getp(
                ("axis_title_y", "margin")
            ).get_as("r", "fig")
            self.axis_title_y = bbox_in_figure_space(
                pack.axis_title_y, pack.figure, pack.renderer
            ).width

        # Account for the space consumed by the axis
        self.axis_text_y = pack.axis_text_y_max_width("first_col")
        self.axis_ticks_y = pack.axis_ticks_y_max_width("first_col")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = pack.axis_text_x_left_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @cached_property
    def _legend_size(self) -> tuple[float, float]:
        if not (self.pack.legends and self.pack.legends.left):
            return (0, 0)

        bbox = bbox_in_figure_space(
            self.pack.legends.left.box, self.pack.figure, self.pack.renderer
        )
        return bbox.width, bbox.height

    def edge(self, item: str) -> float:
        """
        Distance w.r.t figure width from the left edge of the figure
        """
        return self.sum_upto(item)


@dataclass
class right_spaces(_side_spaces):
    """
    Space in the figure for artists on the right of the panels

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    legend: float = 0
    legend_box_spacing: float = 0
    strip_text_y_width_right: float = 0

    def _calculate(self):
        pack = self.pack
        theme = self.pack.theme

        self.plot_margin = theme.getp("plot_margin_right")
        if pack.legends and pack.legends.right:
            self.legend = self._legend_width
            self.legend_box_spacing = theme.getp("legend_box_spacing")

        self.strip_text_y_width_right = pack.strip_text_y_width("right")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = pack.axis_text_x_right_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @cached_property
    def _legend_size(self) -> tuple[float, float]:
        if not (self.pack.legends and self.pack.legends.right):
            return (0, 0)

        bbox = bbox_in_figure_space(
            self.pack.legends.right.box, self.pack.figure, self.pack.renderer
        )
        return bbox.width, bbox.height

    def edge(self, item: str) -> float:
        """
        Distance w.r.t figure width from the right edge of the figure
        """
        return 1 - self.sum_upto(item)


@dataclass
class top_spaces(_side_spaces):
    """
    Space in the figure for artists above the panels

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
        pack = self.pack
        theme = self.pack.theme
        W, H = theme.getp("figure_size")
        F = W / H

        self.plot_margin = theme.getp("plot_margin_top") * F
        if pack.plot_title:
            self.plot_title = bbox_in_figure_space(
                pack.plot_title, pack.figure, pack.renderer
            ).height
            self.plot_title_margin_bottom = (
                theme.getp(("plot_title", "margin")).get_as("b", "fig") * F
            )

        if pack.plot_subtitle:
            self.plot_subtitle = bbox_in_figure_space(
                pack.plot_subtitle, pack.figure, pack.renderer
            ).height
            self.plot_subtitle_margin_bottom = (
                theme.getp(("plot_subtitle", "margin")).get_as("b", "fig") * F
            )

        if pack.legends and pack.legends.top:
            self.legend = self._legend_height
            self.legend_box_spacing = theme.getp("legend_box_spacing") * F

        self.strip_text_x_height_top = pack.strip_text_x_height("top")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = pack.axis_text_y_top_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @cached_property
    def _legend_size(self) -> tuple[float, float]:
        if not (self.pack.legends and self.pack.legends.top):
            return (0, 0)

        bbox = bbox_in_figure_space(
            self.pack.legends.top.box, self.pack.figure, self.pack.renderer
        )
        return bbox.width, bbox.height

    def edge(self, item: str) -> float:
        """
        Distance w.r.t figure height from the top edge of the figure
        """
        return 1 - self.sum_upto(item)


@dataclass
class bottom_spaces(_side_spaces):
    """
    Space in the figure for artists below the panels

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
        pack = self.pack
        theme = self.pack.theme
        W, H = theme.getp("figure_size")
        F = W / H

        self.plot_margin = theme.getp("plot_margin_bottom") * F

        if pack.plot_caption:
            self.plot_caption = bbox_in_figure_space(
                pack.plot_caption, pack.figure, pack.renderer
            ).height
            self.plot_caption_margin_top = (
                theme.getp(("plot_caption", "margin")).get_as("t", "fig") * F
            )

        if pack.legends and pack.legends.bottom:
            self.legend = self._legend_height
            self.legend_box_spacing = theme.getp("legend_box_spacing") * F

        if pack.axis_title_x:
            self.axis_title_x = bbox_in_figure_space(
                pack.axis_title_x, pack.figure, pack.renderer
            ).height
            self.axis_title_x_margin_top = (
                theme.getp(("axis_title_x", "margin")).get_as("t", "fig") * F
            )

        # Account for the space consumed by the axis
        self.axis_ticks_x = pack.axis_ticks_x_max_height("last_row")
        self.axis_text_x = pack.axis_text_x_max_height("last_row")

        # Adjust plot_margin to make room for ylabels that protude well
        # beyond the axes
        # NOTE: This adjustment breaks down when the protrusion is large
        protrusion = pack.axis_text_y_bottom_protrusion("all")
        adjustment = protrusion - (self.total - self.plot_margin)
        if adjustment > 0:
            self.plot_margin += adjustment

    @cached_property
    def _legend_size(self) -> tuple[float, float]:
        if not (self.pack.legends and self.pack.legends.bottom):
            return (0, 0)

        bbox = bbox_in_figure_space(
            self.pack.legends.bottom.box, self.pack.figure, self.pack.renderer
        )
        return bbox.width, bbox.height

    def edge(self, item: str) -> float:
        """
        Distance w.r.t figure height from the bottom edge of the figure
        """
        return self.sum_upto(item)


@dataclass
class EdgeSpaces:
    """
    Space for components along the edges of the panels
    """

    pack: LayoutPack

    def __post_init__(self):
        self.l = left_spaces(self.pack)
        self.r = right_spaces(self.pack)
        self.t = top_spaces(self.pack)
        self.b = bottom_spaces(self.pack)

    @property
    def left(self):
        """
        Left of the panels in figure space
        """
        return self.l.total

    @property
    def right(self):
        """
        Right of the panels in figure space
        """
        return 1 - self.r.total

    @property
    def top(self):
        """
        Top of the panels in figure space
        """
        return 1 - self.t.total

    @property
    def bottom(self):
        """
        Bottom of the panels in figure space
        """
        return self.b.total


def calculate_panel_spacing(
    pack: LayoutPack, spaces: EdgeSpaces
) -> WHSpaceParts:
    """
    Spacing between the panels (wspace & hspace)

    Both spaces are calculated from a fraction of the width.
    This ensures that the same fraction gives equals space
    in both directions.
    """
    if isinstance(pack.facet, facet_wrap):
        return _calculate_panel_spacing_facet_wrap(pack, spaces)
    elif isinstance(pack.facet, facet_grid):
        return _calculate_panel_spacing_facet_grid(pack, spaces)
    elif isinstance(pack.facet, facet_null):
        return _calculate_panel_spacing_facet_null(pack, spaces)
    return WHSpaceParts(0, 0, 0, 0, 0, 0, 0, 0)


def _calculate_panel_spacing_facet_grid(
    pack: LayoutPack, spaces: EdgeSpaces
) -> WHSpaceParts:
    """
    Calculate spacing parts for facet_grid
    """
    pack.facet = cast(facet_grid, pack.facet)
    theme = pack.theme

    ncol = pack.facet.ncol
    nrow = pack.facet.nrow

    W, H = theme.getp("figure_size")

    # Both spacings are specified as fractions of the figure width
    # Multiply the vertical by (W/H) so that the gullies along both
    # directions are equally spaced.
    sw = theme.getp("panel_spacing_x")
    sh = theme.getp("panel_spacing_y") * W / H

    # width and height of axes as fraction of figure width & height
    w = ((spaces.right - spaces.left) - sw * (ncol - 1)) / ncol
    h = ((spaces.top - spaces.bottom) - sh * (nrow - 1)) / nrow

    # Spacing as fraction of axes width & height
    wspace = sw / w
    hspace = sh / h

    return WHSpaceParts(W, H, w, h, sw, sh, wspace, hspace)


def _calculate_panel_spacing_facet_wrap(
    pack: LayoutPack, spaces: EdgeSpaces
) -> WHSpaceParts:
    """
    Calculate spacing parts for facet_wrap
    """
    pack.facet = cast(facet_wrap, pack.facet)
    theme = pack.theme

    ncol = pack.facet.ncol
    nrow = pack.facet.nrow

    W, H = theme.getp("figure_size")

    # Both spacings are specified as fractions of the figure width
    sw = theme.getp("panel_spacing_x")
    sh = theme.getp("panel_spacing_y") * W / H

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
        sh += spaces.t.strip_text_x_height_top * (1 + strip_align_x)

    if pack.facet.free["x"]:
        sh += pack.axis_text_x_max_height("all")
        sh += pack.axis_ticks_x_max_height("all")
    if pack.facet.free["y"]:
        sw += pack.axis_text_y_max_width("all")
        sw += pack.axis_ticks_y_max_width("all")

    # width and height of axes as fraction of figure width & height
    w = ((spaces.right - spaces.left) - sw * (ncol - 1)) / ncol
    h = ((spaces.top - spaces.bottom) - sh * (nrow - 1)) / nrow

    # Spacing as fraction of axes width & height
    wspace = sw / w
    hspace = sh / h

    return WHSpaceParts(W, H, w, h, sw, sh, wspace, hspace)


def _calculate_panel_spacing_facet_null(
    pack: LayoutPack, spaces: EdgeSpaces
) -> WHSpaceParts:
    """
    Calculate spacing parts for facet_null
    """
    W, H = pack.theme.getp("figure_size")
    w = spaces.right - spaces.left
    h = spaces.top - spaces.bottom
    return WHSpaceParts(W, H, w, h, 0, 0, 0, 0)
