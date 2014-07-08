from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys

from .geom import geom
from ggplot.utils import is_categorical
import numpy as np


class geom_linerange(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black',
                   'linetype': 'solid',
                   'size': 2}
    REQUIRED_AES = {'x', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity', 'cmap': None}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _units = {'alpha', 'color', 'linestyle'}

    def __init__(self, *args, **kwargs):
        super(geom_linerange, self).__init__(*args, **kwargs)
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

        x = pinfo.pop('x')
        x = np.vstack([x, x])

        ymin = pinfo.pop('ymin')
        ymax = pinfo.pop('ymax')
        y = np.vstack([ymin, ymax])

        ax.plot(x, y, **pinfo)
