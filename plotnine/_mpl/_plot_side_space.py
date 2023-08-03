"""
Routines to adjust subplot params so that subplots are
nicely fit in the figure. In doing so, only axis labels, tick labels, axes
titles and offsetboxes that are anchored to axes are currently considered.

Internally, this module assumes that the margins (left margin, etc.) which are
differences between ``Axes.get_tightbbox`` and ``Axes.bbox`` are independent of
Axes position. This may fail if ``Axes.adjustable`` is ``datalim`` as well as
such cases as when left or right margin are affected by xlabel.
"""
from __future__ import annotations

import typing
from abc import ABC
from dataclasses import dataclass, fields
from itertools import chain

from matplotlib._tight_layout import get_subplotspec_list

from ..facets import facet_grid, facet_null, facet_wrap
from .patches import SFancyBboxPatch
from .utils import bbox_in_figure_space, tight_bbox_in_figure_space

if typing.TYPE_CHECKING:
    from dataclasses import Field
    from typing import (
        Generator,
        Iterator,
        Literal,
        Sequence,
        TypeAlias,
    )

    from plotnine.typing import Artist, Axes, Text, XTick, YTick

    from .layout_engine import LayoutPack

    AxesLocation: TypeAlias = Literal[
        "all", "first_row", "last_row", "first_col", "last_col"
    ]

# Note
# Margins around the plot are specfied in figure coordinates
# We interprete that value to be a fraction of the width. So along
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


@dataclass
class _side_spaces(ABC):
    """
    Base class to for spaces

    A *_space class should track the size taken up by all the objects that
    may fall on that side of the panel. The same name may appear in multiple
    side classes (e.g. legend), but atmost only one of those parameters will
    have a non-zero value.
    """

    pack: LayoutPack

    def __post_init__(self):
        self._calculate()

    def _calculate(self):
        """
        Calculate the space taken up by each artist
        """
        ...

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
    axis_ylabels: float = 0
    axis_yticks: float = 0

    def _calculate(self):
        _property = self.pack.theme.themeables.property
        pack = self.pack

        self.plot_margin = _property("plot_margin_left")
        if pack.legend and pack.legend_position == "left":
            self.legend += bbox_in_figure_space(
                pack.legend, pack.figure, pack.renderer
            ).width
            self.legend_box_spacing = _property("legend_box_spacing")

        if pack.axis_title_y:
            self.axis_title_y_margin_right = _property(
                "axis_title_y", "margin"
            ).get_as("r", "fig")
            self.axis_title_y = bbox_in_figure_space(
                pack.axis_title_y, pack.figure, pack.renderer
            ).width

        self.axis_ylabels = max_ylabels_width(pack, "first_col")
        self.axis_yticks = max_yticks_width(pack, "first_col")

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
    right_strip_width: float = 0

    def _calculate(self):
        pack = self.pack
        _property = self.pack.theme.themeables.property

        self.plot_margin = _property("plot_margin_right")
        if pack.legend and pack.legend_position == "right":
            self.legend = bbox_in_figure_space(
                pack.legend, pack.figure, pack.renderer
            ).width
            self.legend_box_spacing = _property("legend_box_spacing")

        right_strips = get_right_strip_boxpatches_in_last_col(pack.axs)
        self.right_strip_width = max_width(pack, right_strips)

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
    top_strip_height: float = 0

    def _calculate(self):
        pack = self.pack
        _property = self.pack.theme.themeables.property
        W, H = _property("figure_size")
        F = W / H

        self.plot_margin = _property("plot_margin_top")
        if pack.plot_title:
            self.plot_title = bbox_in_figure_space(
                pack.plot_title, pack.figure, pack.renderer
            ).height
            self.plot_title_margin_bottom = (
                _property("plot_title", "margin").get_as("b", "fig") * F
            )

        if pack.plot_subtitle:
            self.plot_subtitle = bbox_in_figure_space(
                pack.plot_subtitle, pack.figure, pack.renderer
            ).height
            self.plot_subtitle_margin_bottom = (
                _property("plot_subtitle", "margin").get_as("b", "fig") * F
            )

        if pack.legend and pack.legend_position == "top":
            self.legend = bbox_in_figure_space(
                pack.legend, pack.figure, pack.renderer
            ).height
            self.legend_box_spacing = _property("legend_box_spacing") * F

        top_strips = get_top_strip_boxpatches_in_first_row(pack.axs)
        self.top_strip_height = max_height(pack, top_strips)

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
    axis_xlabels: float = 0
    axis_xticks: float = 0

    def edge(self, item: str) -> float:
        """
        Distance w.r.t figure height from the bottom edge of the figure
        """
        return self.sum_upto(item)

    def _calculate(self):
        pack = self.pack
        _property = self.pack.theme.themeables.property
        W, H = _property("figure_size")
        F = W / H

        self.plot_margin = _property("plot_margin_bottom") * F

        if pack.plot_caption:
            self.plot_caption = bbox_in_figure_space(
                pack.plot_caption, pack.figure, pack.renderer
            ).height
            self.plot_caption_margin_top = (
                _property("plot_caption", "margin").get_as("t", "fig") * F
            )

        if pack.legend and pack.legend_position == "bottom":
            self.legend = bbox_in_figure_space(
                pack.legend, pack.figure, pack.renderer
            ).height
            self.legend_box_spacing = _property("legend_box_spacing") * F

        if pack.axis_title_x:
            self.axis_title_x = bbox_in_figure_space(
                pack.axis_title_x, pack.figure, pack.renderer
            ).height
            self.axis_title_x_margin_top = (
                _property("axis_title_x", "margin").get_as("t", "fig") * F
            )

        # Account for the space consumed by the axis
        self.axis_xticks = max_xticks_height(pack, "last_row")
        self.axis_xlabels = max_xlabels_height(pack, "last_row")


