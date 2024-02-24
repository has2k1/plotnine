from __future__ import annotations

import typing

from .._utils import resolution
from ..doctools import document
from .geom_rect import geom_rect

if typing.TYPE_CHECKING:
    import pandas as pd


@document
class geom_bar(geom_rect):
    """
    Bar plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    width : float, default=None
        Bar width. If `None`{.py}, the width is set to
        `90%` of the resolution of the data.

    See Also
    --------
    plotnine.geom_histogram
    """

    REQUIRED_AES = {"x", "y"}
    NON_MISSING_AES = {"xmin", "xmax", "ymin", "ymax"}
    DEFAULT_PARAMS = {
        "stat": "count",
        "position": "stack",
        "na_rm": False,
        "width": None,
    }

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        if "width" not in data:
            if self.params["width"]:
                data["width"] = self.params["width"]
            else:
                data["width"] = resolution(data["x"], False) * 0.9

        bool_idx = data["y"] < 0

        data["ymin"] = 0.0
        data.loc[bool_idx, "ymin"] = data.loc[bool_idx, "y"]

        data["ymax"] = data["y"]
        data.loc[bool_idx, "ymax"] = 0.0

        data["xmin"] = data["x"] - data["width"] / 2
        data["xmax"] = data["x"] + data["width"] / 2
        del data["width"]
        return data
