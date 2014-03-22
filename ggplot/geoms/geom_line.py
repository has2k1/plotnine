from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from itertools import groupby
from operator import itemgetter
import sys
from .geom import geom


class geom_line(geom):
    VALID_AES = {'x', 'y', 'color', 'alpha', 'linetype', 'size', 'group'}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity', 'label': ''}

    _groups = {'color', 'alpha', 'linetype'}
    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}

    def __init__(self, *args, **kwargs):
        super(geom_line, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        pinfo['label'] = self.params['label']

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
        if 'linestyle' in pinfo and 'color' not in pinfo:
            pinfo['color'] = 'k'
        if 'group' not in pinfo:
            ax.plot(x, y, **pinfo)
        else:
            g = pinfo.pop('group')
            for k, v in groupby(sorted(zip(x, y, g), key=itemgetter(2)),
                                key=itemgetter(2)):
                x_g, y_g, _ = zip(*v)
                ax.plot(x_g, y_g, **pinfo)
