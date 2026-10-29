from __future__ import annotations

import typing

import narwhals as nw
import numpy as np

from .._utils import SIZE_FACTOR, frame, to_rgba
from ..doctools import document
from .geom import geom
from .geom_polygon import geom_polygon

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes

    from plotnine._utils.frame import DataFrame
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

    draw_legend = staticmethod(geom_polygon.draw_legend)

    def draw_panel(
        self,
        data: DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ):
        """
        Plot all groups
        """
        if not coord.is_linear:
            data = _rectangles_to_polygons(data)
            # Each rectangle is its own closed polygon. Grouping by the
            # `group` aesthetic would merge a stacked bar's segments into one
            # open path, and coord.munch would then bend the join between
            # consecutive rectangles into a spurious spike.
            data = frame.assign(
                data, group=np.repeat(np.arange(len(data) // 4), 4)
            )
            for _, gdata in frame.group_split(data, "group"):
                geom_polygon.draw_group(
                    gdata, panel_params, coord, ax, self.params
                )
        else:
            self.draw_group(data, panel_params, coord, ax, self.params)

    @staticmethod
    def draw_group(
        data: DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        data = coord.transform(data, panel_params, munch=True)
        fill_rects(data, ax, params)


def fill_rects(
    data: DataFrame,
    ax: Axes,
    params: dict[str, Any],
) -> None:
    """
    Draw rectangles from panel-coordinate data

    Parameters
    ----------
    data :
        Rectangle data in panel coordinates.
    ax :
        Axes on which to draw the rectangles.
    params :
        Geom and stat parameters used to style the rectangles.
    """
    from matplotlib.collections import PolyCollection

    linewidth = frame.to_numpy(data["size"]) * SIZE_FACTOR
    limits = zip(
        frame.to_numpy(data["xmin"]),
        frame.to_numpy(data["xmax"]),
        frame.to_numpy(data["ymin"]),
        frame.to_numpy(data["ymax"]),
    )
    verts = [[(l, b), (l, t), (r, t), (r, b)] for (l, r, b, t) in limits]
    fill = to_rgba(data["fill"], data["alpha"])
    color = data["color"].to_list()

    # prevent unnecessary borders
    if frame.isna(data["color"]).all():
        color = "none"

    col = PolyCollection(
        verts,
        facecolors=fill,
        edgecolors=color,
        linestyles=data["linetype"].to_list(),
        linewidths=linewidth,
        zorder=params["zorder"],
        rasterized=params["raster"],
    )
    ax.add_collection(col)


def _rectangles_to_polygons(df: DataFrame) -> DataFrame:
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
    x[xmin_idx] = frame.to_numpy(df["xmin"]).repeat(2)
    x[xmax_idx] = frame.to_numpy(df["xmax"]).repeat(2)
    y[ymin_idx] = frame.to_numpy(df["ymin"]).repeat(2)
    y[ymax_idx] = frame.to_numpy(df["ymax"]).repeat(2)

    # Aesthetic columns and others
    other_cols = sorted(
        set(df.columns) - {"x", "y", "xmin", "xmax", "ymin", "ymax"}
    )
    others = frame.take(df.select(other_cols), np.repeat(np.arange(n), 4))
    xy = frame.frame_like(df, {"x": x, "y": y})
    if not other_cols:
        return xy
    return nw.concat([xy, others], how="horizontal")
