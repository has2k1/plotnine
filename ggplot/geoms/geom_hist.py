import matplotlib.pyplot as plt
from copy import deepcopy
from .geom import geom


class geom_hist(geom):
    VALID_AES = ['x', 'color', 'alpha', 'label']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        plt.hist(**layer)
