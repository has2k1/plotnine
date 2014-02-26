from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
import sys
from .geom import geom


class geom_histogram(geom):
    VALID_AES = ['x', 'color', 'alpha', 'label', 'binwidth']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.items() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'binwidth' in layer:
            binwidth = layer.pop('binwidth')
            try:
                binwidth = float(binwidth)
                bottom = plt.np.nanmin(layer['x'])
                top = plt.np.nanmax(layer['x'])
                layer['bins'] = plt.np.arange(bottom, top + binwidth, binwidth)
            except:
                pass
        if 'bins' not in layer:
            layer['bins'] = 30
            sys.stderr.write("binwidth defaulted to range/30. " +
                             "Use 'binwidth = x' to adjust this.\n")
                
        plt.hist(**layer)
