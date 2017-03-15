from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import copy
import numpy as np

from ..exceptions import PlotnineError
from ..utils import match, suppress
from .position import position


class position_dodge(position):
    """
    Dodge overlaps and place objects side-by-side

    Parameters
    ----------
    width: float
        Dodging width, when different to the width of the
        individual elements. This is useful when you want
        to align narrow geoms with wider geoms
    preserve: 'total' or 'single'
        Should dodging preserve the total width of all elements
        at a position, or the width of a single element?
    """
    REQUIRED_AES = {'x'}

    def __init__(self, width=None, preserve='total'):
        self.params = {'width': width, 'preserve': preserve}

    def setup_params(self, data):
        if (('xmin' not in data) and
                ('xmax' not in data) and
                (self.params['width'] is None)):
            msg = ("Width not defined. "
                   "Set with `position_dodge(width = ?)`")
            raise PlotnineError(msg)

        params = copy(self.params)

        if params['preserve'] == 'total':
            params['n'] = None
        else:
            params['n'] = data['xmin'].value_counts().max()

        return params

    @classmethod
    def compute_panel(cls, data, scales, params):
        return cls.collide(data, params=params)

    @staticmethod
    def strategy(data, params):
        """
        Dodge overlapping interval

        Assumes that each set has the same horizontal position.
        """
        width = params['width']
        with suppress(TypeError):
            iter(width)
            width = np.asarray(width)
            width = width[data.index]

        udata_group = data['group'].drop_duplicates()

        n = params.get('n', None)
        if n is None:
            n = len(udata_group)
        if n == 1:
            return data

        if not all([col in data.columns for col in ['xmin', 'xmax']]):
            data['xmin'] = data['x']
            data['xmax'] = data['x']

        d_width = np.max(data['xmax'] - data['xmin'])

        # Have a new group index from 1 to number of groups.
        # This might be needed if the group numbers in this set don't
        # include all of 1:n
        udata_group = udata_group.sort_values()
        groupidx = match(data['group'], udata_group)
        groupidx = np.asarray(groupidx) + 1

        # Find the center for each group, then use that to
        # calculate xmin and xmax
        data['x'] = data['x'] + width * ((groupidx - 0.5) / n - 0.5)
        data['xmin'] = data['x'] - (d_width / n) / 2
        data['xmax'] = data['x'] + (d_width / n) / 2

        return data
