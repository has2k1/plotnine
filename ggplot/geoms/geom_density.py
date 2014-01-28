from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
from copy import deepcopy
from .geom import geom
from scipy.stats import gaussian_kde
import numpy as np


class geom_density(geom):
    VALID_AES = ['x', 'color', 'alpha', 'linestyle', 'fill', 'label']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        else:
            raise Exception("geom_density(): Need a aesthetic x mapping!")
            
        if 'fill' in layer:
            fill = layer.pop('fill')
        else:
            fill = None
        try:
            float(x[0])
        except:
            try:
                # try to use it as a pandas.tslib.Timestamp
                x = [ts.toordinal() for ts in x]
            except:
                raise Exception("geom_density(): aesthetic x mapping needs to be convertable to float!")         
        kde = gaussian_kde(x)
        bottom = np.min(x)
        top = np.max(x)
        step = (top - bottom) / 1000.0
        x = np.arange(bottom, top, step)
        y = kde.evaluate(x)
        plt.plot(x, y, **layer)
        if fill:
            plt.fill_between(x, y1=np.zeros(len(x)), y2=y, **layer)
