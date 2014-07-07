from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from .geom import geom


class geom_line(geom):
    DEFAULT_AES = {'color': 'black', 'alpha': None, 'linetype': 'solid', 'size': 1.0}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _units = {'alpha', 'color', 'linestyle'}

    def __init__(self, *args, **kwargs):
        super(geom_line, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def _plot_unit(self, pinfo, ax):
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

        pinfo = self.sort_by_x(pinfo)
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        ax.plot(x, y, **pinfo)
