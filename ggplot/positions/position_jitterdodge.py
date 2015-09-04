from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import numpy as np

from ..utils import jitter
from ..scales.utils import resolution
from .position import position
from .collide import collide, pos_dodge


# Adjust position by simultaneously dodging and jittering
class position_jitterdodge(position):
    REQUIRED_AES = ['x', 'y', 'fill']

    def __init__(self, jitter_width=None, jitter_height=0,
                 dodge_width=0.75):
        self.params = {'jitter_width': jitter_width,
                       'jitter_height': jitter_height,
                       'dodge_width': dodge_width}

    def setup_params(self, data):
        params = deepcopy(self.params)
        width = params['jitter_width']
        if width is None:
            width = resolution(data['x']) * .4

        # Adjust the x transformation based on the number
        # of 'fill' variables
        try:
            nfill = len(data['fill'].cat.categories)
        except AttributeError:
            nfill = len(np.unique(data['fill']))

        params['jitter_width'] = width/(nfill+2)
        return params

    @classmethod
    def compute_panel(cls, data, scales, params):
        trans_x = None
        trans_y = None

        if params['jitter_width'] > 0:
            def trans_x(x):
                return jitter(x, amount=params['jitter_width'])

        if params['jitter_height'] > 0:
            def trans_y(y):
                return jitter(y, amount=params['jitter_height'])

        # dodge, then jitter
        data = collide(data, width=params['dodge_width'],
                       name='position_jitterdodge',
                       strategy=pos_dodge)
        data = cls.transform_position(data, trans_x, trans_y)
        return data
