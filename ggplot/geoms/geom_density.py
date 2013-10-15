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
        if 'fill' in layer:
            fill = layer.pop('fill')
        else:
            fill = None
        kde = gaussian_kde(x)
        bottom = np.min(x)
        top = np.max(x)
        step = (top - bottom) / 1000.0
        x = np.arange(bottom, top, step)
        y = kde.evaluate(x)
        plt.plot(x, y, **layer)
        if fill:
            plt.fill_between(x, y1=np.zeros(len(x)), y2=y, **layer)
