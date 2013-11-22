import matplotlib.pyplot as plt
from itertools import groupby
from operator import itemgetter
from copy import deepcopy
from .geom import geom


class geom_line(geom):
    VALID_AES = ['x', 'y', 'color', 'alpha', 'group', 'linestyle', 'linewidth' 'label', 'size']
    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        if 'y' in layer:
            y = layer.pop('y')
        if 'size' in layer:
            layer['linewidth'] = layer['size']
            del layer['size']
        if 'linestyle' in layer and 'color' not in layer:
            layer['color'] = 'k'
        if 'group' not in layer:
            plt.plot(x, y, **layer)
        else:
            g = layer.pop('group')
            for k, v in groupby(sorted(zip(x, y, g), key=itemgetter(2)), key=itemgetter(2)):
                x_g, y_g, _ = zip(*v) 
                plt.plot(x_g, y_g, **layer)
