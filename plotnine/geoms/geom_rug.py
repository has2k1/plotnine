from __future__ import annotations

import typing

import numpy as np

from .._utils import SIZE_FACTOR, make_line_segments, to_rgba
from ..coords import coord_flip
from ..doctools import document
from .geom import geom
from .geom_path import geom_path

if typing.TYPE_CHECKING:
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
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "sides": "bl",
        "length": 0.03,
    }
    draw_legend = staticmethod(geom_path.draw_legend)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        from matplotlib.collections import LineCollection

        data = coord.transform(data, panel_params)
        sides = params["sides"]

        # coord_flip does not flip the side(s) on which the rugs
        # are plotted. We do the flipping here
        if isinstance(coord, coord_flip):
            t = str.maketrans("tblr", "rlbt")
            sides = sides.translate(t)

        linewidth = data["size"] * SIZE_FACTOR

        has_x = "x" in data.columns
        has_y = "y" in data.columns

        if has_x or has_y:
            n = len(data)
        else:
            return

        rugs = []
        xmin, xmax = panel_params.x.range
        ymin, ymax = panel_params.y.range
        xheight = (xmax - xmin) * params["length"]
        yheight = (ymax - ymin) * params["length"]

        # Please the type checker
        x: FloatArray
        y: FloatArray

        if has_x:
            if "b" in sides:
                x = np.repeat(data["x"].to_numpy(), 2)
                y = np.tile([ymin, ymin + yheight], n)
                rugs.extend(make_line_segments(x, y, ispath=False))

            if "t" in sides:
                x = np.repeat(data["x"].to_numpy(), 2)
                y = np.tile([ymax - yheight, ymax], n)
                rugs.extend(make_line_segments(x, y, ispath=False))

        if has_y:
            if "l" in sides:
                x = np.tile([xmin, xmin + xheight], n)
                y = np.repeat(data["y"].to_numpy(), 2)
                rugs.extend(make_line_segments(x, y, ispath=False))

            if "r" in sides:
                x = np.tile([xmax - xheight, xmax], n)
                y = np.repeat(data["y"].to_numpy(), 2)
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
