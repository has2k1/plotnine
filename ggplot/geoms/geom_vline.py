from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.collections as mcoll

from ..utils import make_rgba, make_line_segments
from .geom import geom


class geom_vline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.0, 'alpha': 1, 'x': None,
                   'ymin': None, 'ymax': None}
    REQUIRED_AES = {'xintercept'}
    DEFAULT_PARAMS = {'stat': 'vline', 'position': 'identity',
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
        ymin = pinfo.get('ymin')
        ymax = pinfo.get('ymax')

        ranges = coordinates.range(scales)
        if ymin is None:
            ymin = ranges.y[0]
        if ymax is None:
            ymax = ranges.y[1]

        pinfo['color'] = make_rgba(pinfo['color'], pinfo['alpha'])

        x = np.repeat(pinfo['xintercept'], 2)
        y = np.zeros(len(x))
        y[::2], y[1::2] = ymin, ymax  # interleave
        segments = make_line_segments(x, y, ispath=False)
        coll = mcoll.LineCollection(segments,
                                    edgecolor=pinfo['color'],
                                    linewidth=pinfo['size'],
                                    linestyle=pinfo['linetype'],
                                    zorder=pinfo['zorder'])
        ax.add_collection(coll)
