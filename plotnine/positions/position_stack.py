from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from warnings import warn
import pandas as pd

from ..utils import remove_missing
from .collide import collide, pos_stack
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
            neg = collide(neg, width=None, name=cls.__name__,
                          strategy=pos_stack, params=params)

        if len(pos):
            pos = collide(pos, width=None, name=cls.__name__,
                          strategy=pos_stack, params=params)

        data = pd.concat([neg, pos], axis=0, ignore_index=True)
        return data
