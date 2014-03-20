from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom

import matplotlib.pyplot

if hasattr(matplotlib.pyplot, 'hist2d'):
    class stat_bin2d(geom):
        VALID_AES = ['x', 'y', 'alpha', 'label']

        def plot_layer(self, data, ax):
            groups = {'color', 'alpha'}
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

            x = layer.pop('x')
            y = layer.pop('y')

            ax.hist2d(x, y, cmap=matplotlib.pyplot.cm.Blues, **layer)
else:
    def stat_bin2d(*args, **kwargs):
        import matplotlib
        print("stat_bin2d only works with newer matplotlib versions, but found only %s" %
              matplotlib.__version__)
