from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.lines as mlines

from ..utils import to_rgba
from .geom import geom


class geom_point(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'shape': 'o', 'size': 5, 'stroke': 1}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _units = {'shape'}

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups
        """
        data = coord.transform(data, panel_scales)
        pinfos = self._make_pinfos(data, params)
        for pinfo in pinfos:
            self.draw_group(pinfo, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_group(pinfo, panel_scales, coord, ax, **params):
        pinfo['fill'] = to_rgba(pinfo['fill'], pinfo['alpha'])
        pinfo['color'] = to_rgba(pinfo['color'], pinfo['alpha'])

        # A single RGBA color will be seen as 4 locations in a
        # colormap by MPL if there are 4 points. We don't
        # want that
        if len(pinfo['x']) == 4:
            if isinstance(pinfo['fill'], tuple):
                pinfo['fill'] = [list(pinfo['fill'])] * 4
            if isinstance(pinfo['color'], tuple):
                pinfo['color'] = [list(pinfo['color'])] * 4

        if pinfo['fill'] is None:
            pinfo['fill'] = pinfo['color']

        ax.scatter(x=pinfo['x'],
                   y=pinfo['y'],
                   facecolor=pinfo['fill'],
                   edgecolor=pinfo['color'],
                   linewidth=pinfo['stroke'],
                   marker=pinfo['shape'],
                   # Our size is in 'points' while
                   # scatter wants 'points^2'. The
                   # stroke is outside.
                   s=np.square(
                       np.array(pinfo['size']) +
                       pinfo['stroke']),
                   zorder=pinfo['zorder'])

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
                            markersize=data['size'],
                            markerfacecolor=data['fill'],
                            markeredgecolor=data['color'],
                            markeredgewidth=data['stroke'])
        da.add_artist(key)
        return da
