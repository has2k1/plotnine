from __future__ import annotations

import typing

import narwhals as nw
import numpy as np

from .._utils import copy_missing_columns, frame, resolution
from ..doctools import document
from .geom import geom
from .geom_path import geom_path
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes

    from plotnine._utils.frame import DataFrame
    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view


@document
class geom_errorbar(geom):
    """
    Vertical interval represented as an errorbar

    {usage}

    Parameters
    ----------
    {common_parameters}
    width : float, default=0.5
        Bar width as a fraction of the resolution of the data.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "black",
        "linetype": "solid",
        "size": 0.5,
    }
    REQUIRED_AES = {"x", "ymin", "ymax"}
    DEFAULT_PARAMS = {"width": 0.5}

    draw_legend = staticmethod(geom_path.draw_legend)

    def setup_data(self, data: DataFrame) -> DataFrame:
        if "width" not in data.columns:
            if self.params["width"]:
                width = self.params["width"]
            else:
                width = resolution(data["x"], False) * 0.9
            data = frame.assign(data, width=width)

        x = nw.col("x")
        half_width = nw.col("width") / 2
        return data.with_columns(
            xmin=x - half_width, xmax=x + half_width
        ).drop("width")

    @staticmethod
    def draw_group(
        data: DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        def f(*columns: str):
            return np.hstack([frame.to_numpy(data[c]) for c in columns])

        # create (two horizontal bars) + vertical bar
        bars = frame.frame_like(
            data,
            {
                "x": f("xmin", "xmin", "x"),
                "xend": f("xmax", "xmax", "x"),
                "y": f("ymin", "ymax", "ymax"),
                "yend": f("ymin", "ymax", "ymin"),
            },
        )

        bars = copy_missing_columns(bars, data)
        geom_segment.draw_group(bars, panel_params, coord, ax, params)
