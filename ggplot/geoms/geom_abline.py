from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.collections as mcoll

from ..utils import make_line_segments, make_rgba
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
    DEFAULT_PARAMS = {'stat': 'abline', 'position': 'identity',
                      'inherit_aes': False}
    guide_geom = 'path'

    def draw_groups(self, data, scales, coordinates, ax, **params):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, params)
        for pinfo in pinfos:
            self.draw(pinfo, scales, coordinates, ax, **params)

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **params):
        ranges = coordinates.range(scales)
        n = len(pinfo['slope'])
        slope = np.asarray(pinfo['slope'])
        intercept = np.asarray(pinfo['intercept'])
        x = np.array(ranges.x)
        x = np.tile(x, (n, 1))
        y = np.zeros(x.shape)
        y[:, 0] = x[:, 0] * slope + intercept
        y[:, 1] = x[:, 1] * slope + intercept
        segments = make_line_segments(x.ravel(),
                                      y.ravel(),
                                      ispath=False)
        pinfo['color'] = make_rgba(pinfo['color'],
                                   pinfo['alpha'])
        coll = mcoll.LineCollection(segments,
                                    edgecolor=pinfo['color'],
                                    linewidth=pinfo['size'],
                                    linestyle=pinfo['linetype'],
                                    zorder=pinfo['zorder'])
        ax.add_collection(coll)
