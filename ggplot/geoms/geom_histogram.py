from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from .geom import geom


class geom_histogram(geom):
    VALID_AES = {'x', 'alpha', 'color', 'fill', 'linetype',
                 'size', 'weight'}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack', 'label': ''}
    
    _groups = {'color', 'alpha', 'shape'}
    def __init__(self, *args, **kwargs):
        super(geom_histogram, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def plot(self, layer, ax):
        layer['label'] = self.params['label']

        if 'binwidth' in layer:
            binwidth = layer.pop('binwidth')
            try:
                binwidth = float(binwidth)
                bottom = np.nanmin(layer['x'])
                top = np.nanmax(layer['x'])
                layer['bins'] = np.arange(bottom, top + binwidth, binwidth)
            except:
                pass
        if 'bins' not in layer:
            layer['bins'] = 30
            if not self._warning_printed:
                sys.stderr.write("binwidth defaulted to range/30. " +
                             "Use 'binwidth = x' to adjust this.\n")
                self._warning_printed = True

        ax.hist(**layer)
