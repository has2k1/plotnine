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
                   'linetype': 'solid', 'size': 1.5,
                   'ymin': None, 'ymax': None}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'smooth', 'position': 'identity'}

    _units = {'alpha', 'color', 'fill', 'linetype', 'size'}

    @staticmethod
    def draw_group(pinfo, panel_scales, coord, ax, **params):
        has_ribbon = (pinfo['ymin'] is not None and
                      pinfo['ymax'] is not None)
        if has_ribbon:
            pinfo2 = deepcopy(pinfo)
            pinfo2['color'] = ''
            geom_ribbon.draw_group(pinfo2, panel_scales,
                                   coord, ax, **params)

        pinfo['alpha'] = 1
        geom_line.draw_group(pinfo, panel_scales, coord, ax, **params)

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
                           facecolor=data['fill'],
                           edgecolor=data['color'])
            da.add_artist(bg)

        data.is_copy = False
        data['alpha'] = 1
        return geom_path.draw_legend(data, da, lyr)
