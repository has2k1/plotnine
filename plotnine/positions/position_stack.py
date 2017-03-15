from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from warnings import warn

import numpy as np
import pandas as pd

from ..utils import remove_missing
from .position import position


class position_stack(position):
    """
    Stack plotted objects on top of each other

    The objects to stack are those that have
    an overlapping x range.
    """
    fill = False

    def __init__(self, vjust=1, reverse=False):
        self.params = {'vjust': vjust,
                       'reverse': reverse}

    def setup_params(self, data):
        """
        Verify, modify & return a copy of the params.
        """
        # Variable for which to do the stacking
        if 'ymax' in data:
            if any((data['ymin'] != 0) & (data['ymax'] != 0)):
                warn("Stacking not well defined when not "
                     "anchored on the axis.")
            var = 'ymax'
        elif 'y' in data:
            var = 'y'
        else:
            warn("Stacking requires either ymin & ymax or y "
                 "aesthetics. Maybe you want position = 'identity'?")
            var = None

        params = self.params.copy()
        params['var'] = var
        params['fill'] = self.fill
        return params

    def setup_data(self, data, params):
        if not params['var']:
            return data

        if params['var'] == 'y':
            data['ymax'] = data['y']
        elif params['var'] == 'ymax':
            bool_idx = data['ymax'] == 0
            data.loc[bool_idx, 'ymax'] = data.loc[bool_idx, 'ymin']

        data = remove_missing(
            data,
            vars=('x', 'xmin', 'xmax', 'y'),
            name='position_stack')

        return data

    @classmethod
    def compute_panel(cls, data, scales, params):
        if not params['var']:
            return data

        negative = data['ymax'] < 0
        neg = data.loc[negative]
        pos = data.loc[~negative]
        neg.is_copy = None
        pos.is_copy = None

        if len(neg):
            neg = cls.collide(neg, params=params)

        if len(pos):
            pos = cls.collide(pos, params=params)

        data = pd.concat([neg, pos], axis=0, ignore_index=True)
        return data

    @staticmethod
    def strategy(data, params):
        """
        Stack overlapping intervals.

        Assumes that each set has the same horizontal position
        """
        vjust = params['vjust']

        y = data['y'].copy()
        y[np.isnan(y)] = 0
        heights = np.append(0, y.cumsum())

        if params['fill']:
            heights = heights / np.abs(heights[-1])

        data['ymin'] = np.min([heights[:-1], heights[1:]], axis=0)
        data['ymax'] = np.max([heights[:-1], heights[1:]], axis=0)
        # less intuitive than (ymin + vjust(ymax-ymin)), but
        # this way avoids subtracting numbers of potentially
        # similar precision
        data['y'] = ((1-vjust)*data['ymin'] + vjust*data['ymax'])
        return data
