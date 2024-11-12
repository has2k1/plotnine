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

from typing import TYPE_CHECKING

from ..utils import get_transPanels
from ._plot_side_space import GridSpecParams, LayoutSpaces

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.text import Text
    from matplotlib.transforms import Transform

    from plotnine._mpl.offsetbox import FlexibleAnchoredOffsetbox
    from plotnine.iapi import legend_artists

    from ._layout_pack import LayoutPack


def compute_layout(pack: LayoutPack) -> LayoutSpaces:
    """
    Compute tight layout parameters
    """
    return LayoutSpaces(pack)


def adjust_figure_artists(pack: LayoutPack, spaces: LayoutSpaces):
    """
    Set the x,y position of the artists around the panels
    """
    theme = pack.theme
    params = spaces.gsparams

    if pack.plot_title:
        ha = theme.getp(("plot_title", "ha"))
        pack.plot_title.set_y(spaces.t.edge("plot_title"))
        horizontally_align_text_with_panels(pack.plot_title, params, ha, pack)

    if pack.plot_subtitle:
        ha = theme.getp(("plot_subtitle", "ha"))
        pack.plot_subtitle.set_y(spaces.t.edge("plot_subtitle"))
        horizontally_align_text_with_panels(
            pack.plot_subtitle, params, ha, pack
        )

    if pack.plot_caption:
        ha = theme.getp(("plot_caption", "ha"), "right")
        pack.plot_caption.set_y(spaces.b.edge("plot_caption"))
        horizontally_align_text_with_panels(
            pack.plot_caption, params, ha, pack
        )

    if pack.axis_title_x:
        ha = theme.getp(("axis_title_x", "ha"), "center")
        pack.axis_title_x.set_y(spaces.b.edge("axis_title_x"))
        horizontally_align_text_with_panels(
            pack.axis_title_x, params, ha, pack
        )

    if pack.axis_title_y:
        va = theme.getp(("axis_title_y", "va"), "center")
        pack.axis_title_y.set_x(spaces.l.edge("axis_title_y"))
        vertically_align_text_with_panels(pack.axis_title_y, params, va, pack)

    if pack.legends:
        set_legends_position(pack.legends, spaces, pack.figure)


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

    width = pack.calc.width(text)
    x = params.left * (1 - f) + (params.right - width) * f
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

    height = pack.calc.height(text)
    y = params.bottom * (1 - f) + (params.top - height) * f
    text.set_y(y)
    text.set_verticalalignment("bottom")


def set_legends_position(
    legends: legend_artists,
    spaces: LayoutSpaces,
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

    params = fig.subplotpars
    if legends.right:
        j = legends.right.justification
        y = (
            params.bottom * (1 - j)
            + (params.top - spaces.r._legend_height) * j
        )
        x = spaces.r.edge("legend")
        set_position(legends.right.box, (x, y), (1, 0))

    if legends.left:
        j = legends.left.justification
        y = (
            params.bottom * (1 - j)
            + (params.top - spaces.l._legend_height) * j
        )
        x = spaces.l.edge("legend")
        set_position(legends.left.box, (x, y), (0, 0))

    if legends.top:
        j = legends.top.justification
        x = params.left * (1 - j) + (params.right - spaces.t._legend_width) * j
        y = spaces.t.edge("legend")
        set_position(legends.top.box, (x, y), (0, 1))

    if legends.bottom:
        j = legends.bottom.justification
        x = params.left * (1 - j) + (params.right - spaces.b._legend_width) * j
        y = spaces.b.edge("legend")
        set_position(legends.bottom.box, (x, y), (0, 0))

    # Inside legends are placed using the panels coordinate system
    if legends.inside:
        transPanels = get_transPanels(fig)
        for l in legends.inside:
            set_position(l.box, l.position, l.justification, transPanels)
