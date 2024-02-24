from __future__ import annotations

import typing

from .._utils import resolution
from ..doctools import document
from .geom_rect import geom_rect

if typing.TYPE_CHECKING:
    import pandas as pd


@document
class geom_tile(geom_rect):
    """
    Rectangles specified using a center points

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geom_rect
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": None,
        "fill": "#333333",
        "linetype": "solid",
        "size": 0.1,
    }
    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
    }

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        try:
            width = data.pop("width")
        except KeyError:
            width = resolution(data["x"], False)

        try:
            height = data.pop("height")
        except KeyError:
            height = resolution(data["y"], False)

        data["xmin"] = data["x"] - width / 2
        data["xmax"] = data["x"] + width / 2
        data["ymin"] = data["y"] - height / 2
        data["ymax"] = data["y"] + height / 2
        return data
