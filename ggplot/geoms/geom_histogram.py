from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from .geom import geom


class geom_histogram(geom):
    VALID_AES = ['x', 'color', 'alpha', 'label', 'binwidth']
    
    def __init__(self, *args, **kwargs):
        super(geom_histogram, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def plot_layer(self, data, ax):
        # NOTE: Remove 'shape' and fix the result image of the
        # test that depends on it
        groups = {'color', 'alpha', 'shape'}
        groups = groups & set(data.columns)
        if groups:
            for name, _data in data.groupby(list(groups)):
                _data = _data.to_dict('list')
                for ae in groups:
                    _data[ae] = _data[ae][0]
                self._plot(_data, ax)
        else:
            _data = data.to_dict('list')
            self._plot(_data, ax)

    def _plot(self, layer, ax):
        layer = dict((k, v) for k, v in layer.items() if k in self.VALID_AES)
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
            if not self._warning_printed:
                sys.stderr.write("binwidth defaulted to range/30. " +
                             "Use 'binwidth = x' to adjust this.\n")
                self._warning_printed = True
                
        ax.hist(**layer)
