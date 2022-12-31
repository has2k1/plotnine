from __future__ import annotations

import typing

from ..doctools import document
from .geom import geom
from .geom_path import geom_path
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    import matplotlib as mpl
    import pandas as pd

    import plotnine as p9


@document
class geom_linerange(geom):
    """
    Vertical interval represented by lines

    {usage}

    Parameters
    ----------
    {common_parameters}
    """
    DEFAULT_AES = {'alpha': 1, 'color': 'black',
                   'linetype': 'solid', 'size': 0.5}
    REQUIRED_AES = {'x', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False}
    draw_legend = staticmethod(geom_path.draw_legend)  # type: ignore

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: p9.iapi.panel_view,
        coord: p9.coords.coord.coord,
        ax: mpl.axes.Axes,
        **params: Any
    ) -> None:
        data.eval("""
                     xend = x
                     y = ymin
                     yend = ymax""",
                  inplace=True)
        geom_segment.draw_group(data, panel_params, coord, ax, **params)
