from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
import matplotlib.cbook as cbook
from .geom import geom
from pandas.lib import Timestamp


class geom_bar(geom):
    DEFAULT_AES = {'alpha': None, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.0, 'weight': None, 'y': None}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack'}

    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'fill': 'facecolor', 'color': 'edgecolor'}

    # Every geom should be able to list the essential parameters
    # that it requires to draw the plot. This would include those
    # computed by the stats but not part of the user API
    # _requires = {'x', 'y', 'width'}

    # NOTE: Currently, geom_bar does not support mapping
    # to alpha and linestyle. TODO: raise exception
    _units = {'alpha', 'linestyle', 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        pinfo.pop('weight')
        x = pinfo.pop('x')
        width = pinfo.pop('width')
        heights = pinfo.pop('y')
        labels = x
        _left_gap = 0.2
        _spacing_factor = 0.1     # of the bin width

        if cbook.is_numlike(x[0]):
            left = np.array([x[i]-width[i]/2 for i in range(len(x))])
            _sep = width[0] * _spacing_factor
        else:
            _breaks = [0] + [width] * len(x)
            left = np.cumsum(_breaks[:-1])
            _sep = width * _spacing_factor

        left = left + _left_gap + [_sep * i for i in range(len(left))]


        # mapped coloring aesthetics are required in ascending order acc. x
        # NOTE: This is now broken
        # Solution: When the statistics change the length of an aesthetic,
        # all other aesthetics must have their lengths changed
        for ae in ('edgecolor', 'facecolor'):
            if isinstance(pinfo[ae], list):
                pinfo[ae] = [color for _, color in
                             sorted(set(zip(x, pinfo[ae])))]

        # TODO: When x is numeric, need to use better xticklabels
        ax.bar(left, heights, width, **pinfo)
        ax.autoscale()
        ax.set_xticks(left+width/2)
        ax.set_xticklabels(x)
