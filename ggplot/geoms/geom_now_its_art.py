import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from copy import deepcopy
from .geom import geom
import os

_ROOT = os.path.abspath(os.path.dirname(__file__))


class geom_now_its_art(geom):
    VALID_AES = ['x', 'y']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        x = np.array(layer['x'])
        y = np.array(layer['y'])

        img = mpimg.imread(os.path.join(_ROOT, 'bird.png'))
        # plt.imshow(img, alpha=0.5, extent=[x.min(), x.max(), y.min(), y.max()])
        plt.imshow(img, alpha=0.5)
        print "Put a bird on it!"
