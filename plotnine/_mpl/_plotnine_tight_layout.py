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

import typing
from copy import deepcopy
from dataclasses import dataclass

from matplotlib.offsetbox import AnchoredOffsetbox

from ._plot_side_space import LRTBSpaces, WHSpaceParts, calculate_panel_spacing

if typing.TYPE_CHECKING:
    from typing import Literal, TypeAlias

    from plotnine.typing import (
        Facet,
        Figure,
        LegendPosition,
        Text,
    )

    from .layout_engine import LayoutPack

    AxesLocation: TypeAlias = Literal[
        "all", "first_row", "last_row", "first_col", "last_col"
    ]


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
class TightParams:
    """
    All parameters computed for the plotnine tight layout engine
    """

    sides: LRTBSpaces
    gullies: WHSpaceParts

    def __post_init__(self):
        self.grid = GridSpecParams(
            left=self.sides.left,
            right=self.sides.right,
            top=self.sides.top,
            bottom=self.sides.bottom,
            wspace=self.gullies.wspace,
            hspace=self.gullies.hspace,
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
        sides = params.sides
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
        sides.t.plot_margin += dh
        sides.b.plot_margin += dh
        return params

    def _reduce_width(
        self, facet: Facet, ratio: float, parts: WHSpaceParts
    ) -> TightParams:
        """
        Reduce the width of axes to get the aspect ratio
        """
        params = deepcopy(self)
        sides = params.sides
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
        sides.l.plot_margin += dw
        sides.r.plot_margin += dw
        return params


def get_plotnine_tight_layout(pack: LayoutPack) -> TightParams:
    """
    Compute tight layout parameters
    """
    sides = LRTBSpaces(pack)
    gullies = calculate_panel_spacing(pack, sides)
    tight_params = TightParams(sides, gullies)
    ratio = pack.facet._aspect_ratio()
    if ratio is not None:
        tight_params = tight_params.to_aspect_ratio(pack.facet, ratio, gullies)
    return tight_params


def set_figure_artist_positions(
    pack: LayoutPack,
    tparams: TightParams,
):
    """
    Set the x,y position of the artists around the panels
    """
    theme = pack.theme
    sides = tparams.sides
    grid = tparams.grid

    if pack.plot_title:
        ha = theme.getp(("plot_title", "ha"))
        pack.plot_title.set_y(sides.t.edge("plot_title"))
        horizonally_align_text_with_panels(pack.plot_title, grid, ha)

    if pack.plot_subtitle:
        ha = theme.getp(("plot_subtitle", "ha"))
        pack.plot_subtitle.set_y(sides.t.edge("plot_subtitle"))
        horizonally_align_text_with_panels(pack.plot_subtitle, grid, ha)

    if pack.plot_caption:
        ha = theme.getp(("plot_caption", "ha"), "right")
        pack.plot_caption.set_y(sides.b.edge("plot_caption"))
        horizonally_align_text_with_panels(pack.plot_caption, grid, ha)

    if pack.axis_title_x:
        ha = theme.getp(("axis_title_x", "ha"), "center")
        pack.axis_title_x.set_y(sides.b.edge("axis_title_x"))
        horizonally_align_text_with_panels(pack.axis_title_x, grid, ha)

    if pack.axis_title_y:
        va = theme.getp(("axis_title_y", "va"), "center")
        pack.axis_title_y.set_x(sides.l.edge("axis_title_y"))
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
    sides = tparams.sides

    if position in ("right", "left"):
        y = (grid.top + grid.bottom) / 2
        if position == "left":
            x = sides.l.edge("legend")
            loc = "center left"
        else:
            x = sides.r.edge("legend")
            loc = "center right"
    elif position in ("top", "bottom"):
        x = (grid.right + grid.left) / 2
        if position == "top":
            y = sides.t.edge("legend")
            loc = "upper center"
        else:
            y = sides.b.edge("legend")
            loc = "lower center"
    else:
        x, y = position
        loc = "center"

    anchor_point = (x, y)
    legend.loc = AnchoredOffsetbox.codes[loc]
    legend.set_bbox_to_anchor(anchor_point, fig.transFigure)  # type: ignore
