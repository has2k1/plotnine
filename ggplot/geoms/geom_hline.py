import matplotlib.pyplot as plt
from copy import deepcopy
from .geom import geom

class geom_hline(geom):
    VALID_AES = ['y', 'xmin', 'xmax', 'color', 'linestyle', 'alpha', 'label']
    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'y' in layer:
            y = layer.pop('y')
        xmin, xmax = None, None
        if 'xmin' in layer:
            xmin = layer.pop('xmin')
        else:
            xmin = 0
        if 'xmax' in layer:
            xmax = layer.pop('xmax')
        else:
            xmax = 0
        if xmin and xmax:
            plt.axhline(y=y, xmin=xmin, xmax=xmax, **layer)
        elif xmin:
            plt.axhline(y=y, xmin=xmin, **layer)
        elif xmax:
            plt.axhline(y=y, xmax=xmax, **layer)
        else:
            plt.axhline(y=y, **layer)


