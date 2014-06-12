from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import matplotlib.cbook as cbook

from .geom import geom
from ggplot.utils import is_string


class geom_area(geom):
    DEFAULT_AES = {'alpha': None, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.0}
    REQUIRED_AES = {'x', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'stack'}

    _aes_renames = {'linetype': 'linestyle', 'ymin': 'y1', 'ymax': 'y2',
                    'size': 'linewidth', 'fill': 'facecolor', 'color': 'edgecolor'}
    _units = { 'alpha', 'edgecolor', 'facecolor', 'linestyle', 'linewidth'}

    def _sort_list_types_by_x(self, pinfo):
        """
        Sort the lists in pinfo according to pinfo['x']
        """
        # Remove list types from pinfo
        _d = {}
        for k in list(pinfo.keys()):
            if not is_string(pinfo[k]) and cbook.iterable(pinfo[k]):
                _d[k] = pinfo.pop(k)

        # Sort numerically if all items can be cast
        try:
            x = list(map(np.float, _d['x']))
        except ValueError:
            x = _d['x']
        idx = np.argsort(x)

        # Put sorted lists back in pinfo
        for key in _d:
            pinfo[key] = [_d[key][i] for i in idx]

        return pinfo

    def _plot_unit(self, pinfo, ax):
        pinfo = self._sort_list_types_by_x(pinfo)
        ax.fill_between(**pinfo)
