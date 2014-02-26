from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
from .geom import geom

class geom_vline(geom):
    VALID_AES = ['x', 'ymin', 'ymax', 'color', 'linestyle', 'alpha', 'label']
    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        ymin, ymax = None, None
        if 'ymin' in layer:
            ymin = layer.pop('ymin')
        else:
            ymin = 0
        if 'ymax' in layer:
            ymax = layer.pop('ymax')
        else:
            ymax = 0
        if ymin and ymax:
            plt.axvline(x=x, ymin=ymin, ymax=ymax, **layer)
        elif ymin:
            plt.axvline(x=x, ymin=ymin, **layer)
        elif ymax:
            plt.axvline(x=x, ymax=ymax, **layer)
        else:
            plt.axvline(x=x, **layer)


