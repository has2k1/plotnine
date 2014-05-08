from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from .geom import geom
import numpy as np


class geom_pointrange(geom):
    DEFAULT_AES = {'color': 'black', 'alpha': None, 'linetype': 'solid', 'size': 1.0}
    REQUIRED_AES = {'x', 'y', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _units = {'alpha', 'color', 'linestyle'}

    def __init__(self, *args, **kwargs):
        super(geom_pointrange, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def _plot_unit(self, pinfo, ax):
        if 'linewidth' in pinfo and isinstance(pinfo['linewidth'], list):
            # ggplot also supports aes(size=...) but the current mathplotlib
            # is not. See https://github.com/matplotlib/matplotlib/issues/2658
            pinfo['linewidth'] = 4
            if not self._warning_printed:
                msg = "'geom_lineragne()' currenty does not support the mapping of " +\
                      "size ('aes(size=<var>'), using size=4 as a replacement.\n" +\
                      "Use 'geom_pointrange(size=x)' to set the size for the whole line.\n"
                sys.stderr.write(msg)
                self._warning_printed = True

        x = pinfo.pop('x')
        y = pinfo.pop('y')
        ymin = pinfo.pop('ymin')
        ymax = pinfo.pop('ymax')

        _left_gap = 0
        _spacing_factor = 0
        _sep = 0
        
        left = np.arange(0, len(x) + 2)
        i = 0
        for (_x, _y, _ymin, _ymax) in zip(x, y, ymin, ymax):
            i += 1
            ax.scatter(i, _y, **pinfo)
            ax.plot([i, i], [_ymin, _ymax], **pinfo)

        ax.set_xticks(left)
        ax.set_xticklabels([""] + x)
