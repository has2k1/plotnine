from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom import geom


class geom_area(geom):
    DEFAULT_AES = {'alpha': None, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.0}
    REQUIRED_AES = {'x', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'stack'}

    _aes_renames = {'linetype': 'linestyle', 'ymin': 'y1', 'ymax': 'y2',
                    'size': 'linewidth', 'fill': 'facecolor', 'color': 'edgecolor'}
    _units = { 'alpha', 'edgecolor', 'facecolor', 'linestyle', 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        pinfo = self.sort_by_x(pinfo)
        ax.fill_between(**pinfo)
