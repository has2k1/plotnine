from __future__ import annotations

import typing

import narwhals as nw

from ..doctools import document
from .geom_ribbon import geom_ribbon

if typing.TYPE_CHECKING:
    from plotnine._utils.frame import DataFrame


@document
class geom_area(geom_ribbon):
    """
    Area plot

    {usage}

    An area plot is a special case of geom_ribbon,
    where the minimum of the range is fixed to 0,
    and the position adjustment defaults to 'stack'.

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geom_ribbon
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {"position": "stack", "outline_type": "upper"}

    def setup_data(self, data: DataFrame) -> DataFrame:
        return data.with_columns(ymin=nw.lit(0), ymax=nw.col("y"))
