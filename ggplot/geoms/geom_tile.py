from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd
from .geom import geom


class geom_tile(geom):
    VALID_AES = {'x', 'y', 'alpha', 'colour', 'fill', 'linetype', 'size'}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _groups = {'fill'}
    _aes_renames = {'linetype': 'linestyle'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        fill = pinfo.pop('fill')
        X = pd.DataFrame({'x': x,
                          'y': y,
                          'fill': fill}).set_index(['x', 'y']).unstack(0)
        x_ticks = range(0, len(set(x)))
        y_ticks = range(0, len(set(y)))

        ax.imshow(X, interpolation='nearest', **pinfo)
        ax.set_xticklabels(x)
        ax.set_xticks(x_ticks)
        ax.set_yticklabels(y)
        ax.set_yticks(y_ticks)
