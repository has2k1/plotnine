from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.lines as mlines

from ..utils import to_rgba, groupby_with_null
from .geom import geom


class geom_point(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'shape': 'o', 'size': 5, 'stroke': 1}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    @staticmethod
    def draw_group(data, panel_scales, coord, ax, **params):
        data = coord.transform(data, panel_scales)
        units = 'shape'
        for _, udata in groupby_with_null(data, units):
            udata.is_copy = None
            udata.reset_index(inplace=True, drop=True)
            geom_point.draw_unit(udata, panel_scales, coord,
                                 ax, **params)

    @staticmethod
    def draw_unit(data, panel_scales, coord, ax, **params):
        fill = to_rgba(data['fill'], data['alpha'])
        color = to_rgba(data['color'], data['alpha'])

        if fill is None:
            fill = color

        ax.scatter(x=data['x'],
                   y=data['y'],
                   facecolor=fill,
                   edgecolor=color,
                   linewidth=data['stroke'],
                   marker=data.loc[0, 'shape'],
                   # Our size is in 'points' while
                   # scatter wants 'points^2'. The
                   # stroke is outside.
                   s=np.square(
                       np.array(data['size']) +
                       data['stroke']),
                   zorder=params['zorder'])

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw a point in the box

        Parameters
        ----------
        data : dataframe
        params : dict
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        if data['fill'] is None:
            data['fill'] = data['color']

        key = mlines.Line2D([0.5*da.width],
                            [0.5*da.height],
                            alpha=data['alpha'],
                            marker=data['shape'],
                            markersize=data['size']+data['stroke'],
                            markerfacecolor=data['fill'],
                            markeredgecolor=data['color'],
                            markeredgewidth=data['stroke'])
        da.add_artist(key)
        return da
