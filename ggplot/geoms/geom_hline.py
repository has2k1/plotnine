from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.collections as mcoll

from ..utils import make_rgba, make_line_segments
from .geom import geom


class geom_hline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.5, 'alpha': 1, 'y': None,
                   'xmin': None, 'xmax': None}
    REQUIRED_AES = {'yintercept'}
    DEFAULT_PARAMS = {'stat': 'hline', 'position': 'identity',
                      'show_guide': False, 'inherit_aes': False}
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
        xmin = pinfo.get('xmin')
        xmax = pinfo.get('xmax')

        ranges = coordinates.range(scales)
        if xmin is None:
            xmin = ranges.x[0]
        if xmax is None:
            xmax = ranges.x[1]

        pinfo['color'] = make_rgba(pinfo['color'], pinfo['alpha'])

        y = np.repeat(pinfo['yintercept'], 2)
        x = np.zeros(len(y))
        x[::2], x[1::2] = xmin, xmax  # interleave
        segments = make_line_segments(x, y, ispath=False)
        coll = mcoll.LineCollection(segments,
                                    edgecolor=pinfo['color'],
                                    linewidth=pinfo['size'],
                                    linestyle=pinfo['linetype'],
                                    zorder=pinfo['zorder'])
        ax.add_collection(coll)
