from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom import geom
from ggplot.components import smoothers

import numpy as np

class stat_smooth(geom):
    DEFAULT_AES = {'alpha': 0.4, 'color': 'black', 'fill': '#999999',
                   'linetype': 'solid', 'size': 1.0}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'smooth', 'position': 'identity', 'method': 'auto',
            'se': True, 'n': 80, 'fullrange': False, 'level': 0.95,
            'span': 2/3., 'window': None, 'label': ''}

    _aes_renames = {'linetype': 'linestyle', 'fill': 'facecolor',
                    'size': 'linewidth'}
    _groups = {'color', 'facecolor', 'linestyle', 'linewidth'}

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

        facecolor = pinfo.pop('facecolor')
        alpha = pinfo.pop('alpha')
        ax.plot(x, y, **pinfo)

        if se==True:
            pinfo.pop('color')
            pinfo.pop('linewidth')
            pinfo['facecolor'] = facecolor
            pinfo['alpha'] = alpha
            ax.fill_between(x, y1, y2, **pinfo)
