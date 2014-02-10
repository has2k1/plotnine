from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
from itertools import groupby
from operator import itemgetter
from .geom import geom


class geom_step(geom):
    VALID_AES = ['x', 'y', 'color', 'alpha', 'linestyle', 'label', 'size',
                 'group']
    def plot_layer(self, layer):
        layer = dict((k, v) for k, v in layer.items() if k in self.VALID_AES)
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        if 'y' in layer:
            y = layer.pop('y')
        if 'size' in layer:
            layer['markersize'] = layer['size']
            del layer['size']
        if 'linestyle' in layer and 'color' not in layer:
            layer['color'] = 'k'

        x_stepped = []
        y_stepped = []
        for i in range(len(x) - 1):
            x_stepped.append(x[i])
            x_stepped.append(x[i+1])
            y_stepped.append(y[i])
            y_stepped.append(y[i])

        if 'group' not in layer:
            plt.plot(x_stepped, y_stepped, **layer)
        else:
            g = layer.pop('group')
            for k, v in groupby(sorted(zip(x_stepped, y_stepped, g), key=itemgetter(2)), key=itemgetter(2)):
                x_g, y_g, _ = zip(*v) 
                plt.plot(x_g, y_g, **layer)
