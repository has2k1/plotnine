from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
from copy import deepcopy
from .geom import geom
import pandas as pd

class stat_bin2d(geom):
    VALID_AES = ['x', 'y', 'alpha', 'label']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        x = layer.pop('x')
        y = layer.pop('y')

        plt.hist2d(x, y, cmap=plt.cm.Blues, **layer)
