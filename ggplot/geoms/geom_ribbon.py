from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import make_color_tuples
from .geom import geom


class geom_ribbon(geom):
    DEFAULT_AES = {'alpha': 1, 'color': '', 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.0}
    REQUIRED_AES = {'x', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    guide_geom = 'polygon'

    _aes_renames = {'linetype': 'linestyle', 'ymin': 'y1', 'ymax': 'y2',
                    'size': 'linewidth', 'fill': 'facecolor',
                    'color': 'edgecolor'}
    _units = {'alpha', 'edgecolor', 'facecolor', 'linestyle', 'linewidth'}

    def draw_groups(self, data, scales, ax, **kwargs):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, kwargs)
        for pinfo in pinfos:
            self.draw(pinfo, scales, ax, **kwargs)

    @staticmethod
    def draw(pinfo, scales, ax, **kwargs):
        for key in ('y', 'weight', 'group'):
            try:
                del pinfo[key]
            except KeyError:
                pass

        # To much ggplot2, the alpha only affects the
        # fill color
        pinfo['facecolor'] = make_color_tuples(
            pinfo['facecolor'], pinfo.pop('alpha'))
        ax.fill_between(**pinfo)
