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
from dataclasses import dataclass

from ._plot_side_space import LRTBSpaces, WHSpaceParts, calculate_panel_spacing
from .utils import bbox_in_figure_space, get_transPanels

if typing.TYPE_CHECKING:
    from typing import Literal, TypeAlias

    from matplotlib.figure import Figure
    from matplotlib.text import Text
    from matplotlib.transforms import Transform

    from plotnine._mpl.offsetbox import FlexibleAnchoredOffsetbox
    from plotnine.facets.facet import facet
    from plotnine.iapi import legend_artists

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

    facet: facet
    sides: LRTBSpaces
    gullies: WHSpaceParts

    def __post_init__(self):
        self.params = GridSpecParams(
            left=self.sides.left,
            right=self.sides.right,
            top=self.sides.top,
            bottom=self.sides.bottom,
            wspace=self.gullies.wspace,
            hspace=self.gullies.hspace,
        )

        if (ratio := self.facet._aspect_ratio()) is not None:
            current_ratio = self.gullies.aspect_ratio
            if ratio > current_ratio:
                # Increase aspect ratio, taller panels
                self._reduce_width(ratio)
            elif ratio < current_ratio:
                # Increase aspect ratio, wider panels
                self._reduce_height(ratio)

    def _reduce_height(self, ratio: float):
        """
        Reduce the height of axes to get the aspect ratio
        """
        parts = self.gullies

        # New height w.r.t figure height
        h1 = ratio * parts.w * (parts.W / parts.H)

        # Half of the total vertical reduction w.r.t figure height
        dh = (parts.h - h1) * self.facet.nrow / 2

        # Reduce plot area height
        self.params.top -= dh
        self.params.bottom += dh
        self.params.hspace = parts.sh / h1

        # Add more vertical plot margin
        self.sides.t.plot_margin += dh
        self.sides.b.plot_margin += dh

    def _reduce_width(self, ratio: float):
        """
        Reduce the width of axes to get the aspect ratio
        """
        parts = self.gullies

        # New width w.r.t figure width
        w1 = (parts.h * parts.H) / (ratio * parts.W)

        # Half of the total horizontal reduction w.r.t figure width
        dw = (parts.w - w1) * self.facet.ncol / 2

        # Reduce width
        self.params.left += dw
        self.params.right -= dw
        self.params.wspace = parts.sw / w1

        # Add more horizontal margin
        self.sides.l.plot_margin += dw
        self.sides.r.plot_margin += dw


def get_plotnine_tight_layout(pack: LayoutPack) -> TightParams:
    """
    Compute tight layout parameters
    """
    sides = LRTBSpaces(pack)
    gullies = calculate_panel_spacing(pack, sides)
    tight_params = TightParams(pack.facet, sides, gullies)
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
    params = tparams.params

    if pack.plot_title:
        ha = theme.getp(("plot_title", "ha"))
        pack.plot_title.set_y(sides.t.edge("plot_title"))
        horizontally_align_text_with_panels(pack.plot_title, params, ha, pack)

    if pack.plot_subtitle:
        ha = theme.getp(("plot_subtitle", "ha"))
        pack.plot_subtitle.set_y(sides.t.edge("plot_subtitle"))
        horizontally_align_text_with_panels(
            pack.plot_subtitle, params, ha, pack
        )

    if pack.plot_caption:
        ha = theme.getp(("plot_caption", "ha"), "right")
        pack.plot_caption.set_y(sides.b.edge("plot_caption"))
        horizontally_align_text_with_panels(
            pack.plot_caption, params, ha, pack
        )

    if pack.axis_title_x:
        ha = theme.getp(("axis_title_x", "ha"), "center")
        pack.axis_title_x.set_y(sides.b.edge("axis_title_x"))
        horizontally_align_text_with_panels(
            pack.axis_title_x, params, ha, pack
        )

    if pack.axis_title_y:
        va = theme.getp(("axis_title_y", "va"), "center")
        pack.axis_title_y.set_x(sides.l.edge("axis_title_y"))
        vertically_align_text_with_panels(pack.axis_title_y, params, va, pack)

    if pack.legends:
        set_legends_position(pack.legends, tparams, pack.figure)


def horizontally_align_text_with_panels(
    text: Text, params: GridSpecParams, ha: str | float, pack: LayoutPack
):
    """
    Horizontal justification

    Reinterpret horizontal alignment to be justification about the panels.
    """
    if isinstance(ha, str):
        lookup = {
            "left": 0.0,
            "center": 0.5,
            "right": 1.0,
        }
        f = lookup[ha]
    else:
        f = ha

    box = bbox_in_figure_space(text, pack.figure, pack.renderer)
    x = params.left * (1 - f) + (params.right - box.width) * f
    text.set_x(x)
    text.set_horizontalalignment("left")


def vertically_align_text_with_panels(
    text: Text, params: GridSpecParams, va: str | float, pack: LayoutPack
):
    """
    Vertical justification

    Reinterpret vertical alignment to be justification about the panels.
    """
    if isinstance(va, str):
        lookup = {
            "top": 1.0,
            "center": 0.5,
            "baseline": 0.5,
            "center_baseline": 0.5,
            "bottom": 0.0,
        }
        f = lookup[va]
    else:
        f = va

    box = bbox_in_figure_space(text, pack.figure, pack.renderer)
    y = params.bottom * (1 - f) + (params.top - box.height) * f
    text.set_y(y)
    text.set_verticalalignment("bottom")


def set_legends_position(
    legends: legend_artists,
    tparams: TightParams,
    fig: Figure,
):
    """
    Place legend on the figure and justify is a required
    """

    def set_position(
        aob: FlexibleAnchoredOffsetbox,
        anchor_point: tuple[float, float],
        xy_loc: tuple[float, float],
        transform: Transform = fig.transFigure,
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

    sides = tparams.sides
    params = fig.subplotpars

    if legends.right:
        j = legends.right.justification
        y = params.bottom * (1 - j) + (params.top - sides.r._legend_height) * j
        x = sides.r.edge("legend")
        set_position(legends.right.box, (x, y), (1, 0))

    if legends.left:
        j = legends.left.justification
        y = params.bottom * (1 - j) + (params.top - sides.l._legend_height) * j
        x = sides.l.edge("legend")
        set_position(legends.left.box, (x, y), (0, 0))

    if legends.top:
        j = legends.top.justification
        x = params.left * (1 - j) + (params.right - sides.t._legend_width) * j
        y = sides.t.edge("legend")
        set_position(legends.top.box, (x, y), (0, 1))

    if legends.bottom:
        j = legends.bottom.justification
        x = params.left * (1 - j) + (params.right - sides.b._legend_width) * j
        y = sides.b.edge("legend")
        set_position(legends.bottom.box, (x, y), (0, 0))

    # Inside legends are placed using the panels coordinate system
    if legends.inside:
        transPanels = get_transPanels(fig)
        for l in legends.inside:
            set_position(l.box, l.position, l.justification, transPanels)
