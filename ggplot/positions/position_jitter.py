from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

from ..utils import jitter
from ..scales.utils import resolution
from .position import position


class position_jitter(position):
    REQUIRED_AES = {'x', 'y'}

    def __init__(self, width=None, height=None):
        self.params = {'width': width, 'height': height}

    def setup_params(self, data):
        params = deepcopy(self.params)
        if not params['width']:
            params['width'] = resolution(data['x']) * .4
        if not self.params['height']:
            params['height'] = resolution(data['y']) * .4
        return params

    @classmethod
    def compute_layer(cls, data, params, panel):
        trans_x = None
        trans_y = None

        if params['width']:
            def trans_x(x):
                return jitter(x, params['width'])

        if params['height']:
            def trans_y(y):
                return jitter(y, params['height'])

        return cls.transform_position(data, trans_x, trans_y)
