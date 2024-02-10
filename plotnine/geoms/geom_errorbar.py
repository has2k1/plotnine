from __future__ import annotations

import typing

import numpy as np
import pandas as pd

from .._utils import copy_missing_columns, resolution
from ..doctools import document
from .geom import geom
from .geom_path import geom_path
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes

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
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "width": 0.5,
    }
    draw_legend = staticmethod(geom_path.draw_legend)

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        if "width" not in data:
            if self.params["width"]:
                data["width"] = self.params["width"]
            else:
                data["width"] = resolution(data["x"], False) * 0.9

        data["xmin"] = data["x"] - data["width"] / 2
        data["xmax"] = data["x"] + data["width"] / 2
        del data["width"]
        return data

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        f = np.hstack
        # create (two horizontal bars) + vertical bar
        bars = pd.DataFrame(
            {
                "x": f([data["xmin"], data["xmin"], data["x"]]),
                "xend": f([data["xmax"], data["xmax"], data["x"]]),
                "y": f([data["ymin"], data["ymax"], data["ymax"]]),
                "yend": f([data["ymin"], data["ymax"], data["ymin"]]),
            }
        )

        copy_missing_columns(bars, data)
        geom_segment.draw_group(bars, panel_params, coord, ax, **params)
