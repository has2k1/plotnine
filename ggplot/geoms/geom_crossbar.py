from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.lines as mlines
from matplotlib.patches import Rectangle

from ..scales.utils import resolution
from ..utils import to_rgba
from .geom import geom
from .geom_polygon import geom_polygon
from .geom_segment import geom_segment


class geom_crossbar(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'linetype': 'solid', 'size': 1.5}
    REQUIRED_AES = {'x', 'y', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'width': 0.5, 'fatten': 2}

    def reparameterise(self, data):
        if 'width' not in data:
            if self.params['width']:
                data['width'] = self.params['width']
            else:
                data['width'] = resolution(data['x'], False) * 0.9

        data['xmin'] = data['x'] - data['width']/2
        data['xmax'] = data['x'] + data['width']/2
        del data['width']
        return data

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **params):
        keys = ['alpha', 'color', 'fill', 'size',
                'linetype', 'zorder']

        def copy_keys(d):
            for k in keys:
                d[k] = pinfo[k]

        middle = {'x': pinfo['xmin'],
                  'y': pinfo['y'],
                  'xend': pinfo['xmax'],
                  'yend': pinfo['y'],
                  'group': pinfo['group']}
        copy_keys(middle)
        middle['size'] = np.asarray(middle['size'])*params['fatten'],

        # No notch
        box = {'x': pinfo['xmin']*2 + pinfo['xmax']*2 + pinfo['xmin'],
               'y': pinfo['ymax'] + pinfo['ymax']*2 + pinfo['ymin']*2,
               'group': np.tile(np.arange(1, len(pinfo['group'])+1), 5)}
        copy_keys(box)

        geom_polygon.draw(box, scales, coordinates, ax, **params)
        geom_segment.draw(middle, scales, coordinates, ax, **params)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw a rectangle with a horizontal strike in the box

        Parameters
        ----------
        data : dataframe
        da : DrawingArea
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        # background
        facecolor = to_rgba(data['fill'], data['alpha'])
        if facecolor is None:
            facecolor = 'none'

        bg = Rectangle((da.width*.125, da.height*.25),
                       width=da.width*.75,
                       height=da.height*.5,
                       linewidth=data['size'],
                       facecolor=facecolor,
                       edgecolor=data['color'],
                       linestyle=data['linetype'],
                       capstyle='projecting',
                       antialiased=False)
        da.add_artist(bg)

        strike = mlines.Line2D([da.width*.125, da.width*.875],
                               [da.height*.5, da.height*.5],
                               linestyle=data['linetype'],
                               linewidth=data['size'],
                               color=data['color'])
        da.add_artist(strike)
        return da
