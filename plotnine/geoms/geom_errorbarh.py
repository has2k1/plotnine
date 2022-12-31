from __future__ import annotations

import typing

import numpy as np
import pandas as pd

from ..doctools import document
from ..utils import copy_missing_columns, resolution
from .geom import geom
from .geom_path import geom_path
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    import matplotlib as mpl

    import plotnine as p9


@document
class geom_errorbarh(geom):
    """
    Horizontal interval represented as an errorbar

    {usage}

    Parameters
    ----------
    {common_parameters}
    height : float or None, optional (default: 0.5)
        Bar height. If :py:`None`, the height is set to
        `90%` of the resolution of the data.
    """
    DEFAULT_AES = {'alpha': 1, 'color': 'black',
                   'linetype': 'solid', 'size': 0.5}
    REQUIRED_AES = {'y', 'xmin', 'xmax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'height': 0.5}
    draw_legend = staticmethod(geom_path.draw_legend)  # type: ignore

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        if 'height' not in data:
            if self.params['height']:
                data['height'] = self.params['height']
            else:
                data['height'] = resolution(data['y'], False) * 0.9

        data['ymin'] = data['y'] - data['height']/2
        data['ymax'] = data['y'] + data['height']/2
        del data['height']
        return data

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: p9.iapi.panel_view,
        coord: p9.coords.coord.coord,
        ax: mpl.axes.Axes,
        **params: Any
    ) -> None:
        f = np.hstack
        # create (two vertical bars) + horizontal bar
        df = pd.DataFrame({
            'y': f([data['ymin'], data['ymin'], data['y']]),
            'yend': f([data['ymax'], data['ymax'], data['y']]),
            'x': f([data['xmin'], data['xmax'], data['xmin']]),
            'xend': f([data['xmin'], data['xmax'], data['xmax']])
        })

        copy_missing_columns(df, data)
        geom_segment.draw_group(df, panel_params, coord, ax, **params)
