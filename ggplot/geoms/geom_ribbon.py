from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import to_rgba
from .geom import geom


class geom_ribbon(geom):
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.5}
    REQUIRED_AES = {'x', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    guide_geom = 'polygon'

    _units = {'color', 'fill', 'linetype', 'size'}

    def draw_groups(self, data, scales, coordinates, ax, **params):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, params)
        for pinfo in pinfos:
            self.draw(pinfo, scales, coordinates, ax, **params)

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **params):
        # To match ggplot2, the alpha only affects the
        # fill color
        pinfo['fill'] = to_rgba(pinfo['fill'], pinfo['alpha'])
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
