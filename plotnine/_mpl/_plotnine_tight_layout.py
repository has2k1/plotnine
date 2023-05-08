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
from copy import deepcopy
from dataclasses import dataclass, fields
from itertools import chain

from matplotlib._tight_layout import get_subplotspec_list
from matplotlib.offsetbox import AnchoredOffsetbox

from ..facets import facet_grid, facet_null, facet_wrap
from .patches import SFancyBboxPatch
from .utils import bbox_in_figure_space, tight_bbox_in_figure_space

if typing.TYPE_CHECKING:
    from dataclasses import Field
    from typing import Generator, Iterator, Literal, TypeAlias

    from plotnine.typing import (
        Artist,
        Axes,
        Facet,
        Figure,
        LegendPosition,
        Text,
        XTick,
        YTick,
    )

    from .layout_engine import LayoutPack

    AxesLocation: TypeAlias = Literal[
        "all", "first_row", "last_row", "first_col", "last_col"
    ]

# Note
# Margin around the plot are specfied in figure coordinates
# We interprete that value to be a fraction of the width. So along
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
class _side_spaces:
    """
    Base class to for spaces

    A *_space class should track the size taken up by all the objects that
    may fall on that side of the panel. The same name may appear in multiple
    side classes (e.g. legend), but atmost only one of those parameters will
    have a non-zero value.
    """

    @property
    def total(self) -> float:
        """
        Total space
        """
        return sum(getattr(self, f.name) for f in fields(self))

    def sum_upto(self, item: str) -> float:
        """
        Sum of space upto but not including item

        Sums starting at the edge of the figure i.e. the "plot_margin".
        """

        def _fields_upto(x: _side_spaces) -> Generator[Field, None, None]:
            for f in fields(x):
                if f.name == item:
                    break
                yield f

        return sum(getattr(self, f.name) for f in _fields_upto(self))


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
    axis_y: float = 0

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
    axis_x: float = 0

    def edge(self, item: str) -> float:
        """
        Distance w.r.t figure height from the bottom edge of the figure
        """
        return self.sum_upto(item)


@dataclass
class LRTBSpaces:
    """
    Space for components in all directions around the panels
    """

    l: left_spaces
    r: right_spaces
    t: top_spaces
    b: bottom_spaces

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
class TightParams:
    """
    All parameters computed for the plotnine tight layout engine
    """

    spaces: LRTBSpaces
    grid: GridSpecParams

    def __init__(self, spaces: LRTBSpaces, wspace: float, hspace: float):
        self.spaces = spaces
        self.grid = GridSpecParams(
            left=spaces.left,
            right=spaces.right,
            top=spaces.top,
            bottom=spaces.bottom,
            wspace=wspace,
            hspace=hspace,
        )

    def to_aspect_ratio(
        self, facet: Facet, ratio: float, parts: WHSpaceParts
    ) -> TightParams:
        """
        Modify TightParams to get a given aspect ratio
        """
        current_ratio = (parts.h * parts.H) / (parts.w * parts.W)
        increase_aspect_ratio = ratio > current_ratio
        if increase_aspect_ratio:  # Taller panel
            return self._reduce_width(facet, ratio, parts)
        else:
            return self._reduce_height(facet, ratio, parts)

    def _reduce_height(
        self, facet: Facet, ratio: float, parts: WHSpaceParts
    ) -> TightParams:
        """
        Reduce the height of axes to get the aspect ratio
        """
        params = deepcopy(self)
        spaces = params.spaces
        grid = params.grid

        # New height w.r.t figure height
        h1 = ratio * parts.w * (parts.W / parts.H)

        # Half of the total vertical reduction w.r.t figure height
        dh = (parts.h - h1) * facet.nrow / 2

        # Reduce plot area height
        grid.top -= dh
        grid.bottom += dh
        grid.hspace = parts.sh / h1

        # Add more vertical plot margin
        spaces.t.plot_margin += dh
        spaces.b.plot_margin += dh
        return params

    def _reduce_width(
        self, facet: Facet, ratio: float, parts: WHSpaceParts
    ) -> TightParams:
        """
        Reduce the width of axes to get the aspect ratio
        """
        params = deepcopy(self)
        spaces = params.spaces
        grid = params.grid

        # New width w.r.t figure width
        w1 = (parts.h * parts.H) / (ratio * parts.W)

        # Half of the total horizontal reduction w.r.t figure width
        dw = (parts.w - w1) * facet.ncol / 2

        # Reduce width
        grid.left += dw
        grid.right -= dw
        grid.wspace = parts.sw / w1

        # Add more horizontal margin
        spaces.l.plot_margin += dw
        spaces.r.plot_margin += dw
        return params


def get_plotnine_tight_layout(pack: LayoutPack) -> TightParams:
    """
    Compute tight layout parameters
    """
    spaces = LRTBSpaces(
        l=calculate_left_spaces(pack),
        r=calculate_right_spaces(pack),
        t=calculate_top_spaces(pack),
        b=calculate_bottom_spaces(pack),
    )
    parts = calculate_panel_spacing(pack, spaces)
    params = TightParams(spaces, parts.wspace, parts.hspace)
    ratio = pack.facet._aspect_ratio()
    if ratio is not None:
        params = params.to_aspect_ratio(pack.facet, ratio, parts)
    return params


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
            sh += get_max_xaxis_height(pack)
        if pack.facet.free["y"]:
            sw += get_max_yaxis_width(pack)

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


