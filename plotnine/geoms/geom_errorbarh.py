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
class geom_errorbarh(geom):
    """
    Horizontal interval represented as an errorbar

    {usage}

    Parameters
    ----------
    {common_parameters}
    height : float, default=0.5
        Bar height as a fraction of the resolution of the data.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "black",
        "linetype": "solid",
        "size": 0.5,
    }
    REQUIRED_AES = {"y", "xmin", "xmax"}
    DEFAULT_PARAMS = {"height": 0.5}

    draw_legend = staticmethod(geom_path.draw_legend)

    def setup_data(self, data: DataFrame) -> DataFrame:
        if "height" not in data.columns:
            if self.params["height"]:
                height = self.params["height"]
            else:
                height = resolution(data["y"], False) * 0.9
            data = frame.assign(data, height=height)

        y = nw.col("y")
        half_height = nw.col("height") / 2
        return data.with_columns(
            ymin=y - half_height, ymax=y + half_height
        ).drop("height")

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

        # create (two vertical bars) + horizontal bar
        bars = frame.frame_like(
            data,
            {
                "y": f("ymin", "ymin", "y"),
                "yend": f("ymax", "ymax", "y"),
                "x": f("xmin", "xmax", "xmin"),
                "xend": f("xmin", "xmax", "xmax"),
            },
        )

        bars = copy_missing_columns(bars, data)
        geom_segment.draw_group(bars, panel_params, coord, ax, params)
