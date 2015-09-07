from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .position import position


class position_nudge(position):
    REQUIRED_AES = {'x', 'y'}

    def __init__(self, x=0, y=0):
        self.params = {'x': x, 'y': y}

    @classmethod
    def compute_layer(cls, data, params, panel):
        def trans_x(x):
            return x + params['x']

        def trans_y(y):
            return y + params['y']

        return cls.transform_position(data, trans_x, trans_y)
