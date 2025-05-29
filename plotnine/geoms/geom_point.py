from __future__ import annotations

import typing

import numpy as np

from .._utils import SIZE_FACTOR, to_rgba
from ..doctools import document
from ..scales.scale_shape import FILLED_SHAPES
from .geom import geom

if typing.TYPE_CHECKING:
    from typing import Any

    import pandas as pd
    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer


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
        coord: coord,
        ax: Axes,
    ):
        """
        Plot all groups
        """
        self.draw_group(data, panel_params, coord, ax, self.params)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        data = coord.transform(data, panel_params)
        units = "shape"
        for _, udata in data.groupby(units, dropna=False):
            udata.reset_index(inplace=True, drop=True)
            geom_point.draw_unit(udata, panel_params, coord, ax, params)

    @staticmethod
    def draw_unit(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        # Our size is in 'points' while scatter wants
        # 'points^2'. The stroke is outside. And pi
        # gives a large enough scaling factor
        # All other sizes for which the MPL units should
        # be in points must scaled using sqrt(pi)
        size = ((data["size"] + data["stroke"]) ** 2) * np.pi
        linewidth = data["stroke"] * SIZE_FACTOR
        color = to_rgba(data["color"], data["alpha"])
        shape = data["shape"].iloc[0]

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
            linewidth=linewidth,
            marker=shape,
            zorder=params["zorder"],
            rasterized=params["raster"],
        )

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
        from matplotlib.lines import Line2D

        if data["fill"] is None:
            data["fill"] = data["color"]

        size = (data["size"] + data["stroke"]) * SIZE_FACTOR
        edgewidth = data["stroke"] * SIZE_FACTOR
        fill = to_rgba(data["fill"], data["alpha"])
        color = to_rgba(data["color"], data["alpha"])

        key = Line2D(
            [0.5 * da.width],
            [0.5 * da.height],
            marker=data["shape"],
            markersize=size,
            markerfacecolor=fill,
            markeredgecolor=color,
            markeredgewidth=edgewidth,
        )
        da.add_artist(key)
        return da

    @staticmethod
    def legend_key_size(
        data: pd.Series[Any], min_size: tuple[int, int], lyr: layer
    ) -> tuple[int, int]:
        w, h = min_size
        pad_w, pad_h = w * 0.5, h * 0.5
        _size = data["size"] * SIZE_FACTOR
        _edgewidth = 2 * data["stroke"] * SIZE_FACTOR
        _w = _h = _size + _edgewidth
        if data["color"] is not None:
            w = max(w, _w + pad_w)
            h = max(h, _h + pad_h)
        return w, h
