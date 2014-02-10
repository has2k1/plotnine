from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .geom import geom


class geom_tile(geom):
    VALID_AES = ['x', 'y', 'fill']

    def plot_layer(self, layer):
        layer = dict((k, v) for k, v in layer.iteritems() if k in self.VALID_AES)
        layer.update(self.manual_aes)

        x = layer.pop('x')
        y = layer.pop('y')
        fill = layer.pop('fill')
        X = pd.DataFrame({'x': x,
                          'y': y,
                          'fill': fill}).set_index(['x', 'y']).unstack(0)
        x_ticks = range(0, len(set(x)))
        y_ticks = range(0, len(set(y)))

        plt.imshow(X, interpolation='nearest', **layer)
        return [
            {'function': 'set_xticklabels', 'args': [x]},
            {'function': 'set_xticks', 'args': [x_ticks]},
            {'function': 'set_yticklabels', 'args': [y]},
            {'function': 'set_yticks', 'args': [y_ticks]}
        ]
