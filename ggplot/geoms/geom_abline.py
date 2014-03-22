from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pandas.lib import Timestamp
import numpy as np
from .geom import geom
import pandas as pd

class geom_abline(geom):
    VALID_AES = {'x', 'color', 'linetype', 'alpha', 'size'}
    DEFAULT_PARAMS = {'stat': 'abline', 'position': 'identity', 'slope': 1.0, 'intercept': 0.0, 'label': ''}

    _groups = {'color', 'linestyle', 'alpha'}
    _aes_renames = {'linetype': 'linestyle'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop(x)
        slope = self.params['slope']
        intercept = self.params['intercept']
        pinfo['label'] = self.params['label']
        if isinstance(x[0], Timestamp):
            ax.set_autoscale_on(False)
            ax.plot(ax.get_xlim(),ax.get_ylim())
        else:
            start, stop = np.max(x), np.min(x)
            step = ((stop-start))  / 100.0
            x_rng = np.arange(start, stop, step)
            y_rng = x_rng * slope + intercept
            ax.plot(x_rng, y_rng, **pinfo)

