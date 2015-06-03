from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from itertools import chain

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
    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'color': 'edgecolor'}

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **kwargs):
        pinfo['edgecolor'] = make_rgba(pinfo['edgecolor'],
                                       pinfo['alpha'])
        x = list(chain(*zip(pinfo['x'], pinfo['xend'])))
        y = list(chain(*zip(pinfo['y'], pinfo['yend'])))
        segments = make_line_segments(x, y, ispath=False)
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