def calculate_left_spaces(pack: LayoutPack) -> left_spaces:
    """
    Left margin
    """
    _property = pack.theme.themeables.property
    space = left_spaces(plot_margin=_property("plot_margin"))

    if pack.legend and pack.legend_position == "left":
        space.legend += bbox_in_figure_space(
            pack.legend, pack.figure, pack.renderer
        ).width
        space.legend_box_spacing = _property("legend_box_spacing")

    if pack.axis_title_y:
        space.axis_title_y_margin_right = _property(
            "axis_title_y", "margin"
        ).get_as("r", "fig")
        space.axis_title_y = bbox_in_figure_space(
            pack.axis_title_y, pack.figure, pack.renderer
        ).width

    # Account for the space consumed by the axis even if it comes
    # after the axis text
    space.axis_y = get_max_yaxis_width(pack, "first_col")
    return space


def calculate_right_spaces(pack: LayoutPack) -> right_spaces:
    """
    Calculate Space for artists on the right of the panel
    """
    _property = pack.theme.themeables.property
    space = right_spaces(plot_margin=_property("plot_margin"))

    if pack.legend and pack.legend_position == "right":
        space.legend = bbox_in_figure_space(
            pack.legend, pack.figure, pack.renderer
        ).width
        space.legend_box_spacing = _property("legend_box_spacing")

    space.right_strip_width = get_right_strip_width_in_last_col(pack)
    return space


def calculate_top_spaces(pack: LayoutPack) -> top_spaces:
    """
    Calculate space for artists above the panels
    """
    _property = pack.theme.themeables.property

    W, H = _property("figure_size")
    F = W / H
    space = top_spaces(plot_margin=_property("plot_margin") * F)

    if pack.plot_title:
        space.plot_title = bbox_in_figure_space(
            pack.plot_title, pack.figure, pack.renderer
        ).height
        space.plot_title_margin_bottom = (
            _property("plot_title", "margin").get_as("b", "fig") * F
        )

    if pack.plot_subtitle:
        space.plot_subtitle = bbox_in_figure_space(
            pack.plot_subtitle, pack.figure, pack.renderer
        ).height
        space.plot_subtitle_margin_bottom = (
            _property("plot_subtitle", "margin").get_as("b", "fig") * F
        )

    if pack.legend and pack.legend_position == "top":
        space.legend = bbox_in_figure_space(
            pack.legend, pack.figure, pack.renderer
        ).height
        space.legend_box_spacing = _property("legend_box_spacing") * F

    space.top_strip_height = get_top_strip_height_in_first_row(pack)
    return space


def calculate_bottom_spaces(pack: LayoutPack) -> bottom_spaces:
    """
    Calculate space for the artists below the panels
    """
    _property = pack.theme.themeables.property

    W, H = pack.theme.themeables.property("figure_size")
    F = W / H
    space = bottom_spaces(plot_margin=_property("plot_margin") * F)

    if pack.plot_caption:
        space.plot_caption = bbox_in_figure_space(
            pack.plot_caption, pack.figure, pack.renderer
        ).height
        space.plot_caption_margin_top = (
            _property("plot_caption", "margin").get_as("t", "fig") * F
        )

    if pack.legend and pack.legend_position == "bottom":
        space.legend = bbox_in_figure_space(
            pack.legend, pack.figure, pack.renderer
        ).height
        space.legend_box_spacing = _property("legend_box_spacing") * F

    if pack.axis_title_x:
        space.axis_title_x = bbox_in_figure_space(
            pack.axis_title_x, pack.figure, pack.renderer
        ).height
        space.axis_title_x_margin_top = (
            _property("axis_title_x", "margin").get_as("t", "fig") * F
        )

    # Account for the space consumed by the axis
    space.axis_x = get_max_xaxis_height(pack, "last_row")
    return space


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


def get_top_strip_height_in_first_row(pack: LayoutPack) -> float:
    """
    Return the height of the top strip
    """
    patches = get_top_strip_boxpatches_in_first_row(pack.axs)
    heights = [
        bbox_in_figure_space(patch, pack.figure, pack.renderer).height
        for patch in patches
    ]
    return max(heights) if len(heights) else 0


def get_right_strip_width_in_last_col(pack: LayoutPack) -> float:
    """
    Return the width of the right strip
    """
    patches = get_right_strip_boxpatches_in_last_col(pack.axs)
    widths = [
        bbox_in_figure_space(patch, pack.figure, pack.renderer).width
        for patch in patches
    ]
    return max(widths) if len(widths) else 0


def get_xticks(ax: Axes) -> Iterator[XTick]:
    """
    Return all XTicks
    """
    return chain(ax.xaxis.get_major_ticks(), ax.xaxis.get_minor_ticks())


