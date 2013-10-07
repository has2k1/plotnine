import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
from geom import geom

class geom_abline(geom):
    VALID_AES = ['x', 'slope', 'intercept', 'color', 'alpha', 'label']
    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
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
        step = (np.max(x) - np.min(x)) / 100.0
        x_rng = np.arange(np.min(x), np.max(x), step)
        y_rng = x_rng * slope + intercept
        plt.plot(x_rng, y_rng, **layer)
