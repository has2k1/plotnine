from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
import matplotlib.collections as mcoll

from ..utils import make_rgba, make_line_segments, suppress
from ..utils import make_iterable
from ..components import aes
from .geom import geom
from .geom_segment import geom_segment


# Note when documenting
# slope and intercept can be functions that compute the slope
# and intercept using the data. If that is the case then the
# x and y aesthetics must be mapped
class geom_abline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'alpha': 1, 'size': 1.5, 'x': None,
                   'y': None}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'inherit_aes': False}
    _extra_requires = {'slope', 'intercept'}
    guide_geom = 'path'

    def __init__(self, *args, **kwargs):
        with suppress(KeyError):
            intercept = make_iterable(kwargs.pop('intercept'))
            data = pd.DataFrame({'intercept': intercept,
                                 'slope': kwargs.pop('slope')})
            kwargs['mapping'] = aes(intercept='intercept', slope='slope')
            kwargs['data'] = data

        geom.__init__(self, *args, **kwargs)

    def draw_groups(self, data, scales, coordinates, ax, **params):
        """
        Plot all groups
        """
        data['x'] = scales['x_range'][0]
        data['xend'] = scales['x_range'][1]
        data['y'] = scales['x_range'][0] * data['slope'] + data['intercept']
        data['yend'] = scales['x_range'][1] * data['slope'] + data['intercept']
        data.drop_duplicates(inplace=True)

        for _, gdata in data.groupby('group'):
            pinfos = self._make_pinfos(gdata, params)
            for pinfo in pinfos:
                geom_segment.draw(pinfo, scales, coordinates, ax, **params)

        # pinfos = self._make_pinfos(data, params)
        # for pinfo in pinfos:
        #     self.draw(pinfo, scales, coordinates, ax, **params)

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
