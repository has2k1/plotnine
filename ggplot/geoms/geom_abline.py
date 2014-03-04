from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pandas.lib import Timestamp
import numpy as np
from .geom import geom
import pandas as pd

class geom_abline(geom):
    VALID_AES = ['x', 'slope', 'intercept', 'color', 'linestyle', 'alpha', 'label']
    def plot_layer(self, layer, ax):
        layer = dict((k, v) for k, v in layer.items() if k in self.VALID_AES)
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        if 'slope' in layer:
            slope = layer.pop('slope')
        else:
            slope = 1.0
        if 'intercept' in layer:
            intercept = layer.pop('intercept')
        else:
            intercept = 0.0
        if isinstance(x[0], Timestamp):
            ax.set_autoscale_on(False)
            ax.plot(ax.get_xlim(),ax.get_ylim())
        else:
            start, stop = np.max(x), np.min(x)
            step = ((stop-start))  / 100.0
            x_rng = np.arange(start, stop, step)
            y_rng = x_rng * slope + intercept
            ax.plot(x_rng, y_rng, **layer)

