from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom import geom
from ggplot.components import smoothers

import numpy as np

class stat_smooth(geom):
    VALID_AES = ['x', 'y', 'color', 'alpha', 'label', 'se', 'linestyle', 'method', 'span', 'level', 'window']

    def plot_layer(self, data, ax):
        groups = {'color', 'fill', 'linestyle'}
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

        if 'x' in layer:
            x = layer.pop('x')
        if 'y' in layer:
            y = layer.pop('y')
        if 'se' in layer:
            se = layer.pop('se')
        else:
            se = None
        if 'span' in layer:
            span = layer.pop('span')
        else:
            span = 2/3.
        if 'window' in layer:
            window = layer.pop('window')
        else:
            window = int(np.ceil(len(x) / 10.0))
        if 'level' in layer:
            level = layer.pop('level')
        else:
            level = 0.95
        if 'method' in layer:
            method = layer.pop('method')
        else:
            method = None

        idx = np.argsort(x)
        x = np.array(x)[idx]
        y = np.array(y)[idx]

        if method == "lm":
            y, y1, y2 = smoothers.lm(x, y, 1-level)
        elif method == "ma":
            y, y1, y2 = smoothers.mavg(x, y, window=window)
        else:
            y, y1, y2 = smoothers.lowess(x, y, span=span)
        ax.plot(x, y, **layer)
        if se==True:
            ax.fill_between(x, y1, y2, alpha=0.2, color="grey")
