import matplotlib.pyplot as plt
from copy import deepcopy
from geom import geom

class geom_point(geom):
    VALID_AES = ['x', 'y', 'size', 'color', 'alpha', 'shape', 'marker', 'label']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        plt.scatter(**layer)
