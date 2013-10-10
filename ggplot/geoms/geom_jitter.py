from copy import deepcopy
from geom import geom
import numpy as np

class geom_jitter(geom):
    VALID_AES = ['jitter']

    def __radd__(self, gg):
        gg = deepcopy(gg)
        x = gg.data['x']
        y = gg.data['y']
        x = x * np.random.uniform(.9, 1.1, len(x))
        y = y * np.random.uniform(.9, 1.1, len(y))
        gg.data['x'] = x
        gg.data['y'] = y
        return gg

    def plot_layer(self, layer):
        pass
