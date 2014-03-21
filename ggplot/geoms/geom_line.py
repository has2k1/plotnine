from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from itertools import groupby
from operator import itemgetter
import sys
from .geom import geom


class geom_line(geom):
    VALID_AES = {'x', 'y', 'color', 'alpha', 'linetype', 'size', 'group'}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity', 'label': ''}

    _groups = {'color', 'alpha', 'linestyle'}
    _translations = {'size': 'linewidth'}

    def __init__(self, *args, **kwargs):
        super(geom_line, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def plot(self, layer, ax):
        x = layer.pop('x')
        y = layer.pop('y')
        layer['label'] = self.params['label']

        if 'linewidth' in layer and isinstance(layer['linewidth'], list):
            # ggplot also supports aes(size=...) but the current mathplotlib
            # is not. See https://github.com/matplotlib/matplotlib/issues/2658
            layer['linewidth'] = 4
            if not self._warning_printed:
                msg = "'geom_line()' currenty does not support the mapping of " +\
                      "size ('aes(size=<var>'), using size=4 as a replacement.\n" +\
                      "Use 'geom_line(size=x)' to set the size for the whole line.\n"
                sys.stderr.write(msg)
                self._warning_printed = True
        if 'linestyle' in layer and 'color' not in layer:
            layer['color'] = 'k'
        if 'group' not in layer:
            ax.plot(x, y, **layer)
        else:
            g = layer.pop('group')
            for k, v in groupby(sorted(zip(x, y, g), key=itemgetter(2)),
                                key=itemgetter(2)):
                x_g, y_g, _ = zip(*v)
                ax.plot(x_g, y_g, **layer)
