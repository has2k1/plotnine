from __future__ import annotations

import typing
from copy import copy

from ..doctools import document
from .geom import geom
from .geom_linerange import geom_linerange
from .geom_path import geom_path
from .geom_point import geom_point

if typing.TYPE_CHECKING:
    from typing import Any

    import pandas as pd
    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer
    from plotnine.typing import TupleInt2


@document
class geom_pointrange(geom):
    """
    Vertical interval represented by a line with a point

    {usage}

    Parameters
    ----------
    {common_parameters}
    fatten : float, default=2
        A multiplicative factor used to increase the size of the
        point along the line-range.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "black",
        "fill": None,
        "linetype": "solid",
        "shape": "o",
        "size": 0.5,
    }
    REQUIRED_AES = {"x", "y", "ymin", "ymax"}
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "fatten": 4,
    }

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        geom_linerange.draw_group(
            data.copy(), panel_params, coord, ax, **params
        )
        data["size"] = data["size"] * params["fatten"]
        data["stroke"] = geom_point.DEFAULT_AES["stroke"]
        geom_point.draw_group(data, panel_params, coord, ax, **params)

    @staticmethod
    def draw_legend(
        data: pd.Series[Any], da: DrawingArea, lyr: layer
    ) -> DrawingArea:
        """
        Draw a point in the box

        Parameters
        ----------
        data : Series
            Data Row
        da : DrawingArea
            Canvas
        lyr : layer
            Layer

        Returns
        -------
        out : DrawingArea
        """
        geom_path.draw_legend(data, da, lyr)
        data["size"] = data["size"] * lyr.geom.params["fatten"]
        data["stroke"] = geom_point.DEFAULT_AES["stroke"]
        geom_point.draw_legend(data, da, lyr)
        return da

    @staticmethod
    def legend_key_size(
        data: pd.Series[Any], min_size: TupleInt2, lyr: layer
    ) -> TupleInt2:
        data = copy(data)
        data["size"] = data["size"] * lyr.geom.params["fatten"]
        data["stroke"] = geom_point.DEFAULT_AES["stroke"]
        return geom_point.legend_key_size(data, min_size, lyr)
