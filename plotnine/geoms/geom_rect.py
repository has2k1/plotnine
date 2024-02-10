from __future__ import annotations

import typing

import numpy as np
import pandas as pd

from .._utils import SIZE_FACTOR, to_rgba
from ..doctools import document
from .geom import geom
from .geom_polygon import geom_polygon

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view


@document
class geom_rect(geom):
    """
    Rectangles

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_AES = {
        "color": None,
        "fill": "#595959",
        "linetype": "solid",
        "size": 0.5,
        "alpha": 1,
    }
    REQUIRED_AES = {"xmax", "xmin", "ymax", "ymin"}
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
    }
    draw_legend = staticmethod(geom_polygon.draw_legend)

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        """
        Plot all groups
        """
        if not coord.is_linear:
            data = _rectangles_to_polygons(data)
            for _, gdata in data.groupby("group"):
                gdata.reset_index(inplace=True, drop=True)
                geom_polygon.draw_group(
                    gdata, panel_params, coord, ax, **params
                )
        else:
            self.draw_group(data, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        from matplotlib.collections import PolyCollection

        data = coord.transform(data, panel_params, munch=True)
        data["size"] *= SIZE_FACTOR

        limits = zip(data["xmin"], data["xmax"], data["ymin"], data["ymax"])

        verts = [[(l, b), (l, t), (r, t), (r, b)] for (l, r, b, t) in limits]

        fill = to_rgba(data["fill"], data["alpha"])
        color = data["color"]

        # prevent unnecessary borders
        if all(color.isna()):
            color = "none"

        col = PolyCollection(
            verts,
            facecolors=fill,
            edgecolors=color,
            linestyles=data["linetype"],
            linewidths=data["size"],
            zorder=params["zorder"],
            rasterized=params["raster"],
        )
        ax.add_collection(col)


def _rectangles_to_polygons(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert rect data to polygons

    Paramters
    ---------
    df : dataframe
        Dataframe with *xmin*, *xmax*, *ymin* and *ymax* columns,
        plus others for aesthetics ...

    Returns
    -------
    data : dataframe
        Dataframe with *x* and *y* columns, plus others for
        aesthetics ...
    """
    n = len(df)

    # Helper indexing arrays
    xmin_idx = np.tile([True, True, False, False], n)
    xmax_idx = ~xmin_idx
    ymin_idx = np.tile([True, False, False, True], n)
    ymax_idx = ~ymin_idx

    # There are 2 x and 2 y values for each of xmin, xmax, ymin & ymax
    # The positions are as layed out in the indexing arrays
    # x and y values
    x = np.empty(n * 4)
    y = np.empty(n * 4)
    x[xmin_idx] = df["xmin"].repeat(2)
    x[xmax_idx] = df["xmax"].repeat(2)
    y[ymin_idx] = df["ymin"].repeat(2)
    y[ymax_idx] = df["ymax"].repeat(2)

    # Aesthetic columns and others
    other_cols = df.columns.difference(
        ["x", "y", "xmin", "xmax", "ymin", "ymax"]
    )
    d = {str(col): np.repeat(df[col].to_numpy(), 4) for col in other_cols}
    data = pd.DataFrame({"x": x, "y": y, **d})
    return data
