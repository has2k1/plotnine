from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.patches import Rectangle

from ..utils import groupby_with_null
from .geom import geom
from .geom_ribbon import geom_ribbon
from .geom_line import geom_line
from .geom_line import geom_path


class geom_smooth(geom):
    DEFAULT_AES = {'alpha': 0.4, 'color': 'black', 'fill': '#999999',
                   'linetype': 'solid', 'size': 1,
                   'ymin': None, 'ymax': None}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'smooth', 'position': 'identity'}

    @staticmethod
    def draw_group(data, panel_scales, coord, ax, **params):
        data = coord.transform(data, panel_scales)
        units = ['color', 'fill', 'linetype', 'size']
        for _, udata in groupby_with_null(data, units):
            udata.is_copy = None
            udata.reset_index(inplace=True, drop=True)
            geom_smooth.draw_unit(udata, panel_scales, coord,
                                  ax, **params)

    @staticmethod
    def draw_unit(data, panel_scales, coord, ax, **params):
        has_ribbon = (data.ix[0, 'ymin'] is not None and
                      data.ix[0, 'ymax'] is not None)
        if has_ribbon:
            data2 = data.copy()
            data2['color'] = ''
            geom_ribbon.draw_group(data2, panel_scales,
                                   coord, ax, **params)

        data['alpha'] = 1
        geom_line.draw_group(data, panel_scales, coord, ax, **params)

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
                           linewidth=0)
            da.add_artist(bg)

        data['alpha'] = 1
        return geom_path.draw_legend(data, da, lyr)
