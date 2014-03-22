from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom import geom
from ggplot.components import smoothers

import numpy as np

class stat_smooth(geom):
    VALID_AES = {'x', 'y', 'alpha', 'color', 'fill', 'linetype',
                 'size', 'weight'}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'smooth', 'position': 'identity', 'method': 'auto',
            'se': True, 'n': 80, 'fullrange': False, 'level': 0.95,
            'span': 2/3., 'window': None, 'label': ''}

    _groups = {'color', 'fill', 'linetype'}
    _aes_renames = {'linetype': 'linestyle'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        se = self.params['se']
        level = self.params['level']
        method = self.params['method']
        span = self.params['span']
        window = self.params['window']
        pinfo['label'] = self.params['label']

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
        ax.plot(x, y, **pinfo)
        if se==True:
            ax.fill_between(x, y1, y2, alpha=0.2, color="grey",
                             label=pinfo['label'])