def get_yticks(ax: Axes) -> Iterator[YTick]:
    """
    Return all YTicks
    """
    return chain(ax.yaxis.get_major_ticks(), ax.yaxis.get_minor_ticks())


def get_max_xaxis_height(
    pack: LayoutPack,
    axes_loc: AxesLocation = "all",
) -> float:
    """
    Return maximum height[inches] of an xaxis
    """
    H = pack.figure.get_figheight()
    # Note: Using the bbox of for axis ignores the ticklines
    heights = [
        tight_bbox_in_figure_space(
            tick.tick1line, pack.figure, pack.renderer
        ).height
        + tick.get_pad() / (72 * H)
        + tight_bbox_in_figure_space(
            tick.label1, pack.figure, pack.renderer
        ).height
        for ax in filter_axes(pack.axs, axes_loc)
        for tick in get_xticks(ax)
    ]
    return max(heights) if len(heights) else 0


def get_max_yaxis_width(
    pack: LayoutPack,
    axes_loc: AxesLocation = "all",
) -> float:
    """
    Return maximum width[inches] of an xaxis
    """
    W = pack.figure.get_figwidth()
    # Note: Using the bbox of for axis ignores the ticklines
    widths = [
        tight_bbox_in_figure_space(
            tick.tick1line, pack.figure, pack.renderer
        ).width
        + tick.get_pad() / (72 * W)
        + tight_bbox_in_figure_space(
            tick.label1, pack.figure, pack.renderer
        ).width
        for ax in filter_axes(pack.axs, axes_loc)
        for tick in get_yticks(ax)
    ]
    return max(widths) if len(widths) else 0


def set_figure_artist_positions(
    pack: LayoutPack,
    tparams: TightParams,
):
    """
    Set the x,y position of the artists around the panels
    """
    _property = pack.theme.themeables.property
    spaces = tparams.spaces
    grid = tparams.grid

    if pack.plot_title:
        try:
            ha = _property("plot_title", "ha")
        except KeyError:
            ha = "center"
        pack.plot_title.set_y(spaces.t.edge("plot_title"))
        horizonally_align_text_with_panels(pack.plot_title, grid, ha)

    if pack.plot_subtitle:
        try:
            ha = _property("plot_subtitle", "ha")
        except KeyError:
            ha = "center"
        pack.plot_subtitle.set_y(spaces.t.edge("plot_subtitle"))
        horizonally_align_text_with_panels(pack.plot_subtitle, grid, ha)

    if pack.plot_caption:
        try:
            ha = _property("plot_caption", "ha")
        except KeyError:
            ha = "right"
        pack.plot_caption.set_y(spaces.b.edge("plot_caption"))
        horizonally_align_text_with_panels(pack.plot_caption, grid, ha)

    if pack.axis_title_x:
        try:
            ha = _property("axis_title_x", "ha")
        except KeyError:
            ha = "center"
        pack.axis_title_x.set_y(spaces.b.edge("axis_title_x"))
        horizonally_align_text_with_panels(pack.axis_title_x, grid, ha)

    if pack.axis_title_y:
        try:
            va = _property("axis_title_y", "va")
        except KeyError:
            va = "center"
        pack.axis_title_y.set_x(spaces.l.edge("axis_title_y"))
        vertically_align_text_with_panels(pack.axis_title_y, grid, va)

    if pack.legend and pack.legend_position:
        set_legend_position(
            pack.legend, pack.legend_position, tparams, pack.figure
        )


def horizonally_align_text_with_panels(
    text: Text, grid: GridSpecParams, ha: str
):
    """
    Horizontal justification

    Reinterpret horizontal alignment to be justification about the panels.
    """
    if ha == "center":
        text.set_x((grid.left + grid.right) / 2)
    elif ha == "left":
        text.set_x(grid.left)
    elif ha == "right":
        text.set_x(grid.right)


def vertically_align_text_with_panels(
    text: Text, grid: GridSpecParams, va: str
):
    """
    Vertical justification

    Reinterpret vertical alignment to be justification about the panels.
    """
    if va == "center":
        text.set_y((grid.top + grid.bottom) / 2)
    elif va == "top":
        text.set_y(grid.top)
    elif va == "bottom":
        text.set_y(grid.bottom)


def set_legend_position(
    legend: AnchoredOffsetbox,
    position: LegendPosition,
    tparams: TightParams,
    fig: Figure,
):
    """
    Place legend and align it centerally with respect to the panels
    """
    grid = tparams.grid
    spaces = tparams.spaces

    if position in ("right", "left"):
        y = (grid.top + grid.bottom) / 2
        if position == "left":
            x = spaces.l.edge("legend")
            loc = "center left"
        else:
            x = spaces.r.edge("legend")
            loc = "center right"
    elif position in ("top", "bottom"):
        x = (grid.right + grid.left) / 2
        if position == "top":
            y = spaces.t.edge("legend")
            loc = "upper center"
        else:
            y = spaces.b.edge("legend")
            loc = "lower center"
    else:
        x, y = position
        loc = "center"

    anchor_point = (x, y)
    legend.loc = AnchoredOffsetbox.codes[loc]
    legend.set_bbox_to_anchor(anchor_point, fig.transFigure)
