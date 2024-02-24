from __future__ import annotations

import typing

import numpy as np
import pandas as pd

from .._utils import copy_missing_columns
from ..doctools import document
from ..exceptions import PlotnineError
from .geom import geom
from .geom_path import geom_path

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view


@document
class geom_step(geom_path):
    """
    Stepped connected points

    {usage}

    Parameters
    ----------
    {common_parameters}
    direction : Literal["hv", "vh", "mid"], default="hv"
        horizontal-vertical steps,
        vertical-horizontal steps or steps half-way between adjacent
        x values.

    See Also
    --------
    plotnine.geom_path : For documentation of extra parameters.
    """

    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "direction": "hv",
    }
    draw_panel = geom.draw_panel

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        direction = params["direction"]
        n = len(data)
        data = data.sort_values("x", kind="mergesort")
        x = data["x"].to_numpy()
        y = data["y"].to_numpy()

        if direction == "vh":
            # create stepped path -- interleave x with
            # itself and y with itself
            xidx = np.repeat(range(n), 2)[:-1]
            yidx = np.repeat(range(n), 2)[1:]
            new_x, new_y = x[xidx], y[yidx]
        elif direction == "hv":
            xidx = np.repeat(range(n), 2)[1:]
            yidx = np.repeat(range(n), 2)[:-1]
            new_x, new_y = x[xidx], y[yidx]
        elif direction == "mid":
            xidx = np.repeat(range(n - 1), 2)
            yidx = np.repeat(range(n), 2)
            diff = x[1::] - x[:-1:]
            mid_x = x[:-1:] + diff / 2
            new_x = np.hstack([x[0], mid_x[xidx], x[-1]])
            new_y = y[yidx]
        else:
            raise PlotnineError(f"Invalid direction `{direction}`")

        path_data = pd.DataFrame({"x": new_x, "y": new_y})
        copy_missing_columns(path_data, data)
        geom_path.draw_group(path_data, panel_params, coord, ax, **params)
