from __future__ import annotations

import typing

from .._utils import frame
from ..doctools import document
from .geom_path import geom_path

if typing.TYPE_CHECKING:
    from plotnine._utils.frame import DataFrame


@document
class geom_line(geom_path):
    """
    Connected points

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geom_path : For documentation of other parameters.
    """

    def setup_data(self, data: DataFrame) -> DataFrame:
        return frame.sort(data, ["PANEL", "group", "x"])
