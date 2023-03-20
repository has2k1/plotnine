from __future__ import annotations

import typing

import numpy as np

from ..doctools import document
from ..scales.scale_shape import FILLED_SHAPES
from ..utils import SIZE_FACTOR, to_rgba
from .geom import geom

if typing.TYPE_CHECKING:
    from typing import Any

    import pandas as pd

    from plotnine.iapi import panel_view
    from plotnine.typing import Axes, Coord, DrawingArea, Layer


@document
class geom_point(geom):
    """
    Plot points (Scatter plot)

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "black",
        "fill": None,
        "shape": "o",
        "size": 1.5,
        "stroke": 0.5,
    }
    REQUIRED_AES = {"x", "y"}
    NON_MISSING_AES = {"color", "shape", "size"}
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
    }

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: Coord,
        ax: Axes,
        **params: Any,
    ):
        """
        Plot all groups
        """
        self.draw_group(data, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: Coord,
        ax: Axes,
        **params: Any,
    ):
        data = coord.transform(data, panel_params)
        units = "shape"
        for _, udata in data.groupby(units, dropna=False):
            udata.reset_index(inplace=True, drop=True)
            geom_point.draw_unit(udata, panel_params, coord, ax, **params)

    @staticmethod
    def draw_unit(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: Coord,
        ax: Axes,
        **params: Any,
    ):
        # Our size is in 'points' while scatter wants
        # 'points^2'. The stroke is outside. And pi
        # gives a large enough scaling factor
        # All other sizes for which the MPL units should
        # be in points must scaled using sqrt(pi)
        size = ((data["size"] + data["stroke"]) ** 2) * np.pi
        stroke = data["stroke"] * SIZE_FACTOR
        color = to_rgba(data["color"], data["alpha"])
        shape = data.loc[0, "shape"]

        # It is common to forget that scatter points are
        # filled and slip-up by manually assigning to the
        # color instead of the fill. We forgive.
        if shape in FILLED_SHAPES:
            if all(c is None for c in data["fill"]):
                fill = color
            else:
                fill = to_rgba(data["fill"], data["alpha"])
        else:
            # Assume unfilled
            fill = color
            color = None

        ax.scatter(
            x=data["x"],
            y=data["y"],
            s=size,
            facecolor=fill,
            edgecolor=color,
            linewidth=stroke,
            marker=shape,
            zorder=params["zorder"],
            rasterized=params["raster"],
        )

    @staticmethod
    def draw_legend(
        data: pd.Series[Any], da: DrawingArea, lyr: Layer
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
        from matplotlib.lines import Line2D

        if data["fill"] is None:
            data["fill"] = data["color"]

        size = (data["size"] + data["stroke"]) * SIZE_FACTOR
        stroke = data["stroke"] * SIZE_FACTOR
        fill = to_rgba(data["fill"], data["alpha"])
        color = to_rgba(data["color"], data["alpha"])

        key = Line2D(
            [0.5 * da.width],
            [0.5 * da.height],
            marker=data["shape"],
            markersize=size,
            markerfacecolor=fill,
            markeredgecolor=color,
            markeredgewidth=stroke,
        )
        da.add_artist(key)
        return da
