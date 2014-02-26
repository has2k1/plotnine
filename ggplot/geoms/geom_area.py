from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .geom import geom



class geom_area(geom):
    VALID_AES = ['x', 'ymin', 'ymax', 'color', 'alpha', 'label']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        x = layer.pop('x')
        y1 = layer.pop('ymin')
        y2 = layer.pop('ymax')
        plt.fill_between(x, y1, y2, **layer)

