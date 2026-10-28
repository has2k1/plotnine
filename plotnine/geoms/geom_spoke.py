from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .._utils import frame
from ..doctools import document
from .geom_segment import geom_segment

if TYPE_CHECKING:
    from plotnine._utils.frame import DataFrame


@document
class geom_spoke(geom_segment):
    """
    Line segment parameterised by location, direction and distance

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geom_segment : For documentation of extra
        parameters.
    """

    REQUIRED_AES = {"x", "y", "angle", "radius"}

    def setup_data(self, data: DataFrame) -> DataFrame:
        if "radius" in data.columns:
            radius = frame.to_numpy(data["radius"])
        else:
            radius = self.aes_params["radius"]

        if "angle" in data.columns:
            angle = frame.to_numpy(data["angle"])
        else:
            angle = self.aes_params["angle"]

        x = frame.to_numpy(data["x"])
        y = frame.to_numpy(data["y"])
        return frame.assign(
            data,
            xend=x + np.cos(angle) * radius,
            yend=y + np.sin(angle) * radius,
        )
