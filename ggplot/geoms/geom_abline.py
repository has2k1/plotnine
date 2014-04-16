from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pandas.lib import Timestamp
import numpy as np
from .geom import geom


class geom_abline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid', 'alpha': None, 'size': 1.0}
    REQUIRED = {'x'} # TODO: Why is x needed.
    DEFAULT_PARAMS = {'stat': 'abline', 'position': 'identity', 'slope': 1.0, 'intercept': 0.0, 'label': ''}

    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth'}
    _groups = {'alpha', 'color', 'linestyle', 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
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

