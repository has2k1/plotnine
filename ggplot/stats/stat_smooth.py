from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
from ggplot.components import smoothers
from .stat import stat


class stat_smooth(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'smooth', 'position': 'identity', 'method': 'auto',
            'se': True, 'n': 80, 'fullrange': False, 'level': 0.95,
            'span': 2/3., 'window': None}
    CREATES = {'ymin', 'ymax'}

    def _calculate(self, pinfo):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        se = self.params['se']
        level = self.params['level']
        method = self.params['method']
        span = self.params['span']
        window = self.params['window']

        if window is None:
            window = int(np.ceil(len(x) / 10.0))

        idx = np.argsort(x)
        x = np.array(x)[idx]
        y = np.array(y)[idx]

        if method == "lm":
            y, y1, y2 = smoothers.lm(x, y, 1-level)
        elif method == "ma":
            y, y1, y2 = smoothers.mavg(x, y, window=window)
        else:
            y, y1, y2 = smoothers.lowess(x, y, span=span)

        pinfo['x'] = x
        pinfo['y'] = y
        if se:
            pinfo['ymin'] = y1
            pinfo['ymax'] = y2
        return pinfo
