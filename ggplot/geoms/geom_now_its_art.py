from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import matplotlib.image as mpimg

from .geom import geom

_ROOT = os.path.abspath(os.path.dirname(__file__))


class geom_now_its_art(geom):
    DEFAULT_AES = {'alpha': 0.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    @staticmethod
    def draw(pinfo, scales, ax, **kwargs):
        img = mpimg.imread(os.path.join(_ROOT, 'bird.png'))
        ax.imshow(img, alpha=pinfo['alpha'])
        print ("Put a bird on it!")
