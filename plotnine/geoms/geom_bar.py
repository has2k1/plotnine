from __future__ import annotations

import typing

import numpy as np

from .._utils import frame, resolution
from ..doctools import document
from .geom_rect import geom_rect

if typing.TYPE_CHECKING:
    from plotnine._utils.frame import DataFrame


@document
class geom_bar(geom_rect):
    """
    Bar plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    just : float, default=0.5
        How to align the column with respect to the axis breaks. The default
        `0.5` aligns the center of the column with the break. `0` aligns the
        left of the of the column with the break and `1` aligns the right of
        the column with the break.
    width : float, default=None
        Bar width. If `None`{.py}, the width is set to
        `90%` of the resolution of the data.

    See Also
    --------
    plotnine.geom_histogram
    plotnine.stat_count : The default `stat` for this `geom`.
    """

    REQUIRED_AES = {"x", "y"}
    NON_MISSING_AES = {"xmin", "xmax", "ymin", "ymax"}
    DEFAULT_PARAMS = {
        "stat": "count",
        "position": "stack",
        "just": 0.5,
        "width": None,
    }

    def setup_data(self, data: DataFrame) -> DataFrame:
        if "width" not in data.columns:
            if self.params["width"]:
                width = self.params["width"]
            else:
                width = resolution(data["x"], False) * 0.9
            data = frame.assign(data, width=width)

        just = self.params["just"]
        x = frame.to_numpy(data["x"])
        y = frame.to_numpy(data["y"])
        width = frame.to_numpy(data["width"])
        negative = y < 0
        return frame.assign(
            data,
            ymin=np.where(negative, y, 0.0),
            ymax=np.where(negative, 0.0, y),
            xmin=x - width * just,
            xmax=x + width * (1 - just),
        ).drop("width")
