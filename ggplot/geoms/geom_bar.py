from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
import matplotlib.cbook as cbook

from .geom import geom
from ggplot.utils import is_string
from ggplot.utils import is_categorical


class geom_bar(geom):
    DEFAULT_AES = {'alpha': None, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.0, 'weight': None, 'y': None, 'width' : None}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack'}

    _extra_requires = {'y', 'width'}
    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'fill': 'color', 'color': 'edgecolor'}
    # NOTE: Currently, geom_bar does not support mapping
    # to alpha and linestyle. TODO: raise exception
    _units = {'edgecolor', 'color', 'alpha', 'linestyle', 'linewidth'}


    def __init__(self, *args, **kwargs):
        # TODO: Change self.__class__ to geom_bar
        super(geom_bar, self).__init__(*args, **kwargs)
        self.bottom = None
        self.ax = None


    def _plot_unit(self, pinfo, ax):
        categorical = is_categorical(pinfo['x'])

        pinfo.pop('weight')
        x = pinfo.pop('x')
        width_elem = pinfo.pop('width')
        # If width is unspecified, default is an array of 1's
        if width_elem == None:
            width = np.ones(len(x))
        else :
            width = np.array(width_elem)

        # Make sure bottom is initialized and get heights. If we are working on
        # a new plot (using facet_wrap or grid), then reset bottom
        _reset = self.bottom == None or (self.ax != None and self.ax != ax)
        self.bottom = np.zeros(len(x)) if _reset else self.bottom
        self.ax = ax
        heights = np.array(pinfo.pop('y'))


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
        ax.bar(left, heights, width, bottom=self.bottom, **pinfo)
        ax.autoscale()

        if categorical:
            ax.set_xticks(left+width/2)
            ax.set_xticklabels(x)

        # Update bottom positions
        self.bottom = heights + self.bottom
