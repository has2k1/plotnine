from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
from itertools import groupby
from operator import itemgetter
import sys
from .geom import geom


class geom_line(geom):
    VALID_AES = ['x', 'y', 'color', 'alpha', 'group', 'linestyle', 'linewidth' 'label', 'size']
    
    def __init__(self, *args, **kwargs):
        super(geom_line, self).__init__(*args, **kwargs)
        self._warning_printed = False
    
    def plot_layer(self, layer):
        layer = dict((k, v) for k, v in layer.items() if k in self.VALID_AES)
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        if 'y' in layer:
            y = layer.pop('y')
        if 'size' in layer:
            # ggplot also supports aes(size=...) but the current mathplotlib is not. See 
            # https://github.com/matplotlib/matplotlib/issues/2658
            if isinstance(layer['size'], list):
                layer['size'] = 4
                if not self._warning_printed:
                    msg = "'geom_line()' currenty does not support the mapping of " +\
                          "size ('aes(size=<var>'), using size=4 as a replacement.\n" +\
                          "Use 'geom_line(size=x)' to set the size for the whole line.\n"
                    sys.stderr.write(msg)
                    self._warning_printed = True
            layer['linewidth'] = layer['size']
            del layer['size']
        if 'linestyle' in layer and 'color' not in layer:
            layer['color'] = 'k'
        if 'group' not in layer:
            plt.plot(x, y, **layer)
        else:
            g = layer.pop('group')
            for k, v in groupby(sorted(zip(x, y, g), key=itemgetter(2)), key=itemgetter(2)):
                x_g, y_g, _ = zip(*v) 
                plt.plot(x_g, y_g, **layer)
