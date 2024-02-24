from __future__ import annotations

import typing

from ..doctools import document
from .geom_ribbon import geom_ribbon

if typing.TYPE_CHECKING:
    import pandas as pd


@document
class geom_area(geom_ribbon):
    """
    Area plot

    An area plot is a special case of geom_ribbon,
    where the minimum of the range is fixed to 0,
    and the position adjustment defaults to 'stack'.

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geom_ribbon
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        **geom_ribbon.DEFAULT_PARAMS,
        "position": "stack",
        "outline_type": "upper",
    }

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data["ymin"] = 0
        data["ymax"] = data["y"]
        return data
