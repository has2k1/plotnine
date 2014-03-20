from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom

class geom_hline(geom):
    VALID_AES = ['y', 'xmin', 'xmax', 'color', 'linestyle', 'alpha', 'label']

    def plot_layer(self, data, ax):
        groups = {'color', 'alpha', 'linestyle'}
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
        if 'y' in layer:
            y = layer.pop('y')
        xmin, xmax = None, None
        if 'xmin' in layer:
            xmin = layer.pop('xmin')
        else:
            xmin = 0
        if 'xmax' in layer:
            xmax = layer.pop('xmax')
        else:
            xmax = 0
        if xmin and xmax:
            ax.axhline(y=y, xmin=xmin, xmax=xmax, **layer)
        elif xmin:
            ax.axhline(y=y, xmin=xmin, **layer)
        elif xmax:
            ax.axhline(y=y, xmax=xmax, **layer)
        else:
            ax.axhline(y=y, **layer)


