from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.image as mpimg
import numpy as np
from .geom import geom
import os

_ROOT = os.path.abspath(os.path.dirname(__file__))


class geom_now_its_art(geom):
    VALID_AES = {'x', 'y'}

    def _plot_unit(self, data, ax):
        x = np.array(pinfo['x'])
        y = np.array(pinfo['y'])

        img = mpimg.imread(os.path.join(_ROOT, 'bird.png'))
        # plt.imshow(img, alpha=0.5, extent=[x.min(), x.max(), y.min(), y.max()])
        ax.imshow(img, alpha=0.5)
        print ("Put a bird on it!")
