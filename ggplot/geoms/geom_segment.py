from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from itertools import chain

import numpy as np
import matplotlib.collections as mcoll

from .geom import geom
from ..utils import make_rgba, make_line_segments


class geom_segment(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'linetype': 'solid',
                   'size': 1.0}
    REQUIRED_AES = {'x', 'y', 'xend', 'yend'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'arrow': None, 'lineend': 'butt'}

    guide_geom = 'path'

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **params):
        pinfo['color'] = make_rgba(pinfo['color'],
                                   pinfo['alpha'])
        x = list(chain(*zip(pinfo['x'], pinfo['xend'])))
        y = list(chain(*zip(pinfo['y'], pinfo['yend'])))
        segments = make_line_segments(x, y, ispath=False)
        coll = mcoll.LineCollection(segments,
                                    edgecolor=pinfo['color'],
                                    linewidth=pinfo['size'],
                                    linestyle=pinfo['linetype'],
                                    zorder=pinfo['zorder'])
        ax.add_collection(coll)

        if 'arrow' in params and params['arrow']:
            pinfo['group'] = np.tile(np.arange(1, len(pinfo['x'])+1), 2)
            pinfo['x'] = pinfo['x'] + pinfo['xend']
            pinfo['y'] = pinfo['y'] + pinfo['yend']
            other = ['color', 'size', 'linetype']
            for param in other:
                if isinstance(pinfo[param], list):
                    pinfo[param] = pinfo[param] * 2

            params['arrow'].draw(
                pinfo, scales, coordinates, ax, constant=False)