class LRTBSpaces:
    """
    Space for components in all directions around the panels
    """

    l: left_spaces
    r: right_spaces
    t: top_spaces
    b: bottom_spaces

    def __init__(self, pack):
        self.l = left_spaces(pack)
        self.r = right_spaces(pack)
        self.t = top_spaces(pack)
        self.b = bottom_spaces(pack)

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
    pack: LayoutPack, spaces: LRTBSpaces
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
    pack: LayoutPack, spaces: LRTBSpaces
) -> WHSpaceParts:
    """
    Calculate spacing parts for facet_grid
    """
    _property = pack.theme.themeables.property

    ncol = pack.facet.ncol
    nrow = pack.facet.nrow

    W, H = _property("figure_size")

    # Both spacings are specified as fractions of the figure width
    sw = _property("panel_spacing_x")
    sh = _property("panel_spacing_y") * W / H

    # width and height of axes as fraction of figure width & heigt
    w = ((spaces.right - spaces.left) - sw * (ncol - 1)) / ncol
    h = ((spaces.top - spaces.bottom) - sh * (nrow - 1)) / nrow

    # Spacing as fraction of axes width & height
    wspace = sw / w
    hspace = sh / h

    return WHSpaceParts(W, H, w, h, sw, sh, wspace, hspace)


def _calculate_panel_spacing_facet_wrap(
    pack: LayoutPack, spaces: LRTBSpaces
) -> WHSpaceParts:
    """
    Calculate spacing parts for facet_wrap
    """
    _property = pack.theme.themeables.property

    ncol = pack.facet.ncol
    nrow = pack.facet.nrow

    W, H = _property("figure_size")

    # Both spacings are specified as fractions of the figure width
    sw = _property("panel_spacing_x")
    sh = _property("panel_spacing_y") * W / H

    # A fraction of the strip height
    # Effectively slides the strip
    #   +ve: Away from the panel
    #    0:  Top of the panel
    #   -ve: Into the panel
    # Where values <= -1, put the strip completly into
    # the panel. We do not worry about larger -ves.
    strip_align_x = _property("strip_align_x")

    # Only interested in the proportion of the strip that
    # does not overlap with the panel
    if strip_align_x > -1:
        sh += spaces.t.top_strip_height * (1 + strip_align_x)

    if isinstance(pack.facet, facet_wrap):
        if pack.facet.free["x"]:
            sh += max_xlabels_height(pack)
            sh += max_xticks_height(pack)
        if pack.facet.free["y"]:
            sw += max_ylabels_width(pack)
            sw += max_yticks_width(pack)

    # width and height of axes as fraction of figure width & heigt
    w = ((spaces.right - spaces.left) - sw * (ncol - 1)) / ncol
    h = ((spaces.top - spaces.bottom) - sh * (nrow - 1)) / nrow

    # Spacing as fraction of axes width & height
    wspace = sw / w
    hspace = sh / h

    return WHSpaceParts(W, H, w, h, sw, sh, wspace, hspace)


def _calculate_panel_spacing_facet_null(
    pack: LayoutPack, spaces: LRTBSpaces
) -> WHSpaceParts:
    """
    Calculate spacing parts for facet_null
    """
    _property = pack.theme.themeables.property
    W, H = pack.theme.themeables.property("figure_size")
    w = spaces.right - spaces.left
    h = spaces.top - spaces.bottom
    return WHSpaceParts(W, H, w, h, 0, 0, 0, 0)


def filter_axes(axs, get: AxesLocation = "all"):
    """
    Return subset of axes
    """
    if get == "all":
        return axs

    # e.g. is_first_row, is_last_row, ..
    pred_method = f"is_{get}"
    return [
        ax
        for spec, ax in zip(get_subplotspec_list(axs), axs)
        if getattr(spec, pred_method)()
    ]


def is_top_strip_boxpatch(artist: Artist) -> bool:
    """
    Return True if artist is a patch/background of the top strip of a facet
    """
    if isinstance(artist, SFancyBboxPatch):
        return artist.position == "top"
    return False


def is_right_strip_boxpatch(artist: Artist) -> bool:
    """
    Return True if artist is a patch/background of the right strip of a facet
    """
    if isinstance(artist, SFancyBboxPatch):
        return artist.position == "right"
    return False


