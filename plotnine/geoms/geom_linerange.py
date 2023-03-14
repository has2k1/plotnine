from __future__ import annotations

import typing

from ..doctools import document
from .geom import geom
from .geom_path import geom_path
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    import pandas as pd

    from plotnine.iapi import panel_view
    from plotnine.typing import Axes, Coord


@document
class geom_linerange(geom):
    """
    Vertical interval represented by lines

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "black",
        "linetype": "solid",
        "size": 0.5,
    }
    REQUIRED_AES = {"x", "ymin", "ymax"}
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
    }
    draw_legend = staticmethod(geom_path.draw_legend)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: Coord,
        ax: Axes,
        **params: Any,
    ):
        data.eval(
            """
            xend = x
            y = ymin
            yend = ymax
            """,
            inplace=True,
        )
        geom_segment.draw_group(data, panel_params, coord, ax, **params)
