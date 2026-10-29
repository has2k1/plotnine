from __future__ import annotations

import typing

import numpy as np

from .._utils import (
    SIZE_FACTOR,
    frame,
    interleave,
    make_line_segments,
    to_rgba,
)
from ..doctools import document
from .geom import geom
from .geom_path import geom_path

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes

    from plotnine._utils.frame import DataFrame
    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view


@document
class geom_segment(geom):
    """
    Line segments

    {usage}

    Parameters
    ----------
    {common_parameters}
    lineend : Literal["butt", "round", "projecting"], default="butt"
        Line end style. This option is applied for solid linetypes.
    arrow : ~plotnine.geoms.geom_path.arrow, default=None
        Arrow specification. Default is no arrow.

    See Also
    --------
    plotnine.arrow : for adding arrowhead(s) to segments.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "black",
        "linetype": "solid",
        "size": 0.5,
    }
    REQUIRED_AES = {"x", "y", "xend", "yend"}
    NON_MISSING_AES = {"linetype", "size", "shape"}
    DEFAULT_PARAMS = {"lineend": "butt", "arrow": None}

    draw_legend = staticmethod(geom_path.draw_legend)
    legend_key_size = staticmethod(geom_path.legend_key_size)

    @staticmethod
    def draw_group(
        data: DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        from matplotlib.collections import LineCollection

        data = coord.transform(data, panel_params)
        linewidth = frame.to_numpy(data["size"]) * SIZE_FACTOR
        color = to_rgba(data["color"], data["alpha"])
        x = frame.to_numpy(data["x"])
        xend = frame.to_numpy(data["xend"])
        y = frame.to_numpy(data["y"])
        yend = frame.to_numpy(data["yend"])
        segments = make_line_segments(
            interleave(x, xend), interleave(y, yend), ispath=False
        )
        coll = LineCollection(
            list(segments),
            edgecolor=color,
            linewidth=linewidth,
            linestyle=data["linetype"].item(0),
            capstyle=params.get("lineend"),
            zorder=params["zorder"],
            rasterized=params["raster"],
        )
        ax.add_collection(coll)

        if "arrow" in params and params["arrow"]:
            idx = np.arange(1, len(data) + 1)
            adata = {
                "group": np.hstack([idx, idx]),
                "x": np.hstack([x, xend]),
                "y": np.hstack([y, yend]),
                "linewidth": np.hstack([linewidth, linewidth]),
            }
            for param in ["color", "alpha", "linetype"]:
                values = data[param].to_list()
                adata[param] = values + values

            params["arrow"].draw(
                frame.frame_like(data, adata),
                panel_params,
                coord,
                ax,
                params,
                constant=False,
            )
