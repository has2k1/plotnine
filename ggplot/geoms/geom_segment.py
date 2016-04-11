from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
import matplotlib.collections as mcoll

from .geom import geom
from ..utils import to_rgba, make_line_segments, interleave
from ..utils import SIZE_FACTOR


class geom_segment(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'linetype': 'solid',
                   'size': 0.5}
    REQUIRED_AES = {'x', 'y', 'xend', 'yend'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'arrow': None, 'lineend': 'butt'}

    legend_geom = 'path'

    @staticmethod
    def draw_group(data, panel_scales, coord, ax, **params):
        data = coord.transform(data, panel_scales)
        data['size'] *= SIZE_FACTOR
        color = to_rgba(data['color'], data['alpha'])

        # start point -> end point, sequence of xy points
        # from which line segments are created
        x = interleave(data['x'], data['xend'])
        y = interleave(data['y'], data['yend'])
        segments = make_line_segments(x, y, ispath=False)
        coll = mcoll.LineCollection(segments,
                                    edgecolor=color,
                                    linewidth=data['size'],
                                    linestyle=data['linetype'][0],
                                    zorder=params['zorder'])
        ax.add_collection(coll)

        if 'arrow' in params and params['arrow']:
            adata = pd.DataFrame(index=range(len(data)*2))
            idx = np.arange(1, len(data)+1)
            adata['group'] = np.hstack([idx, idx])
            adata['x'] = np.hstack([data['x'], data['xend']])
            adata['y'] = np.hstack([data['y'], data['yend']])
            other = ['color', 'alpha', 'size', 'linetype']
            for param in other:
                adata[param] = np.hstack([data[param], data[param]])

            params['arrow'].draw(
                adata, panel_scales, coord, ax, constant=False)
