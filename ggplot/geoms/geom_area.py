from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom



class geom_area(geom):
    VALID_AES = ['x', 'ymin', 'ymax', 'color', 'alpha', 'label']

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
        y1 = layer.pop('ymin')
        y2 = layer.pop('ymax')
        ax.fill_between(x, y1, y2, **layer)

