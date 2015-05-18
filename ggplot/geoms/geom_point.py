from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.lines as lines

from ..utils import make_color_tuples
from .geom import geom


class geom_point(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'shape': 'o', 'size': 20}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {'size': 's', 'shape': 'marker', 'fill': 'facecolor'}
    _units = {'marker'}

    def draw_groups(self, data, scales, coordinates, ax, **kwargs):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, kwargs)
        for pinfo in pinfos:
            self.draw(pinfo, scales, coordinates, ax, **kwargs)

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **kwargs):
        pinfo['facecolor'] = make_color_tuples(
            pinfo['facecolor'], pinfo['alpha'])

        if pinfo['facecolor'] is None:
            pinfo['facecolor'] = pinfo['color']

        del pinfo['group']
        ax.scatter(**pinfo)

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
        key = lines.Line2D([0.5*da.width],
                           [0.5*da.height],
                           alpha=data['alpha'],
                           marker=data['marker'],
                           # scatter size units are points^2, while
                           # Line2D size units are points
                           markersize=np.sqrt(data['s']),
                           color=data['color'],
                           markerfacecolor=data['facecolor'],
                           markeredgecolor=data['color'])
        da.add_artist(key)
        return da
