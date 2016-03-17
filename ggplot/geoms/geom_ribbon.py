from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import to_rgba, groupby_with_null
from .geom import geom


class geom_ribbon(geom):
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.5}
    REQUIRED_AES = {'x', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    legend_geom = 'polygon'

    _munch = True

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups
        """
        data = coord.transform(data, panel_scales, self._munch)
        self.draw_group(data, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_group(data, panel_scales, coord, ax, **params):
        units = ['color', 'fill', 'linetype', 'size']
        for _, udata in groupby_with_null(data, units):
            udata.is_copy = None
            udata.reset_index(inplace=True, drop=True)
            geom_ribbon.draw_unit(udata, panel_scales, coord,
                                  ax, **params)

    @staticmethod
    def draw_unit(data, panel_scales, coord, ax, **params):
        fill = to_rgba(data['fill'], data['alpha'])
        color = to_rgba(data['color'], data['alpha'])

        if fill is None:
            fill = ''

        ax.fill_between(x=data['x'],
                        y1=data['ymin'],
                        y2=data['ymax'],
                        facecolor=fill,
                        edgecolor=color,
                        linewidth=data['size'].iloc[0],
                        linestyle=data['linetype'].iloc[0],
                        zorder=params['zorder'])
