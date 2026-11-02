from __future__ import annotations

from typing import TYPE_CHECKING

from ..doctools import document
from .stat import stat

if TYPE_CHECKING:
    import pandas as pd

    from plotnine.iapi import pos_scales


@document
class stat_identity(stat):
    """
    Identity (do nothing) statistic

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geom_point : The default `geom` for this `stat`.
    """

    DEFAULT_PARAMS = {"geom": "point"}

    def compute_panel(
        self, data: pd.DataFrame, scales: pos_scales
    ) -> pd.DataFrame:
        return data
