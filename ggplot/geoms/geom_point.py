import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
from copy import deepcopy
from geom import geom

class geom_point(geom):
    VALID_AES = ['x', 'y', 'size', 'color', 'alpha', 'shape', 'marker', 'label', 'cmap']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        if "size" in layer:
            layer["s"] = layer["size"]
            del layer["size"]

        if "cmap" in layer:
            layer["c"] = layer["color"]
            del layer["color"]
        plt.scatter(**layer)

