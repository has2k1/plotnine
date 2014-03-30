from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom
from scipy.stats import gaussian_kde
import numpy as np


class geom_density(geom):
    DEFAULT_AES = {'alpha': None, 'color': 'black', 'fill': None,
                   'linetype': 'solid', 'size': 1.0, 'weight': 1}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'density', 'position': 'identity', 'label': ''}

    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'fill': 'facecolor'}
    _groups = {'alpha', 'color', 'facecolor', 'linestyle', 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y = pinfo.pop('y')

        # Only meant to for the stat
        pinfo.pop('weight')

        # These do not apply to the line
        _alpha = pinfo.pop('alpha')
        _fc = pinfo.pop('facecolor')

        ax.plot(x, y, **pinfo)

        if _fc not in (None, False):
            _c = pinfo.pop('color')
            pinfo.pop('linewidth')
            pinfo['alpha'] = _alpha
            pinfo['facecolor'] = _c if _fc == True else _fc
            ax.fill_between(x, y1=np.zeros(len(x)), y2=y, **pinfo)