def get_top_strip_boxpatches_in_first_row(
    axs: list[Axes],
) -> list[SFancyBboxPatch]:
    """
    Return all box patches on the top of the first row
    """
    return [
        child
        for ax in filter_axes(axs, "first_row")
        for child in ax.get_children()
        if is_top_strip_boxpatch(child)
    ]


def get_right_strip_boxpatches_in_last_col(
    axs: list[Axes],
) -> list[SFancyBboxPatch]:
    """
    Return all box patches on the right of the last column
    """
    return [
        child
        for ax in filter_axes(axs, "last_col")
        for child in ax.get_children()
        if is_right_strip_boxpatch(child)
    ]


def max_width(pack: LayoutPack, artists: Sequence[Artist]) -> float:
    """
    Return the maximum width of list of artists
    """
    widths = [
        bbox_in_figure_space(a, pack.figure, pack.renderer).width
        for a in artists
    ]
    return max(widths) if len(widths) else 0


def max_height(pack: LayoutPack, artists: Sequence[Artist]) -> float:
    """
    Return the maximum height of list of artists
    """
    heights = [
        bbox_in_figure_space(a, pack.figure, pack.renderer).height
        for a in artists
    ]
    return max(heights) if len(heights) else 0


def get_xaxis_ticks(pack: LayoutPack, ax: Axes) -> Iterator[XTick]:
    """
    Return all XTicks that will be shown
    """
    is_blank = pack.theme.themeables.is_blank
    major, minor = [], []

    if not is_blank("axis_ticks_major_x"):
        major = ax.xaxis.get_major_ticks()

    if not is_blank("axis_ticks_minor_x"):
        minor = ax.xaxis.get_minor_ticks()

    return chain(major, minor)


def get_yaxis_ticks(pack: LayoutPack, ax: Axes) -> Iterator[YTick]:
    """
    Return all YTicks that will be shown
    """
    is_blank = pack.theme.themeables.is_blank
    major, minor = [], []

    if not is_blank("axis_ticks_major_y"):
        major = ax.yaxis.get_major_ticks()

    if not is_blank("axis_ticks_minor_y"):
        minor = ax.yaxis.get_minor_ticks()

    return chain(major, minor)


def get_xaxis_labels(pack: LayoutPack, ax: Axes) -> Iterator[Text]:
    """
    Return all x-axis labels that will be shown
    """
    is_blank = pack.theme.themeables.is_blank
    major, minor = [], []

    if not is_blank("axis_x_text"):
        major = ax.xaxis.get_major_ticks()

    if not is_blank("axis_x_text"):
        minor = ax.xaxis.get_minor_ticks()

    return (tick.label1 for tick in chain(major, minor))


def get_yaxis_labels(pack: LayoutPack, ax: Axes) -> Iterator[Text]:
    """
    Return all y-axis labels that will be shown
    """
    is_blank = pack.theme.themeables.is_blank
    major, minor = [], []

    if not is_blank("axis_y_text"):
        major = ax.yaxis.get_major_ticks()

    if not is_blank("axis_y_text"):
        minor = ax.yaxis.get_minor_ticks()

    return (tick.label1 for tick in chain(major, minor))


def max_xticks_height(
    pack: LayoutPack,
    axes_loc: AxesLocation = "all",
) -> float:
    """
    Return maximum height[inches] of x ticks
    """
    H = pack.figure.get_figheight()
    heights = [
        tight_bbox_in_figure_space(
            tick.tick1line, pack.figure, pack.renderer
        ).height
        + tick.get_pad() / (72 * H)
        for ax in filter_axes(pack.axs, axes_loc)
        for tick in get_xaxis_ticks(pack, ax)
    ]
    return max(heights) if len(heights) else 0


def max_xlabels_height(
    pack: LayoutPack,
    axes_loc: AxesLocation = "all",
) -> float:
    """
    Return maximum height[inches] of x tick labels
    """
    heights = [
        tight_bbox_in_figure_space(label, pack.figure, pack.renderer).height
        for ax in filter_axes(pack.axs, axes_loc)
        for label in get_xaxis_labels(pack, ax)
    ]
    return max(heights) if len(heights) else 0


def max_yticks_width(
    pack: LayoutPack,
    axes_loc: AxesLocation = "all",
) -> float:
    """
    Return maximum width[inches] of a y ticks
    """
    W = pack.figure.get_figwidth()
    widths = [
        tight_bbox_in_figure_space(
            tick.tick1line, pack.figure, pack.renderer
        ).width
        + tick.get_pad() / (72 * W)
        for ax in filter_axes(pack.axs, axes_loc)
        for tick in get_yaxis_ticks(pack, ax)
    ]
    return max(widths) if len(widths) else 0


def max_ylabels_width(
    pack: LayoutPack,
    axes_loc: AxesLocation = "all",
) -> float:
    """
    Return maximum width[inches] of a y tick labels
    """
    widths = [
        tight_bbox_in_figure_space(label, pack.figure, pack.renderer).width
        for ax in filter_axes(pack.axs, axes_loc)
        for label in get_yaxis_labels(pack, ax)
    ]
    return max(widths) if len(widths) else 0
