import numpy as np
import pandas as pd

from ..exceptions import PlotnineError
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
        One of *hv*, *vh* or *mid*, for horizontal-vertical steps,
        vertical-horizontal steps or steps half-way between adjacent
        x values.

    See Also
    --------
    plotnine.geoms.geom_path : For documentation of extra
        parameters.
    """
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'direction': 'hv'}
    draw_panel = geom.draw_panel

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        direction = params['direction']
        n = len(data)
        data = data.sort_values('x', kind='mergesort')
        x = data['x'].values
        y = data['y'].values

        if direction == 'vh':
            # create stepped path -- interleave x with
            # itself and y with itself
            xidx = np.repeat(range(n), 2)[:-1]
            yidx = np.repeat(range(n), 2)[1:]
            new_x, new_y = x[xidx], y[yidx]
        elif direction == 'hv':
            xidx = np.repeat(range(n), 2)[1:]
            yidx = np.repeat(range(n), 2)[:-1]
            new_x, new_y = x[xidx], y[yidx]
        elif direction == 'mid':
            xidx = np.repeat(range(n-1), 2)
            yidx = np.repeat(range(n), 2)
            diff = x[1::] - x[:-1:]
            mid_x = x[:-1:] + diff/2
            new_x = np.hstack([x[0], mid_x[xidx], x[-1]])
            new_y = y[yidx]
        else:
            raise PlotnineError(
                "Invalid direction `{}`".format(direction))

        df = pd.DataFrame({'x': new_x, 'y': new_y})
        copy_missing_columns(df, data)
        geom_path.draw_group(df, panel_params, coord, ax, **params)
