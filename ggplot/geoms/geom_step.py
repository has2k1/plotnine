from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd

from ..utils import copy_missing_columns, interleave
from .geom import geom
from .geom_path import geom_path


class geom_step(geom_path):
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'direction': 'hv'}
    draw_panel = geom.draw_panel

    @staticmethod
    def draw_group(data, panel_scales, coord, ax, **params):
        x = data['x'].values
        y = data['y'].values

        # create stepped path -- interleave x with
        # itself and y with itself
        if params['direction'] == 'hv':
            xs = interleave(x[:-1], x[1:])
            ys = interleave(y[:-1], y[:-1])
        elif params['direction'] == 'vh':
            xs = interleave(x[:-1], x[:-1])
            ys = interleave(y[:-1], y[1:])

        df = pd.DataFrame({'x': xs, 'y': ys})
        copy_missing_columns(df, data)
        geom_path.draw_group(df, panel_scales, coord, ax, **params)
