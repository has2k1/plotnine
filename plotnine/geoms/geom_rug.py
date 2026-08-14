from __future__ import annotations

from typing import TYPE_CHECKING, cast

import numpy as np

from .._utils import SIZE_FACTOR, make_line_segments, to_rgba
from ..coords import coord_flip
from ..doctools import document
from .geom import geom
from .geom_path import geom_path

if TYPE_CHECKING:
    from typing import Any

    import pandas as pd
    from matplotlib.axes import Axes

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.typing import FloatArray


@document
class geom_rug(geom):
    """
    Marginal rug plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    sides : str, default="bl"
        Sides onto which to draw the marks. Any combination
        chosen from the characters `"btlr"`, for *bottom*, *top*,
        *left* or *right* side marks.
    length: float, default=0.03
        length of marks in fractions of horizontal/vertical panel size.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "black",
        "size": 0.5,
        "linetype": "solid",
    }
    DEFAULT_PARAMS = {"sides": "bl", "length": 0.03}

    draw_legend = staticmethod(geom_path.draw_legend)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        data = coord.transform(data, panel_params)
        sides = params["sides"]

        # coord_flip does not flip the side(s) on which the rugs
        # are plotted. We do the flipping here
        if isinstance(coord, coord_flip):
            sides = sides.translate(str.maketrans("tblr", "rlbt"))

        stroke_rugs(data, panel_params, ax, params, sides)


def stroke_rugs(
    data: pd.DataFrame,
    panel_params: panel_view,
    ax: Axes,
    params: dict[str, Any],
    sides: str,
) -> None:
    """
    Draw rug marks in panel coordinates

    Parameters
    ----------
    data :
        Rug-mark aesthetics. Include `x`, `y`, or both; position values
        must use panel coordinates.
    panel_params :
        Panel ranges used to determine the mark endpoints.
    ax :
        Axes to draw on.
    params :
        Geom and stat parameters that control line appearance.
    sides :
        Panel sides to mark, using any combination of `b`, `t`, `l`, and
        `r`. Resolve any axis flip before calling.
    """
    from matplotlib.collections import LineCollection

    linewidth = data["size"] * SIZE_FACTOR

    has_x = "x" in data.columns
    has_y = "y" in data.columns

    if not (has_x or has_y):
        return

    n = len(data)
    rugs = []
    xmin, xmax = panel_params.x.range
    ymin, ymax = panel_params.y.range
    xheight = (xmax - xmin) * params["length"]
    yheight = (ymax - ymin) * params["length"]

    if has_x:
        x = cast("FloatArray", np.repeat(data["x"].to_numpy(), 2))

        if "b" in sides:
            y = np.tile([ymin, ymin + yheight], n)
            rugs.extend(make_line_segments(x, y, ispath=False))

        if "t" in sides:
            y = np.tile([ymax - yheight, ymax], n)
            rugs.extend(make_line_segments(x, y, ispath=False))

    if has_y:
        y = cast("FloatArray", np.repeat(data["y"].to_numpy(), 2))

        if "l" in sides:
            x = np.tile([xmin, xmin + xheight], n)
            rugs.extend(make_line_segments(x, y, ispath=False))

        if "r" in sides:
            x = np.tile([xmax - xheight, xmax], n)
            rugs.extend(make_line_segments(x, y, ispath=False))

    color = to_rgba(data["color"], data["alpha"])
    coll = LineCollection(
        rugs,
        edgecolor=color,
        linewidth=linewidth,
        linestyle=data["linetype"],
        zorder=params["zorder"],
        rasterized=params["raster"],
    )
    ax.add_collection(coll)
