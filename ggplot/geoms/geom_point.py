from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import Normalize
import numpy as np
from copy import deepcopy
from .geom import geom
import numpy as np

class geom_point(geom):
    VALID_AES = ['x', 'y', 'size', 'color', 'alpha', 'shape', 'label', 'cmap',
                 'position']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        if "size" in layer:
            layer["s"] = layer["size"]
            del layer["size"]

        if "shape" in layer:
            layer["marker"] = layer["shape"]
            del layer["shape"]

        # for some reason, scatter doesn't default to the same color styles
        # as the axes.color_cycle
        if "color" not in layer and "cmap" not in layer:
            layer["color"] = mpl.rcParams.get("axes.color_cycle", ["#333333"])[0]
        
        if "position" in layer:
            del layer["position"]
            layer['x'] *= np.random.uniform(.9, 1.1, len(layer['x']))
            layer['y'] *= np.random.uniform(.9, 1.1, len(layer['y']))

        plt.scatter(**layer)

