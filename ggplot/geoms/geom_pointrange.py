from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys

import matplotlib as mpl
from .geom import geom
from ggplot.utils import is_categorical
import numpy as np


class geom_pointrange(geom):
    """Plot intervals represented by vertical lines with a point in each interval

     Parameters
     ---------

     x
         x values of data
     y
         y value of the point for each x
     ymin
         lower end of the interval for each x
     ymax
         upper end of the interval for each x
     alpha : float
         alpha value, defaults to 1
     color : string
         line color, defaults to 'black'
     fill : string
         Fill type for the points, defaults to 'None'
     linetype : string
         line type, defaults to 'solid'
     shape : string
         shape of the points, defaults to 'o' (i.e. circles)
     size : string
         width of the line and size of the point, defaults to 2

     Examples
     --------

     .. plot::
         :include-source:

         import numpy as np
         import pandas as pd
         from ggplot import *

         np.random.seed(42)
         x = np.linspace(0.5, 9.5, num=10)
         y = np.random.randn(10)
         ymin = y - np.random.uniform(0,1, size=10)
         ymax = y + np.random.uniform(0,1, size=10)

         data = pd.DataFrame({'x': x, 'y': y, 'ymin': ymin, 'ymax': ymax})

         ggplot(aes(x='x', y='y', ymin='ymin', ymax='ymax'), data) \
             + geom_pointrange()

    """

    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'linetype': 'solid',
                   'shape': 'o',
                   'size': 2}
    REQUIRED_AES = {'x', 'y', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity', 'cmap': None}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle', 'shape': 'marker', 'fill': 'facecolor'}
    _units = {'alpha', 'color', 'linestyle', 'marker'}

    def __init__(self, *args, **kwargs):
        super(geom_pointrange, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def _plot_unit(self, pinfo, ax):
        # If x is categorical, calculate positions to plot
        categorical = is_categorical(pinfo['x'])
        if categorical:
            x = pinfo.pop('x')
            new_x = np.arange(len(x))
            ax.set_xticks(new_x)
            ax.set_xticklabels(x)
            pinfo['x'] = new_x

        if 'linewidth' in pinfo and isinstance(pinfo['linewidth'], list):
            # ggplot also supports aes(size=...) but the current mathplotlib
            # is not. See https://github.com/matplotlib/matplotlib/issues/2658
            pinfo['linewidth'] = 4
            if not self._warning_printed:
                msg = "'geom_line()' currenty does not support the mapping of " +\
                      "size ('aes(size=<var>'), using size=4 as a replacement.\n" +\
                      "Use 'geom_line(size=x)' to set the size for the whole line.\n"
                sys.stderr.write(msg)
                self._warning_printed = True

        # Plotting the line
        pinfoline = dict(pinfo)
        del pinfoline['marker']
        del pinfoline['facecolor']
        del pinfoline['y']

        x = pinfoline.pop('x')
        x = np.vstack([x, x])

        ymin = pinfoline.pop('ymin')
        ymax = pinfoline.pop('ymax')
        y = np.vstack([ymin, ymax])

        ax.plot(x, y, **pinfoline)

        # Plotting the points
        pinfopoint = dict(pinfo)
        del pinfopoint['ymin']
        del pinfopoint['ymax']
        del pinfopoint['linestyle']

        _abscent = {None: pinfopoint['color'], False: ''}
        try:
            if pinfopoint['facecolor'] in _abscent:
                pinfopoint['facecolor'] = _abscent[pinfopoint['facecolor']]
        except TypeError:
            pass

        # for some reason, scatter doesn't default to the same color styles
        # as the axes.color_cycle
        if "color" not in pinfopoint and self.params['cmap'] is None:
            pinfopoint["color"] = mpl.rcParams.get("axes.color_cycle", ["#333333"])[0]

        pinfopoint['s'] = pinfopoint.pop('linewidth')**2*4

        ax.scatter(**pinfopoint)
