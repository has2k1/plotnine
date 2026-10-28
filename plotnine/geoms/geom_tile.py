from __future__ import annotations

import typing

from .._utils import frame, resolution
from ..doctools import document
from .geom_rect import geom_rect

if typing.TYPE_CHECKING:
    from plotnine._utils.frame import DataFrame


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
        "width": None,
        "height": None,
    }
    REQUIRED_AES = {"x", "y"}

    def setup_data(self, data: DataFrame) -> DataFrame:
        if "width" in data.columns:
            width = frame.to_numpy(data["width"])
            data = data.drop("width")
        else:
            width = self.aes_params.get(
                "width",
                resolution(data["x"], False),
            )

        if "height" in data.columns:
            height = frame.to_numpy(data["height"])
            data = data.drop("height")
        else:
            height = self.aes_params.get(
                "height",
                resolution(data["y"], False),
            )

        x = frame.to_numpy(data["x"])
        y = frame.to_numpy(data["y"])
        return frame.assign(
            data,
            xmin=x - width / 2,
            xmax=x + width / 2,
            ymin=y - height / 2,
            ymax=y + height / 2,
        )
