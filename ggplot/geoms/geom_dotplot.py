from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
import matplotlib.cbook as cbook

from .geom import geom
from ggplot.utils import is_string
from ggplot.utils import is_categorical


class geom_dotplot(geom):
    DEFAULT_AES = {'alpha': None, 'color': None, 'fill': '#333333',
                   'weight': None, 'y': None}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack'}

    _extra_requires = {'y', 'width'}
    _aes_renames = {'size': 'linewidth', 'fill': 'color', 'color': 'edgecolor'}
    # NOTE: Currently, geom_dotplot does not support mapping
    # to alpha TODO: raise exception
    _units = {'alpha'}

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
        categorical = is_categorical(pinfo['x'])
        # If x is not numeric, the bins are sorted acc. to x
        # so the list type aesthetics must be sorted too
        if categorical:
            pinfo = self._sort_list_types_by_x(pinfo)

        pinfo.pop('weight')
        x = pinfo.pop('x')
        width = np.array(pinfo.pop('width'))
        heights = pinfo.pop('y')
        labels = x

        # layout and spacing
        #
        # matplotlib needs the left of each bin and it's width
        # if x has numeric values then:
        #   - left = x - width/2
        # otherwise x is categorical:
        #   - left = cummulative width of previous bins starting
        #            at zero for the first bin
        #
        # then add a uniform gap between each bin
        #   - the gap is a fraction of the width of the first bin
        #     and only applies when x is categorical
        _left_gap = 0
        _spacing_factor = 0     # of the bin width
        if not categorical:
            left = np.array([x[i]-width[i]/2 for i in range(len(x))])
        else:
            _left_gap = 0.2
            _spacing_factor = 0.105     # of the bin width
            _breaks = np.append([0], width)
            left = np.cumsum(_breaks[:-1])

        _sep = width[0] * _spacing_factor
        left = left + _left_gap + [_sep * i for i in range(len(left))]


        step = np.max(heights) / 24.
        for (_x, _y) in zip(left + width, heights):
            yvals = np.arange(0, _y, step) + step/2
            pinfo['s'] = 240
            ax.scatter(np.repeat(_x, len(yvals)), yvals, **pinfo)
        ax.autoscale()

        if categorical:
            ax.set_xticks(left+width)
            ax.set_xticklabels(x)

