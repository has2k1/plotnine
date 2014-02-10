from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
from .geom import geom
import pandas as pd

if hasattr(plt, 'hist2d'):
    class stat_bin2d(geom):
        VALID_AES = ['x', 'y', 'alpha', 'label']

        def plot_layer(self, layer):
            layer = dict((k, v) for k, v in layer.items() if k in self.VALID_AES)
            layer.update(self.manual_aes)

            x = layer.pop('x')
            y = layer.pop('y')

            plt.hist2d(x, y, cmap=plt.cm.Blues, **layer)
else:
    def stat_bin2d(*args, **kwargs):
        import matplotlib
        print("stat_bin2d only works with newer matplotlib versions, but found only %s" %
              matplotlib.__version__)
