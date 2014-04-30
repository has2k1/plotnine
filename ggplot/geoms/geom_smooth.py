from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom import geom
from ggplot.components import smoothers

import numpy as np

class geom_smooth(geom):
    DEFAULT_AES = {'alpha': 0.4, 'color': 'black', 'fill': '#999999',
                   'linetype': 'solid', 'size': 1.0,
                   'ymin': None, 'ymax': None}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'smooth', 'position': 'identity'}

    _aes_renames = {'linetype': 'linestyle', 'fill': 'facecolor',
                    'size': 'linewidth', 'ymin': 'y1', 'ymax': 'y2'}
    _units = {'color', 'facecolor', 'linestyle', 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y = pinfo.pop('y')

        # Remove parameters not needed for the
        # line/curve plot
        y1 = pinfo.pop('y1')
        y2 = pinfo.pop('y2')
        facecolor = pinfo.pop('facecolor')
        alpha = pinfo.pop('alpha')

        ax.plot(x, y, **pinfo)

        # If the fill limits have been computed,
        # then filling is required
        if (y1 is not None) and (y2 is not None):
            del pinfo['color']
            del pinfo['linewidth']
            pinfo['facecolor'] = facecolor
            pinfo['alpha'] = alpha
            ax.fill_between(x, y1, y2, **pinfo)
