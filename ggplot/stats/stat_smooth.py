from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd

from ..components import smoothers
from .stat import stat


class stat_smooth(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'smooth', 'position': 'identity',
                      'method': 'auto', 'se': True, 'n': 80,
                      'fullrange': False, 'level': 0.95,
                      'span': 2/3., 'window': None}
    CREATES = {'ymin', 'ymax'}

    def _calculate(self, data, scales, **kwargs):
        # sort data by x and
        # convert x and y to lists so that the Series index
        # does not mess with the smoothing functions
        data = data.sort(['x'])
        x = list(data.pop('x'))
        y = list(data.pop('y'))

        se = self.params['se']
        level = self.params['level']
        method = self.params['method']
        span = self.params['span']
        window = self.params['window']
        weight = data.get('weight', 1)  # should make use of this

        if window is None:
            window = int(np.ceil(len(x) / 10.0))

        # TODO: fix the smoothers
        #   - lm : y1, y2 are NaNs
        #   - mvg: investigate unexpected looking output
        if method == "lm":
            x, y, y1, y2 = smoothers.lm(x, y, 1-level)
        elif method == "ma":
            x, y, y1, y2 = smoothers.mavg(x, y, window=window)
        else:
            # TODO: deal with timestamp
            x, y, y1, y2 = smoothers.lowess(x, y, span=span)

        new_data = pd.DataFrame({'x': x, 'y': y})
        if se:
            new_data['ymin'] = y1
            new_data['ymax'] = y2

        return new_data
