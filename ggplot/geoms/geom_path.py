from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.collections import LineCollection

from ..utils import make_iterable, make_iterable_ntimes
from ..utils import hex_to_rgba
from .geom import geom


class geom_path(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'linetype': 'solid',
                   'size': 1.0}

    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}

    def draw(self, pinfo, scales, ax, **kwargs):
        x = pinfo.pop('x')
        y = pinfo.pop('y')

        alpha = make_iterable(pinfo.pop('alpha'))
        color = make_iterable(pinfo.pop('color'))

        if len(color) == 1 and len(alpha) > 1:
            color = make_iterable_ntimes(color[0], len(alpha))

        # bind the alpha value(s) to the color
        if len(color) == len(alpha):
            color = hex_to_rgba(color, alpha)
        else:
            color = hex_to_rgba(color, alpha[0])

        lines = [((x[i], y[i]), (x[i+1], y[i+1])) for i in range(len(x)-1)]
        lines = LineCollection(lines,
                               color=color,
                               linewidths=pinfo['linewidth'],
                               linestyles=pinfo['linestyle'])
        ax.add_collection(lines)
