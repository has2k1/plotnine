from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from ..utils import copy_missing_columns
from ..doctools import document
from .geom import geom
from .geom_path import geom_path


@document
class geom_step(geom_path):
    """
    Stepped connected points

    {usage}

    Parameters
    ----------
    {common_parameters}
    direction : str, optional (default: hv)
        One of *hv* or *vh*, for horizontal-vertical or
        vertical-horizontal steps.

    {aesthetics}

    See Also
    --------
    :class:`~plotnine.geoms.geom_path` for documentation of extra
    parameters.
    """
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'direction': 'hv'}
    draw_panel = geom.draw_panel

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        n = len(data)
        data = data.sort_values('x', kind='mergesort')

        # create stepped path -- interleave x with
        # itself and y with itself
        xs = np.repeat(range(n), 2)[:-1]
        ys = np.repeat(range(0, n), 2)[1:]

        # horizontal first
        if params['direction'] == 'hv':
            xs, ys = ys, xs

        df = pd.DataFrame({'x': data['x'].values[xs],
                           'y': data['y'].values[ys]})
        copy_missing_columns(df, data)
        geom_path.draw_group(df, panel_params, coord, ax, **params)
