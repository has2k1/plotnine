from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.collections import LineCollection
import matplotlib.lines as lines

from ..utils import make_color_tuples
from .geom import geom


class geom_path(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'linetype': 'solid',
                   'size': 1.0}

    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    guide_geom = 'path'

    _aes_renames = {'color': 'edgecolor', 'size': 'linewidth',
                    'linetype': 'linestyle'}

    @staticmethod
    def draw(pinfo, scales, ax, **kwargs):
        x = pinfo.pop('x')
        y = pinfo.pop('y')

        pinfo['edgecolor'] = make_color_tuples(pinfo['edgecolor'],
                                               pinfo['alpha'])

        lines = [((x[i], y[i]), (x[i+1], y[i+1])) for i in range(len(x)-1)]
        lines = LineCollection(lines,
                               edgecolor=pinfo['edgecolor'],
                               linewidths=pinfo['linewidth'],
                               linestyles=pinfo['linestyle'])
        ax.add_collection(lines)

    @staticmethod
    def draw_legend(data, params, da):
        """
        Draw a horizontal line in the box

        Parameters
        ----------
        data : dataframe
        params : dict
        da : DrawingArea

        Returns
        -------
        out : DrawingArea
        """
        x = [0, da.width]
        y = [0.5 * da.height] * 2
        key = lines.Line2D(x,
                           y,
                           alpha=data['alpha'],
                           linestyle=data['linestyle'],
                           linewidth=data['linewidth'],
                           color=data['edgecolor'],
                           solid_capstyle='butt',
                           antialiased=False)
        da.add_artist(key)
        return da
