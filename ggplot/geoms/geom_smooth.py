from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

from matplotlib.patches import Rectangle

from .geom import geom
from .geom_ribbon import geom_ribbon
from .geom_line import geom_line
from .geom_line import geom_path


class geom_smooth(geom):
    DEFAULT_AES = {'alpha': 0.4, 'color': 'black', 'fill': '#999999',
                   'linetype': 'solid', 'size': 1.0,
                   'ymin': None, 'ymax': None}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'smooth', 'position': 'identity'}
    guide_geom = 'smooth'

    _aes_renames = {'linetype': 'linestyle', 'fill': 'facecolor',
                    'color': 'edgecolor', 'size': 'linewidth',
                    'ymin': 'y1', 'ymax': 'y2'}
    _units = {'alpha', 'edgecolor', 'facecolor', 'linestyle', 'linewidth'}

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **kwargs):
        has_ribbon = (pinfo['y1'] is not None) and (pinfo['y2'] is not None)
        if has_ribbon:
            pinfo2 = deepcopy(pinfo)
            pinfo2['edgecolor'] = ''
            geom_ribbon.draw(pinfo2, scales, coordinates, ax, **kwargs)

        pinfo['alpha'] = 1
        geom_line.draw(pinfo, scales, coordinates, ax, **kwargs)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw letter 'a' in the box

        Parameters
        ----------
        data : dataframe
        params : dict
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        if lyr.stat.params['se']:
            bg = Rectangle((0, 0),
                           width=da.width,
                           height=da.height,
                           alpha=data['alpha'],
                           facecolor=data['facecolor'],
                           edgecolor=data['facecolor'])
            da.add_artist(bg)

        data.is_copy = False
        data['alpha'] = 1
        return geom_path.draw_legend(data, da, lyr)
