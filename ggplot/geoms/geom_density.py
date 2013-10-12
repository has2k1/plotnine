import matplotlib.pyplot as plt
from copy import deepcopy
from geom import geom
from scipy.stats import gaussian_kde
import numpy as np


class geom_density(geom):
    VALID_AES = ['x', 'color', 'alpha', 'linestyle', 'label']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        kde = gaussian_kde(x)
        bottom = np.min(x)
        top = np.max(x)
        step = (top - bottom) / 1000.0
        x = np.arange(bottom, top, step)
        y = kde.evaluate(x)
        plt.plot(x, y, **layer)
