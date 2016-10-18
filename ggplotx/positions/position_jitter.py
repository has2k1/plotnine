from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import numpy as np

from ..utils import jitter, resolution
from .position import position


class position_jitter(position):
    """
    Jitter points to avoid overplotting

    Parameters
    ----------
    width : float
        Proportion to jitter in horizontal direction.
        Default is ``0.4`` of the resolution of the data.
    height : float
        Proportion to jitter in vertical direction.
        Default is ``0.4`` of the resolution of the data.
    prng : numpy.random.RandomState
        Random number generator to use. If `None`, then numpy
        global generator (``np.random``) is used.
    """
    REQUIRED_AES = {'x', 'y'}

    def __init__(self, width=None, height=None, prng=None):
        self.params = {'width': width,
                       'height': height,
                       'prng': prng}

    def setup_params(self, data):
        params = deepcopy(self.params)
        if not params['width']:
            params['width'] = resolution(data['x']) * .4
        if not params['height']:
            params['height'] = resolution(data['y']) * .4
        if not params['prng']:
            params['prng'] = np.random
        return params

    @classmethod
    def compute_layer(cls, data, params, layout):
        trans_x = None
        trans_y = None

        if params['width']:
            def trans_x(x):
                return jitter(x, params['width'], prng=params['prng'])

        if params['height']:
            def trans_y(y):
                return jitter(y, params['height'], prng=params['prng'])

        return cls.transform_position(data, trans_x, trans_y)
