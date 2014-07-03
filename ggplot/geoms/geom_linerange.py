from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib as mpl
from .geom import geom
import numpy as np

class geom_linerange(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black',# 'fill': None,
                   'linetype': 'solid',
                   #'shape': 'o',
                   'size': 2}
    REQUIRED_AES = {'x', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity', 'cmap':None}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _units = {'alpha', 'color', 'linestyle'}# 'marker'}

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

        #_abscent = {None: pinfo['color'], False: ''}
        #try:
        #    if pinfo['facecolor'] in _abscent:
        #        pinfo['facecolor'] = _abscent[pinfo['facecolor']]
        #except TypeError:
        #    pass

        # for some reason, scatter doesn't default to the same color styles
        # as the axes.color_cycle
        #f "color" not in pinfo and self.params['cmap'] is None:
        #   pinfo["color"] = mpl.rcParams.get("axes.color_cycle", ["#333333"])[0]

        #if self.params['position'] == 'jitter':
        #    pinfo['x'] *= np.random.uniform(.9, 1.1, len(pinfo['x']))
        #    pinfo['y'] *= np.random.uniform(.9, 1.1, len(pinfo['y']))

        x = pinfo.pop('x')
        x = np.vstack([x, x])

        ymin = pinfo.pop('ymin')
        ymax = pinfo.pop('ymax')
        y = np.vstack([ymin, ymax])

        ax.plot(x, y, **pinfo)
