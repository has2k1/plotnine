from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom



class geom_area(geom):
    VALID_AES = {'x', 'ymax', 'ymin', 'alpha', 'color',
                 'fill', 'linetype', 'size'}
    REQUIRED_AES = {'x', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'stack'}

    _groups = {'color', 'alpha'}

    def plot(self, layer, ax):
        x = layer.pop('x')
        y1 = layer.pop('ymin')
        y2 = layer.pop('ymax')
        ax.fill_between(x, y1, y2, **layer)

