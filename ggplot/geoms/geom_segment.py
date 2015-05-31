from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.collections as mcoll

from .geom import geom
from ..utils import make_color_tuples


class geom_segment(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'linetype': 'solid',
                   'size': 1.0}
    REQUIRED_AES = {'x', 'y', 'xend', 'yend'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'arrow': None, 'lineend': 'butt'}

    guide_geom = 'path'
    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'color': 'edgecolor'}

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **kwargs):
        pinfo['edgecolor'] = make_color_tuples(pinfo['edgecolor'],
                                               pinfo['alpha'])
        segments = np.zeros((len(pinfo['x']), 2, 2))
        segments[:, 0, 0] = pinfo['x']
        segments[:, 0, 1] = pinfo['y']
        segments[:, 1, 0] = pinfo['xend']
        segments[:, 1, 1] = pinfo['yend']
        coll = mcoll.LineCollection(segments,
                                    edgecolor=pinfo['edgecolor'],
                                    linewidth=pinfo['linewidth'],
                                    linestyle=pinfo['linestyle'],
                                    zorder=pinfo['zorder'])
        ax.add_collection(coll)

        if 'arrow' in kwargs and kwargs['arrow']:
            pinfo['group'] = list(range(1, len(pinfo['x'])+1)) * 2
            pinfo['x'] = pinfo['x'] + pinfo['xend']
            pinfo['y'] = pinfo['y'] + pinfo['yend']
            other = ['edgecolor', 'linewidth', 'linestyle']
            for param in other:
                if isinstance(pinfo[param], list):
                    pinfo[param] = pinfo[param] * 2

            kwargs['arrow'].draw(
                pinfo, scales, coordinates, ax, constant=False)
