from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pandas.lib import Timestamp
import matplotlib.cbook as cbook
import numpy as np
from .geom import geom

# Note when documenting
# slope and intercept can be functions that compute the slope
# and intercept using the data
class geom_abline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'alpha': None, 'size': 1.0}
    REQUIRED_AES = {'slope', 'intercept'}
    DEFAULT_PARAMS = {'stat': 'abline', 'position': 'identity'}

    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        slope = pinfo['slope']
        intercept = pinfo['intercept']

        n = len(slope)
        def _make_iterable_ntimes(val):
            if cbook.iterable(val) and not cbook.is_string_like(val):
                return val
            return [val] * n

        linewidth = _make_iterable_ntimes(pinfo['linewidth'])
        linestyle = _make_iterable_ntimes(pinfo['linestyle'])
        alpha = _make_iterable_ntimes(pinfo['alpha'])
        color = _make_iterable_ntimes(pinfo['color'])

        ax.set_autoscale_on(False)
        xlim = ax.get_xlim()

        _x = np.array([np.min(xlim), np.max(xlim)])
        for i in range(len(slope)):
            _y = _x * slope[i] + intercept[i]
            ax.plot(_x, _y,
                    linewidth=linewidth[i],
                    linestyle=linestyle[i],
                    alpha=alpha[i],
                    color=color[i])
