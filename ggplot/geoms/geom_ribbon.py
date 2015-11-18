from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import to_rgba
from .geom import geom


class geom_ribbon(geom):
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.5}
    REQUIRED_AES = {'x', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    legend_geom = 'polygon'

    _units = {'color', 'fill', 'linetype', 'size'}

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, params)
        for pinfo in pinfos:
            self.draw_group(pinfo, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_group(pinfo, panel_scales, coord, ax, **params):
        pinfo['fill'] = to_rgba(pinfo['fill'], pinfo['alpha'])
        pinfo['color'] = to_rgba(pinfo['color'], pinfo['alpha'])
        if pinfo['fill'] is None:
            pinfo['fill'] = ''

        ax.fill_between(x=pinfo['x'],
                        y1=pinfo['ymin'],
                        y2=pinfo['ymax'],
                        facecolor=pinfo['fill'],
                        edgecolor=pinfo['color'],
                        linewidth=pinfo['size'],
                        linestyle=pinfo['linetype'],
                        zorder=pinfo['zorder'])
