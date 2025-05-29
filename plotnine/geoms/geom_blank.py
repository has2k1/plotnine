from __future__ import annotations

import typing

from ..doctools import document
from .geom import geom

if typing.TYPE_CHECKING:
    import pandas as pd
    from matplotlib.axes import Axes

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view


@document
class geom_blank(geom):
    """
    An empty plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
    }

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ):
        pass

    def handle_na(self, data: pd.DataFrame) -> pd.DataFrame:
        return data
