from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from itertools import groupby
from operator import itemgetter
from .geom import geom


class geom_step(geom):

    VALID_AES = {'x', 'y', 'color', 'alpha', 'linetype', 'size',
                 'group'}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
            'direction': 'hv', 'group': None, 'label': ''}

    _groups = {'color', 'alpha', 'linestyle', 'size'}
    _translations = {'size': 'markersize'}

    def plot(self, layer, ax):
        x = layer.pop('x')
        y = layer.pop('y')
        layer['label'] = self.params['label']
        if 'linetype' in layer and 'color' not in layer:
            layer['color'] = 'k'

        x_stepped = []
        y_stepped = []
        for i in range(len(x) - 1):
            x_stepped.append(x[i])
            x_stepped.append(x[i+1])
            y_stepped.append(y[i])
            y_stepped.append(y[i])

        # TODO: Fix this when the group aes/parameter is handled
        # across all geoms
        if 'group' not in layer:
            ax.plot(x_stepped, y_stepped, **layer)
        else:
            g = layer.pop('group')
            for k, v in groupby(sorted(zip(x_stepped, y_stepped, g),
                                       key=itemgetter(2)), key=itemgetter(2)):
                x_g, y_g, _ = zip(*v)
                ax.plot(x_g, y_g, **layer)
