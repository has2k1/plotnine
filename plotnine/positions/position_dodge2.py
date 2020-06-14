from copy import copy

import numpy as np
import pandas as pd

from ..exceptions import PlotnineError
from ..utils import groupby_apply, pivot_apply
from .position_dodge import position_dodge


class position_dodge2(position_dodge):
    """
    Dodge overlaps and place objects side-by-side

    This is an enhanced version of
    :class:`~plotnine.positions.position_dodge` that can deal
    with rectangular overlaps that do not share a lower x border.

    Parameters
    ----------
    width: float
        Dodging width, when different to the width of the
        individual elements. This is useful when you want
        to align narrow geoms with wider geoms
    preserve: str in ``['total', 'single']``
        Should dodging preserve the total width of all elements
        at a position, or the width of a single element?
    padding : float
        Padding between elements at the same position.
        Elements are shrunk by this proportion to allow space
        between them (Default: 0.1)
    """
    REQUIRED_AES = {'x'}

    def __init__(self, width=None, preserve='total', padding=0.1):
        self.params = {
            'width': width,
            'preserve': preserve,
            'padding': padding
        }

    def setup_params(self, data):
        if (('xmin' not in data) and
                ('xmax' not in data) and
                (self.params['width'] is None)):
            msg = ("Width not defined. "
                   "Set with `position_dodge2(width = ?)`")
            raise PlotnineError(msg)

        params = copy(self.params)

        if params['preserve'] == 'total':
            params['n'] = None
        elif 'x' in data:
            # point geom
            def max_x_values(gdf):
                n = gdf['x'].value_counts().max()
                return pd.DataFrame({'n': [n]})

            res = groupby_apply(data, 'PANEL', max_x_values)
            params['n'] = res['n'].max()
        else:
            # interval geoms
            res = groupby_apply(data, 'PANEL', find_x_overlaps)
            params['n'] = res['n'].max()
        return params

    @classmethod
    def compute_panel(cls, data, scales, params):
        return cls.collide2(data, params=params)

    @staticmethod
    def strategy(data, params):
        padding = params['padding']
        n = params['n']

        if not all([col in data.columns for col in ['xmin', 'xmax']]):
            data['xmin'] = data['x']
            data['xmax'] = data['x']

        # Groups of boxes that share the same position
        data['xid'] = find_x_overlaps(data)

        # Find newx using xid, i.e. the center of each group of
        # overlapping elements. for boxes, bars, etc. this should
        # be the same as original x, but for arbitrary rects it
        # may not be
        res1 = pivot_apply(data, 'xmin', 'xid', np.min)
        res2 = pivot_apply(data, 'xmax', 'xid', np.max)
        data['newx'] = (res1 + res2)[data['xid'].values].values / 2

        if n is None:
            # If n is None, preserve total widths of elements at
            # each position by dividing widths by the number of
            # elements at that position
            n = data['xid'].value_counts().values
            n = n[data.loc[:, 'xid'] - 1]
            data['new_width'] = (data['xmax'] - data['xmin']) / n
        else:
            data['new_width'] = (data['xmax'] - data['xmin']) / n

        # Find the total width of each group of elements
        def sum_new_width(gdf):
            return pd.DataFrame({'size': [gdf['new_width'].sum()],
                                 'newx': gdf['newx'].iloc[0]})

        group_sizes = groupby_apply(data, 'newx', sum_new_width)

        # Starting xmin for each group of elements
        starts = group_sizes['newx'] - (group_sizes['size']/2)

        # Set the elements in place
        for i, start in enumerate(starts, start=1):
            bool_idx = data['xid'] == i
            divisions = np.cumsum(
               np.hstack([
                   start,
                   data.loc[bool_idx, 'new_width']
               ])
            )
            data.loc[bool_idx, 'xmin'] = divisions[:-1]
            data.loc[bool_idx, 'xmax'] = divisions[1:]

        # x values get moved to between xmin and xmax
        data['x'] = (data['xmin'] + data['xmax']) / 2

        # Shrink elements to add space between them
        if data['xid'].duplicated().any():
            pad_width = data['new_width'] * (1 - padding)
            data['xmin'] = data['x'] - pad_width / 2
            data['xmax'] = data['x'] + pad_width / 2

        data = data.drop(columns=['xid', 'newx', 'new_width'],
                         errors='ignore')
        return data


def find_x_overlaps(df):
    n = len(df)
    overlaps = np.zeros(n, dtype=int)
    overlaps[0] = 1
    counter = 1
    for i in range(1, n):
        if df['xmin'].iloc[i] >= df['xmax'].iloc[i-1]:
            counter += 1
        overlaps[i] = counter
    return overlaps
