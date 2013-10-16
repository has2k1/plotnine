import matplotlib.pyplot as plt
from copy import deepcopy
from .geom import geom

class geom_line(geom):
    VALID_AES = ['x', 'y', 'color', 'alpha', 'linestyle', 'label', 'size']
    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        if 'y' in layer:
            y = layer.pop('y')
        if 'size' in layer:
            layer['markersize'] = layer['size']
            del layer['size']

        if 'linestyle' in layer and 'color' not in layer:
            layer['color'] = 'k'

        plt.plot(x, y, **layer)
