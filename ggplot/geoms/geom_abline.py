from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from ..utils import make_iterable_ntimes
from .geom import geom


# Note when documenting
# slope and intercept can be functions that compute the slope
# and intercept using the data. If that is the case then the
# x and y aesthetics must be mapped
class geom_abline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'alpha': 1, 'size': 1.0, 'x': None,
                   'y': None}
    REQUIRED_AES = {'slope', 'intercept'}
    DEFAULT_PARAMS = {'stat': 'abline', 'position': 'identity'}

    layer_params = {'inherit_aes': False}

    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth'}

    def draw_groups(self, data, scales, ax, **kwargs):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, kwargs)
        for pinfo in pinfos:
            self.draw(pinfo, scales, ax, **kwargs)

    def draw(self, pinfo, scales, ax, **kwargs):
        slope = pinfo['slope']
        intercept = pinfo['intercept']
        range_x = scales['x'].coord_range()
        zorder = pinfo['zorder']

        n = len(slope)

        linewidth = make_iterable_ntimes(pinfo['linewidth'], n)
        linestyle = make_iterable_ntimes(pinfo['linestyle'], n)
        alpha = make_iterable_ntimes(pinfo['alpha'], n)
        color = make_iterable_ntimes(pinfo['color'], n)

        _x = np.array(range_x)
        for i in range(n):
            _y = _x * slope[i] + intercept[i]
            ax.plot(_x, _y,
                    linewidth=linewidth[i],
                    linestyle=linestyle[i],
                    alpha=alpha[i],
                    color=color[i],
                    zorder=zorder)
