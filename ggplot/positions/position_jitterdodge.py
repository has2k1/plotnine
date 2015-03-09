from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd

from ..utils import jitter, check_required_aesthetics
from ..scales.utils import resolution
from .position import position
from .collide import collide, pos_dodge


# Adjust position by simultaneously dodging and jittering
class position_jitterdodge(position):

    def __init__(self,
                 jitter_width=None,
                 jitter_height=None,
                 dodge_width=None):
        self.jitter_width = jitter_width
        self.jitter_height = jitter_height
        self.dodge_width = dodge_width

    def adjust(self, data):
        if len(data) == 0:
            return pd.DataFrame()

        check_required_aesthetics(
            ['x', 'y', 'fill'], data.columns,
            'position_jitterdodge')

        # Workaround to avoid this warning:
        # ymax not defined: adjusting position using y instead
        if not ('ymax' in data):
            data['ymax'] = data['y']

        # Adjust the x transformation based on the number
        # of 'fill' variables
        nfill = len(data['fill'].cat.categories)

        if self.jitter_width is None:
            self.jitter_width = resolution(data['x'], zero=False) * 0.4

        if self.jitter_height is None:
            self.jitter_height = 0

        trans_x = None
        trans_y = None

        if self.jitter_width > 0:
            amount = self.jitter_width / (nfill + 2)
            trans_x = lambda x: jitter(x, amount=amount)

        if self.jitter_height > 0:
            trans_y = lambda x: jitter(x, amount=self.jitter_height)

        if self.dodge_width is None:
            self.dodge_width = 0.75

        # dodge, then jitter
        data = collide(data, width=self.dodge_width,
                       name='position_jitterdodge',
                       strategy=pos_dodge)
        data = self._transform_position(data, trans_x, trans_y)
        return data
